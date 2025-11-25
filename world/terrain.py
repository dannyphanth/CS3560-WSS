# world/terrain.py

from dataclasses import dataclass #Auto-generates boilerplate methods (init, repr, etc.)
from typing import Tuple #Tuple is a sequence of a fixed number of elements, similar to a list but immutable

Color = Tuple[int, int, int] #Tuple of 3 integers representing RGB values

#The Terrain dataclass
@dataclass(frozen=True) #frozen=True makes instances immutable
class Terrain:
    """
    Terrain type for a single map cell.

    Costs are applied when the player ENTERS the cell:
    - move_cost: strength/energy cost
    - water_cost: water cost
    - food_cost: food cost
    """
    name: str
    move_cost: int
    water_cost: int
    food_cost: int
    color: Color  #Used for drawing with Arcade


# ---- Concrete terrain types ----
PLAINS = Terrain(
    name="Plains",
    move_cost=1,
    water_cost=1,
    food_cost=1,
    color=(80, 170, 80),
)

FOREST = Terrain(
    name="Forest",
    move_cost=2,
    water_cost=1,
    food_cost=2,
    color=(34, 139, 34),
)

MOUNTAIN = Terrain(
    name="Mountain",
    move_cost=3,
    water_cost=2,
    food_cost=2,
    color=(120, 120, 120),
)

DESERT = Terrain(
    name="Desert",
    move_cost=2,
    water_cost=3,
    food_cost=3,
    color=(218, 165, 32),
)

WATER = Terrain(
    name="Water",
    move_cost=1,
    water_cost=0,   #No water cost to stand near water
    food_cost=1,
    color=(65, 105, 225),
)

ALL_TERRAINS = [PLAINS, FOREST, MOUNTAIN, DESERT, WATER]
