import arcade
from typing import Optional

from world.map import World, TILE_SIZE
from actors.player import Player
from actors.trader import Trader


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Wilderness Survival"


class Game(arcade.Window):
    """Main Arcade window for the Wilderness Survival game."""

    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # The game world (grid of Terrain). Created in setup().
        self.world: Optional[World] = None
        self.player = None
        self.trader = None

        # Optional: set a background color behind the tiles
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self) -> None:
        """Create a new world instance. Call this before starting the game."""
        # Compute how many tiles fit in the window, based on TILE_SIZE.
        width_in_tiles = SCREEN_WIDTH // TILE_SIZE
        height_in_tiles = SCREEN_HEIGHT // TILE_SIZE

        #Creates a new world instance!
        self.world = World(width_in_tiles, height_in_tiles, difficulty="normal", tile_size=TILE_SIZE)
        self.player = Player("Player1", (0, 0))  # Example starting position
        self.trader = Trader("Trader1", (5, 5))  # Example starting position

    def on_draw(self) -> None:
        """Arcade draw handler – draws the world each frame."""
        #Clears the screen and draws the world
        self.clear()

        if self.world is not None:
            self.world.draw()
        if self.player is not None:
            self.player.draw()
        if self.trader is not None:
            self.trader.draw()


def main() -> None:
    """Entry point when running this module directly."""
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()


