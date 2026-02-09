import random
import math
import copy
import re
from dataclasses import dataclass, field
from typing import List, Tuple

# ==============================================================================
#      STREFA DANYCH WEJŚCIOWYCH (TUTAJ WPISUJESZ SWOJE DANE)
# ==============================================================================

# 1. POZIOMY RUN (oddzielone spacją)
#    Wpisz tylko maksymalne poziomy. Program sam nazwie je R1, R2, R3...
INPUT_RUNES = "10 6 6"

# 2. KONFIGURACJA KAMIENI (oddzielone PRZECINKAMI)
#    Format: (x, y, boost)
#    Grupy nawiasów oddzielone przecinkiem to osobne kamienie (K1, K2...).
#    Współrzędne: (1,0)=Prawo, (-1,0)=Lewo, (0,1)=Góra, (0,-1)=Dół
INPUT_STONES = """
(0, 1, 2) (-1, 0, 2) (1, 0, 2) (1, -1, 2) (0, -1, 2), 
(1, 0, 2) (1, 1, 1), 
(1, 1, 2) (2, 2, 1)
"""
# Powyżej:
# K1 to ciąg przed pierwszym przecinkiem.
# K2 to ciąg między pierwszym a drugim przecinkiem.
# K3 to ciąg na końcu.

# ==============================================================================
#      SILNIK PROGRAMU
# ==============================================================================

GRID_SIZE = 4

@dataclass
class Rune:
    id: str
    max_level: int
    current_level: int = 0
    raw_score: int = 0 

@dataclass
class StoneVector:
    dx: int
    dy: int
    boost: int

class Stone:
    def __init__(self, id: str, vectors: List[StoneVector]):
        self.id = id
        self.base_vectors = vectors
        self.rotation = 0  # 0=0deg, 1=90deg, 2=180deg, 3=270deg

    def get_active_vectors(self) -> List[Tuple[int, int, int]]:
        """Zwraca wektory po uwzględnieniu rotacji (zgodnie z ruchem wskazówek zegara)."""
        rotated = []
        for v in self.base_vectors:
            dx, dy = v.dx, v.dy
            # Matematyka obrotu wektora: (x, y) -> (y, -x) dla 90 stopni w prawo
            for _ in range(self.rotation):
                dx, dy = dy, -dx
            rotated.append((dx, dy, v.boost))
        return rotated

@dataclass
class BoardState:
    grid: dict = field(default_factory=dict)
    runes: List[Rune] = field(default_factory=list)
    stones: List[Stone] = field(default_factory=list)

    def calculate_total_score(self) -> int:
        # Reset wyników
        rune_map = {r.id: r for r in self.runes}
        for r in self.runes: 
            r.raw_score = 0
            
        rune_positions = {}
        stone_positions = {}
        for pos, item in self.grid.items():
            if isinstance(item, Rune):
                rune_positions[pos] = item
            elif isinstance(item, Stone):
                stone_positions[pos] = item

        # Aplikowanie boostów
        for (sx, sy), stone in stone_positions.items():
            vectors = stone.get_active_vectors()
            for dx, dy, boost in vectors:
                target_x, target_y = sx + dx, sy + dy
                # Sprawdzenie czy cel jest na planszy i jest runą
                if (target_x, target_y) in rune_positions:
                    target_rune = rune_positions[(target_x, target_y)]
                    target_rune.raw_score += boost

        # Sumowanie wyników (z uwzględnieniem limitu MaxLevel)
        total_score = 0
        for r in self.runes:
            final = min(r.raw_score, r.max_level)
            r.current_level = final
            total_score += final
        return total_score

# --- PARSER DANYCH ---

def parse_input_data(rune_str, stone_str):
    # 1. Parsowanie Run
    runes = []
    # Czyścimy input ze zbędnych znaków i dzielimy po spacjach
    lvl_list = [int(x) for x in rune_str.replace(',', ' ').split() if x.strip().isdigit()]
    for i, lvl in enumerate(lvl_list):
        runes.append(Rune(f"R{i+1}", lvl))

    # 2. Parsowanie Kamieni (dzielenie po przecinku)
    # 2. Parsowanie Kamieni (dzielenie po przecinku - ale tylko tym POZA nawiasami)
    stones = []
    
    # Manual split by comma respecting parentheses
    stone_chunks = []
    current_chunk = []
    paren_depth = 0
    
    for char in stone_str:
        if char == '(':
            paren_depth += 1
            current_chunk.append(char)
        elif char == ')':
            paren_depth -= 1
            current_chunk.append(char)
        elif char == ',' and paren_depth == 0:
            # Separator found - zapisujemy chunk i czyścimy bufor
            stone_chunks.append("".join(current_chunk))
            current_chunk = []
        else:
            current_chunk.append(char)
    # Dodaj ostatni kawałek
    if current_chunk:
        stone_chunks.append("".join(current_chunk))
    
    counter: int = 1
    for chunk in stone_chunks:
        chunk = chunk.strip()
        if not chunk: continue
        
        vectors = []
        # Szukamy wszystkich (x, y, boost) w danym fragmencie
        matches = re.findall(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*\)', chunk)
        
        for dx, dy, boost in matches:
            vectors.append(StoneVector(int(dx), int(dy), int(boost)))
        
        if vectors:
            stones.append(Stone(f"K{counter}", vectors))
            counter += 1
            
    return runes, stones

