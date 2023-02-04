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


def parse(x):
    data = read_file(x)
    print(data)


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
