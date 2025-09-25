# Analysis and Recommendations for C Simulator and Python Analysis Package

## 1. Current State of Provided Files

### 1.1. `main.c` (C Simulator)

The `main.c` file implements a basic event-driven simulation of a single-server queuing system. Key features include:

*   **Event-Driven Simulation:** The simulation progresses based on events (arrivals and departures) rather than fixed time steps.
*   **Random Number Generation:** It uses `rand()` and `exponencial()` functions to generate pseudo-random numbers for inter-arrival and service times, following an exponential distribution.
*   **Queuing Metrics:** It calculates and prints several basic queuing metrics, such as maximum queue length, average inter-arrival time, average service time, and server utilization.
*   **Little's Law Implementation:** It includes calculations for E[N] (average number of requests in the system) and E[W] (average waiting time) using the area under the curve approach, and computes the `littleError` to validate Little's Law.
*   **User Input:** It prompts the user to input the mean inter-arrival time and mean service time.
*   **Language:** The code and comments are primarily in Portuguese.

### 1.2. `rafaPlots.py` (Python Analysis Package)

The `rafaPlots.py` file is a Python script designed for scientific analysis and visualization of queue simulation data. Its main functionalities include:

*   **Data Loading:** It can load simulation data from CSV files, expecting specific column names like 'Tempo', 'NumeroMedioRequisicoes', 'TempoMedioEspera', 'Ocupacao', and 'TamanhoFila'.
*   **Visualization:** It generates various plots using `seaborn` and `matplotlib`, including:
    *   Individual E[N] and E[W] over time for each scenario.
    *   Comparative E[N] and E[W] plots across different scenarios.
    *   Trend analysis plots for E[N] and E[W] with curve fitting (linear, exponential, logarithmic).
    *   Queue size vs. utilization plots.
    *   Distribution and evolution of utilization over time.
    *   Correlation matrices.
    *   Scatter plots showing relationships between E[N], E[W], queue size, and utilization.
*   **Analytical Model Adjustment:** It attempts to fit analytical models for E[N] and E[W] as functions of `rho` (utilization) and `mu` (service rate), comparing them against M/M/1 theoretical values.
*   **Output Management:** It creates a directory structure for saving generated plots and a text file for analytical expressions.
*   **Language:** The code, comments, and plot titles are primarily in Portuguese.

## 2. Major Changes Required for the C Simulator

The `pasted_content.txt` outlines significant enhancements for the C simulator, transforming it from a single-queue system to a multi-queue, policy-driven simulator with robust batch processing and validation capabilities. The major changes are:

1.  **Multi-Queue System:** Implement three independent logical queues served by a single server. This requires a new data structure for each queue, holding its specific state and statistics.
2.  **Configurable Decision Policy:** Introduce a mechanism to decide which queue to serve next using function pointers. This will allow for dynamic policy selection.
3.  **Built-in Policies:** Implement three specific decision policies:
    *   Serve the queue with the largest number of waiting customers.
    *   Serve the queue with the largest average waiting time.
    *   Serve the queue containing the customer who has waited the longest.
4.  **Modularity and Readability:** Refactor the existing code into modular functions with descriptive `camelCase` identifiers. Add detailed block comments for functions and `typedef struct` fields using `@param` and `@return` tags in English.
5.  **Batch Mode and Occupancy Scenarios:** Implement a batch mode to run simulations for specified `rho` values (0.80, 0.90, 0.95, 0.999). Derive `lambda` from `rho` and `mu`.
6.  **Configurable Service Rate (`mu`):** Allow `mu` to be supplied per queue via command-line arguments or a configuration file.
7.  **Sampling and Metrics:** Sample and record metrics every 10 seconds for 24 hours of simulated time (86400 seconds). Metrics to record include `timestamp`, `sampleIndex`, `EN`, `EW`, `queueSizes` (per queue), `measuredLambda` (per queue), `measuredOccupancy` (per queue), and `littleError`.
8.  **Multiple Seeds and Output Files:** Support multiple independent seeds. For each seed and scenario, generate a CSV file with a filename encoding the scenario and seed. Also, produce an aggregated summary CSV per scenario combining results from all seeds.
9.  **Measurement and Validation:** Compute `measuredLambda`, `EN`, `EW`, and `littleError` as specified. Implement a test harness to run scenarios across seeds, compute statistical measures (mean, median, std dev, min, max) of `littleError`, and assert that the mean absolute `littleError` is below a configurable tolerance (default 1e-3).
10. **Build System:** Provide a `Makefile` to build the simulator and test harness.
11. **Documentation and Examples:** Include a sample config file, usage examples, and a `README` documenting paths and usage.

## 3. Major Changes Required for the Python Analysis Package

The Python analysis package needs significant expansion to handle the new simulation outputs and perform advanced statistical analysis and machine learning:

1.  **CSV Output Reading:** Adapt the data loading mechanism to read the new CSV file formats, including per-queue metrics and multiple seeds.
2.  **Aggregation Across Seeds:** Implement functionality to aggregate data from multiple seeds for each scenario, allowing for statistical analysis (mean, median, std dev, confidence intervals).
3.  **Stabilization Detection:** Implement automatic stabilization detection using sliding windows and a nonparametric test (e.g., Mann-Whitney U or Kolmogorov-Smirnov) with an adjustable alpha (default 5-sigma acceptance).
4.  **Normality Testing and Transformation:** If data fails normality tests, apply Yeo-Johnson or Box-Cox transformations and show diagnostics before and after transformation.
5.  **Bootstrap-based Error Propagation:** Implement bootstrap resampling across seeds to produce nonparametric confidence intervals for E[N] and E[W]. Offer both nonparametric and transformed parametric estimation.
6.  **Machine Learning Workflow:** Develop a machine learning pipeline including:
    *   **PCA:** For dimensionality reduction.
    *   **K-means:** For unsupervised clustering with automatic `k` selection heuristics.
    *   **Random Forest:** For supervised modeling of policy or scenario labels.
    *   **Model Evaluation:** Use an 80% training / 20% validation split.
    *   **Model Persistence:** Save trained models and metadata.
