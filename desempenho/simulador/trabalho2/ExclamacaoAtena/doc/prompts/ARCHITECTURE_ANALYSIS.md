# ikkiFenix Queuing System - Architecture Analysis & Plan Confirmation

**Date:** 2025-11-20  
**Lead Architect:** Antigravity Agent  
**Mission:** Transform ad-hoc queuing simulator into robust stochastic analysis framework

---

## ✅ ARCHITECTURE UNDERSTANDING CONFIRMED

### **System Overview**
The ikkiFenix project is a **discrete-event simulation (DES)** framework for analyzing multi-queue systems with a shared server. It implements:

- **Event-driven simulation** using min-heap priority queue
- **3 parallel queues** competing for a single server
- **Multiple scheduling policies** for queue selection
- **Stochastic arrivals** (Poisson process) and service times (Exponential distribution)
- **Little's Law verification** for steady-state analysis
- **CSV-based data export** for Python post-processing

---

## 📁 CURRENT CODEBASE STRUCTURE

### **C++ Core (Simulation Engine)**

#### **1. RNG System** (`src/rng.cpp`, `include/rng.hpp`)
- **Current State:** Static methods using `std::srand()` and `std::rand()`
- **Seed Management:** `setSeed()` method exists but NOT enforced globally
- **Issue:** ⚠️ **No Singleton pattern** - seed can be set multiple times
- **Issue:** ⚠️ **No hardcoded seed 42** - seed passed from `main.cpp`

#### **2. Event Management** (`src/events.cpp`, `include/events.hpp`)
- Min-heap implementation for event scheduling
- Event types: ARRIVAL, DEPARTURE, SAMPLE
- **Memory:** Uses value semantics (Event structs), no raw pointers ✅

#### **3. Queue System** (`src/queue.cpp`, `include/queue.hpp`)
- `QueueState` class managing packet arrivals/departures
- Tracks: queue length, waiting times, Little's Law metrics
- **Memory:** Uses `std::vector` for packet storage ✅
- Implements measurement windows for statistics

#### **4. Policies** (`src/policies.cpp`, `include/policies.hpp`)
- **Current Implementation:** Function pointers (`PolicyFunction` typedef)
- **Existing Policies:**
  - `LongestQueue`: Select queue with max length
  - `MaxAverageWait`: Select queue with highest avg wait
  - `OldestPacket`: Select queue with oldest head packet
- **Issue:** ⚠️ **No polymorphic base class** - uses function pointers
- **Issue:** ⚠️ **No Round Robin, Strict Priority, Shortest Queue, or Aging**

#### **5. Simulator** (`src/simulator.cpp`, `include/simulator.hpp`)
- Main event loop orchestrator
- **Memory:** ⚠️ Uses **raw pointers** `std::vector<Queue*>` for queues
- CSV output generation with sampling intervals

#### **6. Main Entry Point** (`src/main.cpp`)
- **Batch Mode:** Supports `--batch` flag
- **Current Scenarios:** 
  - Seeds: `{42, 101, 123, 999, 2025}` (5 seeds)
  - Rhos: `{0.80, 0.90, 0.95, 0.999}` ✅ **CORRECT**
  - Policies: `{LONGEST_QUEUE, MAX_AVG_WAIT, OLDEST_PACKET}`
- **Issue:** ⚠️ Multiple seeds used - **violates determinism requirement**

---

### **Python Analysis** (`analysis/run_analysis.py`)

#### **Current State:**
- **958 lines** of monolithic code
- **Comprehensive features:**
  - Statistical analysis (normality tests, correlation)
  - Temporal analysis (rolling windows)
  - Spectral analysis (FFT, PSD, Welch)
  - Machine learning (PCA, t-SNE, clustering, anomaly detection)
  - Feature importance (Random Forest)
  - Visualization (20+ plot types)
- **Issue:** ⚠️ **No modular OOP structure** - all in one file
- **Issue:** ⚠️ **No explicit `np.random.seed(42)`** enforcement
- **Issue:** ⚠️ **No dedicated modules** for loader, stats, viz

---

## ✅ MASTER PROMPT REQUIREMENTS ACKNOWLEDGED

