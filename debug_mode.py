import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor

# JSON file paths
JSON_FILE = r"C:\Users\HP\Documents\project\memoaura\memoaura\cmd.json"
SETTINGS_FILE = r"C:\Users\HP\Documents\project\memoaura\memoaura\system_info.json"

class StackOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # Transparent overlay
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(400, 300)

        # Center the overlay
        self.center_on_screen()

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)

        # Text area
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            background: rgba(0,0,0,50);
            color: #00FF00;
            border: none;
        """)
        self.text_area.setFont(QFont("Courier", 10))
        layout.addWidget(self.text_area)
        self.setLayout(layout)

        # Stack
        self.stack = []
        self.last_lines = []

        # Timer to monitor JSON every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(1000)

        # Initially hidden
        self.hide()

    # Center overlay on screen
    def center_on_screen(self):
        screen = QDesktopWidget().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    # Check DND mode and push messages if enabled
    def update_overlay(self):
        dnd_enabled = self.is_dnd_enabled()
        if dnd_enabled:
            if not self.isVisible():
                self.show()  # show overlay only when DND is on
            self.read_json()
        else:
            if self.isVisible():
                self.hide()  # hide overlay when DND is off

    # Read JSON messages
    def read_json(self):
        try:
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        new_lines = [line for line in data if line not in self.last_lines]
                        for line in new_lines:
                            self.push_to_stack(line)
                        self.last_lines = data
        except Exception as e:
            self.push_to_stack(f"Error reading JSON: {e}")

    # Push message to stack
    def push_to_stack(self, msg):
        self.stack.append(msg)
        if len(self.stack) > 15:
            self.stack.pop(0)
        self.text_area.setPlainText("\n".join(self.stack))
        self.text_area.moveCursor(QTextCursor.End)

    # Check if DND mode is ON in settings
    def is_dnd_enabled(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("debug_mode", False)
            except:
                return False
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = StackOverlay()
    sys.exit(app.exec_())
