from typing import Tuple, List, Dict, Optional, Any
from abc import ABC, abstractmethod
from ai.vision import *
import random

class Brain(ABC):
    """
    Abstract base class for AI decision-making.
    Subclass to create different play styles.
    """
    
    def __init__(self):
        print('defined')
        # self.vision = Vision()
    

    def make_move(self, player, trader): 
        if player:
            cur_loc = player.location

        if (random.randrange(0,2)):
            # standing still 
            player.strength += 1
            return False

        new_loc = (cur_loc[0] + 1, cur_loc[1] + 0)

        if player and player.strength > 0:
            player.set_location(new_loc)
            return True
        else:
            print("Player has no strength left to move.")
            return False
        

    @abstractmethod
    def decide_action(self) -> Dict[str, Any]:
        """
        Decide next action based on current state.
        
        Returns dict with:
        - action: 'move', 'rest', 'trade', or 'wait'
        - params: dict of action-specific parameters
        """
        pass
    
    def _assess_needs(self) -> Dict[str, float]:
        """Assess urgency of needs (0.0 = satisfied, 1.0 = critical)."""
        # Access Player attributes - provide defaults if not present
        health = getattr(self.player, 'health', 100)
        max_health = getattr(self.player, 'max_health', 100)
        food = getattr(self.player, 'food', 100)
        max_food = getattr(self.player, 'max_food', 100)
        water = getattr(self.player, 'water', 100)
        max_water = getattr(self.player, 'max_water', 100)
        
        return {
            'health': 1.0 - (health / max_health) if max_health > 0 else 0.0,
            'food': 1.0 - (food / max_food) if max_food > 0 else 0.0,
            'water': 1.0 - (water / max_water) if max_water > 0 else 0.0
        }
    
    def _find_path_to(self, target: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Find next move toward target using simple pathfinding."""
        x, y = self.vision.get_player_pos()
        tx, ty = target
        
        # Try moving toward target
        dx = 1 if tx > x else (-1 if tx < x else 0)
        dy = 1 if ty > y else (-1 if ty < y else 0)
        
        if not hasattr(self.world, 'get_movement_cost'):
            return target  # No pathfinding possible
        
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


class CautiousBrain(Brain):
    """Conservative play style: prioritizes safety and resource management."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area()
        player_pos = self.vision.get_player_pos()
        
        # Critical health - rest is priority
        if needs['health'] > 0.7:
            return {'action': 'rest', 'params': {}}
        
        # Urgent water need (more critical than food)
        if needs['water'] > 0.6:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                if water_pos == player_pos:
                    return {'action': 'collect', 'params': {'type': 'water'}}
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Urgent food need
        if needs['food'] > 0.6:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                if food_pos == player_pos:
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


class AggressiveBrain(Brain):
    """Aggressive play style: takes risks, seeks traders and valuable resources."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=7)  # Larger vision
        player_pos = self.vision.get_player_pos()
        
        # Only rest if critically low
        if needs['health'] > 0.85:
            return {'action': 'rest', 'params': {}}
        
        # Seek traders for potential advantage
        if scan['traders'] and max(needs.values()) < 0.7:
            trader_pos = scan['traders'][0][0]
            if trader_pos == player_pos:
                return {'action': 'trade', 'params': {'trader': scan['traders'][0][1]}}
            next_pos = self._find_path_to(trader_pos)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Get resources when needed
        if needs['water'] > 0.5:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                if water_pos == player_pos:
                    return {'action': 'collect', 'params': {'type': 'water'}}
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.5:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                if food_pos == player_pos:
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


class BalancedBrain(Brain):
    """Balanced play style: weighs all factors reasonably."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=6)
        player_pos = self.vision.get_player_pos()
        
        # Rest when health is concerning
        if needs['health'] > 0.6:
            return {'action': 'rest', 'params': {}}
        
        # Handle critical needs first
        max_need = max(needs.values())
        if max_need > 0.65:
            if needs['water'] == max_need:
                water_pos = self.vision.find_nearest('water', scan)
                if water_pos:
                    if water_pos == player_pos:
                        return {'action': 'collect', 'params': {'type': 'water'}}
                    next_pos = self._find_path_to(water_pos)
                    if next_pos:
                        return {'action': 'move', 'params': {'pos': next_pos}}
            elif needs['food'] == max_need:
                food_pos = self.vision.find_nearest('food', scan)
                if food_pos:
                    if food_pos == player_pos:
                        return {'action': 'collect', 'params': {'type': 'food'}}
                    next_pos = self._find_path_to(food_pos)
                    if next_pos:
                        return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Consider trading when in moderate condition
        if scan['traders'] and max_need < 0.5:
            trader_pos = scan['traders'][0][0]
            if trader_pos == player_pos:
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


class OpportunistBrain(Brain):
    """Opportunistic play style: seeks traders and high-value resources."""
    
    def decide_action(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=8)
        player_pos = self.vision.get_player_pos()
        
        # Only handle truly critical situations
        if needs['health'] > 0.8:
            return {'action': 'rest', 'params': {}}
        
        if needs['water'] > 0.75:
            water_pos = self.vision.find_nearest('water', scan)
            if water_pos:
                if water_pos == player_pos:
                    return {'action': 'collect', 'params': {'type': 'water'}}
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.75:
            food_pos = self.vision.find_nearest('food', scan)
            if food_pos:
                if food_pos == player_pos:
                    return {'action': 'collect', 'params': {'type': 'food'}}
                next_pos = self._find_path_to(food_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Prioritize traders
        if scan['traders']:
            trader_pos = scan['traders'][0][0]
            if trader_pos == player_pos:
                return {'action': 'trade', 'params': {'trader': scan['traders'][0][1]}}
            next_pos = self._find_path_to(trader_pos)
            if next_pos:
                return {'action': 'move', 'params': {'pos': next_pos}}
        
        # Seek any resources opportunistically
        if scan['resources']:
            target = scan['resources'][0][0]
            if target == player_pos:
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