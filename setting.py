import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QSlider,
    QPushButton, QTabWidget, QTextEdit, QLineEdit, QCheckBox, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer

SETTINGS_FILE = "settings.json"
DEBUG_FILE = "debug_logs.json"

# ---------------- Settings Load/Save ----------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- Draggable Window Base ----------------
class DraggableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

# ---------------- Draggable Button ----------------
class DraggableButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.parent().frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

# ---------------- Floating Gear Button ----------------
class FloatingSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(800, 600, 100, 100)

        self.gear_btn = DraggableButton("⚙", self)
        self.gear_btn.setStyleSheet("""
            QPushButton { font-size: 32px; color: #00FF00; background-color: rgba(50,50,50,180); border-radius: 25px; }
            QPushButton:hover { background-color: rgba(80,80,80,220); }
        """)
        self.gear_btn.setFixedSize(60, 60)
        self.gear_btn.clicked.connect(self.toggle_settings_window)

    # Toggle the settings window
    def toggle_settings_window(self):
        if self.settings_window is None:
            self.settings_window = TransparentSettings()
        if self.settings_window.isVisible():
            self.settings_window.hide()
        else:
            pos = self.pos()
            self.settings_window.move(pos.x() - 500, pos.y() - 600)
            self.settings_window.show()

