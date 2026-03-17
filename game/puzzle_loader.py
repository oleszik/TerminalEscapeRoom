import json
import os


def load_puzzle(puzzle_id):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    puzzle_path = os.path.join(project_root, "puzzles.json")
    with open(puzzle_path, "r", encoding="utf-8") as f:
        puzzles = json.load(f)
    return puzzles.get(puzzle_id, {})
