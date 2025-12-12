'''
Docstring for items.base



It's important that we have (eq=False) after the @dataclass because this ensures
that the instances are compared based off UNIQUE identifiers such as id(). Instead 
of comparing instances off of equality (like "do two instances have the same name")
'''

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from items.base import *

if TYPE_CHECKING:
    from ..actors.player import Player


# ---------- One-time bonuses ----------



@dataclass(eq=False)
class FoodBonus(Item):
    def __init__(self, location, amount=10):
        super().__init__(
            name="Food",
            texture_path="assets/food.png",
            location=tuple(location),
            amount=amount
        )

    def apply(self, player: "Player", thisItem: Item) -> None:
        self.sprite.kill() # this kills the sprite in every arcade.sprite_list
        player.game.items.remove(thisItem)
        player.inventory.food = min(player.inventory.max_items, player.inventory.food + self.amount)




@dataclass(eq=False)
class WaterBonus(Item):
    def __init__(self, location, amount=10):
        super().__init__(
            name="Water",
            texture_path="assets/water.png",
            location=tuple(location),
            amount=amount
        )

    def apply(self, player: "Player", thisItem: Item) -> None:
        self.sprite.kill() # this kills the sprite in every arcade.sprite_list
        player.game.items.remove(thisItem)
        player.inventory.water = min(player.inventory.max_items, player.inventory.water + self.amount)




@dataclass(eq=False)
class GoldBonus(Item):
    def __init__(self, location, amount=1):
        super().__init__(
            name="Gold",
            texture_path="assets/gold.png",
            location=tuple(location),
            amount=amount
        )

    def apply(self, player: "Player", thisItem: Item) -> None:
        self.sprite.kill() # this kills the sprite in every arcade.sprite_list
        player.game.items.remove(thisItem)
        player.inventory.gold = min(player.inventory.max_items, player.inventory.gold + self.amount)




@dataclass(eq=False)
class RepeatingFoodFountain(RepeatingItem):
    def __init__(self, location, amount=2):
        super().__init__(
            name="Food Fountain",
            texture_path="assets/byson.png",
            location=tuple(location),
            amount=amount
        )

    def apply(self, player: "Player", thisItem: Item) -> None:
        player.inventory.food = min(player.inventory.max_items, player.inventory.food + self.amount)
