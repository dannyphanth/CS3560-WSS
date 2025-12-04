import arcade
from typing import Optional

from actors.player import Player
from actors.trader import Trader

from world.map import World, TILE_SIZE

from ai.ai import CautiousBrain, AggressiveBrain, BalancedBrain, OpportunistBrain

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Wilderness Survival"


class Game(arcade.Window):
    """Main Arcade window for the Wilderness Survival game."""

    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # The game world (grid of Terrain). Created in setup().
        self.world: Optional[World] = None
        
        # AI-controlled player
        self.ai_player: Optional[Player] = None

        # Optional: set a background color behind the tiles
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self) -> None:
        """Create a new world instance. Call this before starting the game."""
        # Compute how many tiles fit in the window, based on TILE_SIZE.
        width_in_tiles = SCREEN_WIDTH // TILE_SIZE
        height_in_tiles = SCREEN_HEIGHT // TILE_SIZE

        # Creates a new world instance!
        self.world = World(width_in_tiles, height_in_tiles, difficulty="normal", tile_size=TILE_SIZE)
        
        # Now that world exists, spawn AI player
        spawn_pos = (5, 5)
        self.ai_player = Player(name="AI Player", location=spawn_pos)
        
        # Attach AI brain to the player
        self.ai_player.brain = BalancedBrain(self.ai_player, self.world)

    def on_draw(self) -> None:
        """Arcade draw handler – draws the world each frame."""
        # Clears the screen and draws the world
        self.clear()

        if self.world is not None:
            self.world.draw()
            
            # Draw the AI player (uses its own sprite)
            if self.ai_player is not None:
                self.ai_player.draw()

    def on_update(self, delta_time: float):
        """Called every frame to update game state."""
        if self.world is None or self.ai_player is None:
            return
        
        # AI decides what to do
        action = self.ai_player.brain.decide_action()
        
        # Execute chosen action
        # You'll need to implement this based on your systems.py
        # Example:
        if action['action'] == 'move':
            new_pos = action['params']['pos']
            self.ai_player.location = new_pos
            # Update sprite position
            self.ai_player.sprite.center_x = new_pos[0] * TILE_SIZE + TILE_SIZE // 2
            self.ai_player.sprite.center_y = new_pos[1] * TILE_SIZE + TILE_SIZE // 2
            # Apply movement costs (food/water/health changes)
            # self.world.apply_movement_cost(self.ai_player, new_pos)
            
        elif action['action'] == 'rest':
            # Restore some health
            # self.ai_player.health = min(self.ai_player.health + 10, self.ai_player.max_health)
            pass
            
        elif action['action'] == 'collect':
            item_type = action['params']['type']
            if self.ai_player.pos in self.world.items:
                # Collect the item
                # self.world.collect_item(self.ai_player.pos, self.ai_player)
                pass
                
        elif action['action'] == 'trade':
            trader = action['params']['trader']
            # Initiate trade
            # trader.negotiate(self.ai_player)
            pass


def main():
    """Main entry point for the game."""
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()