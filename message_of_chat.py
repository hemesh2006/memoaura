import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontMetrics
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FloatingNotifications(QWidget):
    def __init__(self, json_file):
        super().__init__()
        self.json_file = json_file

        # Window flags and transparency
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.99)

        # ----- Automatically set window size and position -----
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()  # Usable screen area
        screen_width = rect.width()
        screen_height = rect.height()

        window_width = int(screen_width * 0.3)   # 30% of screen width
        window_height = int(screen_height * 0.6) # 60% of screen height
        x_pos = screen_width - window_width - 10 # Right side with 10px margin
        y_pos = 10  # Top margin

        self.setGeometry(x_pos, y_pos, window_width, window_height)
        # -------------------------------------------------------

        self.offset = None
        self.notifications = {}  # key: message text, value: container widget
        self.setMouseTracking(True)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.setLayout(self.main_layout)

        self.load_messages()
        self.start_file_monitor()

    # --------- JSON MEMORY FUNCTIONS ----------
    def load_messages(self):
        try:
            # Create JSON file if missing or empty
            if not os.path.exists(self.json_file) or os.path.getsize(self.json_file) == 0:
                with open(self.json_file, "w") as f:
                    json.dump({"messages": []}, f, indent=4)

            with open(self.json_file, "r") as f:
                data = json.load(f)
            messages = data.get("messages", [])

            # Split messages by semicolon
            split_messages = []
            for msg in messages:
                split_messages.extend([m.strip() for m in msg.split(";") if m.strip()])

            self.update_messages(split_messages)
        except Exception as e:
            print(f"Error loading JSON: {e}")

    def update_messages(self, messages):
        new_set = set(messages)
        current_set = set(self.notifications.keys())

        # Add new messages
        for msg in new_set - current_set:
            self.add_message(msg)

        # Remove old messages
        for msg in current_set - new_set:
            self.remove_message_by_text(msg)

    # --------- MESSAGE DISPLAY ----------
    def add_message(self, text):
        container = QWidget()
        container.setStyleSheet("""
            background-color: rgba(0, 0, 0, 220);
            border-radius: 8px;
        """)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        font = QFont("Courier", 19, QFont.Bold)
        label = QLabel("")
        label.setStyleSheet("color: #00FF00;")
        label.setFont(font)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        cancel_btn = QPushButton("✕")
        cancel_btn.setFixedSize(25, 25)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: red;
                border: none;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:pressed {
                background-color: rgba(200, 0, 0, 50);
            }
        """)

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(cancel_btn)
        container.setLayout(layout)

        # Fade-in effect
        opacity_effect = QGraphicsOpacityEffect()
        container.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
        self.fade_in(container, opacity_effect)

        self.main_layout.addWidget(container)
        self.notifications[text] = container

        cancel_btn.clicked.connect(lambda: self.remove_message_by_text(text))

        # Typing animation
        self.animate_text(label, text, container, font)

    def animate_text(self, label, text, container, font):
        index = 0
        metrics = QFontMetrics(font)
        max_width = self.width() - 80  # padding + cancel button

        def type_text():
            nonlocal index
            if index <= len(text):
                label.setText(text[:index])
                lines = metrics.boundingRect(0, 0, max_width, 1000, Qt.TextWordWrap, label.text()).height()
                container.setFixedHeight(lines + 20)
                index += 1
            else:
                timer.stop()

        timer = QTimer()
        timer.timeout.connect(type_text)
        timer.start(10)

    def remove_message_by_text(self, text):
        if text in self.notifications:
            container = self.notifications[text]
            self.main_layout.removeWidget(container)
            container.setParent(None)
            container.deleteLater()
            del self.notifications[text]
            self.remove_from_json(text)
            self.main_layout.update()
            self.adjustSize()

    def remove_from_json(self, text):
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
            messages = data.get("messages", [])

            updated_messages = []
            for msg in messages:
                parts = [m.strip() for m in msg.split(";") if m.strip()]
                if text in parts:
                    parts.remove(text)
                if parts:
                    updated_messages.append("; ".join(parts))

            data["messages"] = updated_messages
            with open(self.json_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error updating JSON: {e}")

    def fade_in(self, widget, effect):
        step = 0.1
        opacity = 0.0
        def increase_opacity():
            nonlocal opacity
            if opacity < 1.0:
                opacity += step
                effect.setOpacity(opacity)
            else:
                timer.stop()

        timer = QTimer()
        timer.timeout.connect(increase_opacity)
        timer.start(50)

    # --------- DRAG FUNCTIONALITY ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.offset = None
        event.accept()

    # --------- FILE MONITOR ----------
    def start_file_monitor(self):
        event_handler = FileChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, ".", recursive=False)
        self.observer.start()

    def stop_file_monitor(self):
        if hasattr(self, "observer"):
            self.observer.stop()
            self.observer.join()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, gui):
        super().__init__()
        self.gui = gui

    def on_modified(self, event):
        if event.src_path.endswith(self.gui.json_file):
            QTimer.singleShot(0, self.gui.load_messages)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = FloatingNotifications("messages.json")
    gui.show()

    try:
        sys.exit(app.exec_())
    finally:
        gui.stop_file_monitor()