### **Hard Constraints**

#### **1. Determinism (Seed 42)**
- ✅ **Understood:** ALL random number generation MUST use seed 42
- ✅ **Understood:** No `time(NULL)` or dynamic seeds allowed
- ✅ **Understood:** Results must be 100% reproducible across runs
- **Action Required:** Refactor RNG to Singleton with hardcoded seed 42

#### **2. Load Scenarios**
- ✅ **Understood:** Exactly 4 scenarios: ρ ∈ {0.800, 0.900, 0.950, 0.999}
- ✅ **Current Status:** `main.cpp` already has these values
- **Action Required:** Remove multiple seeds, use only seed 42

#### **3. CSV Output Format**
- ✅ **Understood:** Must include columns:
  - `time` (or `timestamp`)
  - `queue_id` (individual queue metrics)
  - `queue_len` (queue lengths)
  - `wait_time` (waiting times)
  - `service_time` (service times)
  - `policy_name` (policy identifier)
- **Action Required:** Verify current CSV output and add missing columns

---

## 📋 EXECUTION PLAN CONFIRMATION

### **PHASE 1: Auditing and Determinism (Core C++)** ✅ READY

#### **[JOB-01] RNG Singleton Audit**
- **Scope:** Refactor `RNG` class to Singleton pattern
- **Changes:**
  - Make constructor private
  - Add `getInstance()` static method
  - Hardcode seed 42 in constructor
  - Remove `setSeed()` public method (or make private)
- **Files:** `src/rng.cpp`, `include/rng.hpp`

#### **[JOB-02] Scenario Standardization**
- **Scope:** Enforce single seed (42) and 4 rho scenarios
- **Changes:**
  - Modify `main.cpp` batch config: `seeds = {42}` only
  - Keep `rhos = {0.80, 0.90, 0.95, 0.999}`
  - Optionally create `config/scenarios.json` for future flexibility
- **Files:** `src/main.cpp`, potentially `config/scenarios.json`

#### **[JOB-03] CSV Header Validation**
- **Scope:** Run dry-run and verify CSV columns
- **Changes:**
  - Add missing columns if needed
  - Ensure policy name is written to CSV
  - Add per-queue metrics (wait_time, service_time per queue)
- **Files:** `src/simulator.cpp`

#### **[JOB-04] Memory Safety Check**
- **Scope:** Replace raw pointers with smart pointers
- **Changes:**
  - `std::vector<Queue*>` → `std::vector<std::unique_ptr<Queue>>`
  - Update all queue access patterns
- **Files:** `src/simulator.cpp`, `include/simulator.hpp`

#### **[JOB-05] Policy Interface (Polymorphism)**
- **Scope:** Create abstract base class for policies
- **Changes:**
  - Create `SchedulingPolicy` abstract base class
  - Pure virtual method: `virtual int selectQueue(const std::vector<Queue*>&, double) = 0`
  - Refactor existing policies to inherit from base class
  - Update `Simulator` to use polymorphic policy pointer
- **Files:** `src/policies.cpp`, `include/policies.hpp`, `src/simulator.cpp`

---

### **PHASE 2: Algorithm Expansion** ✅ READY

#### **[JOB-06] Round Robin (RR)**
- **Logic:** Maintain internal counter, cycle through non-empty queues
- **Implementation:** `class RoundRobinPolicy : public SchedulingPolicy`

#### **[JOB-07] Strict Priority (SP)**
- **Logic:** Queue 0 > Queue 1 > Queue 2 (strict QoS)
- **Implementation:** `class StrictPriorityPolicy : public SchedulingPolicy`

#### **[JOB-08] Shortest Queue First (SQF)**
- **Logic:** Select queue with minimum length (inverse of LONGEST_QUEUE)
- **Implementation:** `class ShortestQueuePolicy : public SchedulingPolicy`
- **Note:** Add deterministic tie-breaking (e.g., lowest queue ID)

#### **[JOB-09] Aging (Starvation Avoidance)**
- **Logic:** If packet waits > threshold (e.g., 10 time units), boost priority
- **Implementation:** `class AgingPolicy : public SchedulingPolicy`
- **Parameters:** Configurable aging threshold

