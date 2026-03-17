from .room_loader import load_room
from .puzzle_engine import PuzzleEngine


class Room:
    def __init__(self, json_path, puzzle_engine=None, game_state=None):
        data = load_room(json_path)
        self.game_state = game_state if game_state is not None else {}
        self.game_state.setdefault("flags", set())

        self.puzzle_engine = puzzle_engine or PuzzleEngine()
        self.puzzle = self.puzzle_engine.get(data["puzzle_id"], self.game_state)

        self.name = data["name"]
        self.puzzle_id = data["puzzle_id"]
        self.description_text = self.puzzle.get("description", "You stand in silence.")

        self.objects = data["objects"]
        self.books = self.puzzle.get("books", {})
        self.required_code = self.puzzle.get("required_code", "")
        self.note_text = self.puzzle.get("note", "")
        self.gives_key = data.get("gives_key", False)
        self.next_rooms = data.get("next_rooms", {})
        self.auto_next_room = data.get("auto_next_room")

        self.is_unlocked = False
        self.key_revealed = False

        self.interactions = {}
        puzzle_interactions = self.puzzle.get("interactions", {})
        for action, rules in puzzle_interactions.items():
            self.interactions[action] = list(rules)

        for action, rules in data.get("interactions", {}).items():
            self.interactions.setdefault(action, []).extend(rules)

        # Setup alias map
        self.alias_map = {}
        for canonical, words in data.get("aliases", {}).items():
            for alias in words:
                self.alias_map[alias.lower()] = canonical
                self.alias_map[alias.lower().replace(" ", "")] = canonical  # support 'metalbox'

    def _flags(self):
        return self.game_state.setdefault("flags", set())

    def _normalize_target(self, target):
        target = (target or "").lower().strip()
        return self.alias_map.get(target, target)

    def _render_text(self, text):
        if not isinstance(text, str):
            return text
        try:
            context = dict(self.puzzle)
            context.setdefault("required_code", self.required_code)
            context.setdefault("note", self.note_text)
            return text.format(**context)
        except (KeyError, ValueError):
            return text

    def _is_rule_match(self, rule, target=None, code=None, player=None):
        rule_target = rule.get("target")
        normalized_target = self._normalize_target(target) if target is not None else None

        if rule_target is not None:
            if normalized_target is None:
                return False
            if isinstance(rule_target, list):
                valid_targets = {self._normalize_target(x) for x in rule_target}
                if normalized_target not in valid_targets:
                    return False
            elif normalized_target != self._normalize_target(rule_target):
                return False

        inventory = set(player.inventory) if player else set()
        required_items = set(rule.get("requires_items", []))
        if required_items and not required_items.issubset(inventory):
            return False

        active_flags = self._flags()
        required_flags = set(rule.get("requires_flags", []))
        if required_flags and not required_flags.issubset(active_flags):
            return False

        blocked_flags = set(rule.get("forbid_flags", []))
        if blocked_flags and blocked_flags.intersection(active_flags):
            return False

        if "expected_code" in rule:
            if code is None:
                return False
            expected = self._render_text(str(rule["expected_code"])).strip().upper()
            if code.strip().upper() != expected:
                return False

        return True

    def _apply_rule_effects(self, rule, player=None):
        effects = {}
        if isinstance(rule.get("effects"), dict):
            effects.update(rule["effects"])

        for key in ["set_flags", "clear_flags", "give_items", "unlock_room", "relock_room"]:
            if key in rule:
                effects[key] = rule[key]

        active_flags = self._flags()
        for flag in effects.get("set_flags", []):
            active_flags.add(flag)
        for flag in effects.get("clear_flags", []):
            active_flags.discard(flag)

        if player:
            for item in effects.get("give_items", []):
                player.add_item(item)

        if effects.get("unlock_room"):
            self.is_unlocked = True
        if effects.get("relock_room"):
            self.is_unlocked = False

    def _run_scripted_interaction(self, action, target=None, code=None, player=None):
        for rule in self.interactions.get(action, []):
            if self._is_rule_match(rule, target=target, code=code, player=player):
                self._apply_rule_effects(rule, player=player)
                return self._render_text(rule.get("response", "Nothing happens."))
        return None

    def describe(self):
        return self.description_text

    def look(self, target, player=None):
        target = self._normalize_target(target)

        scripted_response = self._run_scripted_interaction("look", target=target, player=player)
        if scripted_response:
            return scripted_response

        if target in self.objects:
            return self.objects[target]

        elif target in self.books:
            return f"{target.title()}: \"{self.books[target]}\""

        elif target == "books":
            book_list = "\n".join(
                f"- {author.title()}: \"{title}\"" for author, title in self.books.items()
            )
            return (
                "You scan the bookshelf and find these titles:\n" +
                book_list +
                "\nTry 'look [author]' to examine one."
            )

        return "You don't see anything like that."

    def use(self, item, player):
        item = self._normalize_target(item)

        scripted_response = self._run_scripted_interaction("use", target=item, player=player)
        if scripted_response:
            return scripted_response

        if item == "note":
            return self.note_text
        elif item == "painting":
            return "You peel the painting back further… nothing but cold wall."
        elif item == "box":
            return (
                "You examine the mechanical box closely. The dials are responsive.\n"
                "You can try entering a code with: 'enter [code]'"
            )
        elif item == "key":
            if "key" in player.inventory:
                self.is_unlocked = True
                self._flags().add(f"{self.name}_door_unlocked")
                return "🔓 You insert the key into a small hidden slot. The iron door unlocks with a deep click!"
            else:
                return "You don’t have a key."

        return "You can't use that here."

    def activate(self, target, player=None):
        target = self._normalize_target(target)

        scripted_response = self._run_scripted_interaction("activate", target=target, player=player)
        if scripted_response:
            return scripted_response

        return "You can't activate that here."

    def enter_code(self, code, player=None):
        scripted_response = self._run_scripted_interaction("enter", code=code, player=player)
        if scripted_response:
            return scripted_response

        if code.upper() == self.required_code:
            if self.gives_key and not self.key_revealed:
                self.key_revealed = True
                if player:
                    player.add_item("key")
                return (
                    "✅ The box clicks open with a mechanical whir.\n"
                    "Inside lies a small iron key — you take it and add it to your inventory."
                )
            elif self.gives_key and self.key_revealed:
                return "The box is already open. You already took the key."
            else:
                self.is_unlocked = True
                return "✅ The code was correct! The door unlocks immediately."
        else:
            return "❌ Nothing happens. Maybe that’s the wrong code."