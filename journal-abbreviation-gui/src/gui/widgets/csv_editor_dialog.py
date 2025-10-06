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
    QGroupBox,
)
from PyQt5.QtCore import Qt, QTimer
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
        self.is_processing = False  # 処理中フラグ
        self.message_box_active = False  # メッセージボックス表示中フラグ

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

        # 単語・略語追加フォーム
        self.add_form_group = QGroupBox()
        self.add_form_main_layout = QVBoxLayout()

        # 説明ラベル
        self.description_label = QLabel()
        self.update_description_label()
        self.add_form_main_layout.addWidget(self.description_label)

        # フォームレイアウト（動的に変更される）
        self.add_form_layout = QHBoxLayout()

        # 共通要素
        self.original_word_edit = QLineEdit()
        self.abbreviation_edit = QLineEdit()
        self.original_word_label = QLabel("元の単語:")
        self.abbreviation_label = QLabel("略語:")
        self.add_pair_button = QPushButton("追加")
        self.add_pair_button.clicked.connect(self.add_word_pair)

        # Enterキーの接続（イベント制御付き）
        self.original_word_edit.returnPressed.connect(self.handle_enter_key)
        self.abbreviation_edit.returnPressed.connect(self.handle_enter_key)

        # 初期フォームを設定
        self.setup_add_form()

        self.add_form_main_layout.addLayout(self.add_form_layout)
        self.add_form_group.setLayout(self.add_form_main_layout)
        layout.addWidget(self.add_form_group)

        # 編集ボタン部分
        edit_buttons_layout = QHBoxLayout()

        self.delete_selected_button = QPushButton("選択した単語ペアを削除")
        self.delete_selected_button.clicked.connect(self.delete_selected_pair)
        edit_buttons_layout.addWidget(self.delete_selected_button)

        self.clear_all_button = QPushButton("全てクリア")
        self.clear_all_button.clicked.connect(self.clear_all_data)
        edit_buttons_layout.addWidget(self.clear_all_button)

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
            self.update_description_label()
            self.setup_add_form()  # フォームを更新

        except Exception as e:
            QMessageBox.warning(
                self, "エラー", f"CSVファイルの読み込みに失敗しました: {str(e)}"
            )

    def setup_add_form(self):
        """選択されたファイルタイプに応じて追加フォームを設定"""
        # 既存のウィジェットを削除
        for i in reversed(range(self.add_form_layout.count())):
            self.add_form_layout.itemAt(i).widget().setParent(None)

        file_type = self.file_combo.currentText()

        if file_type == "ジャーナル削除 (jo_del.csv)":
            # 削除単語のみの1列形式
            self.add_form_group.setTitle("削除する単語を追加")
            self.original_word_edit.setPlaceholderText("削除する単語を入力...")
            self.add_form_layout.addWidget(QLabel("削除する単語:"))
            self.add_form_layout.addWidget(self.original_word_edit)
            self.add_pair_button.setText("追加")
            self.add_form_layout.addWidget(self.add_pair_button)

            # 略語フィールドを非表示
            self.abbreviation_edit.hide()
        else:
            # 通常の2列形式（元の単語と略語）
            self.add_form_group.setTitle("新しい単語・略語ペアを追加")
            self.original_word_edit.setPlaceholderText("元の単語を入力...")
            self.add_form_layout.addWidget(self.original_word_label)
            self.add_form_layout.addWidget(self.original_word_edit)

            self.abbreviation_edit.setPlaceholderText("略語を入力...")
            self.abbreviation_edit.show()
            self.add_form_layout.addWidget(self.abbreviation_label)
            self.add_form_layout.addWidget(self.abbreviation_edit)

            self.add_pair_button.setText("追加")
            self.add_form_layout.addWidget(self.add_pair_button)

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

    def handle_enter_key(self):
        """Enterキーイベントの統一ハンドラー"""
        # 既に処理中の場合は無視
        if self.is_processing:
            return

        # 処理フラグをセット
        self.is_processing = True

        # 送信者（どの入力フィールドからのイベントか）を特定
        sender = self.sender()

        # フォーカスを一時的に別の場所に移動してEnterキーの連鎖を防ぐ
        self.add_pair_button.setFocus()

        # 少し遅延してから実際の処理を行う
        QTimer.singleShot(50, self.execute_add_word)

    def execute_add_word(self):
        """実際の単語追加処理を実行"""
        try:
            self.add_word_pair_safe()
        finally:
            # 処理完了後にフラグをリセット
            QTimer.singleShot(100, self.reset_processing_flag)

    def reset_processing_flag(self):
        """処理フラグをリセット"""
        self.is_processing = False
        # フォーカスを適切な入力フィールドに戻す
        file_type = self.file_combo.currentText()
        if file_type == "ジャーナル削除 (jo_del.csv)":
            self.original_word_edit.setFocus()
        else:
            self.original_word_edit.setFocus()

    def add_word_pair_safe(self):
        """新しい単語・略語ペア（または削除単語）を追加（安全版）"""
        self.message_box_active = True

        try:
            original_word = self.original_word_edit.text().strip()
            file_type = self.file_combo.currentText()

            if not original_word:
                if file_type == "ジャーナル削除 (jo_del.csv)":
                    QMessageBox.warning(
                        self, "警告", "削除する単語を入力してください。"
                    )
                else:
                    QMessageBox.warning(self, "警告", "元の単語を入力してください。")
                return

            if file_type == "ジャーナル削除 (jo_del.csv)":
                # 削除単語ファイルの場合（1列形式）
                # 既存の単語がないかチェック
                for row_idx in range(1, len(self.csv_data)):  # ヘッダー行をスキップ
                    if (
                        len(self.csv_data[row_idx]) > 0
                        and self.csv_data[row_idx][0] == original_word
                    ):
                        QMessageBox.information(
                            self,
                            "情報",
                            f"「{original_word}」は既に削除リストに含まれています。",
                        )
                        return

                # 新しい行を追加（1列のみ）
                new_row = [original_word]
                self.csv_data.append(new_row)

                # テーブルを更新
                self.populate_table()

                # 入力欄をクリア
                self.original_word_edit.clear()

                # 成功メッセージを表示
                QMessageBox.information(self, "成功", "削除する単語が追加されました。")
            else:
                # 通常の2列形式（元の単語と略語）
                abbreviation = self.abbreviation_edit.text().strip()

                if not abbreviation:
                    QMessageBox.warning(self, "警告", "略語を入力してください。")
                    return

                # 既存の単語がないかチェック
                for row_idx in range(1, len(self.csv_data)):  # ヘッダー行をスキップ
                    if (
                        len(self.csv_data[row_idx]) > 0
                        and self.csv_data[row_idx][0] == original_word
                    ):
                        reply = QMessageBox.question(
                            self,
                            "確認",
                            f"「{original_word}」は既に存在します。上書きしますか？",
                            QMessageBox.Yes | QMessageBox.No,
                        )
                        if reply == QMessageBox.Yes:
                            # 既存の行を更新
                            if len(self.csv_data[row_idx]) > 1:
                                self.csv_data[row_idx][1] = abbreviation
                            else:
                                self.csv_data[row_idx].append(abbreviation)
                            self.populate_table()
                            self.original_word_edit.clear()
                            self.abbreviation_edit.clear()
                            QMessageBox.information(
                                self, "成功", "単語ペアが更新されました。"
                            )
                        return

                # 新しい行を追加
                new_row = [original_word, abbreviation]
                self.csv_data.append(new_row)

                # テーブルを更新
                self.populate_table()

                # 入力欄をクリア
                self.original_word_edit.clear()
                self.abbreviation_edit.clear()

                # 成功メッセージを表示
                QMessageBox.information(
                    self, "成功", "新しい単語ペアが追加されました。"
                )

        finally:
            self.message_box_active = False

    def add_word_pair(self):
        """通常の単語追加メソッド（ボタンクリック用）"""
        if self.is_processing or self.message_box_active:
            return
        self.add_word_pair_safe()

    def delete_selected_pair(self):
        """選択された単語ペアを削除"""
        current_row = self.table.currentRow()

        if current_row <= 0:  # ヘッダー行は削除不可
            QMessageBox.warning(
                self,
                "警告",
                "削除する単語ペアを選択してください。\n（ヘッダー行は選択できません）",
            )
            return

        if current_row < 0:
            QMessageBox.warning(self, "警告", "削除する単語ペアを選択してください。")
            return

        # 削除する単語を表示
        original_word = (
            self.table.item(current_row, 0).text()
            if self.table.item(current_row, 0)
            else ""
        )

        file_type = self.file_combo.currentText()

        if file_type == "ジャーナル削除 (jo_del.csv)":
            # 削除単語ファイルの場合
            reply = QMessageBox.question(
                self,
                "確認",
                f"以下の削除単語を削除しますか？\n\n削除単語: {original_word}",
                QMessageBox.Yes | QMessageBox.No,
            )
            success_message = "削除単語が削除されました。"
        else:
            # 通常の2列形式の場合
            abbreviation = (
                self.table.item(current_row, 1).text()
                if self.table.item(current_row, 1)
                else ""
            )
            reply = QMessageBox.question(
                self,
                "確認",
                f"以下の単語ペアを削除しますか？\n\n元の単語: {original_word}\n略語: {abbreviation}",
                QMessageBox.Yes | QMessageBox.No,
            )
            success_message = "単語ペアが削除されました。"

        if reply == QMessageBox.Yes:
            self.table.removeRow(current_row)
            del self.csv_data[current_row]
            QMessageBox.information(self, "成功", success_message)

    def clear_all_data(self):
        """全データをクリア（ヘッダー行以外）"""
        if len(self.csv_data) <= 1:
            QMessageBox.information(self, "情報", "削除するデータがありません。")
            return

        reply = QMessageBox.question(
            self,
            "確認",
            "全ての単語ペアを削除しますか？\n（この操作は取り消せません）",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # ヘッダー行のみ残す
            self.csv_data = self.csv_data[:1] if self.csv_data else []
            self.populate_table()
            QMessageBox.information(self, "成功", "全ての単語ペアが削除されました。")

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

    def update_description_label(self):
        """現在選択されているファイルに応じて説明を更新"""
        file_type = self.file_combo.currentText()

        descriptions = {
            "ジャーナル略語 (jo_abb.csv)": "ジャーナル名とその略語を管理します。\n例: 「Journal of Example」→「JoE」",
            "ジャーナル削除 (jo_del.csv)": "ジャーナル名から削除する単語を管理します（1列形式）。\n例: 「the」「international」「of」などの不要な単語",
            "月略語 (mo_abb.csv)": "月名とその略語を管理します。\n例: 「January」→「Jan」",
        }

        description = descriptions.get(
            file_type, "CSVファイルの単語・略語ペアを編集できます。"
        )
        self.description_label.setText(description)

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
