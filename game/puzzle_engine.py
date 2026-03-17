import json
import os
import random


class PuzzleEngine:
    def __init__(self, json_path="puzzles.json"):
        self.puzzles = self._load_puzzles(json_path)

    def _load_puzzles(self, path):
        if not os.path.isabs(path):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(project_root, path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, puzzle_id, game_state=None):
        puzzle = dict(self.puzzles.get(puzzle_id, {}))
        variants = puzzle.get("variants", [])

        if not variants:
            return puzzle

        if game_state is None:
            selected_index = 0
        else:
            selected_variants = game_state.setdefault("puzzle_variants", {})
            if puzzle_id not in selected_variants:
                seed = game_state.setdefault("seed", random.randint(1000, 999999))
                rng = random.Random(f"{seed}:{puzzle_id}")
                selected_variants[puzzle_id] = rng.randrange(len(variants))
            selected_index = selected_variants[puzzle_id]

        selected_variant = variants[selected_index]
        puzzle.pop("variants", None)
        puzzle.update(selected_variant)
        return puzzle

    def list_ids(self):
        return list(self.puzzles.keys())

    # (Optional) track puzzle state if needed later
    def is_valid_code(self, puzzle_id, code):
        puzzle = self.get(puzzle_id)
        return puzzle.get("required_code", "").upper() == code.upper()
