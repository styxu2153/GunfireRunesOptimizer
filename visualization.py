"""Visualization utilities for displaying board state."""

from __future__ import annotations

from models import BoardState, Rune, Stone, GRID_SIZE


def print_board(state: BoardState) -> None:
    """
    Print a visual representation of the board state.
    
    Args:
        state: The board state to display.
    """
    score = state.calculate_total_score()
    integer_score = int(score)
    
    print(f"\n=== ZNALEZIONE ROZWIAZANIE (Suma poziomow: {integer_score}) ===")

    # Detailed rune report
    print("Raport Run:")
    for r in state.runes:
        note = ""
        if r.raw_score > r.max_level:
            note = f" (Nadmiar: +{r.raw_score - r.max_level} zmarnowane)"
        print(f"  {r.id}: {r.current_level}/{r.max_level}{note}")

    print("-" * 45)

    # Draw grid (Y=3 at top)
    for y in range(GRID_SIZE - 1, -1, -1):
        row_str = f"Y={y} | "
        for x in range(GRID_SIZE):
            item = state.grid.get((x, y))
            display = " .      "

            if isinstance(item, Rune):
                display = f"{item.id}({item.current_level})  "
            elif isinstance(item, Stone):
                arrows = ['^', '>', 'v', '<']
                arrow = arrows[item.rotation]
                display = f"{item.id} {arrow}   "

            row_str += display.ljust(9) + "|"
        print(row_str)

    print("      " + "-" * 40)
    print("       X=0      X=1      X=2      X=3")
    print("\nLEGENDA:")
    print("  Kx ^ : Kamien nr X obrocony w gore (bez zmian)")
    print("  Kx > : Kamien nr X obrocony o 90 stopni w prawo")
