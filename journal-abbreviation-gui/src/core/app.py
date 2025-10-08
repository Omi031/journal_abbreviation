import csv
import re
import yaml
import os
import sys
from utils.file_loader import load_csv


def get_resource_path(relative_path):
    """PyInstallerパッケージ化対応のリソースパス取得"""
    try:
        # PyInstaller実行時の一時ディレクトリ
        base_path = sys._MEIPASS
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            return full_path
    except AttributeError:
        pass

    # 通常のPython実行時または代替パス
    # 現在のスクリプトファイルからの相対パス
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(current_dir, "..", "..")
    full_path = os.path.join(base_path, relative_path)
    if os.path.exists(full_path):
        return full_path

    # 現在の作業ディレクトリからの相対パス
    full_path = os.path.join(os.getcwd(), relative_path)
    if os.path.exists(full_path):
        return full_path

    # 実行ファイルのディレクトリからの相対パス
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        full_path = os.path.join(exe_dir, relative_path)
        if os.path.exists(full_path):
            return full_path

    # デフォルトとして最初のパスを返す
    return os.path.join(base_path, relative_path)


class App:
    def __init__(self):
        self.settings_path = get_resource_path(os.path.join("data", "settings.yml"))

        self.load_settings()

    def find_journal_abbreviation(self, journal_name: str) -> str:
        """ジャーナル正式名から略語を検索して返す。

        検索仕様:
        - 大文字小文字は無視
        - 余分なスペースをトリム
        - 完全一致を優先。見つからない場合は前方一致候補を返す（最初の1件）。
        - 見つからない場合は空文字列。
        """
        if not journal_name:
            return ""
        name_norm = journal_name.strip().lower()
        if not name_norm:
            return ""

        # jo_abb_list は [元名称リスト, 略語リスト] 形式を想定
        if not self.jo_abb_list or len(self.jo_abb_list) < 2:
            return ""

        originals = self.jo_abb_list[0]
        abbs = self.jo_abb_list[1]

        def format_abbr(a: str) -> str:
            if not a:
                return a
            if a.endswith('.'):
                return a
            # 完全大文字（A-Zと数字のみ）の場合はピリオド付けない（IEEE, AI など）
            if all(c.isupper() or c.isdigit() for c in a if c.isalnum()):
                return a
            # それ以外（短縮形）にはピリオド付与
            return a + '.'
        # 完全一致検索
        for i, orig in enumerate(originals):
            if orig and orig.strip().lower() == name_norm:
                return format_abbr(abbs[i] if i < len(abbs) else "")

        # 前方一致候補
        for i, orig in enumerate(originals):
            if orig and orig.strip().lower().startswith(name_norm):
                return format_abbr(abbs[i] if i < len(abbs) else "")
        return ""

    def build_journal_abbreviation(self, journal_title: str) -> str:
        """ジャーナルタイトル全体を単語ごとに略語化して返す。

        ルール:
        - CSV の original -> abbreviation を単語単位で適用
        - 大文字小文字は無視し、出力は CSV の abbreviation をそのまま使用
        - 括弧・カンマ・ハイフン等の記号は維持
        - 既に略語っぽい（全て大文字 か 3文字以下）単語はそのまま
        - 数字のみのトークンはそのまま
        - アポストロフィやハイフンで分割された部分も個別判定
        """
        if not journal_title:
            return ""
        if not self.jo_abb_list or len(self.jo_abb_list) < 2:
            return journal_title

        # まず削除リスト適用（クイック検索経由でも 'and' などを除去するため）
        try:
            journal_title = self.delete(journal_title, self.jo_del_list)
        except Exception:
            pass

        originals = self.jo_abb_list[0]
        abbs = self.jo_abb_list[1]
        # マッピング辞書（小文字キー）
        mapping_raw = {
            (orig.strip().lower() if orig else ""): (abbs[i] if i < len(abbs) else "")
            for i, orig in enumerate(originals)
            if orig
        }

        def format_abbr(a: str) -> str:
            if not a:
                return a
            if a.endswith('.'):
                return a
            if all(c.isupper() or c.isdigit() for c in a if c.isalnum()):
                return a
            return a + '.'

        # フォーマット済みマッピング
        mapping = {k: format_abbr(v) for k, v in mapping_raw.items()}

        import re

        # トークン分割（単語 or 記号）
        tokens = re.findall(r"[A-Za-z0-9\-']+|[^A-Za-z0-9\s]", journal_title)
        result_tokens = []
        for tok in tokens:
            # 英数字主体のトークンのみ処理
            if re.fullmatch(r"[A-Za-z0-9\-']+", tok):
                # ハイフンやアポストロフィでさらに分割し、再構築
                sub_parts = re.split(r"([-'])", tok)  # 区切り記号も保持
                rebuilt = []
                for part in sub_parts:
                    if part in ["-", "'"]:
                        rebuilt.append(part)
                        continue
                    low = part.lower()
                    if not part or low.isdigit():
                        rebuilt.append(part)
                        continue
                    # 既に略語っぽい
                    if part.isupper() or len(part) <= 3:
                        rebuilt.append(part)
                        continue
                    if low in mapping and mapping[low]:
                        rebuilt.append(mapping[low])
                    else:
                        rebuilt.append(part)
                result_tokens.append("".join(rebuilt))
            else:
                # 記号などはそのまま
                result_tokens.append(tok)

        # スペース再付与: 連続する英数字/記号境界を自然にするため、元文字列の空白を利用せず簡易再構築
        # 記号の前後で不要なスペースを避けるため調整
        out = []
        for i, t in enumerate(result_tokens):
            out.append(t)
            if i < len(result_tokens) - 1:
                nxt = result_tokens[i + 1]
                # コロンで終わるトークンの後はスペースを挿入しない（"2015:18th" など）
                if t.endswith(":"):
                    continue
                # 次が記号ならスペース不要 / 自分が記号ならスペース不要
                if re.fullmatch(r"[^A-Za-z0-9]", nxt):
                    continue
                if re.fullmatch(r"[^A-Za-z0-9]", t):
                    continue
                out.append(" ")
        return "".join(out).strip()

    def load_settings(self):
        """設定を読み込む"""
        try:
            with open(self.settings_path, encoding="utf-8") as yml:
                settings = yaml.safe_load(yml)
        except FileNotFoundError as e:
            # デフォルト設定で続行
            settings = {
                "et_al_th": 4,
                "cite_style": "ris",
                "format": "tex",
                "conf_with_in": False,
                "conf_with_proc": True,
                "conf_with_year": False,
                "ui_font_family": "Segoe UI",
                "ui_font_size": 9,
                "input_font_family": "Consolas",
                "input_font_size": 9,
                "output_font_family": "Consolas",
                "output_font_size": 9,
                "auto_copy_to_clipboard": True,
                "jo_abb_path": "data/jo_abb.csv",
                "jo_del_path": "data/jo_del.csv",
                "mo_abb_path": "data/mo_abb.csv",
            }

        self.et_al_th = settings.get("et_al_th", 4)
        self.cite_style = settings.get("cite_style", "ris")
        self.format_type = settings.get("format", "tex")
        self.with_in = settings.get("conf_with_in", False)
        self.with_proc = settings.get("conf_with_proc", True)
        self.with_year = settings.get("conf_with_year", False)

        # フォント設定
        self.ui_font_family = settings.get("ui_font_family", "Segoe UI")
        self.ui_font_size = settings.get("ui_font_size", 12)
        self.input_font_family = settings.get("input_font_family", "Consolas")
        self.input_font_size = settings.get("input_font_size", 12)
        self.output_font_family = settings.get("output_font_family", "Times New Roman")
        self.output_font_size = settings.get("output_font_size", 14)

        # クリップボード設定
        self.auto_copy_to_clipboard = settings.get("auto_copy_to_clipboard", True)

        # タイトルケース変換設定
        self.title_case_conversion = settings.get("title_case_conversion", True)
        self.auto_detect_proper_nouns = settings.get("auto_detect_proper_nouns", True)

        # Build absolute paths for CSV files using resource path function
        jo_abb_path = get_resource_path(settings.get("jo_abb_path", "data/jo_abb.csv"))
        jo_del_path = get_resource_path(settings.get("jo_del_path", "data/jo_del.csv"))
        mo_abb_path = get_resource_path(settings.get("mo_abb_path", "data/mo_abb.csv"))
        proper_nouns_path = get_resource_path(
            settings.get("proper_nouns_path", "data/proper_nouns.csv")
        )

        try:
            self.jo_abb_list = load_csv(jo_abb_path)
        except FileNotFoundError:
            self.jo_abb_list = [[], []]  # 空のリストで初期化

        try:
            self.jo_del_list = load_csv(jo_del_path)
        except FileNotFoundError:
            self.jo_del_list = [[], []]  # 空のリストで初期化

        try:
            self.mo_abb_list = load_csv(mo_abb_path)
        except FileNotFoundError:
            self.mo_abb_list = [[], []]  # 空のリストで初期化

        try:
            proper_nouns_data = load_csv(proper_nouns_path)
            # 固有名詞リストを作成（最初の列のみを使用）
            self.proper_nouns = (
                set(proper_nouns_data[0])
                if proper_nouns_data and len(proper_nouns_data) > 0
                else set()
            )
        except FileNotFoundError:
            self.proper_nouns = {
                "6G",
                "OFDM",
                "Raician",
                "IoT",
                "AI",
                "ML",
                "DL",
                "CNN",
                "LSTM",
                "BERT",
                "GPS",
                "WiFi",
                "Bluetooth",
                "LTE",
                "5G",
                "4G",
                "3G",
                "MIMO",
                "QoS",
                "TCP",
                "UDP",
                "HTTP",
                "HTTPS",
                "SSL",
                "TLS",
                "API",
                "REST",
                "JSON",
            }  # デフォルトの固有名詞リスト

    def reload_settings(self):
        """設定を再読み込み"""
        self.load_settings()

    def is_likely_proper_noun_auto(self, word):
        """
        単語が固有名詞である可能性を自動判定
        """
        import re

        # 一般的な英単語（小文字）のセット
        common_words = {
            "the",
            "and",
            "or",
            "with",
            "for",
            "in",
            "on",
            "at",
            "to",
            "from",
            "by",
            "of",
            "system",
            "method",
            "approach",
            "technique",
            "analysis",
            "study",
            "research",
            "performance",
            "evaluation",
            "implementation",
            "algorithm",
            "model",
            "based",
            "using",
            "proposed",
            "novel",
            "efficient",
            "enhanced",
            "improved",
            "optimal",
            "design",
            "development",
            "application",
            "network",
            "wireless",
            "communication",
            "signal",
            "processing",
            "detection",
            "estimation",
            "classification",
            "learning",
            "deep",
            "machine",
            "artificial",
            "neural",
            "data",
            "information",
            "control",
        }

        # パターン1: 全て大文字の略語（2-6文字程度）
        if word.isupper() and 2 <= len(word) <= 6:
            return True

        # パターン2: 数字+文字の組み合わせ（6G, 5G, WiFi6等）
        if re.match(r"^\d+[A-Za-z]+$", word) or re.match(r"^[A-Za-z]+\d+$", word):
            return True

        # パターン3: CamelCaseパターン（IoT, WiFi等）
        if re.match(r"^[A-Z][a-z]*[A-Z]", word):
            return True

        # パターン4: 一般単語でない場合の推定
        if word.lower() not in common_words:
            # 大文字が多い場合
            upper_count = sum(1 for c in word if c.isupper())
            if len(word) > 2 and upper_count / len(word) > 0.5:
                return True

        return False

    def convert_to_title_case(self, title):
        """
        タイトルを適切な大文字小文字に変換
        - 最初の文字は大文字
        - 固有名詞はそのまま保持（辞書 + 自動判定）
        - その他は小文字
        """
        if not self.title_case_conversion or not title:
            return title

        import re

        def replace_word(match):
            word = match.group()
            word_index = getattr(replace_word, "counter", 0)
            replace_word.counter = word_index + 1

            # 辞書による固有名詞チェック（大文字小文字を区別しない）
            is_dict_proper_noun = any(
                word.lower() == noun.lower() for noun in self.proper_nouns
            )

            # 自動判定による固有名詞チェック（設定で有効な場合のみ）
            is_auto_proper_noun = (
                self.auto_detect_proper_nouns and self.is_likely_proper_noun_auto(word)
            )

            if is_dict_proper_noun:
                # 辞書にある固有名詞の場合、辞書の表記を使用
                original_noun = next(
                    noun for noun in self.proper_nouns if word.lower() == noun.lower()
                )
                return original_noun
            elif is_auto_proper_noun:
                # 自動判定で固有名詞の場合、元の表記を保持
                return word
            elif word_index == 0:
                # 最初の単語は最初の文字のみ大文字
                return word.capitalize()
            else:
                # その他の単語は小文字
                return word.lower()

        # カウンターを初期化
        replace_word.counter = 0

        # 単語境界を使って単語のみを置換
        result = re.sub(r"\b\w+\b", replace_word, title)

        return result

    def make_cite_dict(self, ori):
        data = {}
        for line in ori.splitlines():
            if " - " in line:
                key, value = line.split(" - ", 1)
                key, value = key.strip(), value.strip()
                if key in data:
                    if isinstance(data[key], list):
                        data[key].append(value)
                    else:
                        data[key] = [data[key], value]
                else:
                    data[key] = value
            elif line.strip() == "":
                pass
            else:
                print(f"Warning: Input format is not in expected 'key - value' format.")
                return None
        return data

    def delete(self, text, del_list):
        """削除単語リスト(del_list)に含まれる語をジャーナル名文字列から除去。

        改良点:
        - 大文字小文字を無視
        - 単語の前後に付いた句読点 (.,:;!?()[]{}) / カンマ / & などを無視して判定
        - '&' 単体もリストにあれば削除
        - 削除後の余分なスペースを整形
        注意: 'of,' のような語を除去した場合、その語に付随していた句読点も同時に消える（シンプル実装）
        """
        if not text:
            return text
        # del_list 期待形式: [ [word1, word2, ...] ]
        try:
            raw_words = del_list[0] if del_list and len(del_list) > 0 else []
        except Exception:
            raw_words = []
        del_set = {w.strip().lower() for w in raw_words if w and w.strip()}
        if not del_set:
            return text

        import re

        tokens = text.split()
        kept = []
        for tok in tokens:
            # 前後の句読点を除去したクリーン版（内部のハイフンやアポストロフィは保持）
            cleaned = re.sub(r"^[\s\.,;:!\?\(\)\[\]\{\}\"']+|[\s\.,;:!\?\(\)\[\]\{\}\"']+$", "", tok)
            if cleaned.lower() in del_set:
                continue  # 削除
            kept.append(tok)

        # 連続スペースを1つに
        return re.sub(r"\s+", " ", " ".join(kept)).strip()

    def abbreviate(self, text, abb_list):
        """単語ごとの略語化。

        改良点:
        - 大文字小文字非依存
        - 末尾句読点等 (.,:;!?)]}) を保持
        - 既存の略語が既にピリオド付きなら重ねて付けない
        - 全大文字(AI, LTE など)はピリオドを付与しない
        """
        if not text:
            return text
        try:
            originals = abb_list[0] if abb_list and len(abb_list) > 0 else []
            abbrevs = abb_list[1] if abb_list and len(abb_list) > 1 else []
        except Exception:
            return text

        mapping = {}
        for i, orig in enumerate(originals):
            if not orig:
                continue
            ab = abbrevs[i] if i < len(abbrevs) else ""
            if ab:
                if not ab.endswith('.') and not all(c.isupper() or c.isdigit() for c in ab if c.isalnum()):
                    ab = ab + '.'
                mapping[orig.strip().lower()] = ab

        import re
        tokens = text.split()
        out = []
        for tok in tokens:
            m = re.match(r"^(.*?)([\.,;:!\?\]\)\}\"]+)$", tok)
            core = tok
            tail = ""
            if m:
                core = m.group(1)
                tail = m.group(2)
            repl = mapping.get(core.lower())
            if repl:
                out.append(repl + tail)
            else:
                out.append(tok)
        return " ".join(out)

    def au_formatter(self, au_list, format="tex"):
        if isinstance(au_list, str):
            author = au_list
            return author

        elif not au_list:
            return ""

        elif len(au_list) >= self.et_al_th:
            if format == "plain":
                return au_list[0] + " et al."
            elif format == "tex":
                return au_list[0] + " \\textit{et al}."
            else:
                return None

        elif len(au_list) == 1:
            return au_list[0]
        elif len(au_list) == 2:
            return " and ".join(au_list)
        else:
            return ", ".join(au_list[:-1]) + ", and " + au_list[-1]

    def ti_formatter(self, title, format="tex"):
        # タイトルケース変換を適用
        title = self.convert_to_title_case(title)

        if format == "plain":
            return '"' + title + ',"'
        elif format == "tex":
            return "``" + title + ",''"
        else:
            return None

    def jo_formatter(self, jornal, format="tex", ty="JOUR"):
        jornal = self.delete(jornal, self.jo_del_list)
        jornal = self.abbreviate(jornal, self.jo_abb_list)

        if ty == "CONF":
            if not self.with_year:
                jornal = re.sub(r"^\s*\d{4}\s*", "", jornal)
            if self.with_proc and not jornal.startswith("Proc."):
                jornal = "Proc. " + jornal

        if format == "tex":
            jornal = "\\textit{" + jornal + "}"
        if ty == "CONF" and self.with_in and not jornal.startswith("in"):
            jornal = "in " + jornal

        return jornal

    def vo_formatter(self, volume):
        if not volume:
            return None
        else:
            return "vol. " + volume

    def no_formatter(self, number):
        if not number:
            return None
        else:
            return "no. " + number

    def pp_formatter(self, sp, ep, format="tex"):
        if not sp or not ep:
            return None
        elif format == "plain":
            return "pp. " + sp + "-" + ep
        elif format == "tex":
            return "pp. " + sp + "--" + ep
        else:
            return None

    def y1_formatter(self, y1):
        y1 = re.sub(r"^\s*\d{1,2}(?:\s*-\s*\d{1,2})?\s*", "", y1)
        return self.abbreviate(y1, self.mo_abb_list)

    def do_formatter(self, doi):
        if not doi:
            return None
        else:
            return "doi: " + doi

    def format(self, data, format="tex", year_input_callback=None):
        if data["TY"] == "JOUR":
            authors = self.au_formatter(data.get("AU", ""), format=format)
            title = self.ti_formatter(data.get("TI", ""), format=format)
            journal = self.jo_formatter(data.get("JO", ""), format=format, ty="JOUR")
            volume = self.vo_formatter(data.get("VL", ""))
            number = self.no_formatter(data.get("IS", ""))
            pages = self.pp_formatter(
                data.get("SP", ""), data.get("EP", ""), format=format
            )
            year = self.y1_formatter(data.get("Y1", ""))
            # Early access article
            if not volume and not number:
                if not year:
                    if year_input_callback:
                        user_year = year_input_callback()
                        if user_year:
                            year = self.y1_formatter(user_year)
                        else:
                            year = "Unknown Year"
                    else:
                        year = "Unknown Year"
                doi = self.do_formatter(data.get("DO", ""))
                parts = [
                    part
                    for part in [
                        authors,
                        title + " " + journal,
                        "early access",
                        year,
                        doi,
                    ]
                    if part
                ]
            else:
                parts = [
                    part
                    for part in [
                        authors,
                        title + " " + journal,
                        volume,
                        number,
                        pages,
                        year,
                    ]
                    if part
                ]
        elif data["TY"] == "CONF":
            authors = self.au_formatter(data.get("AU", ""))
            title = self.ti_formatter(data.get("TI", ""))
            journal = self.jo_formatter(data.get("JO", ""), ty="CONF")
            pages = self.pp_formatter(data.get("SP", ""), data.get("EP", ""))
            year = self.y1_formatter(data.get("Y1", ""))

            parts = [
                part for part in [authors, title + " " + journal, year, pages] if part
            ]
        else:
            print(f"Warning: Reference type '{data['TY']}' is not supported.")
            return None

        return ", ".join(parts) + "."
