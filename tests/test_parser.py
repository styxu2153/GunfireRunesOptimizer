"""Tests for input parser."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from parser import parse_runes, parse_stones, parse_input_data


class TestParseRunes:
    """Tests for rune parsing."""

    def test_parse_simple_runes(self) -> None:
        """Test parsing space-separated rune levels."""
        runes = parse_runes("10 6 6")
        assert len(runes) == 3
        assert runes[0].id == "R1"
        assert runes[0].max_level == 10
        assert runes[1].max_level == 6
        assert runes[2].max_level == 6

    def test_parse_single_rune(self) -> None:
        """Test parsing a single rune."""
        runes = parse_runes("5")
        assert len(runes) == 1
        assert runes[0].max_level == 5

    def test_parse_runes_with_extra_spaces(self) -> None:
        """Test parsing runes with extra whitespace."""
        runes = parse_runes("  10   6  6  ")
        assert len(runes) == 3

    def test_parse_runes_comma_separated(self) -> None:
        """Test parsing comma-separated runes (alternative format)."""
        runes = parse_runes("10,6,6")
        assert len(runes) == 3


class TestParseStones:
    """Tests for stone parsing."""

    def test_parse_single_stone(self) -> None:
        """Test parsing a single stone with multiple vectors."""
        stones = parse_stones("(1, 0, 2) (0, 1, 1)")
        assert len(stones) == 1
        assert stones[0].id == "K1"
        assert len(stones[0].base_vectors) == 2

    def test_parse_multiple_stones(self) -> None:
        """Test parsing multiple stones separated by commas."""
        stone_str = """
        (0, 1, 2) (-1, 0, 2) (1, 0, 2), 
        (1, 0, 2) (1, 1, 1), 
        (1, 1, 2) (2, 2, 1)
        """
        stones = parse_stones(stone_str)
        assert len(stones) == 3
        assert stones[0].id == "K1"
        assert stones[1].id == "K2"
        assert stones[2].id == "K3"

    def test_parse_stone_with_negative_coords(self) -> None:
        """Test parsing stones with negative coordinates."""
        stones = parse_stones("(-1, -1, 3)")
        assert len(stones) == 1
        v = stones[0].base_vectors[0]
        assert v.dx == -1
        assert v.dy == -1
        assert v.boost == 3

    def test_parse_stones_respects_parentheses(self) -> None:
        """Test that commas inside parentheses don't split stones."""
        # This is the key test - commas inside (x, y, boost) should not split
        stone_str = "(0, 1, 2), (1, 0, 3)"
        stones = parse_stones(stone_str)
        assert len(stones) == 2
        assert stones[0].base_vectors[0].boost == 2
        assert stones[1].base_vectors[0].boost == 3


class TestParseInputData:
    """Tests for combined parsing."""

    def test_parse_full_input(self) -> None:
        """Test parsing complete input data."""
        rune_str = "10 6 6"
        stone_str = "(1, 0, 2), (0, 1, 1)"
        
        runes, stones = parse_input_data(rune_str, stone_str)
        
        assert len(runes) == 3
        assert len(stones) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
