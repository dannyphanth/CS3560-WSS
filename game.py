import arcade
from typing import Optional
import random

# Import custom classes
from items.base import Item
from items.bonuses import FoodBonus, WaterBonus, GoldBonus, RepeatingFoodFountain
from world.map import World, TILE_SIZE
from actors.player import Player
from actors.trader import Trader
from systems.inventory import Inventory


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Wilderness Survival"
ITEM_TYPES = [WaterBonus, FoodBonus, GoldBonus, RepeatingFoodFountain]


class Game(arcade.Window):
    """Main Arcade window for the Wilderness Survival game."""

    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # The game world (grid of Terrain). Created in setup().
        self.world: Optional[World] = None
        self.player = None
        self.trader = None
        self.items: list[Item] = []
        
        # Optional: set a background color behind the tiles
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self) -> None:
        """Create a new world instance. Call this before starting the game."""
        # Compute how many tiles fit in the window, based on TILE_SIZE.
        width_in_tiles = SCREEN_WIDTH // TILE_SIZE
        height_in_tiles = SCREEN_HEIGHT // TILE_SIZE

        #Creates a new world instance!
        self.world = World(width_in_tiles, height_in_tiles, difficulty="normal", tile_size=TILE_SIZE)

        self.player = Player("Player1", strength=1000, location=(0, 0), inventory=Inventory(12, 12, 12, max_items=300))  # With starting position
        self.trader = Trader("Trader1", location=(1, 1), inventory=Inventory(100, 50, 50, max_items=3000))  # With starting position

        self.place_items(width_in_tiles, height_in_tiles, difficulty="normal", tiles_size=TILE_SIZE)

    def on_draw(self) -> None:
        """Arcade draw handler – draws the world each frame."""
        #Clears the screen and draws the world
        self.clear()
        if self.world:
            self.world.draw()
        if self.player:
            self.player.draw()
        if self.trader:
            self.trader.draw()
        if self.items:
            # because the item instances share a sprite_list, 
            # simply use one item to draw the entire list
            self.items[0].sprite_list.draw()
                
    def on_key_press(self, symbol, modifiers):
        if self.player:
            current_location = self.player.location
        new_location = list(current_location)
        moved = False
        
        if self.player and self.trader and self.player.strength > 0:
            # get potential location from user input
            if symbol == arcade.key.LEFT or symbol == arcade.key.A:
                new_location[0] -= 1
                moved = True
            elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
                new_location[0] += 1
                moved = True
            elif symbol == arcade.key.UP or symbol == arcade.key.W:
                new_location[1] += 1
                moved = True
            elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
                new_location[1] -= 1
                moved = True

            # check for tile overlap with trader
            if moved and tuple(new_location) == self.trader.location:
                print(f"Movement denied: Player cannot occupy the same tile as {self.trader.name}.")
                return # block the move

            # movement occurred and move is valid, update player location
            if moved:
                self.player.set_location(tuple(new_location)) 
                self.player.is_at_trader_location(self.trader)
                self.player.is_at_item_location(self.items)
        else:
            print("Player has no strength left to move.")


    def place_items(self, width_in_tiles, height_in_tiles, difficulty="normal", tiles_size=TILE_SIZE): 
        """
        Populates self.items with randomly placed items.
        """
        # Clear existing items if needed
        self.items.clear()

        # How many items? Scale by difficulty
        area = width_in_tiles * height_in_tiles

        if difficulty == "easy":
            item_count = max(5, area // 50)
        elif difficulty == "hard":
            item_count = max(2, area // 120)
        else:  # normal
            item_count = max(area-5, 1)

        for _ in range(item_count):
            # Choose a random item class
            item_class = random.choice(ITEM_TYPES)

            while True:
                x = random.randint(0, width_in_tiles - 1)
                y = random.randint(0, height_in_tiles - 1)
                loc = (x, y)

                # avoid placing same class objects together 
                # avoid placing objects on traders or player
                if (not any(existing.location == loc and isinstance(existing, item_class)
                            for existing in self.items)
                    and loc != self.player.location
                    and loc != self.trader.location
                ):
                    break

            item = item_class(tuple([x, y]))
            self.items.append(item)


def main() -> None:
    """Entry point when running this module directly."""
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()