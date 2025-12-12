'''
items.base
It's important that we have (eq=False) after the @dataclass because this ensures
that the instances are compared based off UNIQUE identifiers such as id(). Instead 
of comparing instances off of equality (like "do two instances have the same name")
'''

from __future__ import annotations
from world.map import World, TILE_SIZE
import arcade 
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..actors.player import Player

@dataclass(eq=False)
class Item(ABC):
    # Class-level shared sprite list
    sprite_list = arcade.SpriteList()

    def __init__(self, name, texture_path, location, amount=0):
        self.name = name
        self.sprite = arcade.Sprite(texture_path, scale=0.75)
        self.amount = amount
        self.location = location # (x, y) tuple
        self.sprite.center_x = location[0] * TILE_SIZE + TILE_SIZE // 2 
        self.sprite.center_y = location[1] * TILE_SIZE + TILE_SIZE // 2
        self.sprite_list.append(self.sprite)
        
    @abstractmethod
    def apply(self, player: "Player", thisItem: Item) -> None:
        raise NotImplementedError


@dataclass(eq=False)
class RepeatingItem(Item):
    def __init__(self, name, texture_path, location, amount=0):
        super().__init__(
            name=name,
            texture_path=texture_path,
            location=location,
            amount=amount,
        )
        self.used_this_round = False # internal state if needed

    @abstractmethod
    def apply(self, player: "Player") -> None:
        raise NotImplementedError