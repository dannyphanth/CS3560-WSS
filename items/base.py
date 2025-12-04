from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..actors.player import Player

@dataclass
class Item(ABC):
    name: str
    symbol: str  # how it appears on the map, e.g. 'F', 'W', 'G'

    @abstractmethod
    def apply(self, player: "Player") -> None:
        raise NotImplementedError

    def on_pickup(self, player: "Player") -> bool:
        self.apply(player)
        return True  # default: one-shot item


@dataclass
class RepeatingItem(Item):
    # keep internal state if needed
    times_used: int = field(default=0, init=False)

    def on_pickup(self, player: "Player") -> bool:
        self.apply(player)
        self.times_used += 1
        return False  # stays on the map