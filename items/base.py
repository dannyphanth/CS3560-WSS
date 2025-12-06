from __future__ import annotations
from world.map import World, TILE_SIZE
import arcade 
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..actors.player import Player

@dataclass
class Item(ABC):
    def __init__(self, name, texture_path, tile_x, tile_y, amount=0):
        self.name = name
        self.amount = amount
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.sprite = arcade.Sprite(texture_path, scale=0.75)
        self.sprite.center_x = tile_x * TILE_SIZE + TILE_SIZE // 2 
        self.sprite.center_y = tile_y * TILE_SIZE + TILE_SIZE // 2

    @abstractmethod
    def apply(self, player: "Player") -> None:
        raise NotImplementedError

    def on_pickup(self, player: "Player") -> bool:
        self.apply(player)
        return True  # default: one-shot item

    
    def add_to_sprite_list(self, sprite_list):
        sprite_list.append(self.sprite)

    def draw(self):
        sprite_list = arcade.SpriteList()
        self.add_to_sprite_list(sprite_list)
        # print(f"The item location: {self.sprite.center_x},{self.sprite.center_y}")
        sprite_list.draw()


@dataclass
class RepeatingItem(Item):
    def __init__(self, name, texture_path, tile_x, tile_y, amount=0):
        super().__init__(
            name=name,
            texture_path=texture_path,
            tile_x=tile_x,
            tile_y=tile_y,
            amount=amount,
        )
        self.used_this_round = False # internal state if needed

    def on_pickup(self, player: "Player") -> bool:
        self.apply(player)
        self.times_used += 1
        return False  # stays on the map