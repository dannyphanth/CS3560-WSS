import random
from typing import List, Tuple
import arcade
from .terrain import Terrain, PLAINS, FOREST, MOUNTAIN, DESERT, WATER



TILE_SIZE = 32  # pixels per tile


class World:
    """
    The game world: a grid of Terrain cells.

    - width, height: size in tiles (grid cells)
    - difficulty: affects how terrain is distributed
    """

    def __init__(self, width: int, height: int, difficulty: str = "hard", tile_size: int = TILE_SIZE):
        self.width = width
        self.height = height
        self.difficulty = difficulty.lower()
        self.tile_size = tile_size

        #2D grid: grid[y][x] holds instances of the Terrain object
        self.grid = []  # type: List[List[Terrain]]

        #Calls helper method to fill the grid
        self._generate_terrain()

    # ------------------------------------------------------------------
    # Map generation
    # ------------------------------------------------------------------

    def _generate_terrain(self) -> None:
        """
        Fill the grid with terrain based on difficulty.
        Can adjust this later to match further feature implementations
        """
        terrains = [PLAINS, FOREST, MOUNTAIN, DESERT, WATER]
        weights = self._terrain_weights_for_difficulty(self.difficulty)

        self.grid = []
        for y in range(self.height):
            row: List[Terrain] = []
            for x in range(self.width):
                # choose a terrain according to difficulty weights
                terrain = random.choices(terrains, weights=weights, k=1)[0]
                row.append(terrain)
            self.grid.append(row)


    def _terrain_weights_for_difficulty(self, difficulty: str) -> List[float]:
        """
        Decide how common each terrain type is, based on difficulty.
        Return order: [PLAINS, FOREST, MOUNTAIN, DESERT, WATER]
        """
        if difficulty == "easy":
            # mostly safe, mostly plains
            return [0.6, 0.2, 0.05, 0.05, 0.10]
        elif difficulty == "hard":
            # more mountains and desert
            return [0.2, 0.2, 0.25, 0.25, 0.10]
        else:  # "normal" or anything else
            return [0.4, 0.2, 0.15, 0.15, 0.10]


    # ------------------------------------------------------------------
    # Basic helpers
    # ------------------------------------------------------------------

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is inside the world grid."""
        return 0 <= x < self.width and 0 <= y < self.height


    def get_terrain(self, x: int, y: int) -> Terrain:
        """Return the Terrain at grid cell (x, y)."""
        if not self.in_bounds(x, y):
            raise IndexError(f"Cell ({x}, {y}) is outside the world.")
        return self.grid[y][x]


    def spawn_point(self) -> Tuple[int, int]:
        """
        Starting cell for the player.
        For now: west edge (x = 0), vertical middle.
        """
        x = 0
        y = self.height // 2
        return x, y


    def is_east_edge(self, x: int, y: int) -> bool:
        """Return True if (x, y) is on the east edge of the map."""
        return self.in_bounds(x, y) and x == self.width - 1


    def neighbors8(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Return all 8 neighbors (including diagonals) that are inside the map.
        Useful later for Vision and pathfinding.
        """
        result: List[Tuple[int, int]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if self.in_bounds(nx, ny):
                    result.append((nx, ny))
        return result


    # ------------------------------------------------------------------
    # Drawing with Arcade
    # ------------------------------------------------------------------

    def draw(self) -> None:
        """
        Draw the world as colored rectangles.
        Later you can replace this with sprites/tilesheets.
        """
        for y in range(self.height):
            for x in range(self.width):
                terrain = self.grid[y][x]

                left = x * self.tile_size
                right = left + self.tile_size
                bottom = y * self.tile_size
                top = bottom + self.tile_size

                # Some versions of Arcade expose draw_lrbt_rectangle_filled
                # (left, right, bottom, top, color) instead of lrtb.
                arcade.draw_lrbt_rectangle_filled(
                    left,
                    right,
                    bottom,
                    top,
                    terrain.color,
                )
