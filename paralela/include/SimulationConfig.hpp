/**
 * @file SimulationConfig.hpp
 * @brief Simulation parameters with sensible defaults and CLI argument parsing.
 *
 * @details
 * SimulationConfig is a plain-data struct that centralises every tunable
 * parameter of the AGN N-body simulation.  Parameters can be overridden from
 * the command line; the parse() factory method handles this.
 *
 * Physical units used throughout the simulation (natural/dimensionless):
 *   - Length : parsec-like units (L)
 *   - Mass   : solar-mass-like units (M)
 *   - Time   : Myr-like units (T)
 *   - G = 1.0 (absorbed into the unit system)
 *
 * Defaults are tuned to produce stable Keplerian orbits around the central
 * black hole at the given initial conditions for ~500 timesteps.
 */

#pragma once

#include <string>
#include <stdexcept>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief All tunable parameters for the AGN N-body simulation.
 *
 * @details
 * Typical usage:
 * @code
 *   SimulationConfig cfg = SimulationConfig::parse(argc, argv);
 * @endcode
 */
struct SimulationConfig {

    // ── Physical parameters ───────────────────────────────────────────────────

    int    numParticles{1000};    ///< Total number of bodies (BH + stars)
    int    numSteps{500};         ///< Number of integration timesteps
    double dt{0.005};             ///< Timestep size [time units]
                                  ///<   With r_min=8 and M_BH=50000: T_inner ≈ 0.63 → 126 steps/orbit
    double G{1.0};                ///< Gravitational constant (natural units)
    double softeningEps{0.3};     ///< Gravitational softening ε — prevents singularity near BH

    // ── AGN initial conditions ────────────────────────────────────────────────

    double blackHoleMass{50000.0}; ///< Mass of the central supermassive black hole
    double starMass{1.0};          ///< Mass of each stellar body
    double diskRadiusMin{8.0};     ///< Inner edge of the stellar disk [L]
                                   ///<   v_k(r=8) = sqrt(G*M_BH/r) ≈ 79  →  T ≈ 0.63 → dt OK
    double diskRadiusMax{60.0};    ///< Outer edge of the stellar disk [L]
    double diskThickness{1.0};     ///< Half-thickness of the disk in Z [L]

    // ── Output & reporting ────────────────────────────────────────────────────

    int         reportInterval{50};            ///< Steps between progress rows
    std::string outputDir{"data/output"};       ///< Directory for CSV snapshots
    bool        writeOutput{true};             ///< Enable CSV snapshot writing
    bool        benchmarkMode{false};          ///< Suppress detailed output; print only timing
    unsigned    randomSeed{42};               ///< RNG seed for reproducibility

    // ── Factory: build config from CLI arguments ──────────────────────────────

    /**
     * @brief Parses command-line arguments and returns a populated config.
     *
     * @details
     * Recognised flags:
     *   --particles  <int>    Total number of particles
     *   --steps      <int>    Number of timesteps
     *   --dt         <float>  Timestep size
     *   --bh-mass    <float>  Black hole mass
     *   --eps        <float>  Softening parameter
     *   --seed       <int>    Random seed
     *   --no-output           Disable CSV writing
     *   --benchmark           Enable benchmark mode (quiet)
     *   --help                Print usage and exit
     *
     * @param argc Argument count from main().
     * @param argv Argument vector from main().
     * @return Fully populated SimulationConfig.
     * @throws std::invalid_argument if a required value is missing or invalid.
     */
    static SimulationConfig parse(int argc, char* argv[]);

    /**
     * @brief Prints a usage / help message to stdout.
     */
    static void printHelp();

    /**
     * @brief Validates the configuration and throws if any value is illegal.
     * @throws std::invalid_argument on invalid configuration.
     */
    void validate() const;
};
