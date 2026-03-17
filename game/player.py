class Player:
    def __init__(self):
        self.inventory = []

    def add_item(self, item):
        if item not in self.inventory:
            self.inventory.append(item)

    def show_inventory(self):
        if not self.inventory:
            return "You’re not carrying anything."
        return "Inventory: " + ", ".join(self.inventory)
