from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import get_distribution
import Orange.data

from PyQt5.QtWidgets import QTextEdit, QPushButton, QComboBox, QLabel, QHBoxLayout, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from orangecontrib.orange3example.utils import microbit


class OWMicrobit(OWWidget):
    name = "Microbit Communicator"
    description = "통신 포트를 통해 마이크로비트와 데이터를 주고받는 위젯"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 20

    class Inputs:
        text_data = Input("입력 텍스트", Orange.data.Table)

    class Outputs:
        received_data = Output("수신 데이터", Orange.data.Table)

    def __init__(self):
        super().__init__()

        self.text_data = None
        self.received_text = ""
        self.is_listening = False

        # 포트 선택 UI
        port_layout = QHBoxLayout()
        port_widget = QWidget()
        port_widget.setLayout(port_layout)

        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        port_layout.addWidget(self.port_combo)

        self.refresh_button = QPushButton("🔄")
        self.refresh_button.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_button)

        self.connect_button = QPushButton("연결")
        self.connect_button.clicked.connect(self.connect_to_microbit)
        port_layout.addWidget(self.connect_button)

        self.status_label = QLabel("연결되지 않음")
        port_layout.addWidget(self.status_label)

        self.controlArea.layout().addWidget(port_widget)

        # 전송 텍스트 입력
        self.send_box = QTextEdit()
        self.send_box.setPlaceholderText("마이크로비트로 보낼 텍스트를 입력하세요")
        self.send_box.setMaximumHeight(80)
        self.controlArea.layout().addWidget(self.send_box)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("전송")
        self.send_button.clicked.connect(self.send_to_microbit)
        button_layout.addWidget(self.send_button)
        
        self.auto_send_checkbox = QPushButton("자동 전송")
        self.auto_send_checkbox.setCheckable(True)
        self.auto_send_checkbox.setChecked(True)
        button_layout.addWidget(self.auto_send_checkbox)
        
        self.listen_button = QPushButton("응답 리스닝 시작")
        self.listen_button.clicked.connect(self.toggle_listening)
        button_layout.addWidget(self.listen_button)
        
        self.controlArea.layout().addLayout(button_layout)

        # 수신 텍스트 표시
        self.receive_box = QTextEdit()
        self.receive_box.setReadOnly(True)
        self.mainArea.layout().addWidget(self.receive_box)

        # 로그 출력창
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(100)
        self.controlArea.layout().addWidget(self.log_box)

        # 응답 리스닝을 위한 타이머 (더 빠른 주기로 변경)
        self.response_timer = QTimer()
        self.response_timer.timeout.connect(self.check_response)
        self.response_timer.start(50)  # 50ms마다 응답 확인 (더 빠르게)

        # 초기 포트 목록 로드
        self.refresh_ports()

    def log(self, text):
        self.log_box.append(text)

    def refresh_ports(self):
        self.port_combo.clear()
        self.log("🔄 포트 새로고침 중...")
        if microbit:
            try:
                ports = microbit.list_ports()
                if ports:
                    self.port_combo.addItems(ports)
                    self.log(f"사용 가능한 포트: {', '.join(ports)}")
                else:
                    self.log("사용 가능한 포트가 없습니다.")
            except Exception as e:
                self.log(f"포트 검색 실패: {str(e)}")
        else:
            self.log("microbit 모듈이 로드되지 않았습니다.")

    def connect_to_microbit(self):
        if not microbit:
            self.status_label.setText("microbit 모듈 없음")
            self.log("microbit 모듈이 없습니다.")
            return

        port = self.port_combo.currentText()
        try:
            microbit.connect(port)
            self.status_label.setText(f"연결됨 ({port})")
            self.log(f"{port} 포트에 연결되었습니다.")
            
            # 연결 후 자동으로 응답 리스닝 시작
            if not self.is_listening:
                self.start_listening()
                
        except Exception as e:
            self.status_label.setText(f"연결 실패")
            self.log(f"연결 실패: {str(e)}")

    def toggle_listening(self):
        """응답 리스닝 토글"""
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        """응답 리스닝 시작"""
        if not microbit or not microbit.is_connected():
            self.log("마이크로비트가 연결되지 않았습니다.")
            return
            
        try:
            # microbit 모듈의 리스닝 시작
            if hasattr(microbit, 'start_text_listening'):
                microbit.start_text_listening(self.on_microbit_response)
                self.is_listening = True
                self.listen_button.setText("응답 리스닝 중지")
                self.log("응답 리스닝이 시작되었습니다.")
            else:
                self.log("응답 리스닝 기능을 사용할 수 없습니다.")
        except Exception as e:
            self.log(f"리스닝 시작 실패: {str(e)}")

    def stop_listening(self):
        """응답 리스닝 중지"""
        try:
            if hasattr(microbit, 'stop_text_listening'):
                microbit.stop_text_listening()
            self.is_listening = False
            self.listen_button.setText("응답 리스닝 시작")
            self.log("응답 리스닝이 중지되었습니다.")
        except Exception as e:
            self.log(f"리스닝 중지 실패: {str(e)}")

    def on_microbit_response(self, response):
        """마이크로비트로부터 응답을 받았을 때 호출되는 콜백"""
        if not response or response.strip() == "":
            return
            
        self.received_text = response
        self.receive_box.setPlainText(response)
        self.log(f"응답 수신: {response}")
        
        # 출력 데이터 전송
        domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("Received")])
        out_table = Orange.data.Table(domain, [[response]])
        self.Outputs.received_data.send(out_table)

    def check_response(self):
        """타이머 기반 응답 확인 (백업 방법)"""
        if not microbit or not microbit.is_connected():
            return
            
        try:
            # microbit 모듈에서 직접 응답 확인
            if hasattr(microbit, '_connection') and microbit._connection and microbit._connection.in_waiting > 0:
                response = microbit._connection.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    self.log(f"타이머로 응답 감지: {response}")
                    self.on_microbit_response(response)
                    
            # 추가 디버깅: 연결 상태 확인
            if hasattr(microbit, '_connection') and microbit._connection:
                # 연결 상태 로그 (1초마다 한 번씩만)
                if not hasattr(self, '_last_debug_time'):
                    self._last_debug_time = 0
                
                import time
                current_time = time.time()
                if current_time - self._last_debug_time > 1.0:  # 1초마다
                    self._last_debug_time = current_time
                    if microbit._connection.in_waiting > 0:
                        self.log(f"대기 중인 데이터: {microbit._connection.in_waiting} bytes")
                        
        except Exception as e:
            # 오류를 로그에 기록
            self.log(f"응답 확인 오류: {str(e)}")

    @Inputs.text_data
    def set_text_data(self, data):
        if isinstance(data, Orange.data.Table):
            self.text_data = data
            try:
                # string-meta 변수에서 텍스트 추출
                string_meta_indices = [
                    idx for idx, var in enumerate(data.domain.metas)
                    if isinstance(var, Orange.data.StringVariable)
                ]
                
                if string_meta_indices:
                    text_content = [
                        " ".join(str(row.metas[idx]) for idx in string_meta_indices)
                        for row in data
                    ]
                    text = "\n".join(text_content)
                else:
                    # 일반 데이터에서 텍스트 추출
                    try:
                        text = str(data[0][0])
                    except (IndexError, AttributeError):
                        # 데이터가 비어있거나 다른 형태인 경우
                        text = str(data)
                
                self.log(f"입력 데이터를 수신했습니다: {text}")
                
                # 자동 전송이 활성화되어 있으면 즉시 전송
                if self.auto_send_checkbox.isChecked():
                    self.send_text_to_microbit(text)
                else:
                    # 수동 전송 모드면 입력창에 표시
                    self.send_box.setPlainText(text)
                    
            except Exception as e:
                self.log(f"입력 텍스트 추출 실패: {e}")
                # 오류가 발생해도 데이터를 표시
                try:
                    text = str(data)
                    self.log(f"원본 데이터: {text}")
                    if self.auto_send_checkbox.isChecked():
                        self.send_text_to_microbit(text)
                    else:
                        self.send_box.setPlainText(text)
                except Exception as e2:
                    self.log(f"데이터 표시 실패: {e2}")

    def send_text_to_microbit(self, text: str):
        if not text:
            self.receive_box.setPlainText("전송할 텍스트가 없습니다.")
            self.log("전송할 텍스트가 없습니다.")
            return

        if not microbit:
            self.receive_box.setPlainText("[Error] microbit 모듈이 없습니다.")
            self.log("microbit 모듈이 없습니다.")
            return

        if not microbit.is_connected():
            self.receive_box.setPlainText("먼저 포트를 연결하세요.")
            self.log("포트가 연결되지 않았습니다.")
            return

        try:
            # 즉시 전송 (응답 대기 없음)
            if hasattr(microbit, 'send_text'):
                success = microbit.send_text(text)
                if success:
                    self.log(f"전송됨: {text}")
                    # 응답 대기 시작
                    self.wait_for_response()
                else:
                    self.log("전송 실패")
            else:
                # 기존 방식으로 전송
                response = microbit.send_and_receive(text)
                self.receive_box.setPlainText(response)
                self.log(f"보냄: {text}")
                self.log(f"수신: {response}")
                
                domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("Received")])
                out_table = Orange.data.Table(domain, [[response]])
                self.Outputs.received_data.send(out_table)
                
        except Exception as e:
            self.receive_box.setPlainText(f"[Error] {str(e)}")
            self.log(f"전송 중 오류 발생: {str(e)}")

    def wait_for_response(self):
        """응답 대기 타이머 시작"""
        # 기존 타이머가 있으면 중지
        if hasattr(self, 'response_wait_timer'):
            self.response_wait_timer.stop()
            
        # 응답 대기 타이머 설정 (3초 후 타임아웃)
        self.response_wait_timer = QTimer()
        self.response_wait_timer.timeout.connect(self.check_response_timeout)
        self.response_wait_timer.start(3000)  # 3초로 단축
        self.log("응답 대기 시작 (3초 타임아웃)")

    def check_response_timeout(self):
        """응답 대기 타임아웃 체크"""
        if hasattr(self, 'response_wait_timer'):
            self.response_wait_timer.stop()
        self.log("응답 대기 타임아웃 - 응답이 없습니다.")
        self.receive_box.setPlainText("응답 대기 타임아웃")
        
        # 타임아웃 결과도 출력으로 전송
        domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("Timeout")])
        timeout_data = Orange.data.Table(domain, [["응답 대기 타임아웃"]])
        self.Outputs.received_data.send(timeout_data)

    def send_to_microbit(self):
        text = self.send_box.toPlainText().strip()
        self.send_text_to_microbit(text)
