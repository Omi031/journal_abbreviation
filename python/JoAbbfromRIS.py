import csv
import re
import sys

import pyperclip


FORMAT = "tex"
# FORMAT = "plain"
DEL_PATH = r"del.csv"
REP_PATH = r"replace.csv"

with open(DEL_PATH, encoding="utf-8") as f:
    reader = csv.reader(f)
    era = [row for row in reader][1:]
    era = list(map(list, zip(*era)))

with open(REP_PATH, encoding="utf-8") as f:
    reader = csv.reader(f)
    rep = [row for row in reader][1:]
    rep = list(map(list, zip(*rep)))


def abbrebiation(words):
    words = words.split()
    for i, word in enumerate(words):
        if "," in word:
            word = word.replace(",", "")
            comma = ","
        else:
            comma = ""
        if word in era[0]:
            words[i] = ""
        elif word in rep[0]:
            words[i] = rep[1][rep[0].index(word)] + "." + comma

    words = " ".join([w for w in words if w != ""])
    if FORMAT == "tex":
        words = re.sub(r"(pp\. )(\d+)-(\d+)", r"\1\2--\3", words)
    # words = re.sub(r",\s*,", ",", words)
    # words = words.rstrip()
    words = re.sub(r",$", ".", words)
    if not words.endswith("."):
        words += "."
    if FORMAT == "tex":
        words = "\\textit{" + words
        words = words.replace(",", "},", 1)
    return words


def search(pattern, text):
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    else:
        return None


def main(ori):
    ori = re.sub(r"doi:.*", "", ori)
    ori = re.sub(r"\n.*", "", ori)
    name = search(r"(.*?), \"", ori)
    title = search(r"\"(.*?)\"", ori)
    journal_info = search(r",\" (.*?)$", ori)

    name_rep = name.replace(" and", ", and")
    if FORMAT == "tex":
        name_rep = name_rep.replace("et al", "\\textit{et al}")
        ori = ori.replace('"', "``", 1).replace('"', "''", 1)

    journal_info_abb = abbrebiation(journal_info)

    ori = ori.replace(name, name_rep)
    ori = ori.replace(journal_info, journal_info_abb)

    pyperclip.copy(ori)
    print(ori)


while True:
    print("Input the reference (or 'exit' to quit):")
    ori = sys.stdin.read()
    if ori == "exit":
        break
    else:
        main(ori)
