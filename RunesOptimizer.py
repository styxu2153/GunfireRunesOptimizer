"""
Runes Optimizer - Main Entry Point

Optimizes the placement of runes and stones on a 4x4 grid to maximize
the total rune levels while prioritizing high-max-level runes.
"""

from rune_parser import parse_input_data
from solver import solve_with_restarts, SolverConfig
from visualization import print_board

# ==============================================================================
#      STREFA DANYCH WEJSCIOWYCH (TUTAJ WPISUJESZ SWOJE DANE)
# ==============================================================================

# 1. POZIOMY RUN (oddzielone spacja)
#    Wpisz tylko maksymalne poziomy. Program sam nazwie je R1, R2, R3...
INPUT_RUNES = "10 6 6 4"

# 2. KONFIGURACJA KAMIENI (oddzielone PRZECINKAMI)
#    Format: (x, y, boost)
#    Grupy nawiasow oddzielone przecinkiem to osobne kamienie (K1, K2...).
#    Wspolrzedne: (1,0)=Prawo, (-1,0)=Lewo, (0,1)=Gora, (0,-1)=Dol
INPUT_STONES = """
(0, 1, 2) (-1, 0, 2) (1, 0, 2) (1, -1, 2) (0, -1, 2), 
(1, 0, 2) (1, 1, 1), 
(1, 1, 2) (2, 2, 1),
(1, 1, 3) (1, 0, 3)
"""
# Powyzej:
# K1 to ciag przed pierwszym przecinkiem.
# K2 to ciag miedzy pierwszym a drugim przecinkiem.
# K3 to ciag na koncu.

# ==============================================================================
#      MAIN
# ==============================================================================


def main() -> None:
    """Main entry point for the optimizer."""
    print(f"Wczytuje dane... Runy: {INPUT_RUNES}")
    
    try:
        my_runes, my_stones = parse_input_data(INPUT_RUNES, INPUT_STONES)
        print(f"Wczytano: {len(my_stones)} Kamieni.")

        print("Szukam najlepszego ulozenia (potrwa kilka sekund)...")

        config = SolverConfig(
            iterations=100000,
            num_restarts=3
        )
        
        best_state, _ = solve_with_restarts(my_runes, my_stones, config)
        print_board(best_state)

    except Exception as e:
        print("\n!!! BLAD WPROWADZANIA DANYCH !!!")
        print("Upewnij sie, ze format jest poprawny.")
        print("Przyklad kamieni: (1,0,2), (0,1,3) (2,2,1)")
        print(f"Szczegoly bledu: {e}")


if __name__ == "__main__":
    main()