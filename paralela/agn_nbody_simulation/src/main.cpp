/**
 * @file main.cpp
 * @brief Entry point and main simulation loop for the AGN N-Body MPI simulation.
 *
 * @details
 * ## Architecture Overview
 *
 * This file orchestrates the complete simulation lifecycle:
 *
 *   1. MPI initialisation (MPIManager)
 *   2. Configuration parsing + broadcast to all ranks
 *   3. Initial condition generation on rank 0 (AGNInitializer)
 *   4. Particle scatter: each rank receives N/P particles (MPIManager)
 *   5. Global mass + type arrays built via allgather (static, one-time)
 *   6. Initial force computation (GravitySolver)
 *   7. Main Leapfrog loop (see below)
 *   8. Final statistics and cleanup
 *
 * ## Leapfrog KDK Loop (per timestep):
 * @code
 *   [1] halfKick(dt)              ← v(t)      → v(t + dt/2)
 *   [2] drift(dt)                 ← x(t)      → x(t + dt)
 *   [3] MPI_Allgatherv positions  ← share new positions (HOT PATH)
 *   [4] resetForces()             ← clear accumulated force
 *   [5] computeForces()           ← F(t + dt) on local particles
 *   [6] halfKick(dt)              ← v(t+dt/2) → v(t + dt)
 *   [7] [every reportInterval]    ← reduce & print energy stats + CSV log
 *   [8] [if writeOutput]          ← dump global position snapshot CSV
 * @endcode
 *
 * ## MPI Communication per step:
 *   - 3 × MPI_Allgatherv (positions x, y, z)  — hot path
 *   - 2 × MPI_Reduce     (energy KE, PE)       — cold path, report only
 *
 * @note
 * Only rank 0 calls AGNInitializer, parses CLI args, and prints to stdout.
 * All other ranks operate silently unless an error occurs.
 */

#include "MPIManager.hpp"
#include "SimulationConfig.hpp"
#include "AGNInitializer.hpp"
#include "ParticleSystem.hpp"
#include "GravitySolver.hpp"
#include "Integrator.hpp"
#include "StatsReporter.hpp"

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <filesystem>
#include <vector>
#include <stdexcept>
#include <cstdlib>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Writes a global position snapshot to a single CSV file (rank 0 only).
 *
 * @details
 * Called after MPI_Allgather so rank 0 has the full allPosX/Y/Z arrays.
 * Writes one row per particle: id, type (BH/STAR), x, y, z, mass.
 * Particle 0 is always the black hole; all others are stars.
 *
 * @param step    Current simulation step.
 * @param totalN  Total number of particles.
 * @param allPosX Global X positions (size totalN).
 * @param allPosY Global Y positions (size totalN).
 * @param allPosZ Global Z positions (size totalN).
 * @param allMass Global masses (size totalN).
 * @param outDir  Output directory path.
 */
static void writeGlobalSnapshot(int                        step,
                                 int                        totalN,
                                 const std::vector<double>& allPosX,
                                 const std::vector<double>& allPosY,
                                 const std::vector<double>& allPosZ,
                                 const std::vector<double>& allMass,
                                 const std::string&          outDir) {
    namespace fs = std::filesystem;
    fs::create_directories(outDir);

    std::ostringstream fname;
    fname << outDir << "/snap_step"
          << std::setfill('0') << std::setw(6) << step << ".csv";

    std::ofstream out(fname.str());
    if (!out.is_open()) return;

    out << "id,type,x,y,z,mass\n";
    out << std::fixed << std::setprecision(8);

    for (int i = 0; i < totalN; ++i) {
        const char* typeStr = (i == 0) ? "BH" : "STAR";
        out << i         << ','
            << typeStr   << ','
            << allPosX[i] << ',' << allPosY[i] << ',' << allPosZ[i] << ','
            << allMass[i] << '\n';
    }
}

// ─────────────────────────────────────────────────────────────────────────────

