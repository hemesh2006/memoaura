import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QProgressBar, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

# List of motivational quotes
quotes = [
    "Keep pushing forward!",
    "This too shall pass.",
    "Stay positive, work hard, make it happen.",
    "Every day is a fresh start.",
    "Believe in yourself!"
]

class StressOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 800, 450)  # Slightly taller overlay
        self.center()
        
        # Semi-transparent background panel
        self.bg_label = QLabel(self)
        self.bg_label.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 15px;")
        self.bg_label.setGeometry(0, 0, 800, 450)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Slightly increase spacing between widgets
        
        # Stress message
        self.stress_label = QLabel("You are stressed!")
        self.stress_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.stress_label.setStyleSheet("color: lime;")
        self.addGlow(self.stress_label)
        self.stress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stress_label)
        
        # Motivational quote
        self.quote_label = QLabel(random.choice(quotes))
        self.quote_label.setFont(QFont("Arial", 16))
        self.quote_label.setStyleSheet("color: lime;")
        self.addGlow(self.quote_label)
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.quote_label)
        
        # Stress percentage
        self.progress = QProgressBar()
        self.progress.setValue(random.randint(50, 100))
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: lime;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress)
        
        # Buttons with increased size
        self.remind_button = QPushButton("Remind me after 1 hour")
        self.remind_button.setStyleSheet("""
            background-color: green; 
            color: white; 
            font-weight: bold; 
            font-size: 16px; 
            padding: 10px 20px;
            min-height: 45px;
        """)
        self.remind_button.clicked.connect(self.remind_me)
        layout.addWidget(self.remind_button)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("""
            background-color: darkgreen; 
            color: white; 
            font-weight: bold; 
            font-size: 16px; 
            padding: 10px 20px;
            min-height: 45px;
        """)
        self.submit_button.clicked.connect(self.submit_action)
        layout.addWidget(self.submit_button)
        
        # Apply layout to background
        self.bg_label.setLayout(layout)
        
    def addGlow(self, widget):
        glow = QGraphicsDropShadowEffect()
        glow.setColor(QColor(0, 255, 0))
        glow.setBlurRadius(20)
        glow.setOffset(0)
        widget.setGraphicsEffect(glow)
    
    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def remind_me(self):
        # Optional: set reminder message somewhere or schedule action
        print("Reminder set for 1 hour later")  # For debugging/logging
        self.close()
        sys.exit(0)  # Close overlay after button pressed

    def submit_action(self):
        print("Submit pressed")  # For debugging/logging
        self.close()
        sys.exit(0)  # Close overlay after button pressed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = StressOverlay()
    overlay.show()
    app.exec_()
