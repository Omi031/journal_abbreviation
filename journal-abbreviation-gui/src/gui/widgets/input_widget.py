from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from core.app import App

class InputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.app = App()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Input the reference (or 'exit' to quit):")
        layout.addWidget(self.label)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.handle_submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def handle_submit(self):
        input_text = self.text_edit.toPlainText()
        if input_text.strip().lower() == "exit":
            self.close()
        else:
            data = self.app.make_cite_dict(input_text)
            if data:
                formatted = self.app.format(data, format="tex")
                self.show_message("Formatted Reference", formatted)
            else:
                self.show_message("Error", "Invalid input format.")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()