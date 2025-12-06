from dataclasses import dataclass, field

@dataclass
class Inventory:
    def __init__(self, gold=100, food=50, water=50, max_items=300): 
        self.gold = gold
        self.food = food
        self.water = water
        self.max_items = 300
        
    def show_inventory(self): 
        print(f"Gold: {self.gold}, Food: {self.food}, Water: {self.water}")