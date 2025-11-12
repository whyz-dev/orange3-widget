# -*- coding: utf-8 -*-
from Orange.widgets.widget import OWWidget, Input
import Orange.data
from Orange.data import StringVariable

from AnyQt.QtWidgets import QTextEdit, QPushButton, QComboBox, QLabel, QHBoxLayout, QWidget, QVBoxLayout, QCheckBox
from orangecontrib.orange3example.utils import microbit


class OWMicrobit(OWWidget):
    name = "Microbit Communicator"
    description = "Send data to Microbit through serial port"
    icon = "../icons/machine-learning-03-svgrepo-com.svg"
    priority = 20

    class Inputs:
        text_data = Input("Text Input", Orange.data.Table)

    def __init__(self):
        super().__init__()

        self.text_data = None

        # Port selection UI
        port_layout = QHBoxLayout()
        port_widget = QWidget()
        port_widget.setLayout(port_layout)

        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        port_layout.addWidget(self.port_combo)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_button)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_microbit)
        port_layout.addWidget(self.connect_button)

        self.status_label = QLabel("Not Connected")
        port_layout.addWidget(self.status_label)

        self.controlArea.layout().addWidget(port_widget)

        # Text input for sending
        self.send_box = QTextEdit()
        self.send_box.setPlaceholderText("Enter text to send to Microbit")
        self.send_box.setMaximumHeight(80)
        self.controlArea.layout().addWidget(self.send_box)

        # Button layout
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_to_microbit)
        button_layout.addWidget(self.send_button)
        
        self.auto_send_checkbox = QCheckBox("Auto Send")
        self.auto_send_checkbox.setChecked(True)
        button_layout.addWidget(self.auto_send_checkbox)
        
        self.controlArea.layout().addLayout(button_layout)

        # Log output area
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(100)
        self.controlArea.layout().addWidget(self.log_box)

        # Load initial port list
        self.refresh_ports()

    def log(self, text):
        self.log_box.append(text)

    def refresh_ports(self):
        self.port_combo.clear()
        self.log("Refreshing ports...")
        if microbit:
            try:
                ports = microbit.list_ports()
                if ports:
                    self.port_combo.addItems(ports)
                    self.log(f"Available ports: {', '.join(ports)}")
                else:
                    self.log("No available ports.")
            except Exception as e:
                self.log(f"Port search failed: {str(e)}")
        else:
            self.log("Microbit module not loaded.")

    def connect_to_microbit(self):
        if not microbit:
            self.status_label.setText("No microbit module")
            self.log("No microbit module.")
            return

        port = self.port_combo.currentText()
        try:
            microbit.connect(port)
            self.status_label.setText(f"Connected ({port})")
            self.log(f"Connected to port {port}.")
                
        except Exception as e:
            self.status_label.setText(f"Connection failed")
            self.log(f"Connection failed: {str(e)}")

    @Inputs.text_data
    def set_text_data(self, data):
        """Handle input text data"""
        if data is None:
            self.log("Input data is None.")
            self.text_data = None
            if not self.auto_send_checkbox.isChecked():
                self.send_box.clear()
            return
            
        if not isinstance(data, Orange.data.Table):
            self.log(f"Unexpected data type: {type(data)}")
            return
            
        self.text_data = data
        text = ""
        
        try:
            # Extract text from all string variables (attributes, class, metas)
            all_vars = data.domain.variables + data.domain.metas
            string_vars = [var for var in all_vars if isinstance(var, StringVariable)]
            
            if string_vars:
                text_content = []
                for row in data:
                    row_texts = []
                    for var in string_vars:
                        value = str(row[var]) 
                        if value != "?" and value:
                            row_texts.append(value)
                    if row_texts:
                        text_content.append(" ".join(row_texts))
                        
                if text_content:
                    text = "\n".join(text_content)
                else:
                    self.log("String variables exist but no valid text.")
            else:
                self.log("No String variables in input table.")

            if text:
                self.log(f"Received input data: {text}")
                if self.auto_send_checkbox.isChecked():
                    self.send_text_to_microbit(text)
                else:
                    self.send_box.setPlainText(text)
            else:
                self.log("No text extracted from input.")
                if not self.auto_send_checkbox.isChecked():
                    self.send_box.clear()
                    
        except Exception as e:
            self.log(f"Failed to extract input text: {e}")

    def send_text_to_microbit(self, text: str):
        """Send text to Microbit (one-way)"""
        if not text:
            self.log("No text to send.")
            return

        if not microbit:
            self.log("No microbit module.")
            return

        if not microbit.is_connected():
            self.log("Port not connected.")
            return

        try:
            # Use non-blocking send only
            if hasattr(microbit, 'send_text'):
                success = microbit.send_text(text)
                if success:
                    self.log(f"Sent: {text}")
                else:
                    self.log("Send failed")
            else:
                self.log("Error: 'send_text' function not found in microbit module.")
                
        except Exception as e:
            self.log(f"Error during send: {str(e)}")

    def send_to_microbit(self):
        text = self.send_box.toPlainText().strip()
        self.send_text_to_microbit(text)