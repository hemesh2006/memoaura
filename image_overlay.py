import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

class ImageOverlay(QMainWindow):
    def __init__(self, json_path):
        super().__init__()

        self.json_path = json_path

        # Set window to be frameless, transparent, always on top, full screen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setAttribute(Qt.WA_TranslucentBackground)

        # Lists to store images and timers
        self.image_labels = []
        self.blink_timers = []

        # Load initial images
        self.load_images_from_json()

        # Timer to reload JSON periodically
        self.reload_timer = QTimer(self)
        self.reload_timer.timeout.connect(self.load_images_from_json)
        self.reload_timer.start(1000)  # reload every 1 second

    def load_images_from_json(self):
        """Read JSON file and load images."""
        try:
            with open(self.json_path, "r") as file:
                images = json.load(file)
                self.load_images(images)
        except Exception as e:
            print(f"Error reading JSON file: {e}")

    def load_images(self, images):
        """Load images and handle blinking."""
        self.clear_images()

        for image_data in images:
            if len(image_data) != 3:
                print("Invalid image format, expected [filename, position, blink_interval]")
                continue

            image_file, position, blink_interval = image_data
            x, y = position
            label = QLabel(self)
            image_path =  image_file
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                print(f"Failed to load image: {image_path}")
                continue

            label.setPixmap(pixmap)
            label.setAttribute(Qt.WA_TranslucentBackground)
            label.adjustSize()
            label.move(x, y)
            label.show()

            self.image_labels.append(label)

            # Only blink if interval > 0
            if blink_interval > 0:
                self.start_blinking(label, blink_interval)

    def start_blinking(self, label, blink_interval):
        """Start blinking a label indefinitely."""
        timer = QTimer(self)

        # Use a proper function to toggle visibility
        def toggle_visibility():
            label.setVisible(not label.isVisible())

        timer.timeout.connect(toggle_visibility)
        timer.start(blink_interval)
        self.blink_timers.append(timer)

    def clear_images(self):
        """Remove all current images and stop blinking."""
        for label in self.image_labels:
            label.hide()
            label.deleteLater()
        self.image_labels.clear()

        # Stop all timers
        for timer in self.blink_timers:
            timer.stop()
        self.blink_timers.clear()

    def show_overlay(self):
        """Show the overlay window."""
        self.show()

def main():
    app = QApplication(sys.argv)

    # Path to JSON file
    json_path = r"images.json"

    overlay = ImageOverlay(json_path)
    overlay.show_overlay()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
