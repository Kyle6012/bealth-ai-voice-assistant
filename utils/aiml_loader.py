import os
import aiml

def load_aiml(directory):
    kernel = aiml.Kernel()
    for file in os.listdir(directory):
        if file.endswith(".aiml"):
            kernel.learn(os.path.join(directory, file))
    return kernel

def aiml_chat(input_text, kernel):
    return kernel.respond(input_text)
