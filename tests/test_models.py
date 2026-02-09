"""Tests for data models."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from models import Rune, Stone, StoneVector, BoardState


class TestRune:
    """Tests for Rune dataclass."""

    def test_rune_creation(self) -> None:
        """Test basic rune creation."""
        rune = Rune("R1", 10)
        assert rune.id == "R1"
        assert rune.max_level == 10
        assert rune.current_level == 0
        assert rune.raw_score == 0

    def test_rune_with_initial_values(self) -> None:
        """Test rune with specified initial values."""
        rune = Rune("R2", 6, current_level=3, raw_score=5)
        assert rune.current_level == 3
        assert rune.raw_score == 5


class TestStoneVector:
    """Tests for StoneVector dataclass."""

    def test_stone_vector_creation(self) -> None:
        """Test basic vector creation."""
        vector = StoneVector(1, 0, 2)
        assert vector.dx == 1
        assert vector.dy == 0
        assert vector.boost == 2

    def test_negative_direction(self) -> None:
        """Test vector with negative direction."""
        vector = StoneVector(-1, -1, 3)
        assert vector.dx == -1
        assert vector.dy == -1


class TestStone:
    """Tests for Stone class."""

    def test_stone_creation(self) -> None:
        """Test basic stone creation."""
        vectors = [StoneVector(1, 0, 2), StoneVector(0, 1, 1)]
        stone = Stone("K1", vectors)
        assert stone.id == "K1"
        assert len(stone.base_vectors) == 2
        assert stone.rotation == 0

    def test_get_active_vectors_no_rotation(self) -> None:
        """Test vectors without rotation."""
        vectors = [StoneVector(1, 0, 2)]
        stone = Stone("K1", vectors)
        active = stone.get_active_vectors()
        assert active == [(1, 0, 2)]

    def test_get_active_vectors_90_degrees(self) -> None:
        """Test vectors with 90 degree clockwise rotation."""
        vectors = [StoneVector(1, 0, 2)]  # Right
        stone = Stone("K1", vectors)
        stone.rotation = 1  # 90 degrees clockwise
        active = stone.get_active_vectors()
        # (1, 0) rotated 90° CW -> (0, -1) (down)
        assert active == [(0, -1, 2)]

    def test_get_active_vectors_180_degrees(self) -> None:
        """Test vectors with 180 degree rotation."""
        vectors = [StoneVector(1, 0, 2)]  # Right
        stone = Stone("K1", vectors)
        stone.rotation = 2  # 180 degrees
        active = stone.get_active_vectors()
        # (1, 0) rotated 180° -> (-1, 0) (left)
        assert active == [(-1, 0, 2)]

    def test_get_active_vectors_270_degrees(self) -> None:
        """Test vectors with 270 degree rotation."""
        vectors = [StoneVector(1, 0, 2)]  # Right
        stone = Stone("K1", vectors)
        stone.rotation = 3  # 270 degrees (or 90° CCW)
        active = stone.get_active_vectors()
        # (1, 0) rotated 270° CW -> (0, 1) (up)
        assert active == [(0, 1, 2)]


class TestBoardState:
    """Tests for BoardState class."""

    def test_empty_board_score(self) -> None:
        """Test score of empty board."""
        runes = [Rune("R1", 10)]
        state = BoardState(runes=runes)
        score = state.calculate_total_score()
        assert int(score) == 0

    def test_simple_boost(self) -> None:
        """Test simple boost from stone to rune."""
        rune = Rune("R1", 10)
        stone = Stone("K1", [StoneVector(1, 0, 5)])  # Boost right
        
        state = BoardState(runes=[rune], stones=[stone])
        state.grid[(0, 0)] = stone
        state.grid[(1, 0)] = rune  # Rune is to the right of stone
        
        state.calculate_total_score()
        assert rune.current_level == 5

    def test_boost_capped_at_max_level(self) -> None:
        """Test that boost is capped at rune's max level."""
        rune = Rune("R1", 3)
        stone = Stone("K1", [StoneVector(1, 0, 10)])  # More boost than max
        
        state = BoardState(runes=[rune], stones=[stone])
        state.grid[(0, 0)] = stone
        state.grid[(1, 0)] = rune
        
        state.calculate_total_score()
        assert rune.current_level == 3  # Capped at max
        assert rune.raw_score == 10  # Raw score tracks actual boost

    def test_priority_scoring(self) -> None:
        """Test that high max_level runes get priority bonus."""
        rune1 = Rune("R1", 10)  # Higher max level
        rune2 = Rune("R2", 5)   # Lower max level
        
        stone = Stone("K1", [StoneVector(1, 0, 5)])
        
        # Scenario 1: High-max rune boosted
        state1 = BoardState(runes=[rune1, rune2], stones=[stone])
        state1.grid[(0, 0)] = stone
        state1.grid[(1, 0)] = rune1  # R1 (max 10) gets boost
        state1.grid[(2, 0)] = rune2
        score1 = state1.calculate_total_score()
        
        # Scenario 2: Low-max rune boosted
        rune1b = Rune("R1", 10)
        rune2b = Rune("R2", 5)
        stone2 = Stone("K1", [StoneVector(1, 0, 5)])
        
        state2 = BoardState(runes=[rune1b, rune2b], stones=[stone2])
        state2.grid[(0, 0)] = stone2
        state2.grid[(1, 0)] = rune2b  # R2 (max 5) gets boost
        state2.grid[(2, 0)] = rune1b
        score2 = state2.calculate_total_score()
        
        # Both have same rune level (5), but score1 is higher due to priority bonus
        assert rune1.current_level == rune2b.current_level == 5
        assert score1 > score2  # Priority bonus for high-max rune

    def test_even_level_preference(self) -> None:
        """Test that even levels are preferred over odd levels."""
        # Scenario 1: Rune with even level (4)
        rune1 = Rune("R1", 10)
        stone1 = Stone("K1", [StoneVector(1, 0, 4)])
        
        state1 = BoardState(runes=[rune1], stones=[stone1])
        state1.grid[(0, 0)] = stone1
        state1.grid[(1, 0)] = rune1
        score1 = state1.calculate_total_score()
        
        # Scenario 2: Rune with odd level (3)
        rune2 = Rune("R1", 10)
        stone2 = Stone("K1", [StoneVector(1, 0, 3)])
        
        state2 = BoardState(runes=[rune2], stones=[stone2])
        state2.grid[(0, 0)] = stone2
        state2.grid[(1, 0)] = rune2
        score2 = state2.calculate_total_score()
        
        # Even level (4) should have bonus in decimal part
        assert rune1.current_level == 4
        assert rune2.current_level == 3
        assert score1 > score2
        # score1: (4*100) + 4 + 0.01 = 404.01
        # score2: (3*100) + 3 + 0 = 303.0

    def test_sub_10_max_achievement_bonus(self) -> None:
        """Test that sub-10 runes get a bonus for reaching max level."""
        # Scenario 1: Rune at max level (6/6)
        rune1 = Rune("R6", 6)
        stone1 = Stone("K1", [StoneVector(1, 0, 6)])
        
        state1 = BoardState(runes=[rune1], stones=[stone1])
        state1.grid[(0, 0)] = stone1
        state1.grid[(1, 0)] = rune1
        score1 = state1.calculate_total_score()
        
        # Scenario 2: Rune nearly at max level (5/6)
        rune2 = Rune("R6", 6)
        stone2 = Stone("K1", [StoneVector(1, 0, 5)])
        
        state2 = BoardState(runes=[rune2], stones=[stone2])
        state2.grid[(0, 0)] = stone2
        state2.grid[(1, 0)] = rune2
        score2 = state2.calculate_total_score()
        
        # Difference should be > 1.0 (1.0 for level + 0.1 for max bonus + even bonus)
        assert score1 - score2 > 1.0

    def test_priority_hierarchy(self) -> None:
        """Verify the priority: 10/10 > 6/6 > 6/5."""
        # 1. 10/10 case (R10 level 5, R6 level 0)
        rune_10a = Rune("R10", 10)
        rune_6a = Rune("R6", 6)
        state_10 = BoardState(runes=[rune_10a, rune_6a], stones=[Stone("K1", [StoneVector(1,0,5)])])
        state_10.grid[(0,0)] = state_10.stones[0]
        state_10.grid[(1,0)] = rune_10a
        score_10 = state_10.calculate_total_score()
        
        # 2. 6/6 case (R10 level 0, R6 level 6)
        rune_10b = Rune("R10", 10)
        rune_6b = Rune("R6", 6)
        state_6_max = BoardState(runes=[rune_10b, rune_6b], stones=[Stone("K1", [StoneVector(1,0,6)])])
        state_6_max.grid[(0,0)] = state_6_max.stones[0]
        state_6_max.grid[(1,0)] = rune_6b
        score_6_max = state_6_max.calculate_total_score()
        
        # R10 level 5 should win over R6 level 6 due to highest priority
        assert score_10 > score_6_max
        assert state_10.get_integer_score() == 5
        assert state_6_max.get_integer_score() == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
