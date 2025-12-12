from typing import Tuple, List, Dict, Optional, Any
from abc import ABC, abstractmethod
from ai.vision import *
import random

class Brain(ABC):
    """
    Abstract base class for AI decision-making.
    Subclass to create different play styles.
    """
    
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.vision = Vision(game, player)
        self.path = []

    
    @abstractmethod
    def decide_path(self) -> Dict[str, Any]:
        """
        Decide next action based on current state.
        
        Returns dict with:
        - action: 'move', 'rest', 'trade'
        - params: dict of action-specific parameters
        """
        pass
    
    
    def make_move(self): 
        if self.path == []: 
            # no more moves to make a decision on a previous turn
            # so find a new path
            self.path = self.decide_path()

        if self.path != []: 
            move = self.path[0]
            self.path.remove(move)
            self.player.set_location(move)
            return 
        else: 
            # if the path list is STILL empty, 
            # the player will a skip a turn and gain a strength point
            self.player.rest()
            
    
    def _assess_needs(self) -> Dict[str, float]:
        """Assess urgency of needs (0.0 = satisfied, 1.0 = critical)."""
        
        # Access Player attributes
        return {
            'strength': self.player.strength / self.player.inventory.max_items,
            'food': self.player.inventory.food / self.player.inventory.max_items,
            'water': self.player.inventory.water / self.player.inventory.max_items,
        }

            
    def find_path_to(
        self,
        target_resource: str,
        player_pos,
        scan: Dict[str, Any]
    ) -> List[any]:
        """
        Choose the *most cost-effective* path to the requested resource type.
        
        - target_resource: 'water', 'food', 'foodFountain', 'traders', etc.
        - player_pos: (x, y)
        - scan: output of scan_area()
        
        Returns a list of positions from the first step after player_pos
        up to and including the chosen target tile. Returns [] if no path.
        """

        candidates = scan.get(target_resource, [])

        if not candidates:
            return []

        best_path = []
        best_cost: float = float('inf')

        for entry in candidates:
            path, total_cost = self._a_star_path(player_pos, entry[0])

            if path and total_cost < best_cost:
                best_cost = total_cost
                best_path = path

        return best_path



    
    def assess_danger(self, pos: Tuple[int, int]) -> float:
        """
        Assess danger level at position (0.0 = safe, 1.0 = deadly).
        Based on terrain cost and distance to hazards.
        """
        x, y = pos
        if hasattr(self.game.world, 'get_movement_cost'):
            terrain_cost = self.game.world.get_movement_cost(x, y)
            
            # Impassable is deadly
            if terrain_cost == float('inf'):
                return 1.0
            
            # High cost terrain is moderately dangerous
            danger = min(terrain_cost / 10.0, 0.8)
            return danger
        
        return 0.0




    def _heuristic(self, a, b) -> float:
        # Manhattan distance as heuristic (assuming 4-directional movement)
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


    def _neighbors(self, pos):
        x, y = pos
        world = self.game.world
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.width and 0 <= ny < world.height:
                yield (nx, ny)


    def _a_star_path(self, start, goal):
        """
        A* search using terrain.move_cost as edge weight.

        Returns (path, total_cost)
        - path: list of positions from first step after start to goal inclusive
        - total_cost: sum of move_costs along the path
        """

        world = self.game.world

        frontier = []
        heapq.heappush(frontier, (0.0, start))

        came_from = {start: None}
        cost_so_far = {start: 0.0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for nxt in self._neighbors(current):
                terrain = world.get_terrain(nxt)
                move_cost = getattr(terrain, "move_cost", 1)

                # You can define "impassable" however you like:
                if move_cost is None or move_cost == float("inf"):
                    continue

                new_cost = cost_so_far[current] + move_cost

                if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                    cost_so_far[nxt] = new_cost
                    priority = new_cost + self._heuristic(nxt, goal)
                    heapq.heappush(frontier, (priority, nxt))
                    came_from[nxt] = current



        if goal not in came_from:
            # No path
            return [], float("inf")

        # Reconstruct path from goal back to start
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = came_from[cur]
        path.reverse()  # now from start->goal

        # We usually don’t repeat start in the path
        # path currently is [start, step1, ..., goal] if you pushed start above
        # If you want only steps AFTER start, do:
        if path and path[0] == start:
            path = path[1:]

        return path, cost_so_far[goal]



class CautiousBrain(Brain):
    """Conservative play style: prioritizes safety and resource management."""
    
    def decide_path(self) -> Dict[str, Any]:
        """
        Returns a path of squares to move to based on what is needed most.
        """
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=20)
        playerPos = self.player.location
        
        # Critical strength - rest is priority
        if needs['strength'] < 0.3:
            print("Need to rest")
            return []
        
        # Urgent water need (more critical than food)
        if needs['water'] < 0.4:
            print("Looking for water")
            pathTo = self.find_path_to('water', playerPos, scan)
            if pathTo: return pathTo
            
        # Urgent food need
        if needs['food'] < 0.4:
            print("Looking for food")
            pathTo = self.find_path_to('food', playerPos, scan)
            if pathTo: return pathTo
        
        # Moderate needs - seek resources proactively
        if needs['water'] < 0.7:
            print("Looking for water, casually")
            pathTo = self.find_path_to('water', playerPos, scan)
            if pathTo: return pathTo
        
        if needs['food'] < 0.7:
            print("Looking for food, casually")
            pathTo = self.find_path_to('food', playerPos, scan)
            if pathTo: return pathTo
        
        # Rest if low on resources
        if needs['strength'] < 0.7:
            print("Just hanging out")
            return []
        
        # if all else fails, keep moving forward ✊
        return [(playerPos[0] + 1, playerPos[1])]




class AggressiveBrain(Brain):
    """Aggressive play style: takes risks, seeks traders and valuable resources."""
    
    def decide_path(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=7)  # Larger vision
        player_pos = self.player.location
        
        # Only rest if critically low
        if needs['strength'] > 0.85:
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
            return self.find_path_to('water', scan)
            if water_pos:
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.5:
            return self.find_path_to('food', scan)
            if food_pos:
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
        

class BalancedBrain(Brain):
    """Balanced play style: weighs all factors reasonably."""
    
    def decide_path(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=6)
        player_pos = self.player.location
        
        # Rest when strength is concerning
        if needs['strength'] > 0.6:
            return {'action': 'rest', 'params': {}}
        
        # Handle critical needs first
        max_need = max(needs.values())
        if max_need > 0.65:
            if needs['water'] == max_need:
                return self.find_path_to('water', scan)
                if water_pos:
                    next_pos = self._find_path_to(water_pos)
                    if next_pos:
                        return {'action': 'move', 'params': {'pos': next_pos}}
            elif needs['food'] == max_need:
                return self.find_path_to('food', scan)
                if food_pos:
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
            return self.find_path_to('water', scan)
            if water_pos:
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.35:
            return self.find_path_to('food', scan)
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
    
    def decide_path(self) -> Dict[str, Any]:
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=8)
        player_pos = self.player.location
        
        # Only handle truly critical situations
        if needs['strength'] > 0.8:
            return {'action': 'rest', 'params': {}}
        
        if needs['water'] > 0.75:
            return self.find_path_to('water', scan)
            if water_pos:
                next_pos = self._find_path_to(water_pos)
                if next_pos:
                    return {'action': 'move', 'params': {'pos': next_pos}}
        
        if needs['food'] > 0.75:
            return self.find_path_to('food', scan)
            if food_pos:
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