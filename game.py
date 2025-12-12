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
from ai.brains import BRAIN_TYPES, VISION_TYPES, BRAIN_CLASS_MAP, VISION_CLASS_MAP

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Wilderness Survival"
ITEM_TYPES = [WaterBonus, FoodBonus, GoldBonus, RepeatingFoodFountain]


class Game(arcade.Window):
    """Main Arcade window for the Wilderness Survival game."""

    # ===============================================================
    # setting up
    # ===============================================================
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        # Game state: menu or playing
        self.state = "menu"

        # Game objects
        self.world: Optional[World] = None
        self.turn_timer = 0
        self.turn_interval = 0.2  # update the speed of each round
        self.player: Optional[Player] = None
        self.traders: list[Trader] = []
        self.items: list[Item] = []
        self.vision_squares = []

        # Menu options
        self.map_sizes = [
            ("Small", 10, 8),
            ("Medium", 20, 15),
            ("Large", 25, 18),
        ]
        self.map_size_index = 1  # Medium

        self.difficulties = ["easy", "normal", "hard"]
        self.difficulty_index = 1  # normal

        # Brain / vision selection (menu)
        self.brain_index = 0
        self.vision_index = 0

        arcade.set_background_color(arcade.color.BLACK)

    def setup(
        self,
        width_in_tiles: int | None = None,
        height_in_tiles: int | None = None,
        difficulty: str = "normal",
        brain_name: str = "Balanced",
        vision_name: Optional[str] = None,
    ) -> None:

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

        # Player
        self.player = Player(
            "Player1",
            location=(0, 6),
            inventory=Inventory(12, 12, 12, max_items=30),
            game=self,
            strength=10,
        )

        # Create brain for this player using menu choices
        BrainClass = BRAIN_CLASS_MAP[brain_name]
        VisionClass = VISION_CLASS_MAP[vision_name] if vision_name is not None else None
        self.player.brain = BrainClass(
            self,
            self.player,
            brain_type=brain_name,
            vision_cls=VisionClass,
        )

        # Place traders at random tiles not occupied by player
        self.traders = self.place_traders(width_in_tiles, height_in_tiles)

        # Items
        self.place_items(width_in_tiles, height_in_tiles, difficulty=difficulty)

        # Switch screen
        self.state = "playing"

    def on_draw(self) -> None:

        # Draw end message if game finished
        if self.state == "finished":
            arcade.draw_text(
                "You Made It!",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - 100,
                arcade.color.WHITE,
                font_size=40,                     # font size
                anchor_x="center",
                anchor_y="center"
            )
            return

        self.clear()
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            if self.world:
                self.world.draw()
            if self.traders:
                for trader in self.traders:
                    trader.draw()
            if self.items:
                # because the item instances share a sprite_list,
                # simply use one item to draw the entire list
                self.items[0].sprite_list.draw()
            if self.player:
                self.player.draw()
            if self.vision_squares:
                for square in self.vision_squares:
                    center_x = square[0] * TILE_SIZE + TILE_SIZE / 2
                    center_y = square[1] * TILE_SIZE + TILE_SIZE / 2
                    arcade.draw_circle_filled(
                        center_x,
                        center_y,
                        TILE_SIZE / 2 + 7,
                        (170, 225, 255, 50),
                    )


    def check_end_of_board(self, player):
        if player.location[0] >= self.map_sizes[self.map_size_index][1]:
            self.state = "finished"


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
            item_count = max(3, area // 80)

        for _ in range(item_count):
            # Choose a random item class
            item_class = random.choice(ITEM_TYPES)

            while True:
                x = random.randint(0, width_in_tiles - 1)
                y = random.randint(0, height_in_tiles - 1)
                loc = (x, y)

                # avoid placing same class objects together
                # avoid placing objects on traders or player
                if (
                    not any(
                        existing.location == loc and isinstance(existing, item_class)
                        for existing in self.items
                    )
                    and loc != self.player.location
                    and all(loc != trader.location for trader in self.traders)
                ):
                    break

            item = item_class((x, y))
            self.items.append(item)

    # ===============================================================
    # Turn logic
    # ===============================================================

    def on_update(self, delta_time):
        """Arcade function called every few seconds to update game state."""
        if self.state == "finished":
            return
            
        self.turn_timer += delta_time
        if self.player and self.turn_timer >= self.turn_interval:
            self.turn_timer = 0
            self.player.brain.make_move()
            

    def apply_terrain_cost(self, player: Player):
        if not self.world.in_bounds(player.location):
            return 
        terrainObj = self.world.get_terrain(player.location)
        # deduct strength (you had just `player.strength - terrainObj.move_cost`)
        player.strength -= terrainObj.move_cost
        player.inventory.spend("water", terrainObj.water_cost)
        player.inventory.spend("food", terrainObj.food_cost)

    def list_items_at_location(self, loc) -> list[Item]:
        itemsAtLoc = []
        for item in self.items[:]:  # iterate over a copy
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
        brain_name = BRAIN_TYPES[self.brain_index]
        vision_name = VISION_TYPES[self.vision_index]

        # --- Map size ---
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

        # --- Difficulty ---
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

        # --- Brain Type ---
        arcade.draw_text(
            f"Brain: {brain_name}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 120,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press 1 / 2 to change brain",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 150,
            arcade.color.GRAY,
            font_size=14,
            anchor_x="center",
        )

        # --- Vision Type ---
        arcade.draw_text(
            f"Vision: {vision_name}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 200,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press 3 / 4 to change vision",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 230,
            arcade.color.GRAY,
            font_size=14,
            anchor_x="center",
        )

        # --- START GAME (yellow) AT THE END ---
        arcade.draw_text(
            "Press ENTER to start",
            SCREEN_WIDTH / 2,
            40,
            arcade.color.YELLOW,
            font_size=18,
            anchor_x="center",
        )

    def on_key_press(self, symbol, modifiers):
        if self.state == "menu":
            self.handle_menu_input(symbol)
        else:
            # This is where we can handle game input
            self.handle_game_input(symbol)

    def handle_menu_input(self, symbol) -> None:
        # get map size selection
        if symbol in (arcade.key.LEFT, arcade.key.A):
            self.map_size_index = (self.map_size_index - 1) % len(self.map_sizes)

        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.map_size_index = (self.map_size_index + 1) % len(self.map_sizes)

        # get difficulty selection
        elif symbol in (arcade.key.UP, arcade.key.W):
            self.difficulty_index = (self.difficulty_index - 1) % len(self.difficulties)

        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)

        # get brain selection
        elif symbol == arcade.key.KEY_1:
            self.brain_index = (self.brain_index - 1) % len(BRAIN_TYPES)
        elif symbol == arcade.key.KEY_2:
            self.brain_index = (self.brain_index + 1) % len(BRAIN_TYPES)

        # get vision selection
        elif symbol == arcade.key.KEY_3:
            self.vision_index = (self.vision_index - 1) % len(VISION_TYPES)
        elif symbol == arcade.key.KEY_4:
            self.vision_index = (self.vision_index + 1) % len(VISION_TYPES)

        elif symbol == arcade.key.ENTER:
            _, w_tiles, h_tiles = self.map_sizes[self.map_size_index]
            difficulty = self.difficulties[self.difficulty_index]
            brain_name = BRAIN_TYPES[self.brain_index]
            vision_name = VISION_TYPES[self.vision_index]

            self.setup(
                width_in_tiles=w_tiles,
                height_in_tiles=h_tiles,
                difficulty=difficulty,
                brain_name=brain_name,
                vision_name=vision_name,
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

    def handle_game_input(self, symbol) -> None:
        """
        handle_game_input
        This is an outdated function that takes keyboard input from the human user.
        We leave it in in order to override and test functionality.

        :param symbol:
        """
        if not self.player:
            return

        current = self.player.location
        new = list(current)

        if symbol in (arcade.key.LEFT, arcade.key.A):
            new[0] -= 1
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            new[0] += 1
        elif symbol in (arcade.key.UP, arcade.key.W):
            new[1] += 1
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            new[1] -= 1

        if self.player.strength <= 0:
            print("Player has no strength left to move.")
            return
        self.player.set_location(tuple(new))


# ===============================================================
# Start this file
# ===============================================================
def main():
    """Main entry point for the game."""
    window = Game()
    arcade.run()


if __name__ == "__main__":
    main()