#### **[JOB-10] Data Consistency**
- **Scope:** Ensure all policies write unique identifier to CSV
- **Verification:** Check CSV output includes policy name column

---

### **PHASE 3: Python Refactoring (OOP)** ✅ READY

#### **[JOB-11] Package Structure**
```
analysis/
├── lib/
│   ├── __init__.py
│   ├── loader.py
│   ├── stats.py
│   └── viz.py
├── run_analysis.py (legacy, keep for reference)
└── generate_report.py (new orchestrator)
```

#### **[JOB-12] DataLoader Module**
- **Class:** `LogParser` in `analysis/lib/loader.py`
- **Methods:**
  - `load_csv(file_path)` → DataFrame
  - `filter_warmup(df, warmup_ratio=0.15)` → DataFrame
  - `parse_scenario_metadata(filename)` → dict

#### **[JOB-13] Statistics Module**
- **Class:** `StatsEngine` in `analysis/lib/stats.py`
- **Methods:**
  - `calculate_confidence_interval(data, confidence=0.95)`
  - `verify_littles_law(E_N, lambda_rate, E_W)`
  - `calculate_summary_stats(df)` → dict

#### **[JOB-14] Seed 42 in Python**
- **Scope:** Add `np.random.seed(42)` at module initialization
- **Files:** All Python modules using random sampling

#### **[JOB-15] Visualization Module**
- **Class:** `PlotterFactory` in `analysis/lib/viz.py`
- **Methods:**
  - `plot_timeseries(df, metric, policy, rho)`
  - `plot_boxplot(df, metric, policies, rho)`
  - `plot_histogram(df, metric, policy, rho)`
  - `plot_autocorrelation(df, metric, policy, rho, max_lag=50)`

---

### **PHASE 4: Rich Analysis and Reporting** ✅ READY

#### **[JOB-16] Autocorrelation Analysis**
- **Scope:** ACF plot for queue size to measure system memory
- **Implementation:** Use `statsmodels.tsa.stattools.acf`

#### **[JOB-17] RR vs MAX_AVG_WAIT Comparison**
- **Scope:** Jitter/stability comparison visualization
- **Metrics:** Standard deviation, coefficient of variation

#### **[JOB-18] Transient Detection**
- **Scope:** MSER or visual heuristic for steady-state detection
- **Implementation:** Rolling mean/std analysis

#### **[JOB-19] Automated Report**
- **Scope:** `generate_report.py` orchestrator
- **Output:** Markdown with statistical tables (Mean, Median, 95% CI, Std Dev)

#### **[JOB-20] Final Review**
- **Scope:** Documentation, Doxygen comments, README_REFACTOR.md
- **Deliverables:** Complete documentation suite

---

## 🎯 EXECUTION READINESS

### **Confirmed Understanding:**
✅ Queuing system architecture (DES, 3 queues, shared server)  
✅ Current implementation (function-based policies, raw pointers)  
✅ RNG system (static methods, no Singleton)  
✅ Batch configuration (multiple seeds, 4 rhos)  
✅ Python analysis (monolithic, comprehensive but not modular)  
✅ Master Prompt requirements (Seed 42, 4 scenarios, determinism)  

### **Ready to Execute:**
✅ PHASE 1: C++ Auditing and Determinism (5 jobs)  
✅ PHASE 2: Algorithm Expansion (5 jobs)  
✅ PHASE 3: Python Refactoring (5 jobs)  
✅ PHASE 4: Rich Analysis (5 jobs)  

---

## 🚀 NEXT STEPS

**Awaiting User Confirmation to Proceed with:**

1. **PHASE 1 Implementation** - C++ core refactoring
2. **Verification** - Dry-run and CSV validation
3. **PHASE 2 Implementation** - New scheduling policies
4. **PHASE 3 Implementation** - Python OOP refactoring
5. **PHASE 4 Implementation** - Advanced analytics and reporting

**Ready to begin on your command.**

---

**Status:** ✅ **ANALYSIS COMPLETE - AWAITING GO-AHEAD FOR PHASE 1**
