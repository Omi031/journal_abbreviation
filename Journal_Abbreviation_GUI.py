import tkinter as tk
from tkinter import scrolledtext, messagebox
import csv
import re
import sys
import pyperclip
import os

# --- Core Logic from Journal_Abbreviations_ver2.py ---
# 定数
DEL_FILENAME = "del.csv"
REP_FILENAME = "replace.csv"

# グローバル変数としてルールを保持
era_words = []
rep_dict = {}

def load_rules():
    """CSVファイルからルールを読み込む"""
    global era_words, rep_dict
    
    if not os.path.exists(DEL_FILENAME):
        return False
    with open(DEL_FILENAME, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        era_words = [row[0] for row in reader if row]

    if not os.path.exists(REP_FILENAME):
        return False
    with open(REP_FILENAME, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        rep_dict = {row[0]: row[1] for row in reader if len(row) >= 2}
        
    return True

def abbreviation(words, format_style):
    """ジャーナル情報を短縮形に変換する"""
    words_list = words.split()
    for i, word in enumerate(words_list):
        comma = "," if "," in word else ""
        cleaned_word = word.replace(",", "")

        if cleaned_word in era_words:
            words_list[i] = ""  # オリジナルのロジックと同様に空文字列に置換
        elif cleaned_word in rep_dict:
            words_list[i] = rep_dict[cleaned_word] + "." + comma

    result = " ".join([w for w in words_list if w]) # 空白の要素をフィルタリング

    if format_style == "tex":
        result = re.sub(r"(pp\. )(\d+)-(\d+)", r"\1\2--\3", result)

    result = re.sub(r",$", ".", result)
    if not result.endswith("."):
        result += "."
        
    if format_style == "tex":
        result = "\\textit{" + result
        result = result.replace(",", "},", 1)
        
    return result

def search(pattern, text):
    """正規表現でテキストを検索し、指定したグループを返す"""
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None

def format_reference(original_text, format_style):
    """文献情報全体を整形する"""
    # doi以降を削除（大文字小文字を無視）
    text = re.sub(r"doi:.*", "", original_text, flags=re.IGNORECASE)
    text = re.sub(r"\n.*", "", text).strip() # 末尾の空白も削除
    
    name = search(r"(.*?), \"", text)
    title = search(r"\"(.*?)\"", text)
    journal_info = search(r",\" (.*?)$", text)

    if not all([name, title, journal_info]):
        return "入力形式が正しくない可能性があります。\n'著者名, \"タイトル\" ジャーナル情報' の形式か確認してください。"

    name_rep = name.replace(" and", ", and")
    if format_style == "tex":
        name_rep = name_rep.replace("et al", "\\textit{et al}")

    journal_info_abb = abbreviation(journal_info, format_style)

    # doi削除済みの 'text' をベースに最終結果を構築
    final_text = text.replace(name, name_rep)
    if format_style == "tex":
        final_text = final_text.replace(f'\"{title}\"', f"``{title}''")
    
    final_text = final_text.replace(journal_info, journal_info_abb)
    
    pyperclip.copy(final_text)
    return final_text

# --- GUI Application ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("文献情報フォーマッター")
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(options_frame, text="出力形式:").pack(side=tk.LEFT, padx=(0, 10))
        self.format_var = tk.StringVar(value="tex")
        tk.Radiobutton(options_frame, text="TeX", variable=self.format_var, value="tex").pack(side=tk.LEFT)
        tk.Radiobutton(options_frame, text="Plain", variable=self.format_var, value="plain").pack(side=tk.LEFT)

        input_frame = tk.LabelFrame(main_frame, text="元の文献情報を入力", padx=5, pady=5)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        self.convert_button = tk.Button(main_frame, text="変換実行", command=self.process_text)
        self.convert_button.pack(fill=tk.X, pady=5)

        output_frame = tk.LabelFrame(main_frame, text="変換後の文献情報 (クリップボードにコピーされます)", padx=5, pady=5)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.configure(state='disabled')

    def process_text(self):
        input_val = self.input_text.get("1.0", tk.END).strip()
        if not input_val:
            messagebox.showwarning("警告", "入力が空です。")
            return
            
        format_style = self.format_var.get()
        result = format_reference(input_val, format_style)
        
        self.output_text.configure(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", result)
        self.output_text.configure(state='disabled')
        messagebox.showinfo("完了", "変換が完了し、クリップボードにコピーしました。")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Start with window hidden
    
    if load_rules():
        root.deiconify() # Show window only if rules loaded
        app = App(root)
        root.mainloop()
    else:
        messagebox.showerror("起動エラー", f"ルールファイル ({DEL_FILENAME}, {REP_FILENAME}) の読み込みに失敗しました。\nファイルがアプリケーションと同じディレクトリに存在するか確認してください。")
        root.destroy()
