import re

class Formatter:
    def __init__(self, et_al_th=4):
        self.et_al_th = et_al_th

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

    def pp_formatter(self, sp, ep, format="tex"):
        if not sp or not ep:
            return None
        elif format == "plain":
            return "pp. " + sp + "-" + ep
        elif format == "tex":
            return "pp. " + sp + "--" + ep
        else:
            return None

    def format_reference(self, data, format="tex"):
        authors = self.au_formatter(data.get("AU", ""), format=format)
        title = self.ti_formatter(data.get("TI", ""), format=format)
        volume = data.get("VL", "")
        number = data.get("IS", "")
        pages = self.pp_formatter(data.get("SP", ""), data.get("EP", ""), format=format)
        year = data.get("Y1", "")

        parts = [part for part in [authors, title, volume, number, year, pages] if part]
        return ", ".join(parts) + "."