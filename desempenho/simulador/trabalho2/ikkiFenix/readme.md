# Advanced Queueing System Simulator

## Overview

This project implements a **modular, high-performance queueing system simulator** in C++, designed for academic and research purposes. It models complex queue behaviors, customizable policies, and comprehensive measurement capabilities, supporting development, testing, and analysis workflows.

## Architecture

### Core Modules

- **Simulator**: Main orchestrator, controlling initialization, execution, and finalization.
- **Queue**: Supports different queue types, with enqueue, dequeue, size operations.
- **Policy**: Interface for queue management policies; concrete classes include FIFO, LIFO, PriorityPolicy.
- **Event Management**: Schedules and processes discrete events (Arrival, Departure).
- **Random Number Generator (RNG)**: Encapsulates stochastic behavior.
- **Configuration**: Loads parameters from external files for flexible setup.
- **Measurement Window**: Records runtime metrics, enabling performance analysis.
- **Little's Law Module**: Validates theoretical queuing results.

### Testing Suite

Includes unit tests for each critical component:
- `test_simulator.cpp`
- `test_queue.cpp`
- `test_policies.cpp`
- `test_events.cpp`
- `test_littles_law.cpp`
- `test_measurement_window.cpp`
- `test_rng.cpp`

Tests are run with the debug build, ensuring reliability.

## Build System

- Supports **release**, **debug**, and **profile** configurations with appropriate flags.
- Automates directory and dependency management.
- Provides targets for:
  - Running simulations (`run`)
  - Batch runs (`run-batch`)
  - Testing (`run-tests`)
  - Profiling and memory checks (`valgrind-check`)
  - Code formatting and linting (`format`, `lint`)
- Uses **Makefile** for portability and automation.

## Simulation Workflow

1. **Initialization**: Loads configs, sets RNG, initializes queue and policies.
2. **Event Scheduling**: Schedules initial arrival events.
3. **Execution Loop**:
   - Executes scheduled events.
   - Arrival events enqueue items, schedule departures.
   - Departure events dequeue items, schedule next arrivals.
4. **Measurement**: Collects performance data via `MeasurementWindow`.
5. **Post-processing**: Uses Python scripts for analysis, validating results with Little's Law.

## Usage

make # Compile all modes (release by default)
make run # Run simulation with current config
make run-tests # Execute all unit tests
make analysis # Run post-simulation Python analysis


The system is ready for extension—new policies, events, and analysis modules can be easily integrated.

## Directory Structure

src/ # Source code
tests/ # Unit tests
config/ # Config files
analysis/ # Python analytics scripts
build/ # Build artifacts
out/bin/ # Compiled executables
results/ # Simulation results


## Dependencies

- **C++17 compiler** (g++, clang++)
- **Python 3.x** for analysis
- Standard build tools (`make`, `gcc`)

## Contribution

Contributions welcome via pull requests. Follow existing coding standards and testing practices.

---

*This documentation aims to provide a clear, comprehensive guide to the simulator system, suitable for academic publication or developer onboarding.*
