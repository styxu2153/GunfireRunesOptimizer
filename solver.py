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


def _mutate_state(state: BoardState, config: SolverConfig) -> BoardState:
    """Create a mutated copy of the state."""
    new_state = copy.deepcopy(state)
    rand_val = random.random()

    if rand_val < config.rotation_probability and new_state.stones:
        # Mutation A: Rotate a stone
        stone_to_rotate = random.choice(new_state.stones)
        for item in new_state.grid.values():
            if isinstance(item, Stone) and item.id == stone_to_rotate.id:
                item.rotation = (item.rotation + 1) % 4
                break
    else:
        # Mutation B: Swap positions
        p1 = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        p2 = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

        i1 = new_state.grid.get(p1)
        i2 = new_state.grid.get(p2)

        if i1 is None and i2 is None:
            return new_state  # No-op

        # Swap in grid
        if i1:
            new_state.grid[p2] = i1
        elif p2 in new_state.grid:
            del new_state.grid[p2]

        if i2:
            new_state.grid[p1] = i2
        elif p1 in new_state.grid:
            del new_state.grid[p1]

    return new_state


def solve_layout(
    runes: List[Rune], 
    stones: List[Stone], 
    config: SolverConfig | None = None
) -> Tuple[BoardState, float]:
    """
    Find optimal rune/stone placement using simulated annealing.
    
    Args:
        runes: List of runes to place.
        stones: List of stones to place.
        config: Solver configuration (uses defaults if None).
    
    Returns:
        Tuple of (best_state, best_score).
    """
    if config is None:
        config = SolverConfig()

    current_state = _create_initial_state(runes, stones)
    best_state = copy.deepcopy(current_state)
    best_score = current_state.calculate_total_score()
    current_score = best_score

    temp = config.initial_temperature

    for _ in range(config.iterations):
        new_state = _mutate_state(current_state, config)
        new_score = new_state.calculate_total_score()

        # Acceptance criterion
        if new_score > current_score:
            accept = True
        else:
            delta = new_score - current_score
            accept = random.random() < math.exp(delta / temp)

        if accept:
            current_state = new_state
            current_score = new_score
            if current_score > best_score:
                best_score = current_score
                best_state = copy.deepcopy(current_state)

        temp *= config.cooling_rate
        if temp < config.min_temperature:
            temp = config.min_temperature

    return best_state, best_score


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
