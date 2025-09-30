import sys
import random
import threading
import time
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

# ------------------------
# Sample motivational quotes
# ------------------------
quotes = [
    "You are stronger than you think.",
    "Take a deep breath, everything will be okay.",
    "Small steps every day lead to big results.",
    "Keep going, you are doing great!",
    "Focus on what you can control."
]

# ------------------------
# Path to JSON file
# ------------------------
JSON_FILE = "account.json"

# ------------------------
# Custom Confirmation Popup
# ------------------------
class ConfirmationPopup(QWidget):
    def __init__(self, message, on_confirm, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.on_confirm = on_confirm

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)

        container = QWidget()
        container.setStyleSheet("background-color: rgba(0,0,0,220); border-radius: 15px;")
        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)
        container.setLayout(container_layout)
        layout.addWidget(container)

        label = QLabel(message)
        label.setStyleSheet("color: lime; font-size: 18pt;")
        label.setWordWrap(True)
        container_layout.addWidget(label, alignment=Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("Yes")
        confirm_btn.setStyleSheet("""
            background-color: rgba(0,255,0,180); 
            color: black; 
            padding: 10px 20px; 
            font-size: 16pt; 
            border-radius: 10px;
        """)
        confirm_btn.clicked.connect(self.confirm)
        cancel_btn = QPushButton("No")
        cancel_btn.setStyleSheet("""
            background-color: rgba(255,0,0,150); 
            color: white; 
            padding: 10px 20px; 
            font-size: 16pt; 
            border-radius: 10px;
        """)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        container_layout.addLayout(btn_layout)

        if parent:
            self.resize(400, 200)
            self.move(parent.width()//2 - self.width()//2, parent.height()//2 - self.height()//2)

    def confirm(self):
        self.on_confirm()
        self.close()

# ------------------------
# Floating Overlay
# ------------------------
class FloatingOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.showFullScreen()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(80, 80, 80, 80)
        main_layout.setSpacing(40)
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: rgba(0,0,0,255);")

        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(30)
        container.setLayout(container_layout)
        container.setStyleSheet("background-color: rgba(0,0,0,230); border-radius: 20px;")
        container.setGraphicsEffect(self.create_glow())
        main_layout.addWidget(container, alignment=Qt.AlignCenter)

        header_layout = QHBoxLayout()
        name_label = QLabel("MemoAura Assistant")
        name_label.setStyleSheet("color: lime; font-weight: bold; font-size: 28pt;")
        header_layout.addWidget(name_label, alignment=Qt.AlignLeft)

        status_label = QLabel("Stress Detected")
        status_label.setStyleSheet("color: red; font-weight: bold; font-size: 28pt;")
        header_layout.addWidget(status_label, alignment=Qt.AlignCenter)
        container_layout.addLayout(header_layout)

        self.quote_label = QLabel(random.choice(quotes))
        self.quote_label.setStyleSheet("color: lime; font-style: italic; font-size: 22pt;")
        self.quote_label.setWordWrap(True)
        container_layout.addWidget(self.quote_label, alignment=Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        remind_btn = QPushButton("Remind")
        remind_btn.setStyleSheet("background-color: darkgreen; color: lime; padding:15px; font-size:18pt; border-radius:10px;")
        remind_btn.clicked.connect(self.remind_action)
        submit_btn = QPushButton("Submit")
        submit_btn.setStyleSheet("background-color: darkgreen; color: lime; padding:15px; font-size:18pt; border-radius:10px;")
        submit_btn.clicked.connect(self.submit_action)
        btn_layout.addWidget(remind_btn)
        btn_layout.addWidget(submit_btn)
        container_layout.addLayout(btn_layout)

        self.stress_label = QLabel(f"Stress Level: {random.randint(1, 100)}%")
        self.stress_label.setStyleSheet("color: lime; font-size: 22pt;")
        container_layout.addWidget(self.stress_label, alignment=Qt.AlignCenter)

        instruction_label = QLabel("Instruction: Press F6 to unlock this widget")
        instruction_label.setStyleSheet("color: lightgreen; font-size: 16pt;")
        container_layout.addWidget(instruction_label, alignment=Qt.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stress)
        self.timer.start(4000)

    def create_glow(self):
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(50)
        glow.setColor(QColor(0, 255, 0))
        glow.setOffset(0)
        return glow

    def update_stress(self):
        self.stress_label.setText(f"Stress Level: {random.randint(1, 100)}%")
        self.quote_label.setText(random.choice(quotes))

    def remind_action(self):
        def on_confirm():
            threading.Thread(target=self.delayed_send_remind, args=(10,), daemon=True).start()
        popup = ConfirmationPopup("Shall I remind this message after 1 hour?", on_confirm, parent=self)
        popup.show()

    def delayed_send_remind(self, seconds):
        time.sleep(seconds)
        print(f"[DEBUG] Reminder sent after {seconds} seconds.")
        self.auto_reset_protect()

    def submit_action(self):
        def on_confirm():
            threading.Thread(target=self.delayed_send_submit, args=(15,), daemon=True).start()
        popup = ConfirmationPopup("Shall I send this message after 4 hours?", on_confirm, parent=self)
        popup.show()

    def delayed_send_submit(self, seconds):
        time.sleep(seconds)
        print(f"[DEBUG] Submit message sent after {seconds} seconds.")
        self.auto_reset_protect()
        self.close()

    def auto_reset_protect(self):
        """Set protect:false in JSON to avoid repeated overlay."""
        try:
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, "r") as f:
                    data = json.load(f)
                data["protect"] = "False"
                with open(JSON_FILE, "w") as f:
                    json.dump(data, f, indent=4)
                print("[DEBUG] protect set to False in JSON")
        except Exception as e:
            print(f"[ERROR] auto_reset_protect: {e}")

# ------------------------
# Infinite JSON monitor
# ------------------------
def infinite_monitor():
    last_mtime = os.path.getmtime(JSON_FILE) if os.path.exists(JSON_FILE) else 0
    while True:
        time.sleep(1)
        if not os.path.exists(JSON_FILE):
            continue
        try:
            current_mtime = os.path.getmtime(JSON_FILE)
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                with open(JSON_FILE, "r") as f:
                    data = json.load(f)
                if str(data.get("protect", "false")).lower() == "true":
                    print("[DEBUG] Protect True - launching overlay")
                    app = QApplication.instance() or QApplication(sys.argv)
                    overlay = FloatingOverlay()
                    overlay.show()
                    app.exec_()  # Blocks until overlay closes
                else:
                    print("[INFO] Protect False - overlay skipped")
        except Exception as e:
            print(f"[ERROR] Monitoring JSON: {e}")

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    infinite_monitor()
