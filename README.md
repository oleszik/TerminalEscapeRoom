# Terminal Escape Room

A text-based escape room adventure in Python.
Inspect rooms, solve code puzzles, trigger mechanisms, and make your way out.

## Quick Start

1. Clone the repo.
2. (Optional but recommended) create a virtual environment:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
3. Install dependencies:
  - `pip install -r requirements.txt`
4. Run the game:
  - `python -m game.main`

## Goal

Escape by progressing through connected rooms:
`study -> library -> vault -> observatory -> exit_hall -> courtyard`

Each room has clues, objects, and lock conditions. Some doors open with a code, some with state flags from interactions.

## Command Reference

- `help`: show available commands.
- `look`: print the current room description.
- `look <object>`: inspect an object (example: `look bookshelf`).
- `use <object_or_item>`: interact with object/item logic (example: `use panel`).
- `activate <object>`: trigger powered mechanisms in specific rooms (example: `activate gate`).
- `enter <code>`: submit a puzzle code (example: `enter EKAR`).
- `go <room>`: move to a connected room if unlocked (example: `go library`).
- `inventory`: show carried items.
- `quit`: exit the game.

## How To Play Effectively

1. Start each room with `look`.
2. Inspect key objects with `look <object>`.
3. Use interactive objects to reveal hints (`use note`, `use globe`, etc.).
4. Enter discovered codes with `enter <code>`.
5. When a path unlocks, move using `go <room>`.
6. In the final sequence, remember the extra mechanic: `activate gate`.

## First Room Example

```text
look
look bookshelf
use note
enter EKAR
use key
go library
```

## Troubleshooting

- If colors are noisy in your terminal, disable ANSI coloring:
  - `NO_COLOR=1 python -m game.main`
- `Exit code 130` usually means the game was interrupted with `Ctrl+C`.

## Project Structure

- `game/main.py`: launcher.
- `game/game_engine.py`: game loop and command handling.
- `game/room.py`: room behavior and interaction rules.
- `game/player.py`: inventory model.
- `rooms/*.json`: room definitions and interaction scripts.
- `puzzles.json`: puzzle text, clues, and required codes.
- `assets/ascii_art.txt`: startup banner.
- `assets/room_visuals.json`: per-room visual cards.
- `tests/test_progression.py`: regression tests for progression and unlock flow.

## Run Tests

`python -m unittest discover -s tests -p "test_*.py" -v`
