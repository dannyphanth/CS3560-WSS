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

        # Preserve existing inventories if setup is called again
        player_inventory = self.player.inventory if self.player else None
        trader_inventory = self.trader.inventory if self.trader else None

        self.player = Player("Player1", 100, (0, 0), inventory=player_inventory)  # Example starting position
        self.trader = Trader("Trader1", (5, 5), inventory=trader_inventory if trader_inventory else None)  # Example starting position

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
                self.player.is_at_same_location(self.trader)
                
        else:
            print("Player has no strength left to move.")

def main() -> None:
    """Entry point when running this module directly."""
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()