7.  **Enhanced Plotting:** Generate a wider range of plots:
    *   Boxplots, pairplots, overlays, and time series plots.
    *   E[N] and E[W] over time.
    *   E[N] versus E[W] with overlaid regression and error bands.
    *   E[N] and E[W] as a function of queue sizes and occupancy.
    *   Queue sizes over time.
8.  **Combined Report:** Produce a combined report in HTML or PDF format containing key plots, statistics, and conclusions.
9.  **Packaging and Documentation:** Ensure all Python scripts have docstrings, provide a `requirements.txt`, and update the `README` with usage examples.
10. **Unit Tests:** Include unit tests or small reproducible runs to verify `littleError` is close to zero and store proof files.

## 4. Detailed Implementation Plan

### Phase 1: C Simulator Core Refactoring and Multi-Queue Implementation

*   **Task 1.1: Project Setup and Header:** Create a new project directory. Add the required header block to `main.c` (or a new C file). Create `Makefile`.
*   **Task 1.2: Modularize `main.c`:** Break down `main.c` into smaller, atomic functions. Encapsulate `aleatorio` and `exponencial` functions. Ensure `camelCase` naming conventions and detailed block comments.
*   **Task 1.3: Multi-Queue Data Structure:** Define a `typedef struct` for a single queue, including its length, waiting times, and Little's Law metrics. Create an array or linked list of these structures to represent multiple queues.
*   **Task 1.4: Event Management:** Adapt the event loop to handle events from multiple queues. This might involve a priority queue for events.
*   **Task 1.5: Queue Selection Policies:** Implement the three specified queue selection policies as functions that can be called via a function pointer.
*   **Task 1.6: Configuration Handling:** Implement logic to read `mu` values per queue from command-line arguments or a configuration file.

### Phase 2: C Simulator Batch Mode, Sampling, and Validation

*   **Task 2.1: Batch Mode Logic:** Implement the overall batch mode structure to iterate through `rho` values and seeds.
*   **Task 2.2: Arrival Rate Calculation:** Implement the calculation of `lambda` for each queue based on `rho` and `mu`.
*   **Task 2.3: Metric Sampling:** Integrate the 10-second sampling mechanism to record all required metrics (`timestamp`, `sampleIndex`, `EN`, `EW`, `queueSizes`, `measuredLambda`, `measuredOccupancy`, `littleError`).
*   **Task 2.4: CSV Output Generation:** Implement functions to write simulation results to CSV files for each seed and scenario, and an aggregated summary CSV.
*   **Task 2.5: Test Harness:** Develop the test harness to run simulations, compute `littleError` statistics, and assert against the tolerance. Generate proof files.
*   **Task 2.6: Documentation:** Update `README` with build instructions, usage examples, and output paths.

### Phase 3: Python Analysis Package - Data Handling and Basic Visualization

*   **Task 3.1: Data Loading Refinement:** Modify `rafaPlots.py` to handle the new CSV file formats, including per-queue data and multiple seeds. Create a class or functions for data aggregation.
*   **Task 3.2: Basic Aggregation:** Implement functions to aggregate data across seeds (e.g., calculating mean, median, std dev for all metrics).
*   **Task 3.3: Initial Plotting Updates:** Adapt existing plotting functions to display aggregated data and per-queue metrics. Ensure high-resolution PNG outputs.
*   **Task 3.4: Requirements and Docstrings:** Create `requirements.txt` and add docstrings to all Python functions and classes.

### Phase 4: Python Analysis Package - Advanced Statistics and ML

*   **Task 4.1: Stabilization Detection:** Implement the sliding window and nonparametric test for stabilization detection.
*   **Task 4.2: Normality Testing and Transformation:** Implement normality tests and apply Yeo-Johnson or Box-Cox transformations as needed, with diagnostic plots.
*   **Task 4.3: Bootstrap Error Propagation:** Implement bootstrap resampling for E[N] and E[W] confidence intervals.
*   **Task 4.4: Machine Learning Pipeline:** Implement PCA, K-means (with automatic `k` selection), and Random Forest (with train/validation split). Save models and metadata.
*   **Task 4.5: Enhanced Plotting:** Implement the new plotting requirements (boxplots, pairplots, overlays, regression with error bands, etc.).
*   **Task 4.6: Combined Report Generation:** Develop functionality to generate a combined HTML or PDF report.
*   **Task 4.7: Unit Tests:** Implement unit tests for the Python analysis package, especially for `littleError` validation.

### Phase 5: Final Review and Delivery

*   **Task 5.1: Code Review:** Review both C and Python code for adherence to style guidelines, modularity, and correctness.
*   **Task 5.2: Documentation Review:** Ensure all documentation (`README`, comments, docstrings) is complete and accurate.
*   **Task 5.3: End-to-End Testing:** Perform a full end-to-end test of the C simulator and Python analysis package across all scenarios and seeds.
*   **Task 5.4: Deliverables Packaging:** Package all source files, documentation, examples, and generated reports for delivery.

This plan provides a structured approach to implementing the requested features while maintaining the core functionalities and adhering to the specified constraints. The next step will be to begin the implementation of Phase 1 tasks for the C simulator.

