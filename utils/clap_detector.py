# utils/clap_detector.py
import pyaudio
import numpy as np
import threading
import time

class ClapDetector:
    """Detects claps to wake up the assistant."""
    def __init__(self, threshold=1000, chunk_size=1024):
        self.threshold = threshold
        self.chunk_size = chunk_size
        self.is_active = False
        self.stop_event = threading.Event()

        self.thread = threading.Thread(target=self.detect_clap)
        self.thread.start()

    def detect_clap(self):
        """Listen for claps."""
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=self.chunk_size)
        
        while not self.stop_event.is_set():
            data = stream.read(self.chunk_size)
            audio_data = np.frombuffer(data, dtype=np.int16)
            peak = np.abs(audio_data).max()
            if peak > self.threshold:
                self.is_active = True
                time.sleep(0.5)  

        stream.stop_stream()
        stream.close()
        p.terminate()

    def reset(self):
        """Reset the clap detector state."""
        self.is_active = False

    def stop(self):
        """Stop the clap detection thread."""
        self.stop_event.set()
        self.thread.join()
