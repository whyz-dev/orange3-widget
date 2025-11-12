# -*- coding: utf-8 -*-
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui
from AnyQt.QtWidgets import QLabel, QPushButton, QVBoxLayout
from AnyQt.QtGui import QPixmap, QImage
from AnyQt.QtCore import QTimer
import sys
import subprocess
import threading
import numpy as np

try:
    from orangecontrib.orange3example.utils import webcam
except ImportError:
    webcam = None

class OWWebcam(OWWidget):
    name = "Webcam Viewer"
    description = "Display webcam in real-time and capture images"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 30

    outputs = [("Image", np.ndarray)]

    def __init__(self):
        super().__init__()

        self.image_label = QLabel("Webcam not started.")
        self.controlArea.layout().addWidget(self.image_label)

        self.start_button = QPushButton("Start Webcam")
        self.stop_button = QPushButton("Stop Webcam")
        self.capture_button = QPushButton("Capture Image")
        self.capture_button.setEnabled(False)

        self.controlArea.layout().addWidget(self.start_button)
        self.controlArea.layout().addWidget(self.stop_button)
        self.controlArea.layout().addWidget(self.capture_button)

        self.start_button.clicked.connect(self.start_webcam)
        self.stop_button.clicked.connect(self.stop_webcam)
        self.capture_button.clicked.connect(self.capture_image)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        self.webcam_active = False
        self.current_frame = None

    def start_webcam(self):
        if webcam:
            webcam.start_camera()
            self.timer.start(30)
            self.webcam_active = True
            self.capture_button.setEnabled(True)
            self.start_button.setEnabled(False)

    def stop_webcam(self):
        self.timer.stop()
        if webcam:
            webcam.stop_camera()
        self.webcam_active = False
        self.capture_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.current_frame = None
        self.image_label.setText("Webcam stopped.")
        self.send("Image", None)

    def update_frame(self):
        """Read webcam frame and display only (don't send output)"""
        if not webcam or not self.webcam_active:
            return
        frame = webcam.read_frame()
        if frame is None:
            return
        
        self.current_frame = frame.copy()
            
        frame_qimage = cvt_frame_to_qimage(frame)
        pixmap = QPixmap.fromImage(frame_qimage)
        self.image_label.setPixmap(pixmap)
        

    def capture_image(self):
        """Capture current frame and send as output"""
        if self.current_frame is None:
            return
        
        try:
            import cv2
        except Exception:
            self.image_label.setText("OpenCV not installed. Cannot capture.\nInstall with 'pip install orange3-example[webcam]'.")
            return
        frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        self.send("Image", frame_rgb)


def cvt_frame_to_qimage(frame):
    h, w, ch = frame.shape
    bytes_per_line = ch * w
    image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
    return image