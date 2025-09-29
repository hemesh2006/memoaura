import sys
import time
import pyautogui
import cv2
import numpy as np
import easyocr
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QBrush
import winsound
import threading
import json
import os
import random
import pyttsx3
spoken_for_cycle = False
# Initialize the speech engine
engine = pyttsx3.init()


def speak(word):
    """Speak a word safely in a thread."""
    def run():
        engine.say(word)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()
# Global variable to track if we already responded


next_speak = True

def beep(triggers, frequency=1000, duration=200):
    """
    Beep and speak **one random trigger word** only if `next_speak` is True.
    `next_speak` is reset when no triggers are detected.
    """
    global next_speak
    
    if not triggers or len(triggers) == 0:
        # No triggers, allow speaking next time triggers appear
        next_speak = True
        return
    
    if next_speak:
        word = random.choice(list(triggers))
        winsound.Beep(frequency, duration)
        print(f"Detected trigger: {word}")
        speak(get_response({word}))
        next_speak = False  # prevent further speaking until triggers disappear


# Initialize OCR
reader = easyocr.Reader(['en'], gpu=True)
with open(r"C:\Users\HP\Documents\project\memoaura\memoaura\login\trigger.json", "r", encoding="utf-8") as f:
    responses = json.load(f)

def get_response(trigg):
    trigg = random.choice(list(trigg))  # pick one word from set
    trigg = trigg.lower()
    if trigg in responses:
        a=random.choice(responses[trigg])
        speak(a)
        return a
    else:
        return ""

# Define trigger words
trigger_words = {'divorce', 'unloved', 'quite', 'recovery', 'jobless', 'cutting',
                 'loneliness', 'guilt', 'cheating', 'rejection', 'mistake', 'loss',
                 'shattered', 'hopelessness', 'sadness', 'lost', 'weak', 'betrayal',
                 'ignored', 'stressed', 'useless', 'hate myself', 'blood', 'strong',
                 'depression', 'overwhelmed', 'helpless', 'empty', 'grateful', 'knife',
                 'broken', 'work', 'pressure', 'workload', 'regret', 'anxiety', 'insecure',
                 'worthless', 'trauma', 'tough', 'sex', 'deadline_is_over', 'abuse',
                 'motivated', 'end life', 'pain', 'jealousy', 'stress', 'depressed', 'alone',
                 'unsafe', 'drained', 'stop', 'danger', 'threat', 'abandonment', 'confident',
                 'bullying', 'unemployment', 'nervous', 'not enough', 'unstable', 'calm',
                 'frustration', 'inspired', 'joy', 'worry', 'devastated', 'self-harm',
                 'painkillers', 'nightmare', 'crying', 'excited', 'happy', 'resssign',
                 'unworthy', 'panic', 'tired', 'resign', 'pills', 'shame', 'overdose',
                 'overwork', 'violence', 'control', 'scared', 'suffocating', 'breakup',
                 'burnout', 'deadline', 'self-doubt', 'anger', 'regretful', 'suicide',
                 'hopeless', 'peaceful', 'pressured', 'uncertain', 'fear', 'unwanted',
                 'change', 'failure', 'quit'}



# Overlay window for highlights
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QApplication.primaryScreen()
        self.setGeometry(0, 0, screen.size().width(), screen.size().height())
        self.boxes = []

    def update_boxes(self, boxes):
        self.boxes = boxes
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for bbox in self.boxes:
            x_min = int(min([pt[0] for pt in bbox]))
            y_min = int(min([pt[1] for pt in bbox]))
            x_max = int(max([pt[0] for pt in bbox]))
            y_max = int(max([pt[1] for pt in bbox]))
            painter.setBrush(QBrush(QColor(255, 0, 0, 120)))  # Semi-transparent red
            painter.setPen(Qt.NoPen)
            painter.drawRect(x_min, y_min, x_max - x_min, y_max - y_min)

# OCR loop running in background
def ocr_loop(overlay):
    #load gif here lkke screen sot emoji
    json_file = r"C:\Users\HP\Documents\project\memoaura\memoaura\login\gif.json"  # Use raw string for path

    while True:
        global spoken_for_cycle
        spoken_for_cycle=False
        # Safely read and modify JSON
        if os.path.exists(json_file):
            with open(json_file, "r") as fread:
                data = json.load(fread)
            
            # Remove existing skull.png entries
            data = [i for i in data if i[0] != "C:\\Users\\HP\\Documents\\project\\memoaura\\memoaura\\login\\df.gif"]
            
            # Add new entry
            data.append(["C:\\Users\\HP\\Documents\\project\\memoaura\\memoaura\\login\\df.gif", [100,500]])
            
            with open(json_file, "w") as fwrite:
                json.dump(data, fwrite, indent=4)

        # Take screenshot
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img_small = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
        gray = cv2.cvtColor(img_small, cv2.COLOR_RGB2GRAY)
        results = reader.readtext(gray)

        scale_x = img.shape[1] / img_small.shape[1]
        scale_y = img.shape[0] / img_small.shape[0]

        boxes_to_show = []
        triggers_found = set()
        if os.path.exists(json_file):
            with open(json_file, "r") as fread:
                data = json.load(fread)
            
            # Remove existing skull.png entries
            data = [i for i in data if i[0] == "C:\\Users\\HP\\Documents\\project\\memoaura\\memoaura\\login\\df.gif"]
            
            # Add new entry
            data.remove(["C:\\Users\\HP\\Documents\\project\\memoaura\\memoaura\\login\\df.gif", [100,500]])
            
            with open(json_file, "w") as fwrite:
                json.dump(data, fwrite, indent=4)
            

        # Exact word matching
        for bbox, text, _ in results:
            text_clean = text.lower()
            if text_clean in trigger_words:
                triggers_found.add(text_clean)
                scaled_bbox = [[pt[0]*scale_x, pt[1]*scale_y] for pt in bbox]
                boxes_to_show.append(scaled_bbox)
        global next_speak
        if triggers_found:
            print(f"Trigger words detected: {triggers_found}")
            beep(frequency=2000, duration=200,triggers=triggers_found)
        else:
            next_speak=True
            

        overlay.update_boxes(boxes_to_show)
        time.sleep(0.3)  # Adjust for speed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    overlay.showFullScreen()

    # Run OCR in a daemon thread
    threading.Thread(target=ocr_loop, args=(overlay,), daemon=True).start()

    sys.exit(app.exec_())
