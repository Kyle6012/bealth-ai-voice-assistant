import threading

def background_task(func):
    thread = threading.Thread(target=func)
    thread.start()