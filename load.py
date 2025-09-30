import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QMovie
import load
class LoadingOverlay(QWidget):
    def __init__(self):
        super().__init__()
        # Floating overlay settings
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(450, 350)  # medium size overlay

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)  # more padding
        layout.setSpacing(30)

        # GIF Animation
        self.gif_label = QLabel()
        self.gif = QMovie("running.gif")  # 👈 Add your GIF path here
        self.gif.setScaledSize(QSize(140, 140))  # slightly larger GIF
        self.gif_label.setMovie(self.gif)
        self.gif.start()
        layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)

        # App Name
        self.app_label = QLabel("MemoAura")
        self.app_label.setFont(QFont("Arial", 34, QFont.Bold))  # bigger text
        self.app_label.setStyleSheet("color: #00FF00; padding: 10px;")
        layout.addWidget(self.app_label, alignment=Qt.AlignCenter)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedSize(380, 35)
        self.progress.setFont(QFont("Arial", 12, QFont.Bold))
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 3px solid #00FF00;
                border-radius: 18px;
                text-align: center;
                color: white;
                background-color: rgba(0,0,0,50);  /* more transparent */
            }
            QProgressBar::chunk {
                background-color: #00FF00;
                border-radius: 18px;
            }
        """)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        # Overlay background very transparent
        self.setStyleSheet("background-color: rgba(0,0,0,50); border-radius: 25px;")

        # Progress Animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance_progress)
        self.value = 0
        self.timer.start(50)

    def advance_progress(self):
        self.value += 1
        if self.value <= 100:
            self.progress.setValue(self.value)
        else:
            self.timer.stop()
            self.close()  # close overlay when done

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loader = LoadingOverlay()
    loader.show()
    app.exec_()
    print("hellowere")
    
