
from qgis.PyQt.QtWidgets import *
import sys, subprocess
try:
    import openai

    print("openai is already installed")
except ImportError:
    print("openai is not installed, installing...")
    if sys.platform.startswith("win"):
        subprocess.check_call(["pip", "install", "openai"],shell = False)
    elif sys.platform.startswith("darwin"):
        subprocess.check_call(["pip3", "install", "openai"],shell = False )
    elif sys.platform.startswith("linux"):
        subprocess.check_call(["pip", "install", "openai"],shell = False)
    else:
        raise Exception(f"Unsupported platform: {sys.platform}")
    print("openai installed successfully")
import time
import os
class MyApp(QWidget):

	def __init__(self,parent):
		super().__init__(parent)

	def ask_gpt(self,prompt,apikey):
		openai.api_key = apikey
		while True:
			try:
				response = openai.ChatCompletion.create(
					model = "gpt-3.5-turbo-16k",
					messages = [
						{"role": "system", "content": prompt}]
				)
				return response['choices'][0]['message']['content']
			except openai.error.APIError as e:
				if e.status == 429:
					time.sleep(5)
				else:
					raise e
