from typing import Tuple, List, Dict, Optional, Any
from abc import ABC, abstractmethod
from ai.vision import Focused, CautiousVision, KeenEyedVision, FarSightVision
import random
import heapq


class Brain(ABC):
    """
    Base class for AI decision-making that works with the Game.make_move()
    logic: decide_path() returns a LIST of positions to walk through.
    """

    def __init__(
        self,
        game,
        player,
        brain_type: str = "Balanced",
        vision_cls=None,
    ):
        self.game = game
        self.player = player
        self.brain_type = brain_type

        # Default mapping from brain type to vision class
        default_vision_map = {
            "Cautious": CautiousVision,
            "Aggressive": KeenEyedVision,
            "Balanced": Focused,
            "Opportunistic": FarSightVision,
        }

        if vision_cls is None:
            VisionClass = default_vision_map.get(brain_type, Focused)
        else:
            VisionClass = vision_cls

        self.vision = VisionClass(game, player)
        # Path is a list of (x, y) tiles we plan to walk through
        self.path: List[Tuple[int, int]] = []

    @abstractmethod
    def decide_path(self) -> List[Tuple[int, int]]:
        """
        Decide the next path (sequence of tiles) we want to travel.

        Returns:
            A list of (x, y) positions.
            - [] means "rest / do nothing this turn".
        """
        raise NotImplementedError

    def make_move(self) -> None:
        """
        Called once per turn from Game.on_update().
        Uses self.path as a queue of upcoming positions.
        """
        if not self.path:
            # No more moves pending – compute a new path
            self.path = self.decide_path()

        if self.path:
            # Take one step along the path
            move = self.path.pop(0)
            self.player.set_location(move)
        else:
            # Still no path -> rest (e.g., regain strength)
            self.player.rest()

    def _assess_needs(self) -> Dict[str, float]:
        """
        Assess needs as numbers in [0, 1].

        NOTE: This is just a placeholder heuristic. You’ll probably want to
        tweak it once you know your Player/Inventory scales.
        """
        inv = self.player.inventory
        max_cap = max(1, getattr(inv, "max_items", 1))

        return {
            "strength": self.player.strength / max_cap,
            "food": inv.food / max_cap,
            "water": inv.water / max_cap,
        }

    def find_path_to(
        self,
        target_resource: str,
        player_pos: Tuple[int, int],
        scan: Dict[str, Any],
    ) -> List[Tuple[int, int]]:
        """
        Choose the *most cost-effective* path to the requested resource type.

        - target_resource: key in scan, e.g. 'water', 'food', 'traders'
        - player_pos: (x, y)
        - scan: output of vision.scan_area()

        Returns:
            List of positions from the first step after player_pos
            up to and including the chosen target tile. Returns [] if no path.
        """
        candidates = scan.get(target_resource, [])
        if not candidates:
            return []

        best_path: List[Tuple[int, int]] = []
        best_cost: float = float("inf")

        for entry in candidates:
            # Expect entry like: (pos, maybe_other_info...)
            target_pos = entry[0]
            path, total_cost = self._a_star_path(player_pos, target_pos)
            if path and total_cost < best_cost:
                best_cost = total_cost
                best_path = path

        return best_path

    def assess_danger(self, pos: Tuple[int, int]) -> float:
        """
        Assess danger level at position (0.0 = safe, 1.0 = deadly).
        Based on terrain cost, if world exposes that info.
        """
        x, y = pos
        if hasattr(self.game.world, "get_movement_cost"):
            terrain_cost = self.game.world.get_movement_cost(x, y)

            # Impassable is deadly
            if terrain_cost == float("inf"):
                return 1.0

            # High cost terrain is moderately dangerous
            danger = min(terrain_cost / 10.0, 0.8)
            return danger

        return 0.0

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        # Manhattan distance as heuristic (assuming 4-directional movement)
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _neighbors(self, pos: Tuple[int, int]):
        x, y = pos
        world = self.game.world
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.width and 0 <= ny < world.height:
                yield (nx, ny)

    def _a_star_path(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> Tuple[List[Tuple[int, int]], float]:
        """
        A* search using terrain.move_cost as edge weight.

        Returns:
            (path, total_cost)
            - path: positions from first step after start to goal inclusive
            - total_cost: sum of move_costs along the path
        """
        world = self.game.world

        frontier: List[Tuple[float, Tuple[int, int]]] = []
        heapq.heappush(frontier, (0.0, start))

        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        cost_so_far: Dict[Tuple[int, int], float] = {start: 0.0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for nxt in self._neighbors(current):
                terrain = world.get_terrain(nxt)
                move_cost = getattr(terrain, "move_cost", 1)

                # Impassable
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
        path: List[Tuple[int, int]] = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = came_from[cur]  # type: ignore
        path.reverse()

        # Ensure we don't include start itself as a move
        if path and path[0] == start:
            path = path[1:]

        return path, cost_so_far[goal]


class CautiousBrain(Brain):
    """Conservative play style: prioritizes safety and resource management."""

    def decide_path(self) -> List[Tuple[int, int]]:
        """
        Returns a path (list of tiles) based on what is needed most.
        """
        needs = self._assess_needs()
        scan = self.vision.scan_area(radius=2)
        player_pos = self.player.location

        # Critical strength - rest is priority
        if needs["strength"] < 0.3:
            return []

        # Urgent water need (more critical than food)
        if needs["water"] < 0.4:
            path_to = self.find_path_to("water", player_pos, scan)
            if path_to:
                return path_to

        # Urgent food need
        if needs["food"] < 0.4:
            path_to = self.find_path_to("food", player_pos, scan)
            if path_to:
                return path_to

        # Moderate needs - seek resources proactively
        if needs["water"] < 0.7:
            path_to = self.find_path_to("water", player_pos, scan)
            if path_to:
                return path_to

        if needs["food"] < 0.7:
            path_to = self.find_path_to("food", player_pos, scan)
            if path_to:
                return path_to

        # Rest if low on resources
        if needs["strength"] < 0.7:
            return []

        # Fallback: step to the right
        return [(player_pos[0] + 1, player_pos[1])]


# For now, other brains reuse CautiousBrain logic so the game runs.
# Later you can override decide_path() in each to customize behavior.

class AggressiveBrain(CautiousBrain):
    """Aggressive play style (currently same path logic as Cautious)."""
    pass


class BalancedBrain(CautiousBrain):
    """Balanced play style (currently same path logic as Cautious)."""
    pass


class OpportunistBrain(CautiousBrain):
    """Opportunistic play style (currently same path logic as Cautious)."""
    pass


# Types available in the UI
BRAIN_TYPES = [
    "Cautious",
    "Aggressive",
    "Balanced",
    "Opportunistic",
]

# The *names* shown in the UI for vision choices
VISION_TYPES = [
    "Focused",
    "Cautious",
    "Keen-Eyed",
    "Far-Sight",
]

# Map from label to Brain class
BRAIN_CLASS_MAP = {
    "Cautious": CautiousBrain,
    "Aggressive": AggressiveBrain,
    "Balanced": BalancedBrain,
    "Opportunistic": OpportunistBrain,
}

# Map from label to Vision class (matches VISION_TYPES)
VISION_CLASS_MAP = {
    "Focused": Focused,
    "Cautious": CautiousVision,
    "Keen-Eyed": KeenEyedVision,
    "Far-Sight": FarSightVision,
}
