import requests
import pyttsx3

engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def search_web(query):
    """Search the web using an API (e.g., Bing Web Search API or Google Custom Search API)."""
    api_key = "YOUR_API_KEY" 
    search_url = "https://api.bing.microsoft.com/v7.0/search"  

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML"}

    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        return search_results["webPages"]["value"]
    except Exception as e:
        speak("I couldn't retrieve the search results. Please check your connection or API key.")
        return []

def summarize_results(results):
    """Summarize the search results for the user."""
    if not results:
        return "I couldn't find any relevant information."

    summary = ""
    for idx, result in enumerate(results[:3], 1):  
        title = result["name"]
        url = result["url"]
        snippet = result.get("snippet", "")
        summary += f"Result {idx}: {title}. {snippet} You can read more at {url}. "
    
    return summary

