import os
import sys

if __package__:
    from .game_engine import start_game
else:
    # Allow running this file directly: python game/main.py
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from game.game_engine import start_game

if __name__ == "__main__":
    start_game()
