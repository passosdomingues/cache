# M/M/1 Multi-Queue Simulator and Analysis Suite

## Project Overview

This project provides a comprehensive suite for simulating and analyzing a multi-queue, single-server queueing system. It consists of two main components:

1.  **C Simulator**: A low-level, event-driven simulator written in C for high performance. It simulates three queues served by a single server with configurable scheduling policies.
2.  **Python Analysis Tool**: A Python package for statistical analysis, machine learning modeling, and visualization of the simulation output data.

**Author**: Rafael Passos Domingues
**Last Update**: 2025 Sep 25 14h36

## C Simulator

The simulator models a system with three independent M/M/1-style queues. Arrivals for each queue are Poisson processes, and the single server has an exponentially distributed service time.

### Features

-   **Event-Driven Architecture**: Efficiently processes events in chronological order.
-   **Configurable Policies**: The server's queue selection logic is determined by a function pointer, allowing for easy extension.
    -   `policyOne`: Serves the longest queue.
    -   `policyTwo`: Serves the queue with the highest average wait time.
    -   `policyThree`: Serves the queue with the globally oldest customer.
-   **Batch Mode**: Runs simulations for a range of server occupancy rates (`rho`).
-   **Detailed Metrics**: Outputs CSV files with time-series data for `E[N]`, `E[W]`, queue sizes, and Little's Law error.
-   **Validation**: Includes a test harness to verify Little's Law (`E[N] = lambda * E[W]`) across all runs.

### Build Instructions

A `Makefile` is provided. To build the simulator and the test harness, run:

```sh
make
