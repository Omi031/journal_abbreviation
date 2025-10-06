from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import yaml
import os

# CSV編集ダイアログのインポート（遅延インポートを回避するため、ここではコメントアウト）
# from .csv_editor_dialog import CSVEditorDialog


class SettingsDialog(QDialog):
    def __init__(self, app_instance, parent=None):
        super().__init__(parent)
        self.app_instance = app_instance
        self.setWindowTitle("設定")
        self.setGeometry(200, 200, 400, 500)
        self.setModal(True)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 引用スタイル設定
        citation_group = QGroupBox("引用設定")
        citation_layout = QFormLayout()

        # et al. 閾値
        self.et_al_spinbox = QSpinBox()
        self.et_al_spinbox.setMinimum(1)
        self.et_al_spinbox.setMaximum(10)
        self.et_al_spinbox.setValue(4)
        citation_layout.addRow("Et al. 閾値:", self.et_al_spinbox)

        # 引用スタイル
        self.cite_style_combo = QComboBox()
        self.cite_style_combo.addItems(["ris"])
        citation_layout.addRow("引用スタイル:", self.cite_style_combo)

        # 出力フォーマット
        self.format_combo = QComboBox()
        self.format_combo.addItems(["tex", "plain"])
        citation_layout.addRow("出力フォーマット:", self.format_combo)

        citation_group.setLayout(citation_layout)
        layout.addWidget(citation_group)

        # 会議論文設定
        conference_group = QGroupBox("会議論文設定")
        conference_layout = QFormLayout()

        self.with_in_checkbox = QCheckBox()
        conference_layout.addRow("'in' を追加:", self.with_in_checkbox)

        self.with_proc_checkbox = QCheckBox()
        conference_layout.addRow("'Proc.' を追加:", self.with_proc_checkbox)

        self.with_year_checkbox = QCheckBox()
        conference_layout.addRow("年を含める:", self.with_year_checkbox)

        conference_group.setLayout(conference_layout)
        layout.addWidget(conference_group)

        # ファイルパス設定
        path_group = QGroupBox("データファイルパス")
        path_layout = QFormLayout()

        self.jo_abb_path_edit = QLineEdit()
        path_layout.addRow("ジャーナル略語ファイル:", self.jo_abb_path_edit)

        self.jo_del_path_edit = QLineEdit()
        path_layout.addRow("ジャーナル削除ファイル:", self.jo_del_path_edit)

        self.mo_abb_path_edit = QLineEdit()
        path_layout.addRow("月略語ファイル:", self.mo_abb_path_edit)

        # CSV編集ボタン
        self.edit_csv_button = QPushButton("CSVファイルを編集...")
        self.edit_csv_button.clicked.connect(self.open_csv_editor)
        path_layout.addRow("", self.edit_csv_button)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # フォント設定
        font_group = QGroupBox("フォント設定")
        font_layout = QFormLayout()

        # UIフォント
        self.ui_font_combo = QComboBox()
        self.ui_font_combo.addItems(
            [
                "Segoe UI",
                "Yu Gothic UI",
                "メイリオ",
                "MS UI Gothic",
                "Arial",
                "Helvetica",
                "Tahoma",
            ]
        )
        self.ui_font_combo.setEditable(True)
        font_layout.addRow("UIフォント:", self.ui_font_combo)

        self.ui_font_size_spinbox = QSpinBox()
        self.ui_font_size_spinbox.setMinimum(8)
        self.ui_font_size_spinbox.setMaximum(24)
        self.ui_font_size_spinbox.setValue(12)
        font_layout.addRow("UIフォントサイズ:", self.ui_font_size_spinbox)

        # 入力フォント
        self.input_font_combo = QComboBox()
        self.input_font_combo.addItems(
            [
                "Consolas",
                "Courier New",
                "Monaco",
                "Inconsolata",
                "Source Code Pro",
                "Fira Code",
            ]
        )
        self.input_font_combo.setEditable(True)
        font_layout.addRow("入力フォント:", self.input_font_combo)

        self.input_font_size_spinbox = QSpinBox()
        self.input_font_size_spinbox.setMinimum(8)
        self.input_font_size_spinbox.setMaximum(24)
        self.input_font_size_spinbox.setValue(12)
        font_layout.addRow("入力フォントサイズ:", self.input_font_size_spinbox)

        # 出力フォント
        self.output_font_combo = QComboBox()
        self.output_font_combo.addItems(
            [
                "Times New Roman",
                "Yu Mincho",
                "游明朝",
                "MS Mincho",
                "Georgia",
                "Cambria",
                "Garamond",
            ]
        )
        self.output_font_combo.setEditable(True)
        font_layout.addRow("出力フォント:", self.output_font_combo)

        self.output_font_size_spinbox = QSpinBox()
        self.output_font_size_spinbox.setMinimum(8)
        self.output_font_size_spinbox.setMaximum(24)
        self.output_font_size_spinbox.setValue(14)
        font_layout.addRow("出力フォントサイズ:", self.output_font_size_spinbox)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        # クリップボード設定
        clipboard_group = QGroupBox("クリップボード設定")
        clipboard_layout = QFormLayout()

        self.auto_copy_checkbox = QCheckBox()
        self.auto_copy_checkbox.setToolTip("フォーマット後に自動的に結果をクリップボードにコピーします")
        clipboard_layout.addRow("自動コピー:", self.auto_copy_checkbox)

        clipboard_group.setLayout(clipboard_layout)
        layout.addWidget(clipboard_group)

        # ボタン
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.reset_button = QPushButton("デフォルトに戻す")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

    def get_settings_path(self):
        """設定ファイルのパスを取得"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, "..", "..", "..")
        return os.path.join(project_root, "data", "settings.yml")

    def load_current_settings(self):
        """現在の設定を読み込んでUIに反映"""
        try:
            settings_path = self.get_settings_path()
            with open(settings_path, encoding="utf-8") as yml:
                settings = yaml.safe_load(yml)

            self.et_al_spinbox.setValue(settings.get("et_al_th", 4))

            cite_style = settings.get("cite_style", "ris")
            index = self.cite_style_combo.findText(cite_style)
            if index >= 0:
                self.cite_style_combo.setCurrentIndex(index)

            format_type = settings.get("format", "tex")
            format_index = self.format_combo.findText(format_type)
            if format_index >= 0:
                self.format_combo.setCurrentIndex(format_index)

            self.with_in_checkbox.setChecked(settings.get("conf_with_in", False))
            self.with_proc_checkbox.setChecked(settings.get("conf_with_proc", True))
            self.with_year_checkbox.setChecked(settings.get("conf_with_year", False))

            self.jo_abb_path_edit.setText(
                settings.get("jo_abb_path", "data/jo_abb.csv")
            )
            self.jo_del_path_edit.setText(
                settings.get("jo_del_path", "data/jo_del.csv")
            )
            self.mo_abb_path_edit.setText(
                settings.get("mo_abb_path", "data/mo_abb.csv")
            )

            # フォント設定の読み込み
            ui_font = settings.get("ui_font_family", "Segoe UI")
            ui_font_index = self.ui_font_combo.findText(ui_font)
            if ui_font_index >= 0:
                self.ui_font_combo.setCurrentIndex(ui_font_index)
            else:
                self.ui_font_combo.setCurrentText(ui_font)
            self.ui_font_size_spinbox.setValue(settings.get("ui_font_size", 12))

            input_font = settings.get("input_font_family", "Consolas")
            input_font_index = self.input_font_combo.findText(input_font)
            if input_font_index >= 0:
                self.input_font_combo.setCurrentIndex(input_font_index)
            else:
                self.input_font_combo.setCurrentText(input_font)
            self.input_font_size_spinbox.setValue(settings.get("input_font_size", 12))

            output_font = settings.get("output_font_family", "Times New Roman")
            output_font_index = self.output_font_combo.findText(output_font)
            if output_font_index >= 0:
                self.output_font_combo.setCurrentIndex(output_font_index)
            else:
                self.output_font_combo.setCurrentText(output_font)
            self.output_font_size_spinbox.setValue(settings.get("output_font_size", 14))

            # クリップボード設定の読み込み
            self.auto_copy_checkbox.setChecked(settings.get("auto_copy_to_clipboard", True))

        except Exception as e:
            QMessageBox.warning(
                self, "エラー", f"設定の読み込みに失敗しました: {str(e)}"
            )

    def save_settings(self):
        """設定を保存"""
        try:
            settings = {
                "et_al_th": self.et_al_spinbox.value(),
                "cite_style": self.cite_style_combo.currentText(),
                "format": self.format_combo.currentText(),
                "conf_with_in": self.with_in_checkbox.isChecked(),
                "conf_with_proc": self.with_proc_checkbox.isChecked(),
                "conf_with_year": self.with_year_checkbox.isChecked(),
                "jo_abb_path": self.jo_abb_path_edit.text(),
                "jo_del_path": self.jo_del_path_edit.text(),
                "mo_abb_path": self.mo_abb_path_edit.text(),
                # フォント設定
                "ui_font_family": self.ui_font_combo.currentText(),
                "ui_font_size": self.ui_font_size_spinbox.value(),
                "input_font_family": self.input_font_combo.currentText(),
                "input_font_size": self.input_font_size_spinbox.value(),
                "output_font_family": self.output_font_combo.currentText(),
                "output_font_size": self.output_font_size_spinbox.value(),
                # クリップボード設定
                "auto_copy_to_clipboard": self.auto_copy_checkbox.isChecked(),
            }

            settings_path = self.get_settings_path()
            with open(settings_path, "w", encoding="utf-8") as yml:
                yaml.dump(settings, yml, default_flow_style=False, allow_unicode=True)

            # アプリケーションの設定を更新
            self.app_instance.reload_settings()

            QMessageBox.information(self, "成功", "設定が保存されました。")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "エラー", f"設定の保存に失敗しました: {str(e)}")

    def reset_to_defaults(self):
        """デフォルト設定に戻す"""
        self.et_al_spinbox.setValue(4)
        self.cite_style_combo.setCurrentText("ris")
        self.format_combo.setCurrentText("tex")
        self.with_in_checkbox.setChecked(False)
        self.with_proc_checkbox.setChecked(True)
        self.with_year_checkbox.setChecked(False)
        self.jo_abb_path_edit.setText("data/jo_abb.csv")
        self.jo_del_path_edit.setText("data/jo_del.csv")
        self.mo_abb_path_edit.setText("data/mo_abb.csv")

        # フォント設定をデフォルトに戻す
        self.ui_font_combo.setCurrentText("Segoe UI")
        self.ui_font_size_spinbox.setValue(12)
        self.input_font_combo.setCurrentText("Consolas")
        self.input_font_size_spinbox.setValue(12)
        self.output_font_combo.setCurrentText("Times New Roman")
        self.output_font_size_spinbox.setValue(14)
        
        # クリップボード設定をデフォルトに戻す
        self.auto_copy_checkbox.setChecked(True)

    def open_csv_editor(self):
        """CSV編集ダイアログを開く"""
        try:
            from .csv_editor_dialog import CSVEditorDialog

            csv_editor = CSVEditorDialog(self.app_instance, self)
            csv_editor.exec_()
        except Exception as e:
            QMessageBox.critical(
                self, "エラー", f"CSV編集ダイアログを開けませんでした: {str(e)}"
            )
