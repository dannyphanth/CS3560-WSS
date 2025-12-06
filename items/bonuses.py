from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import Item, RepeatingItem

if TYPE_CHECKING:
    from ..actors.player import Player

# ---------- One-time bonuses ----------

@dataclass
class FoodBonus(Item):
    def __init__(self, tile_x, tile_y, amount=10):
        super().__init__(
            name="Food Bonus",
            texture_path="assets/food.png",
            tile_x=tile_x,
            tile_y=tile_y,
            amount=amount
        )

    def apply(self, player: "Player") -> None:
        player.food = min(player.max_food, player.food + self.amount)

@dataclass
class WaterBonus(Item):
    def __init__(self, tile_x, tile_y, amount=10):
        super().__init__(
            name="Water Bonus",
            texture_path="assets/water.png",
            tile_x=tile_x,
            tile_y=tile_y,
            amount=amount
        )

    def apply(self, player: "Player") -> None:
        player.water = min(player.max_water, player.water + self.amount)

@dataclass
class GoldBonus(Item):
    def __init__(self, tile_x, tile_y, amount=1):
        super().__init__(
            name="Gold Bonus",
            texture_path="assets/gold.png",
            tile_x=tile_x,
            tile_y=tile_y,
            amount=amount
        )

    def apply(self, player: "Player") -> None:
        player.gold += self.amount

@dataclass
class RepeatingFoodFountain(RepeatingItem):
    def __init__(self, tile_x, tile_y, amount=2):
        super().__init__(
            name="Food Fountain",
            texture_path="assets/byson.png",
            tile_x=tile_x,
            tile_y=tile_y,
            amount=amount
        )

    def apply(self, player: "Player") -> None:
        player.food = min(player.max_food, player.food + self.amount)
