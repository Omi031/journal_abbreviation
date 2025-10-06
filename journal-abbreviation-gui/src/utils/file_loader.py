import csv
import yaml

def load_csv(path, encoding="utf-8"):
    with open(path, encoding=encoding) as f:
        reader = csv.reader(f)
        data = [row for row in reader][1:]
        data = list(map(list, zip(*data)))
    return data

def load_yaml(path, encoding="utf-8"):
    with open(path, encoding=encoding) as yml:
        return yaml.safe_load(yml)