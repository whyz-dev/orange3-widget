from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from Orange.widgets.settings import Setting
import Orange.data
from PyQt5.QtWidgets import QTextEdit, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
import base64
import io
from PIL import Image
from orangecontrib.orange3example.utils.llm import LLM

class OWImageLLM(OWWidget):
    name = "Image LLM"
    description = "마이크로비트 이미지와 텍스트를 입력받아 멀티모달 LLM으로 처리하는 Orange3 위젯"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 20
    api_key = Setting("")

    class Inputs:
        image_data = Input("이미지 데이터", np.ndarray, auto_summary=False)
        text_data = Input("텍스트 데이터", Orange.data.Table)

    class Outputs:
        llm_response = Output("LLM 응답", Orange.data.Table)

    def __init__(self):
        super().__init__()

        # 이미지 표시 영역
        self.image_label = QLabel("이미지가 입력되지 않았습니다")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(200, 150)
        self.image_label.setStyleSheet("border: 2px dashed #ccc;")
        
        # API Key 입력 필드
        self.api_key_input = QLineEdit(self.controlArea)
        self.api_key_input.setPlaceholderText("OpenAI API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.api_key)

        # 프롬프트 입력 필드
        self.prompt = "이 이미지와 텍스트를 분석해주세요."
        self.prompt_input = QTextEdit(self.controlArea)
        self.prompt_input.setPlainText(self.prompt)
        self.prompt_input.setPlaceholderText("여기에 프롬프트를 입력하세요...")
        self.prompt_input.setMinimumHeight(80)
        
        # 실행 버튼
        self.process_button = gui.button(
            self.controlArea, self, "멀티모달 분석 실행", callback=self.process
        )
        self.process_button.setDisabled(True)
        
        # 결과 출력 필드
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMinimumHeight(100)
        
        # 레이아웃 설정
        control_layout = QVBoxLayout()
        control_layout.addWidget(QLabel("입력 이미지:"))
        control_layout.addWidget(self.image_label)
        control_layout.addWidget(QLabel("API Key"))
        control_layout.addWidget(self.api_key_input)
        control_layout.addWidget(QLabel("프롬프트:"))
        control_layout.addWidget(self.prompt_input)
        control_layout.addWidget(self.process_button)
        self.controlArea.layout().addLayout(control_layout)
        
        # 메인 영역에 결과 표시
        self.mainArea.layout().addWidget(QLabel("LLM 응답 결과:"))
        self.mainArea.layout().addWidget(self.result_display)
        
        # 데이터 저장 변수
        self.image_data = None
        self.text_data = None
        self.has_image = False
        self.has_text = False

    @Inputs.image_data
    def set_image_data(self, data):
        """이미지 데이터 입력 처리"""
        if data is not None and isinstance(data, np.ndarray):
            self.image_data = data
            self.has_image = True
            self.display_image(data)
            self.check_inputs()
            # 이미지가 들어오면 자동으로 처리
            if self.has_text:
                self.process()
        else:
            self.image_data = None
            self.has_image = False
            self.image_label.setText("이미지가 입력되지 않았습니다")
            self.image_label.setStyleSheet("border: 2px dashed #ccc;")
            self.check_inputs()

    @Inputs.text_data
    def set_text_data(self, data):
        """텍스트 데이터 입력 처리"""
        if data is not None and isinstance(data, Orange.data.Table):
            self.text_data = data
            self.has_text = True
            self.check_inputs()
            # 텍스트가 들어오면 자동으로 처리
            if self.has_image:
                self.process()
        else:
            self.text_data = None
            self.has_text = False
            self.check_inputs()

    def display_image(self, image_array):
        """numpy 배열을 QPixmap으로 변환하여 표시"""
        try:
            # 이미지가 RGB 형식으로 전달되었으므로 그대로 사용
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # RGB 이미지를 PIL Image로 변환
                pil_image = Image.fromarray(image_array.astype(np.uint8))
            else:
                # 그레이스케일 또는 다른 형식인 경우 RGB로 변환
                pil_image = Image.fromarray(image_array.astype(np.uint8))
                if len(pil_image.getbands()) == 1:
                    pil_image = pil_image.convert('RGB')
            
            # QPixmap으로 변환
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            qimage = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimage)
            
            # 이미지 크기 조정
            pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_label.setStyleSheet("border: none;")
            
        except Exception as e:
            self.image_label.setText(f"이미지 표시 오류: {str(e)}")
            self.image_label.setStyleSheet("border: 2px dashed #ccc;")

    def check_inputs(self):
        """입력 데이터 상태 확인 및 버튼 활성화/비활성화"""
        if self.has_image or self.has_text:
            self.process_button.setDisabled(False)
        else:
            self.process_button.setDisabled(True)

    def process(self):
        """멀티모달 LLM 처리 실행"""
        try:
            self.prompt = self.prompt_input.toPlainText()
            api_key_value = (self.api_key_input.text() or "").strip() or None
            # Setting 저장
            self.api_key = self.api_key_input.text()
            
            # LLM 인스턴스 생성
            llm = LLM(api_key=api_key_value)
            
            # 멀티모달 데이터 준비
            multimodal_data = self.prepare_multimodal_data()
            
            # LLM API 호출
            results = llm.get_multimodal_response(self.prompt, multimodal_data)
            
            # 결과를 Orange 데이터 테이블로 변환 (메타에 저장)
            domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("LLM Response")])
            response_data = Orange.data.Table.from_list(domain, [[str(result)] for result in results])
            
            # 출력 전송
            self.Outputs.llm_response.send(response_data)
            
            # 결과 표시
            self.result_display.setPlainText("\n".join(results))
            
        except Exception as e:
            error_msg = f"처리 중 오류 발생: {str(e)}"
            self.result_display.setPlainText(error_msg)
            
            # 오류 결과도 출력으로 전송
            domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("Error")])
            error_data = Orange.data.Table.from_list(domain, [[error_msg]])
            self.Outputs.llm_response.send(error_data)

    def prepare_multimodal_data(self):
        """멀티모달 데이터 준비"""
        multimodal_content = []
        
        # 이미지 데이터가 있는 경우 base64로 인코딩
        if self.has_image and self.image_data is not None:
            try:
                # 이미지를 base64로 인코딩
                pil_image = Image.fromarray(self.image_data.astype(np.uint8))
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG')
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                multimodal_content.append({
                    "type": "image",
                    "data": image_base64,
                    "description": "마이크로비트에서 전송된 이미지"
                })
            except Exception as e:
                multimodal_content.append({
                    "type": "text",
                    "data": f"이미지 처리 오류: {str(e)}"
                })
        
        # 텍스트 데이터가 있는 경우
        if self.has_text and self.text_data is not None:
            try:
                # string-meta 변수들을 텍스트로 변환
                string_meta_indices = [
                    idx for idx, var in enumerate(self.text_data.domain.metas)
                    if isinstance(var, Orange.data.StringVariable)
                ]
                
                if string_meta_indices:
                    text_content = [
                        " ".join(str(row.metas[idx]) for idx in string_meta_indices)
                        for row in self.text_data
                    ]
                    multimodal_content.append({
                        "type": "text",
                        "data": "\n".join(text_content)
                    })
                else:
                    multimodal_content.append({
                        "type": "text",
                        "data": "텍스트 데이터 없음"
                    })
            except Exception as e:
                multimodal_content.append({
                    "type": "text",
                    "data": f"텍스트 처리 오류: {str(e)}"
                })
        
        return multimodal_content
