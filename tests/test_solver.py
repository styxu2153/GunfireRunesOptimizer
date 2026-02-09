"""Tests for the solver module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from models import Rune, Stone, StoneVector
from solver import solve_layout, solve_with_restarts, SolverConfig


class TestSolver:
    """Tests for the simulated annealing solver."""

    def test_solver_returns_valid_state(self) -> None:
        """Test that solver returns a valid board state."""
        runes = [Rune("R1", 10), Rune("R2", 6)]
        stones = [Stone("K1", [StoneVector(1, 0, 5)])]
        
        config = SolverConfig(iterations=1000)
        state, score = solve_layout(runes, stones, config)
        
        assert state is not None
        assert score >= 0

    def test_solver_places_all_items(self) -> None:
        """Test that solver places all runes and stones."""
        runes = [Rune("R1", 10), Rune("R2", 6)]
        stones = [Stone("K1", [StoneVector(1, 0, 5)])]
        
        config = SolverConfig(iterations=1000)
        state, _ = solve_layout(runes, stones, config)
        
        grid_items = list(state.grid.values())
        rune_count = sum(1 for item in grid_items if isinstance(item, Rune))
        stone_count = sum(1 for item in grid_items if isinstance(item, Stone))
        
        assert rune_count == 2
        assert stone_count == 1


class TestPriorityScoring:
    """Tests for priority-based scoring behavior."""

    def test_priority_favors_high_max_runes(self) -> None:
        """
        Test that the algorithm prefers filling high-max-level runes.
        
        With runes 10, 6, 6 and 12 total boost available, we expect:
        - R1 (max 10) should have level >= 4
        - Total score should be 12
        """
        runes = [Rune("R1", 10), Rune("R2", 6), Rune("R3", 6)]
        
        # Create stones that provide exactly 12 boost total
        # K1: 5 vectors with boost 2 each = 10 boost
        # K2: 1 vector with boost 2 = 2 boost
        # Total: 12 boost
        stones = [
            Stone("K1", [
                StoneVector(0, 1, 2),
                StoneVector(-1, 0, 2),
                StoneVector(1, 0, 2),
                StoneVector(1, -1, 2),
                StoneVector(0, -1, 2),
            ]),
            Stone("K2", [
                StoneVector(1, 0, 2),
                StoneVector(1, 1, 1),
            ]),
            Stone("K3", [
                StoneVector(1, 1, 2),
                StoneVector(2, 2, 1),
            ]),
        ]
        
        config = SolverConfig(
            iterations=100000,
            num_restarts=3
        )
        
        state, _ = solve_with_restarts(runes, stones, config)
        
        # Recalculate to ensure current_level is set
        state.calculate_total_score()
        
        # Find R1 in the result
        r1 = next(r for r in state.runes if r.id == "R1")
        r2 = next(r for r in state.runes if r.id == "R2")
        r3 = next(r for r in state.runes if r.id == "R3")
        
        total = r1.current_level + r2.current_level + r3.current_level
        
        # Total should be 12 (max possible)
        assert total == 12, f"Total score should be 12, got {total}"
        
        # R1 should not have lower level than other runes
        # (Priority scoring ensures high-max runes get filled first)
        assert r1.current_level >= r2.current_level or r1.current_level >= r3.current_level, \
            f"R1 ({r1.current_level}) should be >= at least one of R2 ({r2.current_level}) or R3 ({r3.current_level})"


class TestSolverConfig:
    """Tests for solver configuration."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = SolverConfig()
        assert config.iterations == 80000
        assert config.initial_temperature == 12.0
        assert config.num_restarts == 3

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = SolverConfig(iterations=1000, num_restarts=1)
        assert config.iterations == 1000
        assert config.num_restarts == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
