
import os
import subprocess
import sys
import time

from qgis.PyQt.QtWidgets import *

try:
    import openai

    print("openai is already installed")
except ImportError:
    print("openai is not installed, installing...")
    if sys.platform.startswith("win"):
        subprocess.check_call(["pip", "install", "openai"])
    elif sys.platform.startswith("darwin"):
        subprocess.check_call(["pip3", "install", "openai"])
    elif sys.platform.startswith("linux"):
        subprocess.check_call(["pip", "install", "openai"])
    else:
        raise Exception(f"Unsupported platform: {sys.platform}")
    print("openai installed successfully")
class MyApp(QWidget):

    def __init__(self, api_key, parent=None):
        super().__init__(parent)
        self.api_key = api_key

    def ask_gpt(self, prompt):

        openai.api_key = self.api_key
        for _ in range(3):  # retry up to 3 times
            try:
                response = openai.Completion.create(
                    engine="davinci",
                    prompt=prompt,
                    temperature=0.8,
                    max_tokens=2048
                )
                return response.choices[0].text.strip()
            except openai.error.APIError as e:
                if e.status == 429:
                    time.sleep(5)
                else:
                    raise e
        raise Exception("Failed to call OpenAI API after 3 retries")

def install_openai():
    try:
        import openai
        print("openai is already installed")
    except ImportError:
        print("openai is not installed, installing...")
        if sys.platform.startswith("win"):
            subprocess.check_call(["pip", "install", "openai"])
        elif sys.platform.startswith("darwin"):
            subprocess.check_call(["pip3", "install", "openai"])
        elif sys.platform.startswith("linux"):
            subprocess.check_call(["pip", "install", "openai"])
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        print("openai installed successfully")

if __name__ == "__main__":
    install_openai()
    app = QApplication(sys.argv)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        QMessageBox.critical(None, "Error", "OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    window = MyApp(api_key)
    window.show()
    sys.exit(app.exec_())

