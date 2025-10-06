from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit


class OutputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.output_label = QLabel("Formatted Reference:")
        layout.addWidget(self.output_label)

        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        layout.addWidget(self.output_text_edit)

        self.setLayout(layout)

    def display_output(self, formatted_reference):
        self.output_text_edit.setPlainText(formatted_reference)