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
from lwindow_lock import Ard
# Initialize OCR
reader = easyocr.Reader(['en'], gpu=True)
import winsound  # Add at the top

def trigger_alert():
    try:
        # Windows beep: frequency=1000Hz, duration=300ms
        winsound.Beep(1000, 300)
    except:
        # Fallback: ASCII bell
        print('\a')

# Paths
json_path = "gif.json"
load_gif = "circle.gif"
triggered_words_json = "triggered_words.json"
system_info_json = "system_info.json"
log_file = "log.json"
account_json = "account.json"
def update_protect_only(val="true"):
    try:
        # Read existing account.json
        if os.path.exists(account_json):
            with open(account_json, "r") as f:
                try:
                    account_data_m = json.load(f)
                    if not isinstance(account_data_m, dict):
                        account_data_m = {}
                except json.JSONDecodeError:
                    account_data_m = {}
        else:
            account_data_m = {}

        # Only update the 'protect' key, leave everything else intact
        account_data_m['protect'] = val

        # Write back
        with open(account_json, "w") as f:
            json.dump(account_data_m, f, indent=4)

    except Exception as e:
        print(f"[ERROR] Could not update protect: {e}")

# --- Load trigger words safely ---
def load_json_list(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data_m = json.load(f)
                if not isinstance(data_m, list):
                    data_m = []
        except json.JSONDecodeError:
            data_m = []
    else:
        data_m = []
    return data_m

def load_json_dict(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data_m = json.load(f)
                if not isinstance(data_m, dict):
                    data_m = default if default is not None else {}
        except json.JSONDecodeError:
            data_m = default if default is not None else {}
    else:
        data_m = default if default is not None else {}
    return data_m

trigger_words = set(load_json_list(triggered_words_json))
system_info = load_json_dict(system_info_json, {"keywords": []})

# Merge keywords
trigger_words.update(system_info.get("keywords", []))
system_info["keywords"] = list(trigger_words)

# Save merged keywords back
with open(system_info_json, "w") as f:
    json.dump(system_info, f, indent=4)

# --- Overlay window ---
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

# --- Logging ---
def log_triggers(triggers_found):
    logs = load_json_list(log_file)  

    unique_triggers = list(set([w.lower() for w in triggers_found]))

    # Update account.json if "quite" detected
    if "quite" in unique_triggers:
        account_data_m = load_json_dict(account_json)
        account_data_m['protect'] = "true"
        with open(account_json, "w") as f:
            json.dump(account_data_m, f, indent=4)

    # Save last triggers to log.json
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({"word": unique_triggers}, f, indent=4)

# --- OCR loop ---
def ocr_loop(overlay):
    while True:
        try:
            # Load gif.json safely
            data_m = load_json_list(json_path)

            # Add GIF trigger if not present
            imgs = [i[0] for i in data_m if isinstance(i, list) and len(i) > 0]
            if load_gif not in imgs:
                print("GIF already playing. Skipping new trigger.")
                data_m.append([load_gif, [820,900]])
                with open(json_path, "w") as f:
                    json.dump(data_m, f, indent=4)

            # Take screenshot and run OCR
            screenshot = pyautogui.screenshot()
            img = np.array(screenshot)
            img_small = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))
            gray = cv2.cvtColor(img_small, cv2.COLOR_RGB2GRAY)
            results = reader.readtext(gray)

            scale_x = img.shape[1] / img_small.shape[1]
            scale_y = img.shape[0] / img_small.shape[0]

            boxes_to_show = []
            triggers_found = set()

            for bbox, text, _ in results:
                text_clean = text.lower()
                if text_clean in trigger_words:
                    triggers_found.add(text_clean)
                    scaled_bbox = [[pt[0]*scale_x, pt[1]*scale_y] for pt in bbox]
                    boxes_to_show.append(scaled_bbox)

            overlay.update_boxes(boxes_to_show)

            if triggers_found:
                print(f"Trigger words detected: {triggers_found}")
                log_triggers(triggers_found)
                update_protect_only()
                s=Ard()
                #s.lock_window()
                trigger_alert()
            else:
                update_protect_only("False")
                s=Ard()
                #s.lock_window(False)

                

            # Remove GIF from gif.json after processing
            data_m = [item for item in data_m if not (isinstance(item, list) and item[0] == load_gif)]
            with open(json_path, "w") as f:
                json.dump(data_m, f, indent=4)

        except Exception as e:
            print(f"[ERROR] OCR loop encountered an error: {e}")

        time.sleep(0.3)

# --- Main ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    overlay.showFullScreen()

    threading.Thread(target=ocr_loop, args=(overlay,), daemon=True).start()
    sys.exit(app.exec_())
