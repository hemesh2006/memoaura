import sys
import json
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

class GifOverlay(QMainWindow):
    def __init__(self, json_path):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.json_path = json_path
        self.labels = []

        # Set up a timer to read the JSON file every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_overlays)
        self.timer.start(1000)

    def update_overlays(self):
        try:
            with open(self.json_path, 'r') as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading JSON file: {e}")
            return

        # Clear old labels
        for label in self.labels:
            label.deleteLater()
        self.labels.clear()

        # Create new labels based on JSON data
        for item in data:
            if len(item) != 2:
                print("Invalid item format in JSON. Expected [image_path, [x, y]].")
                continue

            gif_path = item[0]
            position = item[1]

            if not isinstance(position, list) or len(position) != 2:
                print("Invalid position format. Expected [x, y].")
                continue

            x, y = position

            # Set up the QLabel for displaying the GIF
            label = QLabel(self)
            movie = QMovie(gif_path)

            if not movie.isValid():
                print(f"Error: Unable to load GIF at {gif_path}")
                continue

            # Start the GIF and set the label size to match the GIF dimensions
            label.setMovie(movie)
            movie.start()

            # Resize the label to the GIF's dimensions
            gif_size = movie.frameRect().size()
            label.setGeometry(QRect(x, y, gif_size.width(), gif_size.height()))
            label.show()
            self.labels.append(label)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Replace 'overlay_config.json' with the path to your JSON file
    json_path = r'gif.json'
    overlay = GifOverlay(json_path)
    overlay.show()

    sys.exit(app.exec_())
