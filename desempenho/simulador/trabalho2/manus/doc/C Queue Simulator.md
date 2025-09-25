# C Queue Simulator

## Overview

This project implements an event-driven queue simulator in C, designed to model a system with multiple logical queues served by a single server. It supports configurable decision policies for server allocation, batch simulation runs, and detailed metric sampling for analysis. The simulator also includes a test harness to validate the implementation of Little's Law.

## Features

*   **Multi-Queue System:** Simulates three independent logical queues.
*   **Configurable Decision Policies:** Supports different strategies for selecting which queue to serve next, including:
    *   Largest number of waiting customers.
    *   Largest average waiting time.
    *   Customer who has waited the longest.
*   **Batch Mode:** Automates simulations across various occupancy (rho) values and random seeds.
*   **Detailed Metric Sampling:** Records key performance indicators (KPIs) like E[N], E[W], queue sizes, measured lambda, and measured occupancy at regular intervals.
*   **CSV Output:** Generates detailed CSV files for each simulation run, suitable for post-processing and analysis.
*   **Little's Law Validation:** Includes a test harness to verify the accuracy of Little's Law calculations.
*   **Modular Design:** Code is structured into modular functions with clear responsibilities and `camelCase` naming conventions.

## Project Structure

```
c_simulator/
├── src/
│   ├── main.h             # Header file with common definitions and function prototypes
│   ├── main.c             # Single simulation run executable
│   ├── batch_main.c       # Batch simulation run executable
│   └── test_harness.c     # Test harness for Little's Law validation
├── Makefile             # Build script for the simulator and test harness
├── config.txt           # Sample configuration file for queue service rates (mu)
└── README.md            # This documentation file
```

## Building the Project

To build the simulator, batch runner, and test harness, navigate to the `c_simulator` directory and run `make`:

```bash
cd c_simulator
make
```

This will create executables in the `bin/` directory:

*   `bin/simulator`: For running a single simulation.
*   `bin/batch_simulator`: For running multiple simulations in batch mode.
*   `bin/test_harness`: For validating Little's Law across scenarios.

## Usage

### 1. Single Simulation Run

To run a single simulation, use the `simulator` executable. You need to provide the global service rate (`mu_global`), the occupancy (`rho`) for each of the three queues, a random `seed`, and the `output_file.csv` path.

Example:

```bash
./bin/simulator <mu_global> <rho_fila0> <rho_fila1> <rho_fila2> <seed> <output_file.csv>

# Example with mu=1.0, rho=0.8 for all queues, seed=1234, output to results/single_run.csv
./bin/simulator 1.0 0.80 0.80 0.80 1234 results/single_run.csv
```

Or, you can use the `run` target in the Makefile:

```bash
make run
```

### 2. Batch Simulation Run

To run simulations in batch mode, use the `batch_simulator` executable. This allows you to specify multiple `rho` values and `seeds`.

Usage:

```bash
./bin/batch_simulator <mu_global> <politica_id> <num_rhos> [rho1 rho2 ...] <num_seeds> [seed1 seed2 ...] <output_dir>
```

*   `<mu_global>`: Global service rate for all queues.
*   `<politica_id>`: ID of the decision policy to use:
    *   `0`: `politicaMaiorFila` (Largest Queue)
    *   `1`: `politicaMaiorTempoEsperaMedio` (Largest Average Waiting Time)
    *   `2`: `politicaClienteMaisAntigo` (Oldest Customer)
*   `<num_rhos>`: Number of rho values to test.
*   `[rho1 rho2 ...]`: List of rho values (e.g., `0.80 0.90 0.95 0.999`). Each rho value will be applied to all queues.
*   `<num_seeds>`: Number of random seeds to use.
*   `[seed1 seed2 ...]`: List of random seeds (e.g., `123 456 789`).
*   `<output_dir>`: Directory where CSV output files will be saved.

Example:

```bash
# Example with mu=1.0, policy=Largest Queue, rhos=0.8, 0.9, 0.95, 0.999, seeds=123, 456, 789, output to results/
./bin/batch_simulator 1.0 0 4 0.80 0.90 0.95 0.999 3 123 456 789 results/
```

Or, you can use the `batch_run` target in the Makefile:

```bash
make batch_run
```

### 3. Test Harness for Little's Law Validation

The `test_harness` executable runs batch simulations and then calculates statistics on the `littleError` metric to validate the simulator's adherence to Little's Law. It generates a proof file for each scenario.

Usage:

```bash
./bin/test_harness <mu_global> <politica_id> <num_rhos> [rho1 rho2 ...] <num_seeds> [seed1 seed2 ...] <output_dir> <tolerance>
```

*   `<mu_global>`, `<politica_id>`, `<num_rhos>`, `[rho1 rho2 ...]`, `<num_seeds>`, `[seed1 seed2 ...]`, `<output_dir>`: Same as for `batch_simulator`.
*   `<tolerance>`: The maximum acceptable absolute mean `littleError` for a scenario (e.g., `0.001`).

Example:

```bash
# Example with mu=1.0, policy=Largest Queue, rhos=0.8, 0.9, 0.95, 0.999, seeds=123, 456, 789, output to results/, tolerance=0.001
./bin/test_harness 1.0 0 4 0.80 0.90 0.95 0.999 3 123 456 789 results/ 0.001
```

Or, you can use the `test_run` target in the Makefile:

```bash
make test_run
```

## Configuration File (`config.txt`)

The `config.txt` file is a placeholder for future enhancements where `mu` values could be read per queue. Currently, `mu_global` is passed as a command-line argument and applied uniformly. The sample `config.txt` demonstrates how per-queue `mu` values could be specified if the simulator were extended to read them.

```
# Sample Configuration File for C Simulator
# Each line represents the service rate (mu) for a queue.
# The number of lines should match NUM_FILAS defined in main.h (currently 3).
# Example: mu for Queue 0, mu for Queue 1, mu for Queue 2

1.0
1.0
1.0
```

## Output Files

All simulation output CSVs and proof files from the test harness will be stored in the specified `<output_dir>` (e.g., `results/`).

*   `results_rho_X.XXX_seed_Y.csv`: Individual simulation results for a given rho and seed.
*   `proof_rho_X.XXX.txt`: Validation proof file for a given rho scenario, summarizing `littleError` statistics.

## Future Enhancements

*   Implement reading per-queue `mu` values from `config.txt`.
*   Add more sophisticated queue selection policies.
*   Implement a more robust event scheduler (e.g., a min-priority heap).
*   Extend the test harness to include aggregation of results across seeds for each scenario and generate a summary CSV.


