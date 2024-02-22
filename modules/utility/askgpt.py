
from qgis.PyQt.QtWidgets import *
import socket
import sys, subprocess
def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], shell=False)
        print(f"{package_name} installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}. Error: {e}")

try:
    import openai
    print("openai is already installed")
except ImportError:
    print("openai is not installed, installing...")
    install_package("openai")
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

