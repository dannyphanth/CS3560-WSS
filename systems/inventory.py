from dataclasses import dataclass

@dataclass
class Inventory:
    gold: int = 100
    food: int = 50
    water: int = 50
    max_items: int = 300

    @property
    def total_items(self) -> int:
        # total “resource units” carried
        return self.gold + self.food + self.water

    def can_add(self, amount: int) -> bool:
        return self.total_items + amount <= self.max_items

    def add(self, resource: str, amount: int = 1) -> None:
        if resource == "gold":
            self.gold = min(self.gold + amount, self.max_items)
        elif resource == "food":
            self.food = min(self.food + amount, self.max_items)
        elif resource == "water":
            self.water = min(self.water + amount, self.max_items)
        else:
            raise ValueError(f"Unknown resource: {resource}")

    def spend(self, resource: str, amount: int = 1) -> bool:
        # returns True if successful
        if resource == "gold" and self.gold >= amount:
            self.gold -= amount
            return True
        if resource == "food" and self.food >= amount:
            self.food -= amount
            return True
        if resource == "water" and self.water >= amount:
            self.water -= amount
            return True
        return False

    def random_resource(self) -> str | None:
        import random
        choices = []
        if self.gold > 0: choices.append("gold")
        if self.food > 0: choices.append("food")
        if self.water > 0: choices.append("water")
        return random.choice(choices) if choices else None

    def show_inventory(self) -> None:
        print(f"Gold: {self.gold}, Food: {self.food}, Water: {self.water}")

    def balance(self, resource: str): 
        # returns amount you can use
        if resource == "gold": 
            return self.gold
        if resource == "food": 
            return self.food
        if resource == "water": 
            return self.water
        return -1