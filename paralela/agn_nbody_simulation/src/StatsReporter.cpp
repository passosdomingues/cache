/**
 * @file StatsReporter.cpp
 * @brief Formatted terminal output — table headers, progress rows, and summaries.
 */

#include "StatsReporter.hpp"
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>
#include <fstream>
#include <filesystem>

// ── ANSI colour codes (gracefully ignored by terminals that don't support them)
static constexpr const char* BOLD    = "\033[1m";
static constexpr const char* CYAN    = "\033[36m";
static constexpr const char* YELLOW  = "\033[33m";
static constexpr const char* GREEN   = "\033[32m";
static constexpr const char* RED     = "\033[31m";
static constexpr const char* MAGENTA = "\033[35m";
static constexpr const char* RESET   = "\033[0m";

// ── Column widths ─────────────────────────────────────────────────────────────
static constexpr int W_STEP  = 7;
static constexpr int W_TIME  = 12;
static constexpr int W_ENERGY = 17;
static constexpr int W_DRIFT  = 11;

// ─────────────────────────────────────────────────────────────────────────────

StatsReporter::StatsReporter(const SimulationConfig& config, int numRanks)
    : m_config(config), m_numRanks(numRanks) {}

// ─────────────────────────────────────────────────────────────────────────────

void StatsReporter::openLogFile() {
    if (!m_config.writeOutput) return;
    namespace fs = std::filesystem;
    fs::create_directories(m_config.outputDir);
    const std::string path = m_config.outputDir + "/energy_log.csv";
    m_logFile.open(path);
    if (m_logFile.is_open()) {
        m_logFile << "step,time,kinetic_energy,potential_energy,total_energy,drift_pct\n";
    }
}

// ─────────────────────────────────────────────────────────────────────────────

void StatsReporter::logEnergy(int step, double time,
                               double kineticE, double potentialE, double drift) {
    if (!m_logFile.is_open()) return;
    m_logFile << std::fixed << std::setprecision(8)
              << step        << ","
              << time        << ","
              << kineticE    << ","
              << potentialE  << ","
              << (kineticE + potentialE) << ","
              << drift       << "\n";
    m_logFile.flush();
}

// ─────────────────────────────────────────────────────────────────────────────

void StatsReporter::printHeader() const {
    const std::string line80(80, '=');
    const std::string sep(80, '-');

    std::cout << "\n"
              << BOLD << CYAN << line80 << RESET << "\n"
              << BOLD << "  🌌  AGN N-Body Simulation — Active Galactic Nucleus\n"
              << RESET
              << "       Parallel gravitational direct-summation with Leapfrog/KDK\n"
              << "\n"
              << "  CPU   : Intel Core i7-8565U  (4 cores / 8 HT threads  |  AVX2 + FMA)\n"
              << "  MPI   : " << BOLD << m_numRanks << RESET << " processes"
              << "  │  Particles: " << BOLD << m_config.numParticles << RESET
              << "  │  Steps: "    << BOLD << m_config.numSteps     << RESET
              << "  │  dt = "      << BOLD << m_config.dt           << RESET << "\n"
              << "  BH mass: "  << m_config.blackHoleMass
              << "  │  Softening ε = " << m_config.softeningEps
              << "  │  Seed = " << m_config.randomSeed << "\n"
              << BOLD << CYAN << line80 << RESET << "\n";

    // ── Column headers ────────────────────────────────────────────────────────
    std::cout << BOLD
              << std::setw(W_STEP)   << "Step"   << "  │"
              << std::setw(W_TIME)   << "Time"    << "  │"
              << std::setw(W_ENERGY) << "Kin. Energy"  << "  │"
              << std::setw(W_ENERGY) << "Pot. Energy"  << "  │"
              << std::setw(W_ENERGY) << "Total Energy" << "  │"
              << std::setw(W_DRIFT)  << "Drift (%)"
              << RESET << "\n";

    printSeparator();
}

// ─────────────────────────────────────────────────────────────────────────────

void StatsReporter::printSeparator() const {
    std::cout << std::string(80, '-') << "\n";
}

// ─────────────────────────────────────────────────────────────────────────────

void StatsReporter::printStep(int    step,
                               double time,
                               double kineticE,
                               double potentialE) {

    // Potential energy was double-counted (each pair counted from both sides)
    // so we divide by 2 here.
    const double pe    = potentialE * 0.5;
    const double total = kineticE + pe;

    // Initialise reference energy on step 0
    if (!m_hasInitialEnergy) {
        m_initialEnergy    = total;
        m_hasInitialEnergy = true;
    }

    // Relative energy drift as percentage
    double drift = 0.0;
    if (m_initialEnergy != 0.0) {
        drift = std::abs(total - m_initialEnergy) / std::abs(m_initialEnergy) * 100.0;
    }

    // Colour the drift column: green < 0.1%, yellow < 1%, red >= 1%
    const char* driftColor = (drift < 0.1) ? GREEN : (drift < 1.0 ? YELLOW : RED);

    std::cout << std::scientific << std::setprecision(6)
              << std::setw(W_STEP)   << step   << "  │"
              << std::setw(W_TIME)   << std::fixed << std::setprecision(4) << time << "  │"
              << std::setw(W_ENERGY) << std::scientific << std::setprecision(5) << kineticE   << "  │"
              << std::setw(W_ENERGY) << pe    << "  │"
              << std::setw(W_ENERGY) << total  << "  │"
              << driftColor
              << std::setw(W_DRIFT)  << std::fixed << std::setprecision(4) << drift
              << RESET << "\n";

    std::cout.flush();

    // Also write to the energy log CSV (no-op if file not open)
    logEnergy(step, time, kineticE, pe, drift);
}

// ─────────────────────────────────────────────────────────────────────────────

void StatsReporter::printSummary(double wallTime,
                                  int    numParticles,
                                  int    numSteps) const {
    // Throughput in millions of (particle × step) per second
    const double throughput =
        static_cast<double>(numParticles) * numSteps / wallTime / 1.0e6;

    printSeparator();
    std::cout << BOLD << GREEN
              << "  ✔  Simulation complete\n" << RESET
              << "     Wall time   : " << BOLD << std::fixed << std::setprecision(3)
              << wallTime << " s" << RESET << "\n"
              << "     Throughput  : " << BOLD << std::setprecision(2)
              << throughput << " M·(part×step)/s" << RESET << "\n"
              << "     MPI ranks   : " << BOLD << m_numRanks << RESET << "\n"
              << "     Particles/rank: " << BOLD
              << numParticles / m_numRanks << RESET << "\n";
    std::cout << std::string(80, '=') << "\n\n";
}

// ─────────────────────────────────────────────────────────────────────────────

void StatsReporter::printBenchmarkResult(int numRanks, double wallTime) const {
    const double throughput =
        static_cast<double>(m_config.numParticles) * m_config.numSteps
        / wallTime / 1.0e6;

    std::cout << BOLD << MAGENTA
              << "  [BENCHMARK]  NP=" << numRanks << RESET
              << "  │  Time: " << BOLD << std::fixed << std::setprecision(3)
              << wallTime << " s" << RESET
              << "  │  Throughput: " << BOLD
              << std::setprecision(2) << throughput << " M(part·step)/s\n" << RESET;
}
