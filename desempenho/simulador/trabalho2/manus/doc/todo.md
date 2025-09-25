## Todo List

### Phase 1: C Simulator Core Refactoring and Multi-Queue Implementation
- [x] Task 1.1: Project Setup and Header: Create a new project directory. Add the required header block to `main.c` (or a new C file). Create `Makefile`.
- [x] Task 1.2: Modularize `main.c`: Break down `main.c` into smaller, atomic functions. Encapsulate `aleatorio` and `exponencial` functions. Ensure `camelCase` naming conventions and detailed block comments.
- [x] Task 1.3: Multi-Queue Data Structure: Define a `typedef struct` for a single queue, including its length, waiting times, and Little's Law metrics. Create an array or linked list of these structures to represent multiple queues.
- [x] Task 1.4: Event Management: Adapt the event loop to handle events from multiple queues. This might involve a priority queue for events.
- [x] Task 1.5: Queue Selection Policies: Implement the three specified queue selection policies as functions that can be called via a function pointer.
- [x] Task 1.6: Configuration Handling: Implement logic to read `mu` values per queue from command-line arguments or a configuration file.

### Phase 2: C Simulator Batch Mode, Sampling, and Validation
- [x] Task 2.1: Batch Mode Logic: Implement the overall batch mode structure to iterate through `rho` values and seeds.
- [x] Task 2.2: Arrival Rate Calculation: Implement the calculation of `lambda` for each queue based on `rho` and `mu`.
- [x] Task 2.3: Metric Sampling: Integrate the 10-second sampling mechanism to record all required metrics (`timestamp`, `sampleIndex`, `EN`, `EW`, `queueSizes`, `measuredLambda`, `measuredOccupancy`, `littleError`).
- [x] Task 2.4: CSV Output Generation: Implement functions to write simulation results to CSV files for each seed and scenario, and an aggregated summary CSV.
- [x] Task 2.5: Test Harness: Develop the test harness to run simulations, compute `littleError` statistics, and assert against the tolerance. Generate proof files.
- [x] Task 2.6: Documentation: Update `README` with build instructions, usage examples, and output paths.

### Phase 3: Build System and Documentation for C Simulator
- [x] Task 3.1: Finalize Makefile: Ensure the Makefile correctly builds the simulator and test harness.
- [x] Task 3.2: Create Sample Config File: Provide a sample configuration file for `mu` values.
- [x] Task 3.3: Write README: Document usage examples, build instructions and output paths.

### Phase 4: Deliver C Simulator code and documentation
- [x] Task 4.1: Package and Deliver: Provide all C sources, Makefile, sample config, and README to the user.

