"""
AI system for game agents.
Provides vision (scanning environment) and brain (decision making) capabilities.
Works with Player class that uses 'location' attribute for position.
"""

import heapq
from typing import Dict, Any
import arcade




class Vision:
    """Scans nearby tiles for resources, hazards, and traders."""
    
    def __init__(self, game, player):
        self.game = game
        self.player = player


    def scan_area(self, radius: int = 1) -> Dict[str, Any]:
        x = self.player.location[0]
        y = self.player.location[1]
        
        water = []
        food = []
        moveCosts = []
        traders = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if not (0 <= nx < self.game.world.width and 0 <= ny < self.game.world.height):
                    continue
                
                distance = abs(dx) + abs(dy)  # Manhattan distance
                pos = (nx, ny)
                
                # Check for items (food/water)
                items = self.game.list_items_at_location(pos)
                for item in items: 
                    if item.name == 'Food' or item.name == 'Food Fountain':
                        food.append((pos, item, distance))
                    if item.name == 'Water':
                        water.append((pos, item, distance))

                # Check for move cost 
                move_cost = self.game.world.get_terrain(pos).move_cost
                moveCosts.append((pos, move_cost, distance))
                
                # TODO: ADD TRADER LOCATIONS
                # # Check for traders
                # if hasattr(self.game.world, 'traders'):
                #     for trader in self.game.world.traders:
                #         trader_pos = trader.location if hasattr(trader, 'location') else trader.pos
                #         is_alive = getattr(trader, 'alive', True)
                #         if trader_pos == pos and is_alive:
                #             traders.append((pos, trader, distance))
                
        
        return {
            # sort by distance -> that's why we use the x: x[2], because distance is the second index
            'water': sorted(water, key=lambda x: x[2]),
            'food': sorted(food, key=lambda x: x[2]),
            'moveCosts': sorted(moveCosts, key=lambda x: x[2]),
            'traders': sorted(traders, key=lambda x: x[2]),
        }    

        
