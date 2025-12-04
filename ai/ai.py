"""
AI system for game agents.
Provides vision (scanning environment) and brain (decision making) capabilities.
"""

from typing import Tuple, List, Dict, Optional, Any
from abc import ABC, abstractmethod
import math

#-- Vision System --
class Vision:
    """Scans nearby tiles for resources, hazards, and traders."""
    
    def __init__(self, world, actor):
        self.world = world
        self.actor = actor
    
    #locates closest resources, hazards, traders, safe tiles
    def scan_area(self, radius: int = 5) -> Dict[str, Any]:
        """
        Scan tiles within radius for important features.
        
        Returns dict with:
        - resources: list of (pos, type, distance) for food/water
        - hazards: list of (pos, type, distance) for dangerous terrain
        - traders: list of (pos, trader, distance)
        - safe_tiles: list of (pos, cost, distance) for movement
        """
        x, y = self.actor.pos
        
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
                if pos in self.world.items:
                    item = self.world.items[pos]
                    resources.append((pos, item['type'], distance))
                
                # Check for traders
                for trader in self.world.traders:
                    if trader.pos == pos and trader.alive:
                        traders.append((pos, trader, distance))
                
                # Analyze terrain
                terrain = self.world.get_tile(nx, ny)
                move_cost = self.world.get_movement_cost(nx, ny)
                
                # Hazards (high cost terrain)
                if move_cost > 3:
                    hazards.append((pos, terrain, distance))
                elif move_cost < float('inf'):
                    safe_tiles.append((pos, move_cost, distance))
        
        return {
            'resources': sorted(resources, key=lambda x: x[2]),
            'hazards': sorted(hazards, key=lambda x: x[2]),
            'traders': sorted(traders, key=lambda x: x[2]),
            'safe_tiles': sorted(safe_tiles, key=lambda x: x[2])
        }
    
    #locates nearest target of specified type
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
    
    #evaulates danger at a position
    def assess_danger(self, pos: Tuple[int, int]) -> float:
        """
        Assess danger level at position (0.0 = safe, 1.0 = deadly).
        Based on terrain cost and distance to hazards.
        """
        x, y = pos
        terrain_cost = self.world.get_movement_cost(x, y)
        
        # Impassable is deadly
        if terrain_cost == float('inf'):
            return 1.0
        
        # High cost terrain is moderately dangerous
        danger = min(terrain_cost / 10.0, 0.8)
        
        return danger


