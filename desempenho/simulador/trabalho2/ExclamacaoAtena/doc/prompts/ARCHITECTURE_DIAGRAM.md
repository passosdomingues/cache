# Project Chronos - Architecture Diagram

## Overview

This diagram represents the complete architecture of Project Chronos: Adaptive Stochastic Control & Queueing Analysis Framework.

## Key Statistics

- **11 Concrete Scheduling Policies**
- **2 Meta-Policies** (PolicyOrchestrator, MarkovSwitching)
- **4 Occupancy Scenarios**: ρ ∈ {0.8, 0.9, 0.95, 0.999}
- **44 Total Simulation Configurations** (11 policies × 4 scenarios)
- **28 Default Batch Runs** (7 primary policies × 4 scenarios)
- **7 Test Suites** with 60+ individual tests

## Architecture Components

### 1. Core Interface
- **SchedulingPolicy**: Abstract base class for all policies
- **SystemState**: State representation passed to policies

### 2. Concrete Policies (11 Total)

#### Basic Policies (4)
1. `LongestQueuePolicy` - Select queue with most packets
2. `ShortestQueuePolicy` - Select queue with fewest packets
3. `RoundRobinPolicy` - Cycle through queues sequentially
4. `StrictPriorityPolicy` - Always serve higher priority queues

#### Advanced Policies (3)
5. `MaxAverageWaitPolicy` - Select queue with longest average wait
6. `OldestPacketPolicy` - Serve queue with oldest packet
7. `AgingPolicy` - Age-based priority adjustment

#### Optimization Policies (4)
8. `SallesUtilityPolicy` - Utility-based loss minimization
9. `CMuRulePolicy` - c×μ index optimization
10. `WeightedRoundRobinPolicy` - Weighted quantum scheduling
11. `WhittleIndexPolicy` - Whittle index for restless bandits

### 3. Meta-Policies (2)

#### PolicyOrchestrator
- **Min-Heap based decision making**
- Factory pattern for policy creation
- Selects shortest queue using priority queue

#### MarkovSwitchingPolicy
- State-dependent policy switching
- Loads policy matrix from CSV
- Discretizes system state for lookup

### 4. Simulation Core
- **Simulator**: Event-driven simulation engine with Min-Heap event queue
- **Queue**: Multi-class queue with service rates, weights, utility types
- **SimulationConfig**: Configuration with shared_ptr to policy

### 5. Occupancy Scenarios

Four load levels tested for each policy:
- **ρ = 0.800**: Low load (stable)
- **ρ = 0.900**: Medium load
- **ρ = 0.950**: High load (near saturation)
- **ρ = 0.999**: Critical load (stress test)

### 6. Analysis Pipeline
- **CSV Output**: 44 result files (1 per configuration)
- **residual_analysis.py**: Statistical validation
- **train_policy.py**: ML-based policy optimization
- **policy_matrix.csv**: State-to-policy mapping for Markov switching

### 7. Test Coverage
- `test_policies.cpp` - All 11 policies + orchestrator
- `test_simulator.cpp` - Full simulation integration
- `test_queue.cpp` - Queue operations
- `test_events.cpp` - Event management
- `test_rng.cpp` - RNG determinism
- `test_littles_law.cpp` - Theoretical validation
- `test_measurement_window.cpp` - Statistical tracking

## File Locations

- **Source**: [diagram.dot](file:///home/rafael/.gemini/antigravity/scratch/ikkiFenix/doc/diagram.dot)
- **PNG**: [architecture.png](file:///home/rafael/.gemini/antigravity/scratch/ikkiFenix/doc/architecture.png)
- **SVG**: [architecture.svg](file:///home/rafael/.gemini/antigravity/scratch/ikkiFenix/doc/architecture.svg)

## Viewing the Diagram

### Command Line (PNG)
```bash
xdg-open doc/architecture.png
```

### Command Line (SVG)
```bash
firefox doc/architecture.svg
# or
inkscape doc/architecture.svg
```

### Regenerate Diagram
```bash
cd doc
dot -Tpng diagram.dot -o architecture.png
dot -Tsvg diagram.dot -o architecture.svg
```

## Color Coding

- **Blue (#3498db)**: Core interfaces
- **Green (#a8e6cf - #a9dfbf)**: Concrete policies
- **Purple (#d7bde2)**: Meta-policies
- **Orange (#f5cba7)**: Simulation core
- **Red (#f1948a)**: Occupancy scenarios
- **Teal (#a3e4d7)**: Analysis pipeline
- **Yellow (#fdebd0)**: Test suites

## Key Relationships

1. **Inheritance**: All policies inherit from `SchedulingPolicy`
2. **Composition**: Simulator holds shared_ptr to policy
3. **Factory**: PolicyOrchestrator creates policies by name
4. **Orchestration**: MarkovSwitching contains multiple sub-policies
5. **Feedback Loop**: Analysis generates policy matrices that feed Markov policy

## Notes

- All 11 concrete policies can be tested with 4 occupancy scenarios = 44 combinations
- Default batch mode runs 7 primary policies for quick validation = 28 runs
- PolicyOrchestrator demonstrates Min-Heap architecture requested
- System uses shared_ptr for policy flexibility in configuration
- Deterministic with fixed seed (42) for reproducibility

---

**Last Updated**: 2025-11-21  
**Diagram Type**: DOT (Graphviz)  
**Image Formats**: PNG (612KB), SVG (50KB)
