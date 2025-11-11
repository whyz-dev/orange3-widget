# -*- coding: utf-8 -*-
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
import numpy as np
import cv2

try:
    from orangecontrib.orange3example.utils import webcam
except ImportError:
    webcam = None

class OWWebcam(OWWidget):
    name = "Webcam Viewer"
    description = "웹캠을 실시간으로 표시하고 캡쳐 버튼을 눌러 이미지를 전송하는 위젯"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 30

    # Output signal 정의
    outputs = [("Image", np.ndarray)]

    def __init__(self):
        super().__init__()

        self.image_label = QLabel("웹캠이 시작되지 않았습니다.")
        self.controlArea.layout().addWidget(self.image_label)

        self.start_button = QPushButton("웹캠 시작")
        self.stop_button = QPushButton("중지")
        self.capture_button = QPushButton("이미지 캡쳐")
        self.capture_button.setEnabled(False)

        self.controlArea.layout().addWidget(self.start_button)
        self.controlArea.layout().addWidget(self.stop_button)
        self.controlArea.layout().addWidget(self.capture_button)

        self.start_button.clicked.connect(self.start_webcam)
        self.stop_button.clicked.connect(self.stop_webcam)
        self.capture_button.clicked.connect(self.capture_image)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # 웹캠 상태 추적
        self.webcam_active = False
        self.current_frame = None  # 현재 프레임 저장

    def start_webcam(self):
        if webcam:
            webcam.start_camera()
            self.timer.start(30)  # 약 30 FPS
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
        self.image_label.setText("웹캠이 중지되었습니다.")
        # 웹캠 중지 시 output 클리어
        self.send("Image", None)

    def update_frame(self):
        """웹캠 프레임을 읽어서 화면에만 표시 (출력은 보내지 않음)"""
        if not webcam or not self.webcam_active:
            return
        frame = webcam.read_frame()
        if frame is None:
            return
        
        # 현재 프레임을 저장 (캡쳐용)
        self.current_frame = frame.copy()
            
        # 화면에 표시만 (BGR 형식 그대로 사용)
        frame_qimage = cvt_frame_to_qimage(frame)
        pixmap = QPixmap.fromImage(frame_qimage)
        self.image_label.setPixmap(pixmap)
        
        # 출력은 보내지 않음 (캡쳐 버튼을 눌렀을 때만 보냄)

    def capture_image(self):
        """현재 프레임을 캡쳐해서 출력으로 전송"""
        if self.current_frame is None:
            return
        
        # BGR -> RGB 변환 후 출력으로 전송
        frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        self.send("Image", frame_rgb)


def cvt_frame_to_qimage(frame):
    h, w, ch = frame.shape
    bytes_per_line = ch * w
    # OpenCV는 BGR 형식이므로 BGR888 사용
    image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
    return image