
from qgis.PyQt.QtWidgets import *
import socket
import subprocess
import sys

try:
    import openai

    if openai.__version__ == '0.27.8':
        print("OpenAI v0.27.8 is already installed.")
    else:
        raise ImportError('Incompatible version of OpenAI is installed. Installing version 0.27.8...')

except ImportError:
    if sys.platform.startswith("win"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==0.27.8"], shell=False)
    elif sys.platform.startswith("darwin"):
        subprocess.check_call(
            ["/Applications/QGIS.app/Contents/MacOS/bin/python3", "-m", "pip", "install", "openai==0.27.8"],
            shell=False)
    elif sys.platform.startswith("linux"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==0.27.8"], shell=False)
    else:
        raise Exception(f"Unsupported platform: {sys.platform}")

    print("OpenAI v0.27.8 installed successfully")

import time
import os
class MyApp(QWidget):

    def __init__(self,parent):
        super().__init__(parent)

    def ask_gpt(self,prompt,apikey,model):
        openai.api_key = apikey
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model = model,
                    messages = [
                        {"role": "system", "content": prompt}]
                )
                return response['choices'][0]['message']['content']
            except openai.error.APIError as e:
                if e.status == 429:
                    time.sleep(5)
                else:
                    raise e

    def is_connected(self):
        try:
            # Try to connect to one of the DNS servers
            socket.create_connection(("1.1.1.1", 53))
            return True
        except OSError:
            pass
        return False

