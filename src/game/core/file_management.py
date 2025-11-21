import pathlib
import json

def read_settings():
    path = pathlib.Path(__file__).resolve().parents[2] / "data" / "settings.json"
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"<file_management.py | File not found {path}>")
        return {}
    except json.JSONDecodeError as e:
        print(f"<file_management.py | Error parsing JSON: {e}>")
        return {}