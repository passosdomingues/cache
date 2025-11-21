# ikkiFenix Refactoring Project

**Date:** 2025-11-20
**Author:** Antigravity (Google Deepmind)

## Overview

This project involved a comprehensive refactoring of the `ikkiFenix` queuing simulator to transform it into a robust, deterministic, and modular stochastic analysis framework.

## Key Achievements

### Phase 1: Auditing and Determinism (Core C++)
- **RNG Singleton:** Implemented `RNG` as a Singleton to enforce a single source of randomness.
- **Determinism:** Hardcoded seed `42` to ensure strict reproducibility across all runs.
- **Memory Safety:** Replaced raw pointers (`Queue*`, `PolicyFunction`) with smart pointers (`std::unique_ptr`), eliminating memory leaks.
- **Standardized Scenarios:** Enforced 4 load scenarios (ρ = 0.800, 0.900, 0.950, 0.999).

### Phase 2: Algorithm Expansion
- **Polymorphic Policies:** Refactored scheduling policies into a polymorphic class hierarchy (`SchedulingPolicy`).
- **New Policies:** Implemented 4 new policies:
    - `RoundRobinPolicy`: Fair cyclic scheduling.
    - `StrictPriorityPolicy`: Q0 > Q1 > Q2.
    - `ShortestQueuePolicy`: Load balancing.
    - `AgingPolicy`: Starvation avoidance (threshold-based).
- **Factory Pattern:** Implemented `Policies::createPolicy()` for dynamic instantiation.

### Phase 3: Python Refactoring (OOP Modularization)
- **Modular Library:** Created `analysis/lib` package:
    - `loader.py`: `LogParser` for robust CSV loading and preprocessing.
    - `stats.py`: `StatsEngine` for statistical analysis (CI, Little's Law, ACF).
    - `viz.py`: `PlotterFactory` for publication-quality visualizations.
- **Reproducibility:** Enforced `np.random.seed(42)` in all analysis modules.

### Phase 4: Rich Analysis and Reporting
- **Automated Reporting:** Created `analysis/run_analysis.py` to generate comprehensive reports.
- **Advanced Metrics:**
    - **Autocorrelation (ACF):** Analysis of queue length memory.
    - **Transient Detection:** MSER-like heuristic for steady-state identification.
    - **Jitter Analysis:** Comparative stability analysis (e.g., RR vs MaxWait).
- **Little's Law Verification:** Automated validation of simulation correctness.

## Project Structure

```
ikkiFenix/
├── src/                # C++ Source code
├── include/            # C++ Headers
├── analysis/           # Python Analysis
│   ├── lib/            # Modular Analysis Library
│   │   ├── loader.py
│   │   ├── stats.py
│   │   └── viz.py
│   └── run_analysis.py # Main Analysis Script
├── results/            # Simulation Output
│   ├── raw/            # CSV Data
│   └── comprehensive_analysis/ # Reports & Plots
└── Makefile            # Build System
```

## How to Run

1. **Build Simulator:**
   ```bash
   make clean && make
   ```

2. **Run Simulation (Batch):**
   ```bash
   ./out/bin/simulator --batch
   ```

3. **Run Analysis:**
   ```bash
   source venv/bin/activate
   cd analysis
   python run_analysis.py
   ```

## Future Work
- **Unit Tests:** Expand C++ test suite for new policies.
- **Config:** Move hardcoded parameters (aging threshold, etc.) to a config file.
- **GUI:** Develop a web-based dashboard for real-time visualization (Phase 5?).
