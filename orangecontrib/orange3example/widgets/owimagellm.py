# -*- coding: utf-8 -*-
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets import gui
from Orange.widgets.settings import Setting
import Orange.data
from AnyQt.QtWidgets import QTextEdit, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit
from AnyQt.QtGui import QPixmap, QImage
from AnyQt.QtCore import Qt
import numpy as np
import base64
import io
from PIL import Image
from orangecontrib.orange3example.utils.llm import LLM

class OWImageLLM(OWWidget):
    name = "Image LLM"
    description = "Process images and text with multimodal LLM"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 20
    api_key = Setting("")

    class Inputs:
        image_data = Input("Image Data", np.ndarray, auto_summary=False)
        text_data = Input("Text Data", Orange.data.Table)

    class Outputs:
        llm_response = Output("LLM Response", Orange.data.Table)

    def __init__(self):
        super().__init__()

        # Image display area
        self.image_label = QLabel("No image input")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(200, 150)
        self.image_label.setStyleSheet("border: 2px dashed #ccc;")
        
        # API Key input field
        self.api_key_input = QLineEdit(self.controlArea)
        self.api_key_input.setPlaceholderText("OpenAI API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.api_key)

        # Prompt input field
        self.prompt = "Please analyze this image and text."
        self.prompt_input = QTextEdit(self.controlArea)
        self.prompt_input.setPlainText(self.prompt)
        self.prompt_input.setPlaceholderText("Enter prompt here...")
        self.prompt_input.setMinimumHeight(80)
        
        # Execute button
        self.process_button = gui.button(
            self.controlArea, self, "Run Multimodal Analysis", callback=self.process
        )
        self.process_button.setDisabled(True)
        
        # Result output field
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMinimumHeight(100)
        
        # Layout setup
        control_layout = QVBoxLayout()
        control_layout.addWidget(QLabel("Input Image:"))
        control_layout.addWidget(self.image_label)
        control_layout.addWidget(QLabel("API Key"))
        control_layout.addWidget(self.api_key_input)
        control_layout.addWidget(QLabel("Prompt:"))
        control_layout.addWidget(self.prompt_input)
        control_layout.addWidget(self.process_button)
        self.controlArea.layout().addLayout(control_layout)
        
        # Display results in main area
        self.mainArea.layout().addWidget(QLabel("LLM Response Result:"))
        self.mainArea.layout().addWidget(self.result_display)
        
        # Data storage variables
        self.image_data = None
        self.text_data = None
        self.has_image = False
        self.has_text = False

    @Inputs.image_data
    def set_image_data(self, data):
        """Handle image data input"""
        if data is not None and isinstance(data, np.ndarray):
            self.image_data = data
            self.has_image = True
            self.display_image(data)
            self.check_inputs()
            # Auto process when image arrives
            if self.has_text:
                self.process()
        else:
            self.image_data = None
            self.has_image = False
            self.image_label.setText("No image input")
            self.image_label.setStyleSheet("border: 2px dashed #ccc;")
            self.check_inputs()

    @Inputs.text_data
    def set_text_data(self, data):
        """Handle text data input"""
        if data is not None and isinstance(data, Orange.data.Table):
            self.text_data = data
            self.has_text = True
            self.check_inputs()
            # Auto process when text arrives
            if self.has_image:
                self.process()
        else:
            self.text_data = None
            self.has_text = False
            self.check_inputs()

    def display_image(self, image_array):
        """Convert numpy array to QPixmap and display"""
        try:
            # Use image as-is if RGB format
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # Convert RGB image to PIL Image
                pil_image = Image.fromarray(image_array.astype(np.uint8))
            else:
                # Convert grayscale or other formats to RGB
                pil_image = Image.fromarray(image_array.astype(np.uint8))
                if len(pil_image.getbands()) == 1:
                    pil_image = pil_image.convert('RGB')
            
            # Convert to QPixmap
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            qimage = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimage)
            
            # Resize image
            pixmap = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_label.setStyleSheet("border: none;")
            
        except Exception as e:
            self.image_label.setText(f"Image display error: {str(e)}")
            self.image_label.setStyleSheet("border: 2px dashed #ccc;")

    def check_inputs(self):
        """Check input data status and enable/disable button"""
        if self.has_image or self.has_text:
            self.process_button.setDisabled(False)
        else:
            self.process_button.setDisabled(True)

    def process(self):
        """Execute multimodal LLM processing"""
        try:
            self.prompt = self.prompt_input.toPlainText()
            api_key_value = (self.api_key_input.text() or "").strip() or None
            # Save setting
            self.api_key = self.api_key_input.text()
            
            # Create LLM instance
            llm = LLM(api_key=api_key_value)
            
            # Prepare multimodal data
            multimodal_data = self.prepare_multimodal_data()
            
            # Call LLM API
            results = llm.get_multimodal_response(self.prompt, multimodal_data)
            
            # Convert results to Orange data table (store in meta)
            domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("LLM Response")])
            response_data = Orange.data.Table.from_list(domain, [[str(result)] for result in results])
            
            # Send output
            self.Outputs.llm_response.send(response_data)
            
            # Display results
            self.result_display.setPlainText("\n".join(results))
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.result_display.setPlainText(error_msg)
            
            # Send error result as output
            domain = Orange.data.Domain([], metas=[Orange.data.StringVariable("Error")])
            error_data = Orange.data.Table.from_list(domain, [[error_msg]])
            self.Outputs.llm_response.send(error_data)

    def prepare_multimodal_data(self):
        """Prepare multimodal data"""
        multimodal_content = []
        
        # Encode image data to base64 if present
        if self.has_image and self.image_data is not None:
            try:
                # Encode image to base64
                pil_image = Image.fromarray(self.image_data.astype(np.uint8))
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG')
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                multimodal_content.append({
                    "type": "image",
                    "data": image_base64,
                    "description": "Image from Microbit"
                })
            except Exception as e:
                multimodal_content.append({
                    "type": "text",
                    "data": f"Image processing error: {str(e)}"
                })
        
        # Process text data if present
        if self.has_text and self.text_data is not None:
            try:
                # Convert string-meta variables to text
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
                        "data": "No text data"
                    })
            except Exception as e:
                multimodal_content.append({
                    "type": "text",
                    "data": f"Text processing error: {str(e)}"
                })
        
        return multimodal_content