# ---------------- Main Settings Overlay (Draggable) ----------------
class TransparentSettings(DraggableWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.telegram_unlocked = False
        self.debug_last_lines = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Assistant Settings Overlay")
        self.setGeometry(5, 5, 1100, 700)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        main_layout.addWidget(self.cancel_btn, alignment=Qt.AlignRight)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; background: rgba(0,0,0,200);}
            QTabBar::tab { background: rgba(0,0,0,180); color: #00FF00; padding: 10px; border-radius: 5px; font-size: 22px; min-width: 200px; min-height:40px }
            QTabBar::tab:selected { background: rgba(50,50,50,200); }
        """)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.setDocumentMode(True)

        # ---------------- Audio & Mic ----------------
        audio_tab = QWidget()
        audio_layout = QVBoxLayout()
        audio_layout.setContentsMargins(10, 10, 10, 10)
        audio_layout.setSpacing(5)

        audio_layout.addWidget(QLabel("Output Device:"))
        self.output_device = QComboBox()
        self.output_device.addItems(["Speakers", "Headphones", "Bluetooth Device"])
        audio_layout.addWidget(self.output_device)

        audio_layout.addWidget(QLabel("Input Device (Mic):"))
        self.mic_device = QComboBox()
        self.mic_device.addItems(["Mic 1", "Mic 2", "Mic 3"])
        audio_layout.addWidget(self.mic_device)

        audio_layout.addWidget(QLabel("Mic Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(1)
        self.sensitivity_slider.setMaximum(100)
        self.sensitivity_slider.setFixedHeight(30)
        audio_layout.addWidget(self.sensitivity_slider)

        audio_layout.addWidget(QLabel("Speaker Voice:"))
        self.speaker_voice = QComboBox()
        self.speaker_voice.addItems(["Male", "Female", "Robot", "Casual"])
        audio_layout.addWidget(self.speaker_voice)

        audio_layout.addWidget(QLabel("Speaker Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setFixedHeight(30)
        audio_layout.addWidget(self.volume_slider)

        audio_layout.addWidget(QLabel("Privacy Model:"))
        self.privacy_model = QComboBox()
        self.privacy_model.addItems(["Standard", "Strict", "Custom"])
        audio_layout.addWidget(self.privacy_model)

        self.dnd_checkbox = QCheckBox("Do Not Disturb Mode")
        audio_layout.addWidget(self.dnd_checkbox)

        audio_tab.setLayout(audio_layout)
        self.tabs.addTab(audio_tab, "Audio & Mic")

        # ---------------- Theme ----------------
        theme_tab = QWidget()
        theme_layout = QVBoxLayout()
        theme_layout.setContentsMargins(10, 10, 30, 30)
        theme_layout.setSpacing(5)
        theme_layout.addWidget(QLabel("Enable Notifications:"))
        self.notification_checkbox = QCheckBox("Enable")
        theme_layout.addWidget(self.notification_checkbox)
        theme_tab.setLayout(theme_layout)
        self.tabs.addTab(theme_tab, "Notification")

        # ---------------- Telegram Bot ----------------
        self.telegram_tab = QWidget()
        self.telegram_layout = QVBoxLayout()
        self.telegram_layout.setContentsMargins(10, 10, 10, 10)
        self.telegram_layout.setSpacing(20)
        self.telegram_placeholder = QLabel("Click Telegram Bot tab to unlock")
        self.telegram_layout.addWidget(self.telegram_placeholder)
        self.telegram_tab.setLayout(self.telegram_layout)
        self.tabs.addTab(self.telegram_tab, "Telegram Bot")
        self.tabs.currentChanged.connect(self.check_telegram_tab)

        # ---------------- Keywords ----------------
        keyword_tab = QWidget()
        keyword_layout = QVBoxLayout()
        keyword_layout.setContentsMargins(3, 3, 3, 3)
        keyword_layout.setSpacing(0)
        keyword_layout.addWidget(QLabel("Enter trigger keywords (one per line):"))

        self.keyword_input = QTextEdit()
        self.keyword_input.setMinimumHeight(50)
        keyword_layout.addWidget(self.keyword_input)

        keyword_layout.addWidget(QLabel("Trigger Word Count Threshold:"))
        self.trigger_count_slider = QSlider(Qt.Horizontal)
        self.trigger_count_slider.setMinimum(1)
        self.trigger_count_slider.setMaximum(10)
        self.trigger_count_slider.setFixedHeight(20)
        keyword_layout.addWidget(self.trigger_count_slider)

        keyword_tab.setLayout(keyword_layout)
        self.tabs.addTab(keyword_tab, "Keyword Settings")

        # ---------------- Debug Mode ----------------
        debug_tab = QWidget()
        debug_layout = QVBoxLayout()
        debug_layout.setContentsMargins(30, 30, 30, 30)
        debug_layout.setSpacing(20)
        self.debug_terminal = QTextEdit()
        self.debug_terminal.setReadOnly(True)
        self.debug_terminal.setMinimumHeight(200)
        debug_layout.addWidget(self.debug_terminal)
        self.debug_clear = QPushButton("Clear Debug Terminal")
        self.debug_clear.setFixedHeight(40)
        self.debug_clear.clicked.connect(lambda: self.debug_terminal.clear())
        debug_layout.addWidget(self.debug_clear, alignment=Qt.AlignRight)
        debug_tab.setLayout(debug_layout)
        self.tabs.addTab(debug_tab, "Debug Mode")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Load settings and connect signals
        self.load_settings_to_ui()
        self.connect_signals()

        # Timer for debug logs
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_debug_logs)
        self.timer.start(1000)

        self.setStyleSheet("""
            QWidget { background-color: rgba(0,0,0,200); color: #00FF00; }
            QLabel, QTabBar::tab { font-size: 22px; color: #00FF00; margin: 5px 0; padding: 2px; }
            QComboBox, QLineEdit, QTextEdit, QSlider, QCheckBox { background-color: rgba(50,50,50,180); color: #00FF00; font-size: 22px; padding: 10px 12px; min-height: 42px; border: 2px solid #00FF00; margin: 4px 0; }
            QTextEdit { border: 2px solid #00FF00; padding: 2px; }
            QLineEdit { border: 2px solid #00FF00; padding: 2px; }
            QSlider { height: 22px; }
            QPushButton { background-color: rgba(80,80,80,200); border: 2px solid #00FF00; padding: 5px 7px; border-radius: 8px; font-size: 22px; color: #00FF00; min-height: 44px; }
            QPushButton:hover { background-color: rgba(120,120,120,220); }
            QTabWidget::pane { margin: 10px; padding: 10px; min-height: 400px; }
        """)

    # ---------------- Telegram ----------------
    def check_telegram_tab(self, index):
        if self.tabs.tabText(index) == "Telegram Bot" and not self.telegram_unlocked:
            password, ok = QInputDialog.getText(
                self, "Telegram Password",
                "Enter password to unlock Telegram settings:",
                QLineEdit.Password
            )
            if ok and password == self.settings.get("telegram_password", "1234"):
                self.telegram_unlocked = True
                for i in reversed(range(self.telegram_layout.count())):
                    widget = self.telegram_layout.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                self.show_telegram_ui()
            else:
                QMessageBox.warning(self, "Warning", "Incorrect password. Telegram settings locked.")
                self.tabs.setCurrentIndex(0)

    def show_telegram_ui(self):
        self.telegram_layout.addWidget(QLabel("Telegram Bot Connection"))
        self.telegram_steps = QTextEdit()
        self.telegram_steps.setReadOnly(True)
        self.telegram_steps.setText("1. Get Bot Token from BotFather.\n2. Enter User ID.\n3. Press Connect Bot.")
        self.telegram_layout.addWidget(self.telegram_steps)

        self.telegram_layout.addWidget(QLabel("Bot Token:"))
        self.bot_token_input = QLineEdit()
        self.telegram_layout.addWidget(self.bot_token_input)

        self.telegram_layout.addWidget(QLabel("User ID:"))
        self.user_id_input = QLineEdit()
        self.telegram_layout.addWidget(self.user_id_input)

        self.connect_button = QPushButton("Connect Bot")
        self.connect_button.clicked.connect(lambda: QMessageBox.information(self, "Telegram", "Bot connected (simulation)."))
        self.telegram_layout.addWidget(self.connect_button)

        self.bot_token_input.textChanged.connect(self.save_all_settings)
        self.user_id_input.textChanged.connect(self.save_all_settings)

    # ---------------- Other Methods ----------------
    def update_debug_logs(self):
        try:
            if os.path.exists(DEBUG_FILE):
                with open(DEBUG_FILE, "r") as f:
                    logs = json.load(f)
                new_lines = [line for line in logs if line not in self.debug_last_lines]
                if new_lines:
                    for line in new_lines:
                        self.debug_terminal.append(line)
                    self.debug_terminal.verticalScrollBar().setValue(
                        self.debug_terminal.verticalScrollBar().maximum()
                    )
                    self.debug_last_lines = logs
        except Exception as e:
            self.debug_terminal.append(f"Error reading debug JSON: {e}")

    def load_settings_to_ui(self):
        s = self.settings
        try:
            self.output_device.setCurrentText(s.get("output_device", "Speakers"))
            self.mic_device.setCurrentText(s.get("mic_device", "Mic 1"))
            self.sensitivity_slider.setValue(s.get("mic_sensitivity", 50))
            self.speaker_voice.setCurrentText(s.get("speaker_voice", "Male"))
            self.volume_slider.setValue(s.get("speaker_volume", 70))
            self.privacy_model.setCurrentText(s.get("privacy_model", "Standard"))
            self.dnd_checkbox.setChecked(s.get("dnd_mode", False))
            self.notification_checkbox.setChecked(s.get("enable_notifications", True))
            self.keyword_input.setText("\n".join(s.get("keywords", [])))
            self.trigger_count_slider.setValue(s.get("trigger_word_threshold", 3))
        except Exception as e:
            print("Error loading settings:", e)

    def save_all_settings(self):
        s = {
            "output_device": self.output_device.currentText(),
            "mic_device": self.mic_device.currentText(),
            "mic_sensitivity": self.sensitivity_slider.value(),
            "speaker_voice": self.speaker_voice.currentText(),
            "speaker_volume": self.volume_slider.value(),
            "privacy_model": self.privacy_model.currentText(),
            "dnd_mode": self.dnd_checkbox.isChecked(),
            "enable_notifications": self.notification_checkbox.isChecked(),
            "keywords": [k.strip() for k in self.keyword_input.toPlainText().splitlines() if k.strip()],
            "trigger_word_threshold": self.trigger_count_slider.value()
        }
        if self.telegram_unlocked:
            s["telegram_token"] = self.bot_token_input.text()
            s["telegram_user_id"] = self.user_id_input.text()
        s["telegram_password"] = self.settings.get("telegram_password", "1234")
        self.settings = s
        save_settings(s)

    def connect_signals(self):
        self.output_device.currentTextChanged.connect(self.save_all_settings)
        self.mic_device.currentTextChanged.connect(self.save_all_settings)
        self.sensitivity_slider.valueChanged.connect(self.save_all_settings)
        self.speaker_voice.currentTextChanged.connect(self.save_all_settings)
        self.volume_slider.valueChanged.connect(self.save_all_settings)
        self.privacy_model.currentTextChanged.connect(self.save_all_settings)
        self.dnd_checkbox.stateChanged.connect(self.save_all_settings)
        self.notification_checkbox.stateChanged.connect(self.save_all_settings)
        self.keyword_input.textChanged.connect(self.save_all_settings)
        self.trigger_count_slider.valueChanged.connect(self.save_all_settings)

# ---------------- Run Application ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    floating = FloatingSettings()
    floating.show()
    sys.exit(app.exec_())
