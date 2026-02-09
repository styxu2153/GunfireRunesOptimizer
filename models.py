"""Data models for the Runes Optimizer."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union


GRID_SIZE = 4


@dataclass
class Rune:
    """Represents a rune that can accumulate boost points up to max_level."""
    
    id: str
    max_level: int
    current_level: int = 0
    raw_score: int = 0


@dataclass
class StoneVector:
    """Represents a single boost vector emitted by a stone."""
    
    dx: int
    dy: int
    boost: int


class Stone:
    """Represents a stone that emits boost vectors in configurable directions."""
    
    def __init__(self, id: str, vectors: List[StoneVector]) -> None:
        self.id = id
        self.base_vectors = vectors
        self.rotation: int = 0  # 0=0deg, 1=90deg, 2=180deg, 3=270deg

    def get_active_vectors(self) -> List[Tuple[int, int, int]]:
        """Returns vectors after applying rotation (clockwise)."""
        rotated: List[Tuple[int, int, int]] = []
        for v in self.base_vectors:
            dx, dy = v.dx, v.dy
            # Rotation math: (x, y) -> (y, -x) for 90 degrees clockwise
            for _ in range(self.rotation):
                dx, dy = dy, -dx
            rotated.append((dx, dy, v.boost))
        return rotated


@dataclass
class BoardState:
    """Represents the state of the game board with runes and stones placed."""
    
    grid: Dict[Tuple[int, int], Any] = field(default_factory=dict)
    runes: List[Rune] = field(default_factory=list)
    stones: List[Stone] = field(default_factory=list)

    def calculate_total_score(self) -> float:
        """
        Calculate the total score with priority bonus for high-max-level runes.
        
        The scoring uses a weighted system where points given to runes with
        higher max_level contribute more to the score. This ensures the 
        optimizer prioritizes filling high-max-level runes first.
        
        Returns:
            float: Weighted score where integer part approximates total levels.
        """
        # Reset scores
        for r in self.runes:
            r.raw_score = 0

        rune_positions: Dict[Tuple[int, int], Rune] = {}
        stone_positions: Dict[Tuple[int, int], Stone] = {}
        
        for pos, item in self.grid.items():
            if isinstance(item, Rune):
                rune_positions[pos] = item
            elif isinstance(item, Stone):
                stone_positions[pos] = item

        # Apply boosts from stones to runes
        for (sx, sy), stone in stone_positions.items():
            vectors = stone.get_active_vectors()
            for dx, dy, boost in vectors:
                target_x, target_y = sx + dx, sy + dy
                if (target_x, target_y) in rune_positions:
                    target_rune = rune_positions[(target_x, target_y)]
                    target_rune.raw_score += boost

        # Calculate total score with priority weighting
        # Each point to a high-max-level rune is worth more than a point to a low-max-level rune
        max_possible_level = max((r.max_level for r in self.runes), default=1)
        total_score: float = 0.0
        
        for r in self.runes:
            final = min(r.raw_score, r.max_level)
            r.current_level = final
            
            # Base score is the actual level
            total_score += final
            
            # Priority bonus: each point to a high-max rune gets a weighted bonus
            # The bonus is proportional to how "important" the rune is (max_level / max_possible)
            # and scales with the number of points given
            if r.max_level > 0 and max_possible_level > 0:
                priority_weight = r.max_level / max_possible_level
                # Strong priority: each point to a max-level rune adds 0.5 bonus
                total_score += final * priority_weight * 0.5
            
            # Even-level bonus: prefer even levels (2, 4, 6, 8, 10) over odd
            # since bonuses are given every 2 points.
            # Aggressive: +0.1 makes 8 (even) preferred over 9 (odd) even at 1 point cost
            if final > 0 and final % 2 == 0:
                total_score += 0.5

        return total_score

    def get_integer_score(self) -> int:
        """Returns only the integer part of the score (total rune levels)."""
        return int(self.calculate_total_score())
