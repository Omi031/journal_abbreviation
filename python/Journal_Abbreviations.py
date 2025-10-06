import csv
import re

import pyperclip

DEL_PATH = r"C:\Users\naoki\マイドライブ（25wm4346@student.gs.chiba-u.jp）\Chiba-U\Ahn\thesis\del.csv"
REP_PATH = r"C:\Users\naoki\マイドライブ（25wm4346@student.gs.chiba-u.jp）\Chiba-U\Ahn\thesis\replace.csv"

with open(DEL_PATH, encoding="utf-8") as f:
    reader = csv.reader(f)
    era = [row for row in reader][1:]
    era = list(map(list, zip(*era)))

with open(REP_PATH, encoding="utf-8") as f:
    reader = csv.reader(f)
    rep = [row for row in reader][1:]
    rep = list(map(list, zip(*rep)))


def abbrebiation(ori):
    ori = ori.split()

    for i, o in enumerate(ori):
        if o in era[0]:
            ori[i] = ""
        elif o in rep[0]:
            ori[i] = rep[1][rep[0].index(o)] + "."
        else:
            pass
    ori = [o for o in ori if o != ""]
    ori = " ".join(ori)
    ori = re.sub(r"(pp\. )(\d+)-(\d+)", r"\1\2--\3", ori)
    pyperclip.copy(ori)
    print(ori)


while True:
    ori = input("Please input the original journal name: ")
    if ori == "exit":
        break
    else:
        abbrebiation(ori)
