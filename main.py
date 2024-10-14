import pyttsx3
import aiml
import os
import pyaudio
from vosk import Model, KaldiRecognizer
import json
import threading
import queue
import time
from utils.pdf_loader import load_pdfs, semantic_search_pdfs
from utils.aiml_loader import load_aiml
from utils.app_controller import open_application, close_application
from utils.web_search import search_web, summarize_results
from utils.clap_detector import ClapDetector  
from utils.database import initialize_database, get_faq, log_interaction

engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 60)

aiml_kernel = aiml.Kernel()

vosk_model_path = "model"
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError("Vosk model not found! Please check the 'model' directory.")
model = Model(vosk_model_path)

stream_running = True
pdf_data = {}
current_application = None
lock = threading.Lock()

task_queue = queue.Queue()
stop_event = threading.Event()  

context = {
    "last_command": None,
    "current_application": None,
    "mode": None,  
}

clap_detector = ClapDetector()

initialize_database()

def update_context(key, value):
    """Update the global context dictionary."""
    global context
    with lock:
        context[key] = value

def speak(text):
    """Convert text to speech."""
    with lock: 
        engine.say(text)
        engine.runAndWait()

def listen():
    """Listen to voice commands and convert to text using Vosk."""
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    global stream_running
    while stream_running:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            return result['text']

def load_and_train_models():
    """Load and train AIML and PDF models."""
    global pdf_data
    if os.path.exists('data/aiml/'):
        load_aiml('data/aiml/')
        aiml_kernel.respond('LOAD AIML B')
    if os.path.exists('data/pdfs/'):
        pdf_data = load_pdfs('data/pdfs/')

def ask_for_mode():
    """Prompt user to select mode via voice command."""
    speak("Which mode would you like to choose? 1 for Conversation, 2 for Geek, 3 for Controller, or 4 for Study. Say shutdown to exit.")
    mode = listen()
    return mode

def recognize_intent(command):
    """Recognize the intent of the command (open, close, search, etc.)."""
    command = command.lower()
    if "open" in command:
        return "open_application"
    elif "close" in command:
        return "close_application"
    elif "transcribe" in command:
        return "geek_mode"
    elif "study" in command:
        return "study_mode"
    elif "search" in command: 
        return "search_web"
    elif "exit" in command:
        return "exit"
    elif "faq" in command:  
        return "faq"
    else:
        return "conversation"

def cross_mode_tasks(command):
    """Handle tasks from other modes within the current mode."""
    intent = recognize_intent(command)

    if intent == "open_application":
        app_name = command.replace("open", "").strip()
        open_application(app_name)
    elif intent == "close_application":
        close_application(context['current_application'])
        context['current_application'] = None
    elif intent == "geek_mode":
        os.system(f"xdotool type '{command}'")
    elif intent == "study_mode":
        pdf_response = semantic_search_pdfs(command, pdf_data)
        if pdf_response:
            speak(pdf_response)
    elif intent == "search_web":  
        query = command.replace("search", "").strip()
        results = search_web(query)
        summary = summarize_results(results)
        speak(summary)
    elif intent == "faq":  
        question = command.replace("faq", "").strip()
        answer = get_faq(question)
        if answer:
            speak(answer)
        else:
            speak("I couldn't find an answer to your question.")

def mode_task_wrapper(mode_function, mode_name):
    """Wrapper to run mode tasks with concurrency and interruption handling."""
    stop_event.clear() 
    update_context('mode', mode_name)
    
    try:
        mode_function()
    except Exception as e:
        speak(f"An error occurred in {mode_name}: {str(e)}")
    finally:
        speak(f"Exiting {mode_name}.")
        stop_event.set()

def task_scheduler():
    """Background task scheduler for concurrent tasks."""
    while not stop_event.is_set():
        time.sleep(1)

def select_mode(mode):
    """Switch between modes based on user input."""
    update_context('mode', mode)  
    
    if "one" in mode or "1" in mode or "conversation" in mode:
        threading.Thread(target=mode_task_wrapper, args=(conversation_mode, "Conversation Mode")).start()
    elif "two" in mode or "2" in mode or "geek" in mode:
        threading.Thread(target=mode_task_wrapper, args=(geek_mode, "Geek Mode")).start()
    elif "three" in mode or "3" in mode or "controller" in mode:
        threading.Thread(target=mode_task_wrapper, args=(controller_mode, "Controller Mode")).start()
    elif "four" in mode or "4" in mode or "study" in mode:
        threading.Thread(target=mode_task_wrapper, args=(study_mode, "Study Mode")).start()
    elif "shutdown" in mode:
        speak("Shutting down.")
        global stream_running
        stream_running = False
        stop_event.set() 
        return
    else:
        speak("Invalid mode selected. Please try again.")
    
    mode = ask_for_mode()
    select_mode(mode)

def conversation_mode():
    """Handle Conversation Mode using AIML, with task switching."""
    speak("Entering conversation mode.")
    while not stop_event.is_set():
        command = listen()
        if command == "exit":
            break
        
        log_interaction(command, "Processing command")
        
        if recognize_intent(command) != "conversation":
            cross_mode_tasks(command)
            continue 
        
        response = aiml_kernel.respond(command)
        log_interaction(command, response)  
        if response:
            speak(response)
        else:
            speak("I didn't understand that.")

def geek_mode():
    """Handle Geek Mode (transcription), with task switching."""
    speak("Entering geek mode. I will transcribe what you say.")
    while not stop_event.is_set():
        command = listen()
        if command == "exit":
            break

        log_interaction(command, "Processing command")
        
        if recognize_intent(command) != "geek_mode":
            cross_mode_tasks(command)
            continue  
        
        os.system(f"xdotool type '{command}'")

def controller_mode():
    """Handle Controller Mode for opening/closing applications."""
    speak("Entering controller mode.")
    while not stop_event.is_set():
        command = listen()
        if command == "exit":
            break

        log_interaction(command, "Processing command")
        
        if recognize_intent(command) != "controller":
            cross_mode_tasks(command)
            continue  
        
        if "open" in command or "close" in command:
            cross_mode_tasks(command)

def study_mode():
    """Handle Study Mode for semantic search in PDFs."""
    speak("Entering study mode. You can ask me questions about your PDFs.")
    while not stop_event.is_set():
        command = listen()
        if command == "exit":
            break

        log_interaction(command, "Processing command")

        if recognize_intent(command) != "study_mode":
            cross_mode_tasks(command)
            continue  
        
        pdf_response = semantic_search_pdfs(command, pdf_data)
        if pdf_response:
            speak(pdf_response)
        else:
            speak("I couldn't find an answer in the PDFs.")

def main():
    """Main entry point of the application."""
    load_and_train_models()
    mode = ask_for_mode()  
    select_mode(mode)

if __name__ == "__main__":
    main()
