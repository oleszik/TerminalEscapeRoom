import unittest

from game.player import Player
from game.puzzle_engine import PuzzleEngine
from game.room import Room


class ProgressionTests(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.state = {"flags": set(), "puzzle_variants": {}, "seed": 12345}
        self.engine = PuzzleEngine()

    def load_room(self, room_name):
        return Room(f"rooms/{room_name}.json", puzzle_engine=self.engine, game_state=self.state)

    def test_full_progression_reaches_courtyard(self):
        study = self.load_room("study")
        study.enter_code(study.required_code, self.player)
        study.use("key", self.player)
        self.assertIn("study_door_unlocked", self.state["flags"])

        library = self.load_room("library")
        library.use("globe", self.player)
        library.use("ladder", self.player)
        library.use("shelf", self.player)
        library.enter_code(library.required_code, self.player)
        self.assertIn("library_vault_unlocked", self.state["flags"])

        vault = self.load_room("vault")
        vault.use("journal", self.player)
        vault.use("panel", self.player)
        vault.enter_code(vault.required_code, self.player)
        self.assertIn("vault_door_open", self.state["flags"])

        observatory = self.load_room("observatory")
        observatory.use("telescope", self.player)
        observatory.enter_code(observatory.required_code, self.player)
        self.assertIn("observatory_exit_unlocked", self.state["flags"])

        exit_hall = self.load_room("exit_hall")
        exit_hall.use("lever", self.player)
        exit_hall.use("panel", self.player)
        exit_hall.enter_code(exit_hall.required_code, self.player)
        self.assertIn("exit_gate_armed", self.state["flags"])
        self.assertNotIn("exit_gate_open", self.state["flags"])

        exit_hall.activate("gate", self.player)
        self.assertIn("exit_gate_open", self.state["flags"])

        courtyard = self.load_room("courtyard")
        self.assertEqual(courtyard.name, "courtyard")

    def test_exit_gate_requires_activate_step(self):
        exit_hall = self.load_room("exit_hall")
        exit_hall.use("lever", self.player)
        exit_hall.use("panel", self.player)
        exit_hall.enter_code(exit_hall.required_code, self.player)

        self.assertIn("exit_gate_armed", self.state["flags"])
        self.assertNotIn("exit_gate_open", self.state["flags"])


if __name__ == "__main__":
    unittest.main()
