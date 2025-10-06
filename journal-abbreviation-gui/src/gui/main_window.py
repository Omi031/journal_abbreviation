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
    QApplication,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from core.app import App
from gui.widgets.settings_dialog import SettingsDialog
from datetime import datetime, timedelta


class YearMonthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Early Access論文の年月選択")
        self.setGeometry(300, 300, 400, 250)
        self.setModal(True)

        # ダイアログのスタイル設定
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Yu Gothic UI', 'メイリオ', sans-serif;
            }
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin: 10px 0;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
            }
        """
        )

        self.selected_year_month = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 説明ラベル
        label = QLabel("Early Access論文の年月を選択してください：")
        label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #212529;
                margin: 10px 0;
                padding: 8px;
            }
        """
        )
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
        month_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #6c757d;
                margin-bottom: 5px;
            }
        """
        )
        month_layout.addWidget(month_label)

        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet(
            """
            QComboBox {
                font-size: 11px;
                padding: 8px 12px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #80bdff;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6c757d;
            }
        """
        )
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
        selection_layout.addLayout(month_layout)  # 年選択
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
        preview_text_label = QLabel("プレビュー:")
        preview_text_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #6c757d;
            }
        """
        )
        preview_layout.addWidget(preview_text_label)

        self.preview_label = QLabel()
        self.preview_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #007bff;
                background-color: #e7f3ff;
                padding: 6px 12px;
                border-radius: 4px;
                border: 1px solid #b3d9ff;
            }
        """
        )
        preview_layout.addWidget(self.preview_label)

        main_layout.addLayout(preview_layout)  # 選択が変更されたときにプレビューを更新
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
        self.manual_input.setStyleSheet(
            """
            QLineEdit {
                font-size: 11px;
                padding: 10px 12px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #80bdff;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
        """
        )
        manual_layout.addWidget(self.manual_input)

        layout.addWidget(manual_group)

        # OK/Cancelボタン
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet(
            """
            QDialogButtonBox QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                min-width: 80px;
                margin: 5px;
            }
            QDialogButtonBox QPushButton[text="OK"] {
                background-color: #007bff;
                color: white;
                border: 2px solid #007bff;
            }
            QDialogButtonBox QPushButton[text="OK"]:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            QDialogButtonBox QPushButton[text="Cancel"] {
                background-color: #6c757d;
                color: white;
                border: 2px solid #6c757d;
            }
            QDialogButtonBox QPushButton[text="Cancel"]:hover {
                background-color: #545b62;
                border-color: #545b62;
            }
        """
        )
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
        self.setGeometry(100, 100, 800, 600)

        self.app = App()

        # アプリケーション全体のスタイル設定
        self.apply_font_settings()

    def apply_font_settings(self):
        """フォント設定を適用"""
        ui_font = f"{self.app.ui_font_family}"
        ui_size = self.app.ui_font_size
        input_font = f"{self.app.input_font_family}"
        input_size = self.app.input_font_size
        output_font = f"{self.app.output_font_family}"
        output_size = self.app.output_font_size

        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: #f8f9fa;
                font-family: '{ui_font}', sans-serif;
                font-size: {ui_size}px;
            }}
            QMenuBar {{
                background-color: #ffffff;
                color: #212529;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: #e9ecef;
            }}
        """
        )

        # メニューバーを作成
        self.create_menu_bar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.central_widget.setLayout(self.layout)

        # 入力部分
        self.input_label = QLabel("RIS形式の参考文献データを入力してください:")
        self.layout.addWidget(self.input_label)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "例:\nTY  - JOUR\nAU  - Smith, John\nTI  - Sample Article\n..."
        )
        self.layout.addWidget(self.input_text)

        # フォーマットボタン
        self.format_button = QPushButton("📖 Format Reference")
        self.format_button.clicked.connect(self.format_reference)
        self.layout.addWidget(self.format_button)

        # 出力部分
        self.output_label = QLabel("フォーマット済み参考文献:")
        self.layout.addWidget(self.output_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

        # 初期フォント設定を適用
        self.update_font_settings()

    def update_font_settings(self):
        """フォント設定を更新"""
        ui_font = self.app.ui_font_family
        ui_size = self.app.ui_font_size
        input_font = self.app.input_font_family
        input_size = self.app.input_font_size
        output_font = self.app.output_font_family
        output_size = self.app.output_font_size

        # ラベルのスタイル更新
        label_style = f"""
            QLabel {{
                font-family: '{ui_font}', sans-serif;
                font-size: {ui_size + 2}px;
                font-weight: bold;
                color: #495057;
                margin-bottom: 5px;
            }}
        """
        self.input_label.setStyleSheet(label_style)
        self.output_label.setStyleSheet(label_style)

        # 入力テキストエリアのスタイル更新
        input_style = f"""
            QTextEdit {{
                font-family: '{input_font}', 'Courier New', monospace;
                font-size: {input_size}px;
                padding: 12px;
                border: 2px solid #ced4da;
                border-radius: 8px;
                background-color: white;
                line-height: 1.4;
            }}
            QTextEdit:focus {{
                border-color: #007bff;
                outline: none;
            }}
        """
        self.input_text.setStyleSheet(input_style)

        # フォーマットボタンのスタイル更新
        button_style = f"""
            QPushButton {{
                font-family: '{ui_font}', sans-serif;
                font-size: {ui_size + 2}px;
                font-weight: bold;
                padding: 15px 30px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
            QPushButton:pressed {{
                background-color: #004085;
            }}
        """
        self.format_button.setStyleSheet(button_style)

        # 出力テキストエリアのスタイル更新
        output_style = f"""
            QTextEdit {{
                font-family: '{output_font}', 'Yu Mincho', '游明朝', serif;
                font-size: {output_size}px;
                padding: 12px;
                border: 2px solid #28a745;
                border-radius: 8px;
                background-color: #f8fff8;
                line-height: 1.6;
            }}
            QTextEdit:focus {{
                border-color: #20c997;
                outline: none;
            }}
        """
        self.output_text.setStyleSheet(output_style)

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
        if dialog.exec_() == QDialog.Accepted:
            # 設定が保存された場合、フォント設定を更新
            self.update_font_settings()

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
