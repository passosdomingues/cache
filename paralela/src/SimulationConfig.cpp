/**
 * @file SimulationConfig.cpp
 * @brief CLI argument parser and config validator implementation.
 */

#include "SimulationConfig.hpp"
#include <iostream>
#include <stdexcept>
#include <cstdlib>
#include <string>

// ─────────────────────────────────────────────────────────────────────────────

SimulationConfig SimulationConfig::parse(int argc, char* argv[]) {
    SimulationConfig cfg;

    for (int i = 1; i < argc; ++i) {
        std::string arg(argv[i]);

        // ── Print help and exit ──────────────────────────────────────────────
        if (arg == "--help" || arg == "-h") {
            printHelp();
            std::exit(EXIT_SUCCESS);
        }

        // ── Boolean flags ────────────────────────────────────────────────────
        if (arg == "--no-output") {
            cfg.writeOutput = false;
            continue;
        }
        if (arg == "--benchmark") {
            cfg.benchmarkMode = true;
            cfg.writeOutput   = false;
            continue;
        }

        // ── Value flags (require a following argument) ───────────────────────
        auto requireNext = [&](const std::string& name) -> std::string {
            if (i + 1 >= argc) {
                throw std::invalid_argument("Flag " + name + " requires a value.");
            }
            return std::string(argv[++i]);
        };

        if (arg == "--particles") {
            cfg.numParticles = std::stoi(requireNext("--particles"));
        } else if (arg == "--steps") {
            cfg.numSteps = std::stoi(requireNext("--steps"));
        } else if (arg == "--dt") {
            cfg.dt = std::stod(requireNext("--dt"));
        } else if (arg == "--bh-mass") {
            cfg.blackHoleMass = std::stod(requireNext("--bh-mass"));
        } else if (arg == "--eps") {
            cfg.softeningEps = std::stod(requireNext("--eps"));
        } else if (arg == "--seed") {
            cfg.randomSeed = static_cast<unsigned>(std::stoul(requireNext("--seed")));
        } else if (arg == "--report-interval") {
            cfg.reportInterval = std::stoi(requireNext("--report-interval"));
        } else {
            throw std::invalid_argument("Unknown argument: " + arg
                                        + "  (use --help for usage)");
        }
    }

    cfg.validate();
    return cfg;
}

// ─────────────────────────────────────────────────────────────────────────────

void SimulationConfig::printHelp() {
    std::cout << R"(
Usage: mpirun -np <P> agn_simulation [OPTIONS]

Parallel N-body simulation of an Active Galactic Nucleus (AGN).
Distributes N particles across P MPI processes using direct-summation gravity
with Leapfrog (KDK) integration.

OPTIONS
  --particles  <int>    Total number of bodies (default: 1000)
  --steps      <int>    Number of integration steps (default: 500)
  --dt         <float>  Timestep size in sim. units (default: 0.02)
  --bh-mass    <float>  Black hole mass in sim. units (default: 50000)
  --eps        <float>  Gravitational softening length (default: 0.5)
  --seed       <int>    Random seed for reproducibility (default: 42)
  --report-interval <int>  Steps between table rows (default: 50)
  --no-output           Disable CSV snapshot writing
  --benchmark           Benchmark mode: minimal output, no CSV
  --help                Print this message and exit

EXAMPLES
  mpirun -np 8 ./build/agn_simulation --particles 2000 --steps 1000
  mpirun -np 4 ./build/agn_simulation --benchmark
  make run NP=8 N=500 STEPS=200
  make benchmark

HARDWARE NOTES (i7-8565U)
  Optimal NP: 8 (= logical threads)  for compute-bound simulations.
  For N >= 5000, consider NP=4 to reduce MPI_Allgather overhead.
)" << std::endl;
}

// ─────────────────────────────────────────────────────────────────────────────

void SimulationConfig::validate() const {
    if (numParticles < 2)
        throw std::invalid_argument("--particles must be >= 2 (at least 1 BH + 1 star)");
    if (numSteps < 1)
        throw std::invalid_argument("--steps must be >= 1");
    if (dt <= 0.0)
        throw std::invalid_argument("--dt must be positive");
    if (softeningEps <= 0.0)
        throw std::invalid_argument("--eps must be positive");
    if (blackHoleMass <= 0.0)
        throw std::invalid_argument("--bh-mass must be positive");
    if (diskRadiusMin >= diskRadiusMax)
        throw std::invalid_argument("diskRadiusMin must be < diskRadiusMax");
    if (reportInterval < 1)
        throw std::invalid_argument("--report-interval must be >= 1");
}
