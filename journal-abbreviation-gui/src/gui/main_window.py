from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMenuBar,
    QAction,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from core.app import App
from gui.widgets.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Journal Abbreviation Formatter")
        self.setGeometry(100, 100, 600, 400)

        self.app = App()

        # メニューバーを作成
        self.create_menu_bar()

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

    def create_menu_bar(self):
        """メニューバーを作成"""
        menubar = self.menuBar()

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")

        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 設定メニュー
        settings_menu = menubar.addMenu("設定(&S)")

        settings_action = QAction("設定(&P)...", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        settings_menu.addSeparator()
        
        csv_action = QAction("CSVファイル編集(&C)...", self)
        csv_action.triggered.connect(self.open_csv_editor)
        settings_menu.addAction(csv_action)

    def open_settings(self):
        """設定ダイアログを開く"""
        dialog = SettingsDialog(self.app, self)
        dialog.exec_()
        
    def open_csv_editor(self):
        """CSV編集ダイアログを開く"""
        try:
            from gui.widgets.csv_editor_dialog import CSVEditorDialog
            csv_editor = CSVEditorDialog(self.app, self)
            csv_editor.exec_()
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"CSV編集ダイアログを開けませんでした: {str(e)}")

    def format_reference(self):
        input_data = self.input_text.toPlainText()
        if input_data.lower() == "exit":
            self.close()
            return

        cite_dict = self.app.make_cite_dict(input_data)
        if cite_dict:
            formatted_data = self.app.format(cite_dict, format=self.app.format_type)
            if formatted_data:
                self.output_text.setPlainText(formatted_data)
            else:
                self.output_text.setPlainText("Error formatting reference.")
        else:
            self.output_text.setPlainText("Error parsing input data.")
