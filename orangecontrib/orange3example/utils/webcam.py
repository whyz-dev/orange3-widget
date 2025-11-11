import cv2

cap = None

def start_camera(index=0):
    global cap
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
