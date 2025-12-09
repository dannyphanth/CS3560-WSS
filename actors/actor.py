from dataclasses import dataclass

import arcade
import random
from systems.inventory import Inventory
from world.map import TILE_SIZE

# Player can propose tradeOffer to Trader actors


@dataclass(eq=False)
class Actor:
    # Initialize player with name and location (left/bottommost cell)
    def __init__(self, name, texture_path, location = (0,0), inventory=Inventory(gold=1, food=1, water=1, max_items=1)):
        self.name = name
        self.location = location  # (x, y) tuple
        self.inventory = inventory

        self.sprite = arcade.Sprite(texture_path, scale = 0.03)  # Load player sprite
        self.sprite.center_x = location[0] * TILE_SIZE + TILE_SIZE // 2
        self.sprite.center_y = location[1] * TILE_SIZE + TILE_SIZE // 2


    def printStats(self): 
        print(f"Gold\tFood\tWater\tMax Items")
        print(f"{self.inventory.gold}\t{self.inventory.food}\t{self.inventory.water}\t{self.inventory.max_items}")
        

    def add_to_sprite_list(self, sprite_list):
        sprite_list.append(self.sprite)


    def draw(self):
        sprite_list = arcade.SpriteList()
        self.add_to_sprite_list(sprite_list)
        sprite_list.draw()


    def random_resource(self): 
        return self.inventory.random_resource()


    def update_inventory_after_trade(self, item_given, quantity_given, item_requested, quantity_requested):
        # update actor's inventory after trade
        self.inventory.spend(item_given, quantity_given)
        self.inventory.add(item_requested, quantity_requested)
        print(f"Updated {self.name}")
        print(f"Inventory: ", end='')
        self.inventory.show_inventory()