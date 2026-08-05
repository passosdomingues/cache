/**
 * @file AGNInitializer.hpp
 * @brief Generates physically motivated initial conditions for an AGN system.
 *
 * @details
 * An Active Galactic Nucleus (AGN) hosts a supermassive black hole (SMBH) at
 * the galactic centre, surrounded by a rotating accretion disk of stars and gas.
 *
 * This class creates:
 *   1. One central BLACK_HOLE particle at the origin, at rest.
 *   2. (N - 1) STAR particles distributed uniformly in a thin Keplerian disk:
 *        - Radius drawn from a uniform distribution in [r_min, r_max].
 *        - Azimuthal angle drawn uniformly in [0, 2π].
 *        - Z displacement drawn from a uniform distribution in [-h, h].
 *        - Tangential orbital velocity set to the Keplerian speed:
 *              v_k = sqrt(G * M_BH / r)
 *          This ensures stable circular orbits (ignoring stellar self-gravity).
 *
 * Physical analogy: similar to the initial conditions used by GADGET-2 for
 * isolated galaxy simulations, where stellar disks are initialised in
 * centrifugal equilibrium around a central mass concentration.
 *
 * @note
 * Star–star self-gravity is included in the simulation but is negligible
 * compared to BH gravity for the default mass ratio (M_BH / m_star = 50000).
 */

#pragma once

#include "Particle.hpp"
#include "SimulationConfig.hpp"
#include <vector>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Factory class that generates initial conditions for the AGN simulation.
 *
 * @details
 * Usage (rank 0 only):
 * @code
 *   AGNInitializer init(config);
 *   auto particles = init.generate();
 *   // Then scatter via MPIManager::scatterParticles()
 * @endcode
 */
class AGNInitializer {
public:

    /**
     * @brief Constructs the initializer with simulation parameters.
     * @param config Simulation configuration (numParticles, masses, disk geometry, seed).
     */
    explicit AGNInitializer(const SimulationConfig& config);

    /**
     * @brief Generates the full initial particle list (BH + stellar disk).
     *
     * @details
     * Particle indices are assigned globally:
     *   - Index 0      : the central black hole (ParticleType::BLACK_HOLE)
     *   - Index 1..N-1 : stars (ParticleType::STAR) in the Keplerian disk
     *
     * The random number generator is seeded with config.randomSeed for
     * reproducible results across runs.
     *
     * @return Vector of N particles (owned by caller).
     */
    [[nodiscard]] std::vector<Particle> generate() const;

private:

    /**
     * @brief Creates the central supermassive black hole at the origin.
     * @return A single Particle with type BLACK_HOLE, at rest at (0, 0, 0).
     */
    [[nodiscard]] Particle createBlackHole() const;

    /**
     * @brief Creates a single star in Keplerian orbit around the BH.
     *
     * @param id      Global particle ID to assign.
     * @param radius  Orbital radius [length units].
     * @param angle   Azimuthal angle φ in the disk plane [radians].
     * @param z       Vertical displacement from the midplane [length units].
     * @return A Particle with position and velocity set for circular Keplerian orbit.
     */
    [[nodiscard]] Particle createKeplerianStar(int    id,
                                               double radius,
                                               double angle,
                                               double z) const;

    const SimulationConfig& m_config; ///< Simulation parameters
};