int main(int argc, char* argv[]) {

    // ── [1] Initialise MPI ────────────────────────────────────────────────────
    MPIManager mpi(argc, argv);
    const int rank      = mpi.rank();
    const int worldSize = mpi.worldSize();

    // ── [2] Parse configuration (rank 0 reads CLI, then broadcasts) ───────────
    SimulationConfig config;

    if (mpi.isRoot()) {
        try {
            config = SimulationConfig::parse(argc, argv);
        } catch (const std::exception& e) {
            std::cerr << "\n[ERROR] " << e.what() << "\n";
            std::cerr << "Run with --help for usage.\n\n";
            MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        }
    }

    mpi.broadcastConfig(config);

    const int N = config.numParticles;

    // ── [3] Generate initial conditions (rank 0 only) ─────────────────────────
    std::vector<Particle> allParticles;
    if (mpi.isRoot()) {
        AGNInitializer initializer(config);
        allParticles = initializer.generate();
    }

    // ── [4] Scatter particles: each rank receives its slice ───────────────────
    ParticleSystem system(config);
    {
        std::vector<Particle> localSlice;
        mpi.scatterParticles(allParticles, localSlice, N);
        system.setParticles(std::move(localSlice));
    }
    allParticles.clear(); // free rank-0 memory — no longer needed

    const int myLocalN = system.size();
    const int myOffset = mpi.globalOffset(N);

    // ── [5] Build global position and mass arrays (shared, static for masses) ──
    std::vector<double> allPosX(N), allPosY(N), allPosZ(N);
    std::vector<double> allMass(N);

    mpi.allgatherPositions(system.particles(), allPosX, allPosY, allPosZ, N);
    mpi.buildMassArray(system.particles(), allMass, N);

    // ── [6] Compute initial forces (before the loop begins) ───────────────────
    GravitySolver gravity(config);
    Integrator    integrator;

    system.resetForces();
    gravity.computeForces(system.particles(),
                          allPosX, allPosY, allPosZ,
                          allMass, myOffset, N);

    // ── [7] Setup reporter, open CSV log, print header ────────────────────────
    StatsReporter reporter(config, worldSize);
    if (mpi.isRoot()) {
        reporter.openLogFile(); // creates data/output/energy_log.csv
        if (!config.benchmarkMode) {
            reporter.printHeader();
        }
        // Write initial snapshot (step 0)
        if (config.writeOutput) {
            writeGlobalSnapshot(0, N, allPosX, allPosY, allPosZ,
                                allMass, config.outputDir);
        }
    }

    // ── [8] Main simulation loop ───────────────────────────────────────────────
    mpi.barrier();
    const double wallStart = MPIManager::wallTime();

    for (int step = 1; step <= config.numSteps; ++step) {

        // [8.1] Half-kick: v(t) → v(t + dt/2)
        integrator.halfKick(system.particles(), config.dt);

        // [8.2] Drift: x(t) → x(t + dt)
        integrator.drift(system.particles(), config.dt);

        // [8.3] Share new positions with all ranks (hot communication path)
        mpi.allgatherPositions(system.particles(), allPosX, allPosY, allPosZ, N);

        // [8.4] Reset forces and recompute at new positions
        system.resetForces();
        gravity.computeForces(system.particles(),
                              allPosX, allPosY, allPosZ,
                              allMass, myOffset, N);

        // [8.5] Half-kick: v(t + dt/2) → v(t + dt)
        integrator.halfKick(system.particles(), config.dt);

        // ── Reporting (every reportInterval steps and on the final step) ─────
        const bool shouldReport = (step % config.reportInterval == 0)
                                 || (step == config.numSteps);

        if (shouldReport && !config.benchmarkMode) {
            // Gather local energies from all ranks
            const double localKE = system.localKineticEnergy();
            const double localPE = system.localPotentialEnergy(
                allPosX, allPosY, allPosZ, allMass, N);

            double totalKE = 0.0, totalPE = 0.0;
            mpi.reduceEnergy(localKE, localPE, totalKE, totalPE);

            if (mpi.isRoot()) {
                const double simTime = static_cast<double>(step) * config.dt;
                // printStep also writes to energy_log.csv via logEnergy()
                reporter.printStep(step, simTime, totalKE, totalPE);
            }
        }

        // ── Global position snapshots written by rank 0 ───────────────────────
        if (config.writeOutput && shouldReport && mpi.isRoot()) {
            writeGlobalSnapshot(step, N, allPosX, allPosY, allPosZ,
                                allMass, config.outputDir);
        }
    }

    // ── [9] Final timing and summary ──────────────────────────────────────────
    mpi.barrier();
    const double wallEnd  = MPIManager::wallTime();
    const double wallTime = wallEnd - wallStart;

    if (mpi.isRoot()) {
        if (config.benchmarkMode) {
            reporter.printBenchmarkResult(worldSize, wallTime);
        } else {
            reporter.printSummary(wallTime, N, config.numSteps);
        }
    }

    // MPI_Finalize is called in MPIManager destructor.
    return EXIT_SUCCESS;
}
