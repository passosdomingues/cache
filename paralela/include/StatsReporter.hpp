/**
 * @file StatsReporter.hpp
 * @brief Produces formatted, table-aligned terminal output for the simulation.
 *
 * @details
 * StatsReporter is a stateless utility class used exclusively by rank 0 to
 * print progress and benchmark results to stdout.  All methods use std::setw
 * and std::setprecision for column alignment, producing output that looks like:
 *
 * @code
 * ════════════════════════════════════════════════════════════════════════════
 *  🌌  AGN N-Body Simulation — Active Galactic Nucleus
 *      i7-8565U │ 8 MPI ranks │ 1000 particles │ 500 steps
 * ════════════════════════════════════════════════════════════════════════════
 *  Step  │    Time    │   Kin. Energy   │   Pot. Energy   │  Total Energy  │ Drift (%)
 * ────────────────────────────────────────────────────────────────────────────
 *     0  │   0.000000 │  4.837452e+05   │ -9.674903e+05   │ -4.837451e+05  │   0.0000
 *    50  │   1.000000 │  4.839102e+05   │ -9.677012e+05   │ -4.837910e+05  │   0.0095
 *   100  │   2.000000 │  4.840321e+05   │ -9.679441e+05   │ -4.839120e+05  │   0.0014
 * ────────────────────────────────────────────────────────────────────────────
 *  ✔ Simulation complete  │  Wall time: 12.34 s  │  Throughput: 40.5 Mstep·part/s
 * ════════════════════════════════════════════════════════════════════════════
 * @endcode
 *
 * The energy drift column is the key quality metric:
 *   drift = |E(t) - E(0)| / |E(0)| × 100 %
 * For a well-configured Leapfrog integration, this should stay below 0.1%.
 */

#pragma once

#include "SimulationConfig.hpp"
#include <string>
#include <fstream>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Formats and prints simulation progress to the terminal (rank 0 only).
 */
class StatsReporter {
public:

    /**
     * @brief Constructs the reporter and caches initial energy for drift tracking.
     * @param config   Simulation configuration (for metadata display).
     * @param numRanks Total number of MPI processes.
     */
    StatsReporter(const SimulationConfig& config, int numRanks);

    /**
     * @brief Prints the simulation header banner and column headings.
     */
    void printHeader() const;

    /**
     * @brief Opens the energy log CSV file for writing.
     * @details Creates `<outputDir>/energy_log.csv` with a header row.
     *          Should be called once after construction, before printStep().
     */
    void openLogFile();

    /**
     * @brief Logs one energy sample to the CSV file.
     *
     * @param step       Simulation step.
     * @param time       Physical time.
     * @param kineticE   Global kinetic energy.
     * @param potentialE Global potential energy (pre-halved).
     * @param drift      Relative energy drift [%].
     */
    void logEnergy(int step, double time,
                   double kineticE, double potentialE, double drift);

    /**
     * @brief Prints a single progress row for the given timestep.
     *
     * @details
     * If this is step 0, also caches the initial total energy E₀ for drift
     * computation in subsequent calls.
     *
     * @param step      Current simulation step number.
     * @param time      Physical simulation time (step × dt).
     * @param kineticE  Global kinetic energy at this step.
     * @param potentialE Global potential energy at this step.
     */
    void printStep(int step, double time,
                   double kineticE, double potentialE);

    /**
     * @brief Prints the table separator line (─────).
     */
    void printSeparator() const;

    /**
     * @brief Prints the final summary row after the simulation completes.
     *
     * @param wallTime         Total wall-clock time [seconds].
     * @param numParticles     N (for throughput calculation).
     * @param numSteps         Total steps completed.
     */
    void printSummary(double wallTime, int numParticles, int numSteps) const;

    /**
     * @brief Prints the per-process speedup benchmark table.
     *
     * @details
     * Compares this run's timing against a reference (single-process) time.
     * Called in benchmark mode after the simulation loop.
     *
     * @param numRanks  Number of MPI ranks used in this run.
     * @param wallTime  Measured wall time for this run.
     */
    void printBenchmarkResult(int numRanks, double wallTime) const;

private:

    const SimulationConfig& m_config;    ///< Simulation parameters
    int    m_numRanks;                   ///< Number of MPI processes
    double m_initialEnergy{0.0};         ///< E₀ — set on first printStep() call
    bool   m_hasInitialEnergy{false};    ///< Whether E₀ has been set
    std::ofstream m_logFile;             ///< CSV energy log file (rank 0 only)

    static constexpr int COL_WIDTH = 16; ///< Width of energy columns
};
