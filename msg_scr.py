import sys
import time
import pyautogui
import cv2
import numpy as np
import easyocr
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QBrush
import threading
import json
import os
import random

# Initialize OCR
reader = easyocr.Reader(['en'], gpu=True)
json_path = r"C:\Users\HP\Documents\project\memoaura\memoaura\gif.json"
load_gif = r"C:\\Users\\HP\\Documents\\project\\memoaura\\memoaura\\df.gif"

# Paths for trigger words
triggered_words_json = r"C:\Users\HP\Documents\project\memoaura\memoaura\triggered_words.json"
system_info_json = r"C:\Users\HP\Documents\project\memoaura\memoaura\system_info.json"

# --- Load triggered words safely ---
if os.path.exists(triggered_words_json):
    with open(triggered_words_json, "r") as f:
        try:
            trigger_words = json.load(f)
        except json.JSONDecodeError:
            trigger_words = []
else:
    trigger_words = []

# --- Load system info safely ---
if os.path.exists(system_info_json):
    with open(system_info_json, "r") as f:
        try:
            dat = json.load(f)
        except json.JSONDecodeError:
            dat = {"keywords": []}
else:
    dat = {"keywords": []}

key = dat.get("keywords", [])

# Merge triggers
trigger_words.extend(key)
trigger_words = list(set(trigger_words))  # remove duplicates

# Save back safely
dat["keywords"] = trigger_words
with open(system_info_json, "w") as f:
    json.dump(dat, f, indent=4)
trigger_words = set(trigger_words)

# --- Overlay window for highlights ---
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

# --- Log trigger words ---
def log_triggers(triggers_found):
    log_file = "log.json"
    # Load existing log
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    # Unique triggers, all lowercase
    unique_triggers = list(set([w.lower() for w in triggers_found]))

    # Append new log entry
    logs = {
        "word": unique_triggers,
    }

    # Save back
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

# --- OCR loop ---
def ocr_loop(overlay):
    while True:
        # Safe load of gif.json
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        imgs = [i[0] for i in data]
        if load_gif not in imgs:
            print("GIF already playing. Skipping new trigger.")
            data.append([load_gif, [100, 500]])
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)

        # Screenshot and OCR
        screenshot = pyautogui.screenshot()
        img = np.array(screenshot)
        img_small = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
        gray = cv2.cvtColor(img_small, cv2.COLOR_RGB2GRAY)
        results = reader.readtext(gray)

        scale_x = img.shape[1] / img_small.shape[1]
        scale_y = img.shape[0] / img_small.shape[0]

        boxes_to_show = []
        triggers_found = set()

        # Detect trigger words
        for bbox, text, _ in results:
            text_clean = text.lower()
            if text_clean in trigger_words:
                triggers_found.add(text_clean)
                scaled_bbox = [[pt[0]*scale_x, pt[1]*scale_y] for pt in bbox]
                boxes_to_show.append(scaled_bbox)

        # Update overlay highlights
        overlay.update_boxes(boxes_to_show)

        # Log triggers if any
        if triggers_found:
            print(f"Trigger words detected: {triggers_found}")
            log_triggers(triggers_found)

        # Remove GIF after processing
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []

            data = [item for item in data if item[0] != load_gif]

            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)

        time.sleep(0.3)

# --- Main ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    overlay.showFullScreen()

    threading.Thread(target=ocr_loop, args=(overlay,), daemon=True).start()

    sys.exit(app.exec_())
