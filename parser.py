"""Parser for rune and stone input data."""

from __future__ import annotations

import re
from typing import List, Tuple

from models import Rune, Stone, StoneVector


def parse_runes(rune_str: str) -> List[Rune]:
    """
    Parse rune levels from a space-separated string.
    
    Args:
        rune_str: Space-separated rune levels, e.g., "10 6 6"
    
    Returns:
        List of Rune objects named R1, R2, R3, etc.
    """
    runes: List[Rune] = []
    lvl_list = [
        int(x) for x in rune_str.replace(',', ' ').split() 
        if x.strip().isdigit()
    ]
    for i, lvl in enumerate(lvl_list):
        runes.append(Rune(f"R{i + 1}", lvl))
    return runes


def _split_stones_by_separator(stone_str: str) -> List[str]:
    """
    Split stone string by commas, but only commas outside parentheses.
    
    Args:
        stone_str: Raw stone configuration string.
    
    Returns:
        List of stone definition chunks.
    """
    chunks: List[str] = []
    current_chunk: List[str] = []
    paren_depth = 0

    for char in stone_str:
        if char == '(':
            paren_depth += 1
            current_chunk.append(char)
        elif char == ')':
            paren_depth -= 1
            current_chunk.append(char)
        elif char == ',' and paren_depth == 0:
            chunks.append("".join(current_chunk))
            current_chunk = []
        else:
            current_chunk.append(char)

    if current_chunk:
        chunks.append("".join(current_chunk))

    return chunks


def parse_stones(stone_str: str) -> List[Stone]:
    """
    Parse stone configurations from a formatted string.
    
    Args:
        stone_str: Stone configuration with vectors like "(dx, dy, boost)"
    
    Returns:
        List of Stone objects named K1, K2, K3, etc.
    """
    stones: List[Stone] = []
    stone_chunks = _split_stones_by_separator(stone_str)

    counter: int = 1
    for chunk in stone_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        vectors: List[StoneVector] = []
        matches = re.findall(
            r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*\)', 
            chunk
        )

        for dx, dy, boost in matches:
            vectors.append(StoneVector(int(dx), int(dy), int(boost)))

        if vectors:
            stones.append(Stone(f"K{counter}", vectors))
            counter += 1

    return stones


def parse_input_data(rune_str: str, stone_str: str) -> Tuple[List[Rune], List[Stone]]:
    """
    Parse both runes and stones from input strings.
    
    Args:
        rune_str: Space-separated rune levels.
        stone_str: Stone configuration string.
    
    Returns:
        Tuple of (runes, stones).
    """
    runes = parse_runes(rune_str)
    stones = parse_stones(stone_str)
    return runes, stones
