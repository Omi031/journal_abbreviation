from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QMenuBar,
    QAction,
    QMessageBox,
    QInputDialog,
    QDialog,
    QComboBox,
    QDialogButtonBox,
    QLineEdit,
    QSpinBox,
    QGroupBox,
)
from PyQt5.QtCore import Qt
from core.app import App
from gui.widgets.settings_dialog import SettingsDialog
from datetime import datetime, timedelta


class YearMonthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Early Access論文の年月選択")
        self.setGeometry(300, 300, 350, 200)
        self.setModal(True)

        self.selected_year_month = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 説明ラベル
        label = QLabel("Early Access論文の年月を選択してください：")
        layout.addWidget(label)

        # メイン選択部分をグループボックスに
        main_group = QGroupBox("年月選択")
        main_layout = QVBoxLayout()
        main_group.setLayout(main_layout)

        # 年と月の選択部分
        selection_layout = QHBoxLayout()

        # 月選択
        month_layout = QVBoxLayout()
        month_label = QLabel("月:")
        month_layout.addWidget(month_label)

        self.month_combo = QComboBox()
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        self.month_combo.addItems(months)

        # 現在の月を初期選択
        current_month = datetime.now().month - 1
        self.month_combo.setCurrentIndex(current_month)

        month_layout.addWidget(self.month_combo)
        selection_layout.addLayout(month_layout)

        # 年選択
        year_layout = QVBoxLayout()
        year_label = QLabel("年:")
        year_layout.addWidget(year_label)

        self.year_spinbox = QSpinBox()
        current_year = datetime.now().year
        self.year_spinbox.setRange(
            current_year - 10, current_year + 5
        )  # 過去10年〜未来5年
        self.year_spinbox.setValue(current_year)
        self.year_spinbox.setSuffix(" 年")

        # スピンボックスのサイズを調整
        self.year_spinbox.setMinimumWidth(100)

        year_layout.addWidget(self.year_spinbox)
        selection_layout.addLayout(year_layout)

        main_layout.addLayout(selection_layout)

        # プレビュー表示
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("プレビュー:"))

        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        preview_layout.addWidget(self.preview_label)

        main_layout.addLayout(preview_layout)

        # 選択が変更されたときにプレビューを更新
        self.month_combo.currentTextChanged.connect(self.update_preview)
        self.year_spinbox.valueChanged.connect(self.update_preview)

        # 初期プレビュー表示
        self.update_preview()

        layout.addWidget(main_group)

        # 手動入力オプション（オプションとして残す）
        manual_group = QGroupBox("手動入力（オプション）")
        manual_layout = QHBoxLayout()
        manual_group.setLayout(manual_layout)

        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("例: January 2024, Dec. 2023")
        manual_layout.addWidget(self.manual_input)

        layout.addWidget(manual_group)

        # OK/Cancelボタン
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_preview(self):
        """プレビューを更新"""
        month = self.month_combo.currentText()
        year = self.year_spinbox.value()
        preview_text = f"{month} {year}"
        self.preview_label.setText(preview_text)

    def accept_selection(self):
        """選択を確定"""
        # 手動入力がある場合はそれを優先
        manual_text = self.manual_input.text().strip()
        if manual_text:
            self.selected_year_month = manual_text
        else:
            # 月と年の選択から構成
            month = self.month_combo.currentText()
            year = self.year_spinbox.value()
            self.selected_year_month = f"{month} {year}"

        self.accept()

    def get_selected_year_month(self):
        return self.selected_year_month


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
            QMessageBox.critical(
                self, "エラー", f"CSV編集ダイアログを開けませんでした: {str(e)}"
            )

    def get_year_input(self):
        """ユーザーから年月を選択/入力してもらう"""
        dialog = YearMonthDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_year_month = dialog.get_selected_year_month()
            if selected_year_month:
                return selected_year_month
        return None

    def format_reference(self):
        input_data = self.input_text.toPlainText()
        if input_data.lower() == "exit":
            self.close()
            return

        cite_dict = self.app.make_cite_dict(input_data)
        if cite_dict:
            formatted_data = self.app.format(
                cite_dict,
                format=self.app.format_type,
                year_input_callback=self.get_year_input,
            )
            if formatted_data:
                self.output_text.setPlainText(formatted_data)
            else:
                self.output_text.setPlainText("Error formatting reference.")
        else:
            self.output_text.setPlainText("Error parsing input data.")
