"""Simulated Annealing solver for rune optimization."""

from __future__ import annotations

import copy
import math
import random
from dataclasses import dataclass
from typing import List, Tuple

from models import BoardState, Rune, Stone, GRID_SIZE


@dataclass
class SolverConfig:
    """Configuration for the simulated annealing solver."""
    
    iterations: int = 80000
    initial_temperature: float = 12.0
    cooling_rate: float = 0.9997
    min_temperature: float = 0.001
    rotation_probability: float = 0.4
    num_restarts: int = 3


def _create_initial_state(
    runes: List[Rune], 
    stones: List[Stone]
) -> BoardState:
    """Create a random initial board state."""
    all_items = list(runes) + list(stones)
    positions = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
    
    state = BoardState(runes=runes, stones=stones)
    
    random.shuffle(positions)
    for i, item in enumerate(all_items):
        if i < len(positions):
            state.grid[positions[i]] = item
            if isinstance(item, Stone):
                item.rotation = random.randint(0, 3)
    
    return state


def _mutate_in_place(state: BoardState, config: SolverConfig) -> Tuple[str, Any, Any, Any, Any]:
    """
    Mutate the state in place and return info to revert it.
    Returns: (type, p1, p2, old_val1, old_val2)
    """
    rand_val = random.random()

    if rand_val < config.rotation_probability and state.stones:
        # Mutation A: Rotate a stone
        stone = random.choice(state.stones)
        old_rot = stone.rotation
        stone.rotation = (stone.rotation + 1) % 4
        return ("rotate", stone, old_rot, None, None)
    
    # Mutation B: Swap or Move
    p1 = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    p2 = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    while p1 == p2:
        p2 = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

    v1 = state.grid.get(p1)
    v2 = state.grid.get(p2)

    if v1 is None and v2 is None:
        return ("none", None, None, None, None)

    # Apply swap/move
    if v1: state.grid[p2] = v1
    elif p2 in state.grid: del state.grid[p2]

    if v2: state.grid[p1] = v2
    elif p1 in state.grid: del state.grid[p1]
    
    return ("swap", p1, p2, v1, v2)


def _revert_mutation(state: BoardState, undo_info: Tuple[str, Any, Any, Any, Any]) -> None:
    mtype, p1, p2, v1, v2 = undo_info
    if mtype == "rotate":
        p1.rotation = p2 # p1 is stone, p2 is old_rot
    elif mtype == "swap":
        if v1: state.grid[p1] = v1
        elif p1 in state.grid: del state.grid[p1]
        
        if v2: state.grid[p2] = v2
        elif p2 in state.grid: del state.grid[p2]


def solve_layout(
    runes: List[Rune], 
    stones: List[Stone], 
    config: SolverConfig | None = None
) -> Tuple[BoardState, float]:
    """Find optimal placement using optimized SA with in-place mutations."""
    if config is None:
        config = SolverConfig()

    current_state = _create_initial_state(runes, stones)
    current_score = current_state.calculate_total_score()
    
    best_state_grid = copy.deepcopy(current_state.grid)
    best_stone_rotations = {s.id: s.rotation for s in stones}
    best_score = current_score

    temp = config.initial_temperature

    for i in range(config.iterations):
        undo = _mutate_in_place(current_state, config)
        if undo[0] == "none": continue
        
        new_score = current_state.calculate_total_score()

        accept = False
        if new_score > current_score:
            accept = True
        else:
            delta = new_score - current_score
            accept = random.random() < math.exp(delta / temp)

        if accept:
            current_score = new_score
            if current_score > best_score:
                best_score = current_score
                best_state_grid = copy.deepcopy(current_state.grid)
                best_stone_rotations = {s.id: s.rotation for s in current_state.stones}
        else:
            _revert_mutation(current_state, undo)

        # Cooling
        temp *= config.cooling_rate
        if temp < config.min_temperature:
            temp = config.min_temperature

    # Restore best
    final_state = BoardState(grid=best_state_grid, runes=runes, stones=stones)
    for s in final_state.stones:
        s.rotation = best_stone_rotations[s.id]
    
    return final_state, best_score


def solve_with_restarts(
    runes: List[Rune], 
    stones: List[Stone], 
    config: SolverConfig | None = None
) -> Tuple[BoardState, float]:
    """
    Run the solver multiple times and return the best result.
    
    Args:
        runes: List of runes to place.
        stones: List of stones to place.
        config: Solver configuration.
    
    Returns:
        Tuple of (best_state, best_score).
    """
    if config is None:
        config = SolverConfig()

    best_overall_state: BoardState | None = None
    best_overall_score: float = -1.0

    for _ in range(config.num_restarts):
        # Create fresh copies of runes and stones for each restart
        runes_copy = [Rune(r.id, r.max_level) for r in runes]
        stones_copy = [Stone(s.id, list(s.base_vectors)) for s in stones]
        
        state, score = solve_layout(runes_copy, stones_copy, config)
        if score > best_overall_score:
            best_overall_score = score
            best_overall_state = state

    assert best_overall_state is not None
    return best_overall_state, best_overall_score
