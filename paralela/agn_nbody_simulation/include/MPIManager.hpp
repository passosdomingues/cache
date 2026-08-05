/**
 * @file MPIManager.hpp
 * @brief Thin abstraction layer over all MPI communication in the simulation.
 *
 * @details
 * MPIManager owns the MPI lifecycle (init/finalize) and provides semantically
 * clear methods for each communication pattern used by the AGN simulation:
 *
 *   - scatterParticles()   : Rank 0 distributes initial particles to all ranks.
 *   - allgatherPositions() : Every rank shares its current local positions
 *                            with all other ranks (needed for force computation).
 *   - reduceEnergy()       : Sum local kinetic/potential energy across ranks.
 *   - broadcastConfig()    : Rank 0 shares the SimulationConfig to everyone.
 *   - barrier()            : Synchronise all ranks (used for timing).
 *
 * Communication pattern per timestep:
 * @code
 *   MPI_Allgather  ← positions only (3 doubles × N)  [hot path]
 *   MPI_Reduce     ← energy (2 doubles per rank)      [cold path, report only]
 * @endcode
 *
 * Only positions are exchanged in the hot loop — velocities, forces, and masses
 * never leave their rank. Masses are broadcast once at startup.
 */

#pragma once

#include "Particle.hpp"
#include "SimulationConfig.hpp"
#include <mpi.h>
#include <vector>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Manages MPI lifecycle and all inter-process communication.
 *
 * @details
 * Instantiate exactly once in main() before using any other simulation class.
 * The destructor calls MPI_Finalize() if MPI was successfully initialized.
 *
 * @note Non-copyable / non-movable (MPI state is global).
 */
class MPIManager {
public:

    /**
     * @brief Initialises MPI and caches rank / world-size.
     *
     * @param argc Reference to main()'s argc (forwarded to MPI_Init).
     * @param argv Reference to main()'s argv (forwarded to MPI_Init).
     */
    MPIManager(int& argc, char**& argv);

    /**
     * @brief Calls MPI_Finalize() and cleans up.
     */
    ~MPIManager();

    // Non-copyable, non-movable
    MPIManager(const MPIManager&)            = delete;
    MPIManager& operator=(const MPIManager&) = delete;
    MPIManager(MPIManager&&)                 = delete;
    MPIManager& operator=(MPIManager&&)      = delete;

    // ── Accessors ─────────────────────────────────────────────────────────────

    /**
     * @brief Returns the rank of this process in MPI_COMM_WORLD.
     * @return Integer rank in [0, worldSize).
     */
    [[nodiscard]] int rank()      const noexcept { return m_rank; }

    /**
     * @brief Returns the total number of MPI processes.
     * @return World size.
     */
    [[nodiscard]] int worldSize() const noexcept { return m_worldSize; }

    /**
     * @brief Returns true if this process is the root (rank 0).
     * @return rank() == 0.
     */
    [[nodiscard]] bool isRoot()   const noexcept { return m_rank == 0; }

    /**
     * @brief Computes the number of particles assigned to a given rank.
     *
     * @details Uses integer division + remainder: extra particles go to rank 0.
     *
     * @param totalParticles Total N across all ranks.
     * @param targetRank     Rank to query (default: this rank).
     * @return Local particle count for targetRank.
     */
    [[nodiscard]] int localCount(int totalParticles,
                                 int targetRank = -1) const noexcept;

    /**
     * @brief Returns the global index of the first local particle for this rank.
     *
     * @param totalParticles Total N.
     * @param targetRank     Rank to query (default: this rank).
     * @return Starting global index.
     */
    [[nodiscard]] int globalOffset(int totalParticles,
                                   int targetRank = -1) const noexcept;

    // ── Communication methods ─────────────────────────────────────────────────

    /**
     * @brief Broadcasts a SimulationConfig from rank 0 to all other ranks.
     *
     * @param config Config to broadcast (populated on root, filled on others).
     */
    void broadcastConfig(SimulationConfig& config);

    /**
     * @brief Distributes ALL particles from rank 0 to every rank.
     *
     * @details
     * Rank 0 must call this with the full particle list; all other ranks
     * pass an empty or placeholder `allParticles`.
     * On return, `localParticles` contains the slice owned by this rank.
     *
     * @param allParticles   [in]  Full particle list (only meaningful on rank 0).
     * @param localParticles [out] This rank's local subset of particles.
     * @param totalN         Total number of particles across all ranks.
     */
    void scatterParticles(const std::vector<Particle>& allParticles,
                          std::vector<Particle>&       localParticles,
                          int                          totalN);

    /**
     * @brief Gathers all particle positions from every rank into flat arrays.
     *
     * @details
     * Hot-path communication, called every timestep.  Only positions (3 doubles)
     * are exchanged to minimise bandwidth.  Masses (allMass) are static and
     * must be filled once after scatterParticles() via buildMassArray().
     *
     * @param localParticles [in]  This rank's local particles (updated positions).
     * @param allPosX        [out] Global array of X positions (size N).
     * @param allPosY        [out] Global array of Y positions (size N).
     * @param allPosZ        [out] Global array of Z positions (size N).
     * @param totalN         Total number of particles.
     */
    void allgatherPositions(const std::vector<Particle>& localParticles,
                            std::vector<double>&         allPosX,
                            std::vector<double>&         allPosY,
                            std::vector<double>&         allPosZ,
                            int                          totalN);

    /**
     * @brief Reduces local kinetic/potential energy to the root rank.
     *
     * @details Non-root ranks send their local contribution; root receives
     * the global sum. Non-root output parameters are unchanged after return.
     *
     * @param localKE  [in]  Local kinetic energy for this rank.
     * @param localPE  [in]  Local potential energy for this rank.
     * @param totalKE  [out] Global sum of kinetic  energy (meaningful only on root).
     * @param totalPE  [out] Global sum of potential energy (meaningful only on root).
     */
    void reduceEnergy(double  localKE,  double  localPE,
                      double& totalKE,  double& totalPE);

    /**
     * @brief Builds the global mass array from local particles (one-time call).
     *
     * @details Uses MPI_Allgather to share masses. Called once after
     * scatterParticles() so that every rank has all masses for force computation.
     *
     * @param localParticles [in]  This rank's local particles.
     * @param allMass        [out] Global mass array (size N).
     * @param totalN         Total number of particles.
     */
    void buildMassArray(const std::vector<Particle>& localParticles,
                        std::vector<double>&          allMass,
                        int                           totalN);

    /**
     * @brief Blocks until all MPI ranks reach this call.
     */
    void barrier();

    /**
     * @brief Measures wall-clock time via MPI_Wtime().
     * @return Time in seconds (arbitrary epoch).
     */
    [[nodiscard]] static double wallTime() noexcept;

private:

    int m_rank{0};      ///< This process's rank in MPI_COMM_WORLD
    int m_worldSize{1}; ///< Total number of MPI processes
};
