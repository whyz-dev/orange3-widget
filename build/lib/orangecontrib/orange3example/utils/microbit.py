import serial
import time
import serial.tools.list_ports
import threading

_connection = None
_text_input_callback = None
_is_listening = False


def list_ports() -> list:
    """사용 가능한 시리얼 포트 목록 반환"""
    return [port.device for port in serial.tools.list_ports.comports()]


def connect(port: str, baudrate: int = 115200, timeout: float = 1.0) -> str:
    """포트에 연결 시도. 성공 시 포트명 반환."""
    global _connection
    if _connection:
        _connection.close()
    _connection = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    time.sleep(2)  # 연결 안정화 대기
    return _connection.port


def disconnect():
    """연결 해제"""
    global _connection, _is_listening
    _is_listening = False
    if _connection and _connection.is_open:
        _connection.close()
        _connection = None


def is_connected() -> bool:
    """현재 연결 여부 반환"""
    global _connection
    return _connection is not None and _connection.is_open


def send_and_receive(message: str, wait_time: float = 2.0) -> str:
    """메시지 전송 후 응답 수신"""
    global _connection
    if not _connection or not _connection.is_open:
        raise RuntimeError("Microbit 연결이 되어 있지 않습니다. connect(port)를 먼저 호출하세요.")

    _connection.reset_input_buffer()  # 🧹 이전 수신 버퍼 정리
    _connection.write((message + '\n').encode('utf-8'))

    time.sleep(wait_time)

    if _connection.in_waiting > 0:
        try:
            response = _connection.readline().decode('utf-8', errors='ignore').strip()
            return response if response else "[응답 없음]"
        except Exception as e:
            return f"[디코딩 오류: {str(e)}]"
    else:
        return "[타임아웃: 응답 없음]"


def send_text(text: str) -> bool:
    """텍스트를 마이크로비트로 즉시 전송"""
    global _connection
    if not _connection or not _connection.is_open:
        print("Microbit 연결이 되어 있지 않습니다.")
        return False
    
    try:
        # 텍스트에 개행 문자 추가하여 전송
        message = text.strip() + '\n'
        _connection.write(message.encode('utf-8'))
        _connection.flush()  # 버퍼 즉시 전송
        print(f"전송됨: {text}")
        return True
    except Exception as e:
        print(f"전송 오류: {str(e)}")
        return False


def start_text_listening(callback=None):
    """마이크로비트로부터 텍스트 응답을 실시간으로 수신하는 리스너 시작"""
    global _connection, _text_input_callback, _is_listening
    
    if not _connection or not _connection.is_open:
        print("Microbit 연결이 되어 있지 않습니다.")
        return False
    
    _text_input_callback = callback
    _is_listening = True
    
    def listen_thread():
        while _is_listening and _connection and _connection.is_open:
            try:
                if _connection.in_waiting > 0:
                    response = _connection.readline().decode('utf-8', errors='ignore').strip()
                    if response and _text_input_callback:
                        _text_input_callback(response)
                time.sleep(0.1)  # CPU 사용량 줄이기
            except Exception as e:
                print(f"리스닝 오류: {str(e)}")
                break
    
    # 별도 스레드에서 리스닝 시작
    listener = threading.Thread(target=listen_thread, daemon=True)
    listener.start()
    print("마이크로비트 응답 리스닝 시작됨")
    return True


def stop_text_listening():
    """텍스트 응답 리스닝 중지"""
    global _is_listening
    _is_listening = False
    print("마이크로비트 응답 리스닝 중지됨")


def send_text_with_response(text: str, wait_time: float = 1.0) -> str:
    """텍스트 전송 후 응답 대기"""
    if send_text(text):
        time.sleep(wait_time)
        if _connection and _connection.in_waiting > 0:
            try:
                response = _connection.readline().decode('utf-8', errors='ignore').strip()
                return response if response else "[응답 없음]"
            except Exception as e:
                return f"[응답 읽기 오류: {str(e)}]"
        else:
            return "[응답 없음]"
    return "[전송 실패]"
