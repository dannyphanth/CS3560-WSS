import random
import arcade

TILE_SIZE = 32  # pixels per tile
SPRITE_SCALING = 0.5

# Trader class: implements trading behavior for trader actors

class Trader:
    def __init__(self, name, location):
        self.name = name
        self.location = location  # (x, y) tuple
        self.sprite = arcade.Sprite("assets/trader.png", scale=0.5)  # Load trader sprite
        self.sprite.center_x = location[0] * TILE_SIZE + TILE_SIZE // 2
        self.sprite.center_y = location[1] * TILE_SIZE + TILE_SIZE // 2

        # initialize inventory with random values for food, water, and gold
        self.inventory = {
            'food': random.randint(30, 70),
            'water': random.randint(30, 70),
            'gold': random.randint(80, 120)
        }

    def evaluate_trade_offer(self, trade_offer):
        # simple logic: accept if trader has enough of the requested item
        item = trade_offer['item']
        quantity = trade_offer['quantity']
        return self.inventory.get(item, 0) >= quantity
    
    def counter_trade_offer(self, trade_offer):
        # simple logic: counter with half the requested quantity if not enough
        item = trade_offer['item']
        quantity = trade_offer['quantity']
        if self.inventory.get(item, 0) < quantity:
            counter_quantity = self.inventory.get(item, 0) // 2
            if counter_quantity > 0:
                return {'item': item, 'quantity': counter_quantity}
        return None

    def draw(self):
        self.sprite.draw()