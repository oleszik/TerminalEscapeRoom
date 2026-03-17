import json
import os


def load_room(file_path):
    if not os.path.isabs(file_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
