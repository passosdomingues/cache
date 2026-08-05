/**
 * @file ParticleSystem.hpp
 * @brief Manages the subset of particles owned by one MPI rank.
 *
 * @details
 * ParticleSystem is a value-object that wraps a vector of Particle objects
 * together with convenience methods for:
 *   - resetting forces across all local particles
 *   - computing local kinetic energy
 *   - computing local potential energy (requires global positions/masses)
 *   - writing a snapshot of local particles to a CSV file
 *
 * Each MPI rank owns one ParticleSystem. The full simulation state is
 * distributed across all ranks' ParticleSystems.
 */

#pragma once

#include "Particle.hpp"
#include "SimulationConfig.hpp"
#include <vector>
#include <string>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Container for the local particle subset of a single MPI rank.
 *
 * @details
 * Owns a contiguous `std::vector<Particle>` for cache-friendly sequential
 * access in the force-computation and integration loops.
 */
class ParticleSystem {
public:

    /**
     * @brief Constructs an empty system.
     * @param config Reference to the simulation configuration (lifes >= this object).
     */
    explicit ParticleSystem(const SimulationConfig& config);

    // ── Particle management ───────────────────────────────────────────────────

    /**
     * @brief Replaces the local particle list with the given vector.
     * @param particles New particle list (moved in to avoid copy).
     */
    void setParticles(std::vector<Particle> particles);

    /**
     * @brief Returns a mutable reference to the local particle list.
     * @return Reference to internal particle vector.
     */
    [[nodiscard]] std::vector<Particle>& particles() noexcept { return m_particles; }

    /**
     * @brief Returns a const reference to the local particle list.
     * @return Const reference to internal particle vector.
     */
    [[nodiscard]] const std::vector<Particle>& particles() const noexcept { return m_particles; }

    /**
     * @brief Returns the number of particles managed by this rank.
     * @return Local particle count.
     */
    [[nodiscard]] int size() const noexcept {
        return static_cast<int>(m_particles.size());
    }

    // ── Physics helpers ───────────────────────────────────────────────────────

    /**
     * @brief Resets the force vector of every local particle to zero.
     * @details Must be called before each force-computation pass.
     */
    void resetForces() noexcept;

    /**
     * @brief Computes the total kinetic energy of the local particles.
     * @return Sum of 0.5 * m * v² for each local particle.
     */
    [[nodiscard]] double localKineticEnergy() const noexcept;

    /**
     * @brief Computes the local contribution to gravitational potential energy.
     *
     * @details
     * Uses the global positions and masses arrays (allgathered from all ranks)
     * to compute the pair-wise potential between each local particle i and every
     * global particle j (j != i). The factor of 0.5 is applied globally after
     * MPI_Reduce to avoid double-counting.
     *
     * Formula: U_i = -G * sum_{j!=i} m_i * m_j / sqrt(r_ij² + ε²)
     *
     * @param allPosX  Global X-position array (size N).
     * @param allPosY  Global Y-position array (size N).
     * @param allPosZ  Global Z-position array (size N).
     * @param allMass  Global mass array (size N).
     * @param totalN   Total number of particles.
     * @return Local partial potential energy sum.
     */
    [[nodiscard]] double localPotentialEnergy(
        const std::vector<double>& allPosX,
        const std::vector<double>& allPosY,
        const std::vector<double>& allPosZ,
        const std::vector<double>& allMass,
        int                        totalN) const noexcept;

    // ── I/O ───────────────────────────────────────────────────────────────────

    /**
     * @brief Appends the current local particle positions to a CSV snapshot.
     *
     * @details
     * Only rank 0 calls this after gathering all positions (or each rank writes
     * its own shard — current implementation uses per-rank shards for simplicity).
     * CSV columns: id, type, x, y, z, vx, vy, vz, mass
     *
     * @param step    Current simulation step (used to name the file).
     * @param rank    MPI rank of this process (used to name the file).
     */
    void writeSnapshot(int step, int rank) const;

private:

    const SimulationConfig& m_config;    ///< Simulation parameters
    std::vector<Particle>   m_particles; ///< Local particle subset
};
