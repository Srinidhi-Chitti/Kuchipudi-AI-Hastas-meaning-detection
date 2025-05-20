import sys
import cv2
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer
from PIL import Image
import numpy as np
from skimage import feature

class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Video Capture with Image Processing")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)

        self.process_button = QPushButton("Toggle Edge Detection")
        self.process_button.clicked.connect(self.toggle_processing)
        self.processing_enabled = False

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.process_button)
        self.setLayout(layout)

        # Open webcam using OpenCV
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam")

        # Timer to update frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def toggle_processing(self):
        self.processing_enabled = not self.processing_enabled

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Flip frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)

        # Convert BGR (OpenCV) to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image for processing
        img = Image.fromarray(rgb_frame)

        if self.processing_enabled:
            gray = img.convert('L')
            gray_np = np.array(gray)
            edges = feature.canny(gray_np, sigma=1)
            edges_img = Image.fromarray((edges * 255).astype(np.uint8))
            img = edges_img.convert('RGB')

        # Convert PIL Image to Qt QPixmap for display
        qt_img = self.pil2pixmap(img)
        self.image_label.setPixmap(qt_img)

    def pil2pixmap(self, im):
        im = im.convert("RGBA")
        data = im.tobytes("raw", "RGBA")
        qimage = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec())