#-- Brain System --
class Brain(ABC):
    """
    Abstract base class for AI decision-making.
    Subclass to create different play styles.
    """
    
    def __init__(self, actor, world):
        self.actor = actor
        self.world = world
        self.vision = Vision(world, actor)
    
    #must be implemented by subclasses
    @abstractmethod
    def decide_action(self) -> Dict[str, Any]:
        """
        Decide next action based on current state.
        
        Returns dict with:
        - action: 'move', 'rest', 'trade', or 'wait'
        - params: dict of action-specific parameters
        """
        pass
    
    #calculates urgency of needs
    def _assess_needs(self) -> Dict[str, float]:
        """Assess urgency of needs (0.0 = satisfied, 1.0 = critical)."""
        return {
            'health': 1.0 - (self.actor.health / self.actor.max_health),
            'food': 1.0 - (self.actor.food / self.actor.max_food),
            'water': 1.0 - (self.actor.water / self.actor.max_water)
        }
    
    #simple pathfinding to target
    def _find_path_to(self, target: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Find next move toward target using simple pathfinding."""
        x, y = self.actor.pos
        tx, ty = target
        
        # Try moving toward target
        dx = 1 if tx > x else (-1 if tx < x else 0)
        dy = 1 if ty > y else (-1 if ty < y else 0)
        
        # Try diagonal first
        if dx != 0 and dy != 0:
            if self.world.get_movement_cost(x + dx, y + dy) < float('inf'):
                return (x + dx, y + dy)
        
        # Try horizontal
        if dx != 0 and self.world.get_movement_cost(x + dx, y) < float('inf'):
            return (x + dx, y)
        
        # Try vertical
        if dy != 0 and self.world.get_movement_cost(x, y + dy) < float('inf'):
            return (x, y + dy)
        
        return None

#Play style implementations ----

#-- Cautious Brain --
#prioritizes safety and resource management
#rest when health is low
#only explore safe tiles
class CautiousBrain(Brain):
    """Conservative play style: prioritizes safety and resource management."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area()
        
        # Critical health - rest is priority
        if needs['health'] > 0.7:
            return {'action': 'rest', 'params': {}}
        
        # Urgent water need (more critical than food)
        if needs['water'] > 0.6:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                if water_pos == self.actor.pos:
                    return {'action': 'collect', 'params': {'type': 'water'}}
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Urgent food need
        if needs['food'] > 0.6:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                if food_pos == self.actor.pos:
                    return {'action': 'collect', 'params': {'type': 'food'}}
                next_pos = self._find_path_to(food_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Moderate needs - seek resources proactively
        if needs['water'] > 0.3:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.3:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                next_pos = self._find_path_to(food_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Rest if low on resources
        if needs['health'] > 0.3:
            return {'action': 'rest', 'params': {}}
        
        # Explore safely
        if scan['safe_tiles']:
            target = scan['safe_tiles'][0][0]
            next_pos = self._find_path_to(target)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        return {'action': 'wait', 'params': {}}


#-- Aggressive Brain --
#larger vision radius
#seeks traders and valuable resources
#willing to take risks
#rest only when critically low
class AggressiveBrain(Brain):
    """Aggressive play style: takes risks, seeks traders and valuable resources."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=7)  # Larger vision
        
        # Only rest if critically low
        if needs['health'] > 0.85:
            return {'action': 'rest', 'params': {}}
        
        # Seek traders for potential advantage
        if scan['traders'] and max(needs.values()) < 0.7:
            trader_pos = scan['traders'][0][0]
            if trader_pos == self.actor.pos:
                return {'action': 'trade', 'params': {'trader': scan['traders'][0][1]}}
            next_pos = self._find_path_to(trader_pos)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Get resources when needed
        if needs['water'] > 0.5:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                if water_pos == self.actor.pos:
                    return {'action': 'collect', 'params': {'type': 'water'}}
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.5:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                if food_pos == self.actor.pos:
                    return {'action': 'collect', 'params': {'type': 'food'}}
                next_pos = self._find_path_to(food_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Aggressively explore even risky terrain
        if scan['resources']:
            target = scan['resources'][0][0]
            next_pos = self._find_path_to(target)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Keep moving
        if scan['safe_tiles']:
            # Pick tiles further away
            target = scan['safe_tiles'][len(scan['safe_tiles'])//2][0]
            next_pos = self._find_path_to(target)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        return {'action': 'wait', 'params': {}}

#-- Balanced Brain --
#weighs all factors reasonably
#maintains resource buffer
class BalancedBrain(Brain):
    """Balanced play style: weighs all factors reasonably."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=6)
        
        # Rest when health is concerning
        if needs['health'] > 0.6:
            return {'action': 'rest', 'params': {}}
        
        # Handle critical needs first
        max_need = max(needs.values())
        if max_need > 0.65:
            if needs['water'] == max_need:
                water_pos = self.vision.find_nearest('water', scan)
                if water_pos:
                    if water_pos == self.actor.pos:
                        return {'action': 'collect', 'params': {'type': 'water'}}
                    next_pos = self._find_path_to(water_pos)
                    if next_pos:
                        return {'action': 'move', 'params': {'pos': next_pos}}
            elif needs['food'] == max_need:
                food_pos = self.vision.find_nearest('food', scan)
                if food_pos:
                    if food_pos == self.actor.pos:
                        return {'action': 'collect', 'params': {'type': 'food'}}
                    next_pos = self._find_path_to(food_pos)
                    if next_pos:
                        return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Consider trading when in moderate condition
        if scan['traders'] and max_need < 0.5:
            trader_pos = scan['traders'][0][0]
            if trader_pos == self.actor.pos:
                return {'action': 'trade', 'params': {'trader': scan['traders'][0][1]}}
            # Only go to trader if close
            if scan['traders'][0][2] <= 3:
                next_pos = self._find_path_to(trader_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Proactively seek resources
        if needs['water'] > 0.35:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.35:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                next_pos = self._find_path_to(food_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Explore nearest safe areas
        if scan['resources']:
            target = scan['resources'][0][0]
            next_pos = self._find_path_to(target)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        if scan['safe_tiles']:
            target = scan['safe_tiles'][0][0]
            next_pos = self._find_path_to(target)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        return {'action': 'rest', 'params': {}}

#-- Opportunist Brain --
#seeks traders and high-value resources
#larger vision radius
#prioritizes action over safety
#aggressively explores
class OpportunistBrain(Brain):
    """Opportunistic play style: seeks traders and high-value resources."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=8)
        
        # Only handle truly critical situations
        if needs['health'] > 0.8:
            return {'action': 'rest', 'params': {}}
        
        if needs['water'] > 0.75:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                if water_pos == self.actor.pos:
                    return {'action': 'collect', 'params': {'type': 'water'}}
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.75:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                if food_pos == self.actor.pos:
                    return {'action': 'collect', 'params': {'type': 'food'}}
                next_pos = self._find_path_to(food_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Prioritize traders
        if scan['traders']:
            trader_pos = scan['traders'][0][0]
            if trader_pos == self.actor.pos:
                return {'action': 'trade', 'params': {'trader': scan['traders'][0][1]}}
            next_pos = self._find_path_to(trader_pos)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Seek any resources opportunistically
        if scan['resources']:
            target = scan['resources'][0][0]
            if target == self.actor.pos:
                item_type = scan['resources'][0][1]
                return {'action': 'collect', 'params': {'type': item_type}}
            next_pos = self._find_path_to(target)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Explore aggressively
        if scan['safe_tiles']:
            # Prefer distant tiles
            target = scan['safe_tiles'][-1][0]
            next_pos = self._find_path_to(target)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        return {'action': 'wait', 'params': {}}