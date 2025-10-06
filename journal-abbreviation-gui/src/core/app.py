import csv
import re
import yaml
import os
from utils.file_loader import load_csv


class App:
    def __init__(self):
        # Get the directory of the current script and navigate to project root
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.join(self.current_dir, "..", "..")
        self.settings_path = os.path.join(self.project_root, "data", "settings.yml")

        self.load_settings()

    def load_settings(self):
        """設定を読み込む"""
        with open(self.settings_path, encoding="utf-8") as yml:
            settings = yaml.safe_load(yml)

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

        # Build absolute paths for CSV files
        jo_abb_path = os.path.join(
            self.project_root, settings.get("jo_abb_path", "data/jo_abb.csv")
        )
        jo_del_path = os.path.join(
            self.project_root, settings.get("jo_del_path", "data/jo_del.csv")
        )
        mo_abb_path = os.path.join(
            self.project_root, settings.get("mo_abb_path", "data/mo_abb.csv")
        )

        self.jo_abb_list = load_csv(jo_abb_path)
        self.jo_del_list = load_csv(jo_del_path)
        self.mo_abb_list = load_csv(mo_abb_path)

    def reload_settings(self):
        """設定を再読み込み"""
        self.load_settings()

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
        text = text.split()

        for i, t in enumerate(text):
            if t in del_list[0]:
                text[i] = ""

        text = " ".join([w for w in text if w != ""])
        return text

    def abbreviate(self, text, abb_list):
        text = text.split()

        for i, t in enumerate(text):
            if t in abb_list[0]:
                text[i] = abb_list[1][abb_list[0].index(t)] + "."

        text = " ".join(text)
        return text

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
        print(self.with_in, ty, jornal.startswith("in"))
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
