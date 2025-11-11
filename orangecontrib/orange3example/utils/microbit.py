# -*- coding: utf-8 -*-
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
    # CRLF로 전송 (마이크로비트/펌웨어에서 CRLF를 기대하는 경우 대응)
    _connection.write((message + '\r\n').encode('utf-8'))

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
        # 이전 수신 버퍼를 비우고, CRLF로 전송
        _connection.reset_input_buffer()
        message = text.strip() + '\r\n'
        _connection.write(message.encode('utf-8'))
        _connection.flush()  # 버퍼 즉시 전송
        time.sleep(0.05)  # 전송 안정화 짧은 대기
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
                    # 완전한 응답을 받기 위해 타임아웃을 두고 모든 데이터 읽기
                    response_parts = []
                    no_data_count = 0
                    max_no_data = 20  # 0.05초 * 20 = 1초 동안 추가 데이터 없으면 완료로 간주
                    start_time = time.time()
                    max_wait_time = 2.0  # 최대 2초 대기
                    
                    while True:
                        current_time = time.time()
                        if current_time - start_time > max_wait_time:
                            break  # 최대 대기 시간 초과
                        
                        if _connection.in_waiting > 0:
                            # 사용 가능한 모든 바이트 읽기
                            available_bytes = _connection.in_waiting
                            data = _connection.read(available_bytes).decode('utf-8', errors='ignore')
                            if data:
                                response_parts.append(data)
                                no_data_count = 0  # 데이터가 있으면 카운터 리셋
                                start_time = current_time  # 데이터가 오면 시간 리셋
                        else:
                            no_data_count += 1
                            if no_data_count >= max_no_data:
                                break  # 추가 데이터 없음, 응답 완료
                        
                        time.sleep(0.05)  # 짧은 대기
                    
                    if response_parts:
                        # 모든 데이터를 합쳐서 하나의 응답으로 처리
                        full_response = "".join(response_parts).strip()
                        # 개행 문자 제거 및 정리
                        full_response = full_response.replace('\r', '').replace('\n', ' ')
                        # 여러 공백을 하나로 합치기
                        full_response = ' '.join(full_response.split())
                        if full_response and _text_input_callback:
                            _text_input_callback(full_response)
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
