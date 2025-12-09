"""
AI system for game agents.
Provides vision (scanning environment) and brain (decision making) capabilities.
Works with Player class that uses 'location' attribute for position.
"""

from typing import Tuple, List, Dict, Optional, Any
from abc import ABC, abstractmethod


class Vision:
    """Scans nearby tiles for resources, hazards, and traders."""
    
    def __init__(self, world, player):
        self.world = world
        self.player = player
    
    def get_player_pos(self) -> Tuple[int, int]:
        """Get player position, checking both 'location' and 'pos' attributes."""
        if hasattr(self.player, 'location'):
            return self.player.location
        return getattr(self.player, 'pos', (0, 0))
    
    def scan_area(self, radius: int = 5) -> Dict[str, Any]:
        """
        Scan tiles within radius for important features.
        
        Returns dict with:
        - resources: list of (pos, type, distance) for food/water
        - hazards: list of (pos, type, distance) for dangerous terrain
        - traders: list of (pos, trader, distance)
        - safe_tiles: list of (pos, cost, distance) for movement
        """
        x, y = self.get_player_pos()
        
        resources = []
        hazards = []
        traders = []
        safe_tiles = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if not (0 <= nx < self.world.width and 0 <= ny < self.world.height):
                    continue
                
                distance = abs(dx) + abs(dy)  # Manhattan distance
                pos = (nx, ny)
                
                # Check for items (food/water)
                if hasattr(self.world, 'items') and pos in self.world.items:
                    item = self.world.items[pos]
                    resources.append((pos, item.get('type', 'unknown'), distance))
                
                # Check for traders
                if hasattr(self.world, 'traders'):
                    for trader in self.world.traders:
                        trader_pos = trader.location if hasattr(trader, 'location') else trader.pos
                        is_alive = getattr(trader, 'alive', True)
                        if trader_pos == pos and is_alive:
                            traders.append((pos, trader, distance))
                
                # Analyze terrain
                if hasattr(self.world, 'get_movement_cost'):
                    move_cost = self.world.get_movement_cost(nx, ny)
                    
                    # Hazards (high cost terrain)
                    if move_cost > 3:
                        terrain = self.world.get_tile(nx, ny) if hasattr(self.world, 'get_tile') else 'unknown'
                        hazards.append((pos, terrain, distance))
                    elif move_cost < float('inf'):
                        safe_tiles.append((pos, move_cost, distance))
        
        return {
            'resources': sorted(resources, key=lambda x: x[2]),
            'hazards': sorted(hazards, key=lambda x: x[2]),
            'traders': sorted(traders, key=lambda x: x[2]),
            'safe_tiles': sorted(safe_tiles, key=lambda x: x[2])
        }
    
    def find_nearest(self, target_type: str, scan_data: Dict = None) -> Optional[Tuple[int, int]]:
        """Find nearest target of given type (food, water, trader)."""
        if scan_data is None:
            scan_data = self.scan_area()
        
        if target_type in ['food', 'water']:
            for pos, item_type, dist in scan_data['resources']:
                if item_type == target_type:
                    return pos
        elif target_type == 'trader':
            if scan_data['traders']:
                return scan_data['traders'][0][0]
        
        return None
    
    def assess_danger(self, pos: Tuple[int, int]) -> float:
        """
        Assess danger level at position (0.0 = safe, 1.0 = deadly).
        Based on terrain cost and distance to hazards.
        """
        x, y = pos
        if hasattr(self.world, 'get_movement_cost'):
            terrain_cost = self.world.get_movement_cost(x, y)
            
            # Impassable is deadly
            if terrain_cost == float('inf'):
                return 1.0
            
            # High cost terrain is moderately dangerous
            danger = min(terrain_cost / 10.0, 0.8)
            return danger
        
        return 0.0


