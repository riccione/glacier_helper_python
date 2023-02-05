"""
depends on aws console

- parse it
- 2 possible ways:
    - generate html with all commands
    - interactively generate aws console commands for glacier
"""
import argparse
from pathlib import Path
import json
from datetime import datetime as dt
from string import Template


def read_file(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def is_file_exist(x):
    if x is not None:
        x = Path(x)
        if x.is_file() and x.suffix == ".json":
            return True
    return False


def datetime_h(x):
    y = dt.fromisoformat(x)
    return f"{y.day}.{y.month}.{y.year} {y.hour}:{y.minute}"

def size_h(x, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(x) < 1024.0:
            return f"{x:3.1f}{unit}{suffix}"
        x /= 1024.0
    return f"{x:.1f}Yi{suffix}"

def extract(xs: list) -> dict:
    r = {}
    for x in xs:
        ys = json.loads(x["ArchiveDescription"])
        t = []
        t.append(f"{ys['Path']} | \
            {size_h(x['Size'])} | \
            {datetime_h(x['CreationDate'])}")
        r[x['ArchiveId']] = t
    return r

def txt_to_html(xs: dict) -> str:
    v = 'vault_name'
    t = "<!DOCTYPE html><html><title>output.json to output.html</title><body>"
    t += f"<h2>Glacier vault contains: {len(xs)} objects aka files:</h2>"
    t1 = '''
    <button onclick="cp('$id')">Initiate Job</button></br>
    '''
    for x, y in xs.items():
        aws_initiate_job = f"aws glacier initiate-job --vault-name {v} "
        aws_initiate_job += f"--account-id - --job-parameters "
        aws_initiate_job += '{\"Type\":\"archive-retrieval\",\"Tier\":\"Bulk\",\"ArchiveId\":\"'
        aws_initiate_job += x
        aws_initiate_job += '\"}'
        t += f"{y} | <input type='hidden' value='{aws_initiate_job}' id='{x}'>"
        t += Template(t1).safe_substitute(id=x)
    t += "<script>"
    t += "function cp(y) {"
    t += "let x = document.getElementById(y);"
    t += "x.select();"
    t += "x.setSelectionRange(0, 99999);"
    t += "navigator.clipboard.writeText(x.value);"
    t += "navigator.clipboard.writeText(x.value);"
    t += "}"
    t += "</script>"
    t += "</body></html>"
    return t

def save_html(xs, y="output.html"):
    ys = txt_to_html(xs)
    with open(y, "w") as f:
        f.write(ys)

def parse(x):
    data = read_file(x)
    r = extract(data["ArchiveList"])
    save_html(r)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path to json file", type=str)
    args = parser.parse_args()
    if is_file_exist(args.filename):
        parse(args.filename)
    else:
        print("File not found. Please provide a valid path to json filename")


if __name__ == "__main__":
    main()
