import pyautogui
import cv2
import numpy as np
import easyocr
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import winsound
import json
import time
import nltk
nltk.download("punkt")
nltk.download("stopwords")

def beep(frequency=1000, duration=500):
    winsound.Beep(frequency, duration)
def call(triggered_words):
    img="images.json"
    with open(img, "r") as f:
        data = json.load(f)
        data.append(["skull.png", [100, 100], 70])
        time.sleep(4)
        json.dump(data, open(img, "w"), indent=4)
    
# Initialize OCR once (GPU)
reader = easyocr.Reader(['en'], gpu=True)
stop_words = set(stopwords.words('english'))
trigger_words = {"resign","work","resssign","quite","stop","job","pressure","stress","depression","sex","fear","threat","depressed","stressed","anxiety","deadline","deadline_is_over","tough","pressure"}

def full_screen_ocr():
    # Take full-screen screenshot
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)

    # Resize for faster OCR
    img = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))

    # Optional: convert to grayscale (faster on smaller image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # OCR
    results = reader.readtext(gray)

    # Collect all text at once
    texts = " ".join([text for (_, text, _) in results])
    words = set(word.lower() for word in word_tokenize(texts)
                if word not in string.punctuation and word.lower() not in stop_words)

    # Fast trigger detection
    if trigger_words & words:
        print(f"Trigger word detected: {trigger_words & words}")
        beep(2000, 500)
        call(trigger_words & words)

if __name__ == "__main__":
    while True:
        full_screen_ocr()
