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

    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Game state: menu or playing 
        self.state = "menu"

        # Game objects
        self.world: Optional[World] = None
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
            inventory=Inventory(12, 12, 12, max_items=300),
            strength=1000,
        )

        # Place traders at random tiles not occupied by player
        self.traders = self.place_traders(width_in_tiles, height_in_tiles)

        # Items
        self.place_items(width_in_tiles, height_in_tiles, difficulty=difficulty)

        # Switch screen
        self.state = "playing"

    def on_draw(self) -> None:
        self.clear()
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
                self.items[0].sprite_list.draw()

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
            self.handle_game_input(symbol)

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

    def handle_game_input(self, symbol) -> None:
        if not self.player:
            return

        current = self.player.location
        new = list(current)
        moved = False

        if self.player.strength <= 0:
            print("Player has no strength left to move.")
            return

        if symbol in (arcade.key.LEFT, arcade.key.A):
            new[0] -= 1
            moved = True
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            new[0] += 1
            moved = True
        elif symbol in (arcade.key.UP, arcade.key.W):
            new[1] += 1
            moved = True
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            new[1] -= 1
            moved = True

        if moved and self.traders:
            if any(tuple(new) == t.location for t in self.traders):
                print("Movement denied: cannot move onto trader.")
                return

        if moved:
            self.player.set_location(tuple(new))
            for trader in self.traders:
                self.player.is_at_trader_location(trader)
            self.player.is_at_item_location(self.items)

    def place_items(self, width_in_tiles, height_in_tiles, difficulty="normal"):
        self.items.clear()

        area = width_in_tiles * height_in_tiles

        if difficulty == "easy":
            item_count = max(area // 6, 15)
        elif difficulty == "hard":
            item_count = max(area // 12, 10)
        else:
            item_count = max(area // 8, 12)

        for _ in range(item_count):
            item_class = random.choice(ITEM_TYPES)

            while True:
                x = random.randint(0, width_in_tiles - 1)
                y = random.randint(0, height_in_tiles - 1)
                loc = (x, y)

                if (not any(existing.location == loc and isinstance(existing, item_class)
                            for existing in self.items)
                    and loc != self.player.location
                    and all(trader.location != loc for trader in self.traders)):
                    break

            item = item_class((x, y))
            self.items.append(item)

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


def main() -> None:
    window = Game()
    arcade.run()


if __name__ == "__main__":
    main()
