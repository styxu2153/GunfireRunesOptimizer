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
        Calculate the total score with multiple prioritization rules.
        
        Priority hierarchy (in order of importance):
        1. Base score: Sum of all rune levels (weight = 1.0 per level)
        2. High max_level priority: Runes with higher max_level get weighted bonus
        3. Max-level achievement: Bonus for sub-10 runes reaching their max
        4. Even-level preference: Small bonus for even levels (2, 4, 6, 8, 10)
        
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

        total_levels = 0
        r10_level = 0
        maxed_sub10_count = 0
        even_count = 0
        
        for r in self.runes:
            final = min(r.raw_score, r.max_level)
            r.current_level = final
            total_levels += final
            
            if r.max_level == 10:
                r10_level = final
            elif final == r.max_level:
                maxed_sub10_count += 1
            
            if final > 0 and final % 2 == 0:
                even_count += 1
                
        # Heuristic score based on priorities (Strict Hierarchy):
        # 1. R10 Level (Highest Priority)
        # 2. Total Sum of Levels
        # 3. Maxed Sub-10 Count
        # 4. Even Level Count (Lowest Priority)
        # Weights are chosen to ensure hierarchy while staying within reasonable range for the solver
        score = (r10_level * 100.0) + (total_levels * 1.0) + (maxed_sub10_count * 0.1) + (even_count * 0.01)
        return score

    def get_total_rune_levels(self) -> int:
        """Returns the actual sum of all rune levels."""
        return sum(min(r.raw_score, r.max_level) for r in self.runes)

    def get_integer_score(self) -> int:
        """Returns the total sum of levels for display purposes."""
        return self.get_total_rune_levels()
