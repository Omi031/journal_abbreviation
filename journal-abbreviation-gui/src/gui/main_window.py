from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
from core.app import App

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Journal Abbreviation Formatter")
        self.setGeometry(100, 100, 600, 400)

        self.app = App()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.input_label = QLabel("Input the reference:")
        self.layout.addWidget(self.input_label)

        self.input_text = QTextEdit()
        self.layout.addWidget(self.input_text)

        self.format_button = QPushButton("Format Reference")
        self.format_button.clicked.connect(self.format_reference)
        self.layout.addWidget(self.format_button)

        self.output_label = QLabel("Formatted Reference:")
        self.layout.addWidget(self.output_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

    def format_reference(self):
        input_data = self.input_text.toPlainText()
        if input_data.lower() == "exit":
            self.close()
            return

        formatted_data = self.app.format(self.app.make_cite_dict(input_data), format="tex")
        if formatted_data:
            self.output_text.setPlainText(formatted_data)
        else:
            self.output_text.setPlainText("Error formatting reference.")