# --- ALGORYTM (Symulowane Wyżarzanie) ---

def solve_layout(runes: List[Rune], stones: List[Stone], iterations=80000):
    all_items = runes + stones
    positions = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
    
    current_state = BoardState(runes=runes, stones=stones)
    
    # Losowy start
    random.shuffle(positions)
    for i, item in enumerate(all_items):
        if i < len(positions):
            current_state.grid[positions[i]] = item
            if isinstance(item, Stone):
                item.rotation = random.randint(0, 3)

    best_state = copy.deepcopy(current_state)
    best_score = current_state.calculate_total_score()
    current_score = best_score
    
    temp = 12.0
    cooling_rate = 0.9997 # Wolniejsze chłodzenie dla dokładności

    for i in range(iterations):
        new_state = copy.deepcopy(current_state)
        
        # Próba zmiany (Mutacja)
        rand_val = random.random()
        
        if rand_val < 0.4 and new_state.stones:
            # A: Obrót kamienia
            stone_to_rotate = random.choice(new_state.stones)
            for item in new_state.grid.values():
                if isinstance(item, Stone) and item.id == stone_to_rotate.id:
                    item.rotation = (item.rotation + 1) % 4
                    break
        else:
            # B: Przesunięcie lub Zamiana miejscami
            p1 = (random.randint(0, 3), random.randint(0, 3))
            p2 = (random.randint(0, 3), random.randint(0, 3))
            
            i1 = new_state.grid.get(p1)
            i2 = new_state.grid.get(p2)
            
            if i1 is None and i2 is None: continue # Pusto z pustym - bez sensu
            
            # Zamiana w słowniku grid
            if i1: new_state.grid[p2] = i1
            else: 
                if p2 in new_state.grid: del new_state.grid[p2]
            
            if i2: new_state.grid[p1] = i2
            else: 
                if p1 in new_state.grid: del new_state.grid[p1]

        # Ocena nowego stanu
        new_score = new_state.calculate_total_score()
        
        # Czy akceptujemy?
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
        
        temp *= cooling_rate
        if temp < 0.001: temp = 0.001

    return best_state, best_score

# --- WIZUALIZACJA ---

def print_board(state: BoardState):
    score = state.calculate_total_score()
    print(f"\n=== ZNALEZIONE ROZWIĄZANIE (Suma poziomów: {score}) ===")
    
    # Raport szczegółowy
    print("Raport Run:")
    for r in state.runes:
        note = ""
        if r.raw_score > r.max_level:
            note = f" (Nadmiar: +{r.raw_score - r.max_level} zmarnowane)"
        print(f"  {r.id}: {r.current_level}/{r.max_level}{note}")
    
    print("-" * 45)
    
    # Rysowanie siatki (Y=3 na górze)
    for y in range(GRID_SIZE - 1, -1, -1):
        row_str = f"Y={y} | "
        for x in range(GRID_SIZE):
            item = state.grid.get((x, y))
            display = " .      "
            
            if isinstance(item, Rune):
                # Format: R1(6)
                display = f"{item.id}({item.current_level})  "
            elif isinstance(item, Stone):
                # Format: K1 ->
                arrows = ['^', '>', 'v', '<'] # 0, 1, 2, 3
                arrow = arrows[item.rotation]
                display = f"{item.id} {arrow}   "
                
            row_str += display.ljust(9) + "|"
        print(row_str)
        
    print("      " + "-" * 40)
    print("       X=0      X=1      X=2      X=3")
    print("\nLEGENDA:")
    print("  Kx ^ : Kamień nr X obrócony w górę (bez zmian)")
    print("  Kx > : Kamień nr X obrócony o 90 stopni w prawo")

if __name__ == "__main__":
    print(f"Wczytuję dane... Runy: {INPUT_RUNES}")
    try:
        my_runes, my_stones = parse_input_data(INPUT_RUNES, INPUT_STONES)
        print(f"Wczytano: {len(my_stones)} Kamieni.")
        
        print("Szukam najlepszego ułożenia (potrwa kilka sekund)...")
        
        best_overall_state = None
        best_overall_score = -1
        
        # Wykonujemy 3 niezależne próby, żeby uniknąć pechowego startu
        for i in range(3):
            # print(f"  Próba {i+1}...")
            layout, score = solve_layout(my_runes, my_stones, 500000)
            if score > best_overall_score:
                best_overall_score = score
                best_overall_state = layout
        
        print_board(best_overall_state)
        
    except Exception as e:
        print("\n!!! BŁĄD WPROWADZANIA DANYCH !!!")
        print("Upewnij się, że format jest poprawny.")
        print("Przykład kamieni: (1,0,2), (0,1,3) (2,2,1)")
        print(f"Szczegóły błędu: {e}")