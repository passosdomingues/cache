/**
 * @file GravitySolver.hpp
 * @brief Computes pairwise gravitational forces on local particles.
 *
 * @details
 * GravitySolver implements the direct-summation (brute-force) O(N²/P) algorithm:
 * for each local particle i, it iterates over every global particle j and
 * accumulates the gravitational force contribution.
 *
 * The gravitational force between particles i and j is:
 *
 *   F_ij = G * m_i * m_j * (r_j - r_i) / (|r_ij|² + ε²)^(3/2)
 *
 * where ε (softeningEps) is the gravitational softening length that prevents
 * the force from diverging when two particles pass very close together (critical
 * near the central black hole, which has mass >> stellar mass).
 *
 * Parallelism: each MPI rank calls computeForces() for its local particles only.
 * The global positions (allPosX/Y/Z) are received via MPI_Allgather before the
 * call, so every rank has the full information it needs without further comms.
 *
 * Performance: the inner double loop is the computational bottleneck.
 * With -O3 -march=native, the compiler auto-vectorises using AVX2 (256-bit),
 * processing 4 doubles simultaneously on the i7-8565U.
 */

#pragma once

#include "Particle.hpp"
#include "SimulationConfig.hpp"
#include <vector>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Stateless gravitational force calculator.
 *
 * @details
 * GravitySolver holds only a reference to the configuration (for G and ε).
 * It has no mutable state and its methods are safe to call from any rank.
 */
class GravitySolver {
public:

    /**
     * @brief Constructs the solver with a reference to simulation parameters.
     * @param config Simulation configuration (lifetimes >= this object).
     */
    explicit GravitySolver(const SimulationConfig& config);

    /**
     * @brief Computes and accumulates gravitational forces on local particles.
     *
     * @details
     * For each local particle i, iterates over ALL N global particles j and
     * adds the force contribution to `localParticles[i].force`.
     *
     * Forces must have been reset (resetForces) before calling this method.
     *
     * The self-interaction check (i_global == j) is handled by comparing
     * global indices, not by checking distance, to avoid any floating-point
     * coincidence issues.
     *
     * Inner-loop structure (hot path):
     * @code
     *   for (local i)
     *     for (global j)
     *       dx, dy, dz = pos_j - pos_i
     *       dist2 = dx² + dy² + dz² + ε²
     *       factor = G * m_i * mass_j / (dist2 * sqrt(dist2))
     *       F_i += factor * (dx, dy, dz)
     * @endcode
     *
     * @param localParticles [in/out] Local particles; their `force` field is
     *                                updated. Positions and masses are read-only.
     * @param allPosX        [in]     Global X positions (size totalN).
     * @param allPosY        [in]     Global Y positions (size totalN).
     * @param allPosZ        [in]     Global Z positions (size totalN).
     * @param allMass        [in]     Global masses      (size totalN).
     * @param globalOffset   [in]     Global index of localParticles[0] in the
     *                                full particle array (used for self-exclusion).
     * @param totalN         [in]     Total number of particles N.
     */
    void computeForces(std::vector<Particle>&     localParticles,
                       const std::vector<double>& allPosX,
                       const std::vector<double>& allPosY,
                       const std::vector<double>& allPosZ,
                       const std::vector<double>& allMass,
                       int                        globalOffset,
                       int                        totalN) const noexcept;

private:

    const SimulationConfig& m_config; ///< Holds G and softeningEps
};
