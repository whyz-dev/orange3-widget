# -*- coding: utf-8 -*-

cap = None
_cv2 = None


def _ensure_cv2():
    global _cv2
    if _cv2 is None:
        try:
            import cv2 as _imported_cv2  # type: ignore
            _cv2 = _imported_cv2
        except Exception as exc:
            raise RuntimeError("OpenCV가 설치되어 있지 않습니다. 'pip install orange3-example[webcam]' 또는 opencv-python-headless를 설치하세요.") from exc
    return _cv2


def start_camera(index=0):
    global cap
    cv2 = _ensure_cv2()
    if cap is None:
        cap = cv2.VideoCapture(index)


def read_frame():
    global cap
    if cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            return frame
    return None


def stop_camera():
    global cap
    if cap is not None:
        cap.release()
        cap = None
