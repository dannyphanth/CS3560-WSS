"""
AI system for game agents.
Provides vision (scanning environment) and brain (decision making) capabilities.
Works with Player class that uses 'location' attribute for position.
"""

import heapq
from typing import Dict, Any
import arcade
from world.map import TILE_SIZE


class Vision:
    
    def __init__(self, game, player, dx_dy_list: list = [(1, 0)]):
        self.game = game
        self.player = player
        self.dx_dy_list = dx_dy_list # dx dy from the current square to check


    def scan_area(self, radius: int = 1) -> Dict[str, Any]:
        """Scans nearby tiles for resources, and traders."""
        x = self.player.location[0]
        y = self.player.location[1]
        self.game.vision_squares.clear()

        water = []
        food = []
        moveCosts = []
        traders = []
        
        # render the vision squares 
        for new_tile in self.dx_dy_list:
            nx, ny = x + new_tile[0], y + new_tile[1]
            pos = (nx, ny)
            self.game.vision_squares.append(pos)

        for new_tile in self.dx_dy_list:
            nx, ny = x + new_tile[0], y + new_tile[1]
            distance = abs(new_tile[0]) + abs(new_tile[1])  # Manhattan distance
            pos = (nx, ny)

            # Check bounds
            if not (0 <= nx < self.game.world.width and 0 <= ny < self.game.world.height):
                continue
            
            # add the show the current square
            items = self.game.list_items_at_location(pos)
            # Check for items (food/water)
            for item in items: 
                if item.name == 'Food' or item.name == 'Food Fountain':
                    food.append((pos, item, distance))
                if item.name == 'Water':
                    water.append((pos, item, distance))

            # Check for move cost 
            move_cost = self.game.world.get_terrain(pos).move_cost
            moveCosts.append((pos, move_cost, distance))
            
            # traders
            for trader in self.game.traders: 
                if trader.location == pos: 
                    traders.append((pos, trader, distance))

        return {
            # sort by distance: 
            # that's why we use the x: x[2], because distance is the second index
            'water': sorted(water, key=lambda x: x[2]),
            'food': sorted(food, key=lambda x: x[2]),
            'moveCosts': sorted(moveCosts, key=lambda x: x[2]),
            'traders': sorted(traders, key=lambda x: x[2]),
        }    





class Focused(Vision): 
    def __init__(self, game, player, dx_dy_list: list = [(1, 1), (1, 0), (1, -1)]):
        self.game = game
        self.player = player
        self.dx_dy_list = dx_dy_list # dx dy from the current square to check



class CautiousVision(Vision): 
    def __init__(self, game, player, dx_dy_list: list = [(0, 1), (1, 0), (0, -1)]):
        self.game = game
        self.player = player
        self.dx_dy_list = dx_dy_list # dx dy from the current square to check



class KeenEyedVision(Vision): 
    def __init__(self, game, player, dx_dy_list: list = [(0, 1), (1, 0), (0, -1), (1, 1), (2, 0), (1, -1)]):
        self.game = game
        self.player = player
        self.dx_dy_list = dx_dy_list # dx dy from the current square to check



class FarSightVision(Vision): 
    def __init__(
        self, 
        game, 
        player, 
        dx_dy_list: list = [(0, 1), (1, 0), (0, -1), (1, 1), (2, 0), (1, -1), (0, 2), (1, 2), (2, 1), (0, -2), (1, -2), (2, -1)]):
        self.game = game
        self.player = player
        self.dx_dy_list = dx_dy_list # dx dy from the current square to check
