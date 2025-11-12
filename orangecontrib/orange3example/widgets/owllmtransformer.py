# -*- coding: utf-8 -*-
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from Orange.widgets.settings import Setting
import Orange.data
from AnyQt.QtWidgets import QTextEdit, QLineEdit, QLabel
from orangecontrib.orange3example.utils.llm import LLM

class OWLLMTransformer(OWWidget):
    name = "LLM Transformer"
    description = "Transform input data using GPT API"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 10
    api_key = Setting("")

    class Inputs:
        text_data = Input("Input Data", Orange.data.Table)

    class Outputs:
        transformed_data = Output("GPT Response", Orange.data.Table)

    def __init__(self):
        super().__init__()

        self.api_key_input = QLineEdit(self.controlArea)
        self.api_key_input.setPlaceholderText("OpenAI API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.api_key)
        self.controlArea.layout().addWidget(QLabel("API Key"))
        self.controlArea.layout().addWidget(self.api_key_input)

        self.prompt = "Please transform the input data."
        self.prompt_input = QTextEdit(self.controlArea)
        self.prompt_input.setPlainText(self.prompt)
        self.prompt_input.setPlaceholderText("Enter prompt here...")
        self.prompt_input.setMinimumHeight(100)
        self.controlArea.layout().addWidget(self.prompt_input)

        self.transform_button = gui.button(
            self.controlArea, self, "Transform", callback=self.process
        )
        self.transform_button.setDisabled(True)

        # Result output field (QTextEdit)
        self.result_text = ""
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.mainArea.layout().addWidget(self.result_display)

        self.text_data = None

    @Inputs.text_data
    def set_data(self, data):
        if isinstance(data, Orange.data.Table):
            string_meta_indices = [
                idx for idx, var in enumerate(data.domain.metas)
                if isinstance(var, Orange.data.StringVariable)
            ]
            data = [
                " ".join(str(row.metas[idx]) for idx in string_meta_indices)
                for row in data
            ]

        self.text_data = data
        self.transform_button.setDisabled(False)


    def process(self):
        """Call GPT API only when Transform button is clicked"""
        self.prompt = self.prompt_input.toPlainText()
        api_key_value = (self.api_key_input.text() or "").strip() or None
        self.api_key = self.api_key_input.text()
        
        domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("Transformed Text")])

        llm = LLM(api_key=api_key_value)
        results = llm.get_response(self.prompt, self.text_data) 
        transformed_data = Orange.data.Table.from_list(domain, [[str(result)] for result in results])

        self.Outputs.transformed_data.send(transformed_data)

        self.result_text = "\n".join(results)
        self.result_display.setPlainText(self.result_text)
