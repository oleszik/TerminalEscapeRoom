import os

from .room import Room
from .player import Player
from .puzzle_engine import PuzzleEngine


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(PROJECT_ROOT, "assets", "ascii_art.txt")
ROOMS_DIR = os.path.join(PROJECT_ROOT, "rooms")


def load_ascii_art():
    try:
        with open(ASSETS_PATH, "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print("Welcome to the Escape Room!")

def start_game():
    load_ascii_art()
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
        print(room.describe())

    print("Type 'help' for a list of commands.\n")
    print(room.describe())

    while True:
        command = input("> ").strip().lower()

        if command == "quit":
            print("Goodbye!")
            break

        elif command == "help":
            print("Commands: look [object], use [item], enter [code], go [room], inventory, quit")

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
