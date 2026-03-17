import json
import os
import sys

from .room import Room
from .player import Player
from .puzzle_engine import PuzzleEngine


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(PROJECT_ROOT, "assets", "ascii_art.txt")
ROOM_VISUALS_PATH = os.path.join(PROJECT_ROOT, "assets", "room_visuals.json")
ROOMS_DIR = os.path.join(PROJECT_ROOT, "rooms")

ANSI_TOKENS = {
    "{reset}": "\033[0m",
    "{bold}": "\033[1m",
    "{dim}": "\033[2m",
    "{red}": "\033[31m",
    "{green}": "\033[32m",
    "{yellow}": "\033[33m",
    "{blue}": "\033[34m",
    "{magenta}": "\033[35m",
    "{cyan}": "\033[36m",
}


def load_ascii_art():
    try:
        with open(ASSETS_PATH, "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print("Welcome to the Escape Room!")


def load_room_visuals():
    try:
        with open(ROOM_VISUALS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def supports_ansi():
    if os.getenv("NO_COLOR"):
        return False
    if os.getenv("TERM", "").lower() == "dumb":
        return False
    return sys.stdout.isatty()


def render_with_style(text, use_ansi):
    rendered = str(text)
    for token, ansi_code in ANSI_TOKENS.items():
        rendered = rendered.replace(token, ansi_code if use_ansi else "")
    return rendered


def print_room_visual(room_name, room_visuals, use_ansi):
    visual = room_visuals.get(room_name)
    if not isinstance(visual, dict):
        return

    for line in visual.get("art", []):
        print(render_with_style(line, use_ansi))

    caption = visual.get("caption")
    if caption:
        print(render_with_style(caption, use_ansi))

    if visual.get("art") or caption:
        print()

def start_game():
    load_ascii_art()
    room_visuals = load_room_visuals()
    use_ansi = supports_ansi()
    player = Player()
    game_state = {"flags": set(), "puzzle_variants": {}}
    puzzle_engine = PuzzleEngine()
    current_room_path = os.path.join(ROOMS_DIR, "study.json")
    room = Room(current_room_path, puzzle_engine=puzzle_engine, game_state=game_state)

    def transition_is_unlocked(transition):
        required_item = transition.get("unlocked_by_item")
        required_flag = transition.get("unlocked_by_flag")

        if required_item and required_item not in player.inventory:
            return False, f"You can't go there yet. You need item: {required_item}"
        if required_flag and required_flag not in game_state["flags"]:
            return False, f"You can't go there yet. You need to trigger: {required_flag}"

        # Backward compatibility: allow a single requirement to be either an item or a flag.
        legacy_requirement = transition.get("unlocked_by")
        if legacy_requirement:
            if legacy_requirement in player.inventory or legacy_requirement in game_state["flags"]:
                return True, ""
            return False, f"You can't go there yet. You need: {legacy_requirement}"

        required_items = transition.get("requires_items", [])
        for item in required_items:
            if item not in player.inventory:
                return False, f"You can't go there yet. You need item: {item}"

        required_flags = transition.get("requires_flags", [])
        for flag in required_flags:
            if flag not in game_state["flags"]:
                return False, f"You can't go there yet. You need to trigger: {flag}"

        return True, ""

    def move_to(destination):
        nonlocal current_room_path, room
        current_room_path = os.path.join(ROOMS_DIR, f"{destination}.json")
        room = Room(current_room_path, puzzle_engine=puzzle_engine, game_state=game_state)
        print(f"\nYou move into the {destination}...\n")
        print_room_visual(destination, room_visuals, use_ansi)
        print(room.describe())

    print("Type 'help' for a list of commands.\n")
    print_room_visual(room.name, room_visuals, use_ansi)
    print(room.describe())

    while True:
        command = input("> ").strip().lower()

        if command == "quit":
            print("Goodbye!")
            break

        elif command == "help":
            print("Commands: look [object], use [item], activate [object], enter [code], go [room], inventory, quit")

        elif command == "look":
            print(room.describe())

        elif command.startswith("look "):
            print(room.look(command[5:], player))

        elif command.startswith("use "):
            print(room.use(command[4:], player))
            if room.is_unlocked:
                next_rooms = getattr(room, "next_rooms", {})
                auto_destination = getattr(room, "auto_next_room", None)
                if auto_destination and auto_destination in next_rooms:
                    is_unlocked, reason = transition_is_unlocked(next_rooms[auto_destination])
                    if is_unlocked:
                        print("A passage opens to the next room.")
                        move_to(auto_destination)
                    else:
                        print(reason)

        elif command.startswith("activate "):
            print(room.activate(command[9:], player))

        elif command.startswith("enter "):
            code = command[6:]
            print(room.enter_code(code, player))

        elif command.startswith("go "):
            destination = command[3:]
            next_rooms = getattr(room, "next_rooms", {})
            if destination in next_rooms:
                is_unlocked, reason = transition_is_unlocked(next_rooms[destination])
                if is_unlocked:
                    move_to(destination)
                else:
                    print(reason)
            else:
                print("You can't go there from here.")

        elif command == "inventory":
            print(player.show_inventory())

        else:
            print("❓ Unknown command. Type 'help' for options.")
