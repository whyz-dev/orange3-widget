# -*- coding: utf-8 -*-
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from Orange.widgets.settings import Setting
import Orange.data
from AnyQt.QtWidgets import QTextEdit, QLineEdit, QLabel  # QTextEdit 사용
from orangecontrib.orange3example.utils.llm import LLM  # llm.py에서 LLM 클래스를 가져옴

class OWLLMTransformer(OWWidget):
    name = "LLM Transformer"
    description = "GPT API를 통해 입력 데이터를 변환하는 Orange3 위젯"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 10
    api_key = Setting("")

    class Inputs:
        text_data = Input("입력 데이터", Orange.data.Table)

    class Outputs:
        transformed_data = Output("GPT 응답 데이터", Orange.data.Table)

    def __init__(self):
        super().__init__()

        # API Key 입력 필드
        self.api_key_input = QLineEdit(self.controlArea)
        self.api_key_input.setPlaceholderText("OpenAI API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.api_key)
        self.controlArea.layout().addWidget(QLabel("API Key"))
        self.controlArea.layout().addWidget(self.api_key_input)

        # 프롬프트 입력 필드를 크게 만들기 위해 QTextEdit 사용
        self.prompt = "입력 데이터를 변환해주세요."
        self.prompt_input = QTextEdit(self.controlArea)  # QTextEdit으로 프롬프트 입력창 확대
        self.prompt_input.setPlainText(self.prompt)
        self.prompt_input.setPlaceholderText("여기에 프롬프트를 입력하세요...")
        self.prompt_input.setMinimumHeight(100)  # 높이 조정
        self.controlArea.layout().addWidget(self.prompt_input)

        # 변환 실행 버튼
        self.transform_button = gui.button(
            self.controlArea, self, "변환 실행", callback=self.process
        )
        self.transform_button.setDisabled(True)  # 초기에는 비활성화

        # 🛠 결과 출력 필드 (QTextEdit 사용)
        self.result_text = ""
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)  # 읽기 전용 설정
        self.mainArea.layout().addWidget(self.result_display)  # Orange3의 레이아웃에 추가

        self.text_data = None

    @Inputs.text_data
    def set_data(self, data):
        if isinstance(data, Orange.data.Table):
            # 모든 string-meta 변수를 찾음
            string_meta_indices = [
                idx for idx, var in enumerate(data.domain.metas)
                if isinstance(var, Orange.data.StringVariable)
            ]
            # 모든 string-meta 변수를 모아서 하나의 문자열로 합침
            data = [
                " ".join(str(row.metas[idx]) for idx in string_meta_indices)
                for row in data
            ]

        self.text_data = data
        self.transform_button.setDisabled(False)


    def process(self):
        """변환 실행 버튼을 눌렀을 때만 GPT API 호출"""
        self.prompt = self.prompt_input.toPlainText()
        api_key_value = (self.api_key_input.text() or "").strip() or None
        # Setting 저장
        self.api_key = self.api_key_input.text()
        
        # 문자열 데이터를 위한 메타 데이터 설정
        domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("Transformed Text")])

        # GPT API 호출
        llm = LLM(api_key=api_key_value)
        results = llm.get_response(self.prompt, self.text_data) 
        transformed_data = Orange.data.Table.from_list(domain, [[str(result)] for result in results])

        # 변환된 결과를 출력으로 보냄
        self.Outputs.transformed_data.send(transformed_data)

        # 결과 출력 UI 업데이트
        self.result_text = "\n".join(results)  # 결과를 하나의 텍스트로 연결
        self.result_display.setPlainText(self.result_text)
