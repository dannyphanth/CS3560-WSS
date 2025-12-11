import arcade
from typing import Optional
import random

# Import custom classes
from items.base import Item
from items.bonuses import FoodBonus, WaterBonus, GoldBonus, RepeatingFoodFountain
from world.map import World, TILE_SIZE
from actors.player import Player
from actors.trader import Trader, GreedyTrader
from systems.inventory import Inventory

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Wilderness Survival"
ITEM_TYPES = [WaterBonus, FoodBonus, GoldBonus, RepeatingFoodFountain]


class Game(arcade.Window):
    """Main Arcade window for the Wilderness Survival game."""

    #===============================================================
    # setting up
    #===============================================================
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Game state: menu or playing 
        self.state = "menu"

        # Game objects
        self.world: Optional[World] = None
        self.turn_timer = 0
        self.turn_interval = 1
        self.player = None
        self.traders: list[Trader] = []
        self.items: list[Item] = []

        # Menu options
        self.map_sizes = [
            ("Small", 10, 8),
            ("Medium", 20, 15),
            ("Large", 25, 18),
        ]
        self.map_size_index = 1  # Medium

        self.difficulties = ["easy", "normal", "hard"]
        self.difficulty_index = 1  # normal

        arcade.set_background_color(arcade.color.BLACK)


    def on_draw(self) -> None:
        self.clear()
        print("State: ", self.state)
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            if self.world:
                self.world.draw()
            if self.player:
                self.player.draw()
            if self.traders:
                for trader in self.traders:
                    trader.draw()
            if self.items:
                # because the item instances share a sprite_list, 
                # simply use one item to draw the entire list
                self.items[0].sprite_list.draw()


    def setup(self, width_in_tiles: int | None = None,
              height_in_tiles: int | None = None,
              difficulty: str = "normal") -> None:

        if width_in_tiles is None or height_in_tiles is None:
            width_in_tiles = SCREEN_WIDTH // TILE_SIZE
            height_in_tiles = SCREEN_HEIGHT // TILE_SIZE

        # Create world
        self.world = World(
            width_in_tiles,
            height_in_tiles,
            difficulty=difficulty,
            tile_size=TILE_SIZE,
        )

        # Player and Traders
        self.player = Player(
            "Player1",
            location=(0, 0),
            inventory=Inventory(12, 12, 12, max_items=30),
            game=self,
            strength=25,
        )

        # Place traders at random tiles not occupied by player
        self.traders = self.place_traders(width_in_tiles, height_in_tiles)

        # Items
        self.place_items(width_in_tiles, height_in_tiles, difficulty=difficulty)

        # Switch screen
        self.state = "playing"


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
            # item_count = max(3, area // 80)
            item_count = 300

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



    #===============================================================
    # Turn logic
    #===============================================================

    def on_update(self, delta_time):
        """Arcade function called every few seconds to update game state."""
        self.turn_timer += delta_time
        if self.player and self.turn_timer >= self.turn_interval:
            self.turn_timer = 0
            self.player.brain.make_move()


    def apply_terrain_cost(self, player: Player): 
        terrainObj = self.world.get_terrain(player.location)
        player.strength - terrainObj.move_cost
        player.inventory.spend('water', terrainObj.water_cost)
        player.inventory.spend('food', terrainObj.food_cost)
                

    def list_items_at_location(self, loc) -> list[Item]:
        itemsAtLoc = [] 
        for item in self.items[:]:   # iterate over a copy
            if loc == item.location:
                itemsAtLoc.append(item)
        return itemsAtLoc


    def draw_menu(self) -> None:
        arcade.draw_text(
            "Wilderness Survival",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            font_size=32,
            anchor_x="center",
        )

        size_label, w_tiles, h_tiles = self.map_sizes[self.map_size_index]
        difficulty = self.difficulties[self.difficulty_index]

        arcade.draw_text(
            f"Map size: {size_label} ({w_tiles} x {h_tiles})",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 40,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center",
        )
        arcade.draw_text(
            "Use LEFT / RIGHT to change map size",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 10,
            arcade.color.GRAY,
            font_size=14,
            anchor_x="center",
        )

        arcade.draw_text(
            f"Difficulty: {difficulty}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 40,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center",
        )
        arcade.draw_text(
            "Use UP / DOWN to change difficulty",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 70,
            arcade.color.GRAY,
            font_size=14,
            anchor_x="center",
        )

        arcade.draw_text(
            "Press ENTER to start",
            SCREEN_WIDTH / 2,
            120,
            arcade.color.YELLOW,
            font_size=18,
            anchor_x="center",
        )


    def on_key_press(self, symbol, modifiers):
        if self.state == "menu":
            self.handle_menu_input(symbol)
        else:
            # This is where we can handle game input
            # self.handle_game_input(symbol)
            pass


    def handle_menu_input(self, symbol) -> None:
        if symbol in (arcade.key.LEFT, arcade.key.A):
            self.map_size_index = (self.map_size_index - 1) % len(self.map_sizes)

        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.map_size_index = (self.map_size_index + 1) % len(self.map_sizes)

        elif symbol in (arcade.key.UP, arcade.key.W):
            self.difficulty_index = (self.difficulty_index - 1) % len(self.difficulties)

        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)

        elif symbol == arcade.key.ENTER:
            _, w_tiles, h_tiles = self.map_sizes[self.map_size_index]
            difficulty = self.difficulties[self.difficulty_index]
            self.setup(
                width_in_tiles=w_tiles,
                height_in_tiles=h_tiles,
                difficulty=difficulty,
            )


    def place_traders(self, width_in_tiles, height_in_tiles):
        """Spawn regular and greedy traders based on map size."""
        area = width_in_tiles * height_in_tiles
        if area < 150:
            regular_count, greedy_count = 1, 0
        elif area < 300:
            regular_count, greedy_count = 1, 1
        else:
            regular_count, greedy_count = 2, 2

        traders: list[Trader] = []
        occupied = {self.player.location}

        def random_empty_loc():
            while True:
                loc = (
                    random.randint(0, width_in_tiles - 1),
                    random.randint(0, height_in_tiles - 1),
                )
                if loc not in occupied:
                    occupied.add(loc)
                    return loc

        for i in range(regular_count):
            loc = random_empty_loc()
            traders.append(
                Trader(
                    f"Trader{i+1}",
                    location=loc,
                    inventory=Inventory(100, 50, 50, max_items=3000),
                )
            )

        for i in range(greedy_count):
            loc = random_empty_loc()
            traders.append(
                GreedyTrader(
                    f"GreedyTrader{i+1}",
                    location=loc,
                    inventory=Inventory(100, 50, 50, max_items=3000),
                )
            )

        return traders


#===============================================================
# Start this file
#===============================================================
def main():
    """Main entry point for the game."""
    window = Game()
    arcade.run()


if __name__ == "__main__":
    main()
