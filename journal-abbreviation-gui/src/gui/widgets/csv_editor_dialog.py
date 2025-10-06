from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QComboBox,
    QMessageBox,
    QHeaderView,
    QFileDialog,
    QAbstractItemView,
    QLineEdit,
)
from PyQt5.QtCore import Qt
import csv
import os


class CSVEditorDialog(QDialog):
    def __init__(self, app_instance, parent=None):
        super().__init__(parent)
        self.app_instance = app_instance
        self.setWindowTitle("CSVファイル編集")
        self.setGeometry(200, 200, 800, 600)
        self.setModal(True)

        self.current_csv_path = ""
        self.csv_data = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # ファイル選択部分
        file_selection_layout = QHBoxLayout()

        file_label = QLabel("編集するCSVファイル:")
        file_selection_layout.addWidget(file_label)

        self.file_combo = QComboBox()
        self.file_combo.addItems(
            [
                "ジャーナル略語 (jo_abb.csv)",
                "ジャーナル削除 (jo_del.csv)",
                "月略語 (mo_abb.csv)",
            ]
        )
        self.file_combo.currentTextChanged.connect(self.load_selected_csv)
        file_selection_layout.addWidget(self.file_combo)

        layout.addLayout(file_selection_layout)

        # 検索部分
        search_layout = QHBoxLayout()
        search_label = QLabel("検索:")
        search_layout.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("検索キーワードを入力...")
        self.search_edit.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_edit)

        layout.addLayout(search_layout)

        # テーブル部分
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSortingEnabled(True)  # ソート機能を有効化
        layout.addWidget(self.table)

        # 編集ボタン部分
        edit_buttons_layout = QHBoxLayout()

        self.add_row_button = QPushButton("行を追加")
        self.add_row_button.clicked.connect(self.add_row)
        edit_buttons_layout.addWidget(self.add_row_button)

        self.delete_row_button = QPushButton("選択行を削除")
        self.delete_row_button.clicked.connect(self.delete_row)
        edit_buttons_layout.addWidget(self.delete_row_button)

        layout.addLayout(edit_buttons_layout)

        # ファイル操作ボタン部分
        file_buttons_layout = QHBoxLayout()

        self.import_button = QPushButton("CSVインポート")
        self.import_button.clicked.connect(self.import_csv)
        file_buttons_layout.addWidget(self.import_button)

        self.export_button = QPushButton("CSVエクスポート")
        self.export_button.clicked.connect(self.export_csv)
        file_buttons_layout.addWidget(self.export_button)

        layout.addLayout(file_buttons_layout)

        # 保存・キャンセルボタン
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_csv)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # 初期ファイルを読み込み
        self.load_selected_csv()

    def get_csv_file_path(self, file_type):
        """CSVファイルのパスを取得"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, "..", "..", "..")

        if file_type == "ジャーナル略語 (jo_abb.csv)":
            return os.path.join(project_root, "data", "jo_abb.csv")
        elif file_type == "ジャーナル削除 (jo_del.csv)":
            return os.path.join(project_root, "data", "jo_del.csv")
        elif file_type == "月略語 (mo_abb.csv)":
            return os.path.join(project_root, "data", "mo_abb.csv")
        else:
            return ""

    def load_selected_csv(self):
        """選択されたCSVファイルを読み込み"""
        file_type = self.file_combo.currentText()
        self.current_csv_path = self.get_csv_file_path(file_type)

        try:
            with open(self.current_csv_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                self.csv_data = list(reader)

            self.populate_table()

        except Exception as e:
            QMessageBox.warning(
                self, "エラー", f"CSVファイルの読み込みに失敗しました: {str(e)}"
            )

    def populate_table(self):
        """テーブルにデータを表示"""
        if not self.csv_data:
            return

        # テーブルのサイズを設定
        rows = len(self.csv_data)
        cols = len(self.csv_data[0]) if rows > 0 else 2

        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        # ヘッダーを設定
        if rows > 0:
            self.table.setHorizontalHeaderLabels(self.csv_data[0])

        # データを設定
        for row_idx, row_data in enumerate(self.csv_data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                # ヘッダー行は編集不可
                if row_idx == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setBackground(Qt.lightGray)
                self.table.setItem(row_idx, col_idx, item)

        # 列幅を内容に合わせて調整
        self.table.resizeColumnsToContents()

    def add_row(self):
        """新しい行を追加"""
        if not self.csv_data:
            return

        cols = len(self.csv_data[0])
        new_row = [""] * cols

        self.csv_data.append(new_row)

        row_count = self.table.rowCount()
        self.table.setRowCount(row_count + 1)

        for col_idx in range(cols):
            item = QTableWidgetItem("")
            self.table.setItem(row_count, col_idx, item)

    def delete_row(self):
        """選択された行を削除"""
        current_row = self.table.currentRow()

        if current_row <= 0:  # ヘッダー行は削除不可
            QMessageBox.warning(self, "警告", "ヘッダー行は削除できません。")
            return

        if current_row < 0:
            QMessageBox.warning(self, "警告", "削除する行を選択してください。")
            return

        reply = QMessageBox.question(
            self,
            "確認",
            "選択された行を削除しますか？",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.table.removeRow(current_row)
            del self.csv_data[current_row]

    def save_csv(self):
        """CSVファイルを保存"""
        try:
            # テーブルからデータを取得
            rows = self.table.rowCount()
            cols = self.table.columnCount()

            updated_data = []
            for row in range(rows):
                row_data = []
                for col in range(cols):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                updated_data.append(row_data)

            # CSVファイルに保存
            with open(self.current_csv_path, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(updated_data)

            # アプリケーションの設定を再読み込み
            self.app_instance.reload_settings()

            QMessageBox.information(self, "成功", "CSVファイルが保存されました。")
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self, "エラー", f"CSVファイルの保存に失敗しました: {str(e)}"
            )

    def import_csv(self):
        """外部CSVファイルをインポート"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSVファイルをインポート", "", "CSV files (*.csv)"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    imported_data = list(reader)

                self.csv_data = imported_data
                self.populate_table()

                QMessageBox.information(
                    self, "成功", "CSVファイルがインポートされました。"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "エラー", f"CSVファイルのインポートに失敗しました: {str(e)}"
                )

    def export_csv(self):
        """CSVファイルをエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSVファイルをエクスポート", "", "CSV files (*.csv)"
        )

        if file_path:
            try:
                # テーブルからデータを取得
                rows = self.table.rowCount()
                cols = self.table.columnCount()

                export_data = []
                for row in range(rows):
                    row_data = []
                    for col in range(cols):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    export_data.append(row_data)

                # CSVファイルに保存
                with open(file_path, "w", encoding="utf-8", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(export_data)

                QMessageBox.information(
                    self, "成功", "CSVファイルがエクスポートされました。"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "エラー", f"CSVファイルのエクスポートに失敗しました: {str(e)}"
                )

    def filter_table(self):
        """テーブル内容を検索キーワードでフィルタ"""
        search_text = self.search_edit.text().lower()

        for row in range(self.table.rowCount()):
            # ヘッダー行は常に表示
            if row == 0:
                self.table.setRowHidden(row, False)
                continue

            # 各列のテキストを検索
            match_found = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break

            # マッチしない行は非表示にする
            self.table.setRowHidden(row, not match_found)
