"""Centralized solver configurations for the Runes Optimizer."""

from solver import SolverConfig

# --- PRESET DEFINITIONS ---

# 1. FAST: Instant feedback (~8s), lower accuracy
FAST = SolverConfig(
    iterations=200000,
    num_restarts=30,
    initial_temperature=25.0,
    cooling_rate=0.99995,
    workers=12
)

# 2. BALANCED: Good for daily checks (~16s)
BALANCED = SolverConfig(
    iterations=300000,
    num_restarts=48,
    initial_temperature=30.0,
    cooling_rate=0.99997,
    workers=12
)

# 3. PRECISE: The "Sub-60s" sweet spot for Ryzen 7800X3D (~55s)
PRECISE = SolverConfig(
    iterations=600000,
    num_restarts=72,
    initial_temperature=40.0,
    cooling_rate=0.999985,
    workers=12
)

# 4. ULTIMATE: Maximum search depth (~90s+)
ULTIMATE = SolverConfig(
    iterations=600000,
    num_restarts=120,
    initial_temperature=45.0,
    cooling_rate=0.999985,
    workers=14
)

# Mapping for easy access
PRESETS = {
    "FAST": FAST,
    "BALANCED": BALANCED,
    "PRECISE": PRECISE,
    "ULTIMATE": ULTIMATE
}

# The default preset used by the main script
DEFAULT_PRESET = "PRECISE"
