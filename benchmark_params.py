
import time
import statistics
from rune_parser import parse_input_data
from solver import solve_with_restarts, SolverConfig
from models import BoardState
from optimizer_config import PRESETS

# Test Data
INPUT_RUNES = "10 6 6 6 6 6 4"
INPUT_STONES = """
(-1, 1, 4) (1, 0, 2) (2, 0, 2) (1, -1, 2) (0, -1, 2) (0, -2, 2),
(0, 1, 2) (1, 1, 2) (1, 0, 3),
(1, 1, 1) (2, 2, 2),
(1, 0, 1) (0, -1, 3),
(2, 0, 4) (0, -2, 4),
(0, 2, 2) (2, 0, 1),
(2, 0, 3),
(2, 2, 3)
"""

def benchmark():
    runes, stones = parse_input_data(INPUT_RUNES, INPUT_STONES)
    
    # Use centralized presets for benchmarking
    configs = [(name, config) for name, config in PRESETS.items()]
    
    # Run each test 3 times to get an average (SA is stochastic)
    NUM_RUNS = 3
    
    print(f"{'Config Name':<20} | {'Avg Score':<10} | {'Avg Levels':<10} | {'Avg Time (s)':<12}")
    print("-" * 65)
    
    for name, config in configs:
        scores = []
        levels_list = []
        times = []
        
        for i in range(NUM_RUNS):
            start_time = time.time()
            best_state, best_score = solve_with_restarts(runes, stones, config)
            end_time = time.time()
            
            scores.append(best_score)
            levels_list.append(best_state.get_integer_score())
            times.append(end_time - start_time)
        
        avg_score = statistics.mean(scores)
        avg_levels = statistics.mean(levels_list)
        avg_time = statistics.mean(times)
        
        print(f"{name:<20} | {avg_score:<10.2f} | {avg_levels:<10.1f} | {avg_time:<12.3f}")

if __name__ == "__main__":
    benchmark()
