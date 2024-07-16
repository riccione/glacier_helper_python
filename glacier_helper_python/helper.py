"""
depends on aws console

- parse it
- 2 possible ways:
    - generate html with all commands
    - interactively generate aws console commands for glacier
"""
import argparse
import os
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
        p = Path(ys['Path'])
        p = os.path.basename(p)
        t.append(
            f"{p} | \
            {size_h(x['Size'])} | \
            {datetime_h(x['CreationDate'])}"
        )
        r[x["ArchiveId"]] = t
    return r


def txt_to_html(xs: dict, vn="vault_name") -> str:
    t = "<!DOCTYPE html><html><title>output.json to output.html</title><body>"
    t += f"<h2>Glacier vault contains: {len(xs)} objects aka files:</h2>"
    aws_initiate_job = """
    $meta |
    <input type='text' value='aws glacier initiate-job --vault-name $vault_name
    --account-id - --job-parameters
    "{\\"Type\\":\\"archive-retrieval\\",\\"Tier\\":\\"Bulk\\",\\"ArchiveId\\":\\"$archive_id\\"}"'
    id='$id' />
    <button onclick="cp('$id')">Initiate Job</button></br>
    <input type='text' value='$archive_id' id='$archiveId' />
    <button onclick="cp_archive('$archiveId')">ArchiveId</button></br>
    """
    for i, (x, y) in enumerate(xs.items()):
        t2 = Template(aws_initiate_job).safe_substitute(meta=y,vault_name=vn,archive_id=x,id=i)
        t2 = t2.strip()
        t += t2
    t += "<script>"
    t += "function cp(y) {"
    t += "console.log(y);"
    t += "let x = document.getElementById(y);"
    t += "x.select();"
    t += "x.setSelectionRange(0, 99999);"
    t += "navigator.clipboard.writeText(x.value);"
    t += 'alert("Copied: " + x.value);'
    t += "}\n"
    t += "function cp_archive(y) {\n"
    t += "console.log(y);\n"
    t += "let x = document.getElementById(y);\n"
    t += "x.select();\n"
    t += "x.setSelectionRange(0, 99999);\n"
    t += "navigator.clipboard.writeText(x.value);\n"
    t += 'alert("Copied: " + x.value);\n'
    t += "}\n"
    t += "</script>\n"
    t += "</body></html>"
    return t


def save_html(xs, vn, z="output.html"):
    ys = txt_to_html(xs, vn)
    with open(z, "w") as f:
        f.write(ys)


def parse(x, vn):
    data = read_file(x)
    r = extract(data["ArchiveList"])
    save_html(r, vn)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="path to json file", type=str)
    parser.add_argument("vault", help="vault name", type=str)
    args = parser.parse_args()
    if is_file_exist(args.filename):
        parse(args.filename, args.vault)
    else:
        print("File not found. Please provide a valid path to json filename")


if __name__ == "__main__":
    main()
