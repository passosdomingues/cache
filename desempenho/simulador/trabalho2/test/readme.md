# Queueing System Simulator and Analysis Package

**Author:** Rafael Passos Domingues 
**Last Update:** 2025 Oct 7 20h19

## Project Overview

This project provides a comprehensive pipeline for simulating and analyzing queueing systems with three independent queues served by a single server. The implementation consists of two main components:

1. **C Simulator**: Low-level event-driven simulator with configurable scheduling policies
2. **Python Analysis Package**: Statistical analysis and machine learning pipeline for simulation results

## Key Features

### C Simulator
- Three independent M/M/1 queues with single server
- Configurable scheduling policies:
  - Largest queue (number of customers)
  - Largest average waiting time 
  - Longest waiting customer
- Four occupancy scenarios: ρ = 0.80, 0.90, 0.95, 0.999
- 24-hour simulation time with 10-second sampling
- Multiple random seeds for statistical robustness
- Little's Law validation with proof files

### Python Analysis Package
- Statistical analysis and stability detection
- Bootstrap confidence intervals for E[N] and E[W]
- Machine learning pipeline:
  - PCA for dimensionality reduction
  - K-means clustering with automatic k-selection
  - Random Forest for classification and regression
- Comprehensive visualization suite
- HTML/PDF report generation

## Quick Start

### Building and Running C Simulator

```bash
# Clone and build
make all

# Run batch simulations (default configuration)
make run-batch

# Run with memory checking
make valgrind-check


This complete implementation provides:

1. **Low-level C simulator** preserving the original event-driven structure and RNG semantics
2. **Three configurable scheduling policies** with function pointer architecture
3. **Batch execution** for four occupancy scenarios with multiple seeds
4. **Comprehensive Python analysis** with statistical tests, ML pipeline, and visualization
5. **Little's Law validation** with proof files and tolerance checking
6. **Modular, well-commented code** with descriptive naming conventions
7. **Complete build system** with Makefile and dependency management
8. **Extensive documentation** and usage examples

The implementation maintains numerical compatibility with the original `aleatorio` and `exponencial` functions while adding the required features in a modular, maintainable way.
