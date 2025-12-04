from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import Item, RepeatingItem

if TYPE_CHECKING:
    from ..actors.player import Player

# ---------- One-time bonuses ----------

@dataclass
class FoodBonus(Item):
    amount: int = 10

    def __init__(self, amount: int = 10):
        super().__init__(name="Food Bonus", symbol="F")
        self.amount = amount

    def apply(self, player: "Player") -> None:
        player.food = min(player.max_food, player.food + self.amount)

@dataclass
class WaterBonus(Item):
    amount: int = 10

    def __init__(self, amount: int = 10):
        super().__init__(name="Water Bonus", symbol="W")
        self.amount = amount

    def apply(self, player: "Player") -> None:
        player.water = min(player.max_water, player.water + self.amount)

@dataclass
class GoldBonus(Item):
    amount: int = 1

    def __init__(self, amount: int = 1):
        super().__init__(name="Gold", symbol="G")
        self.amount = amount

    def apply(self, player: "Player") -> None:
        player.gold += self.amount

@dataclass
class RepeatingFoodFountain(RepeatingItem):
    amount: int = 2

    def __init__(self, amount: int = 2):
        super().__init__(name="Food Fountain", symbol="f")
        self.amount = amount

    def apply(self, player: "Player") -> None:
        player.food = min(player.max_food, player.food + self.amount)
