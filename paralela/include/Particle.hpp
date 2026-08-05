/**
 * @file Particle.hpp
 * @brief Defines the Particle structure representing a gravitational body.
 *
 * @details
 * A Particle encapsulates all kinematic and intrinsic properties of a single
 * body in the N-body simulation:
 *   - Kinematic state  : position, velocity, accumulated force
 *   - Intrinsic props  : mass, globally-unique ID, body type
 *
 * The `type` field classifies bodies into STAR, BLACK_HOLE, or GAS, allowing
 * future extensions (e.g., different rendering colors, SPH gas physics).
 *
 * MPI serialization: Particle implements pack() / unpack() to convert to/from
 * a flat array of 8 doubles for efficient MPI_Allgather communication.
 *
 * Layout of the serialized buffer (8 doubles):
 *   [0] position.x   [1] position.y   [2] position.z
 *   [3] velocity.x   [4] velocity.y   [5] velocity.z
 *   [6] mass         [7] type (cast to double)
 */

#pragma once

#include "Vector3D.hpp"
#include <cstdint>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Classification of simulated gravitational bodies.
 */
enum class ParticleType : int {
    STAR       = 0, ///< Ordinary stellar body — orbits the central black hole
    BLACK_HOLE = 1, ///< Supermassive black hole — sits at the galactic centre
    GAS        = 2  ///< Gas particle — reserved for future SPH extension
};

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief A single gravitational body in the N-body AGN system.
 *
 * @details
 * At the start of each timestep, `force` is reset to zero by resetForce().
 * During the force-computation pass, contributions from every other particle
 * are accumulated into `force`. The Leapfrog integrator then uses force / mass
 * (acceleration) to update velocity and position.
 *
 * Memory layout note: three Vector3D fields (position, velocity, force) are
 * each 32 bytes, so a Particle occupies 96 + 16 = ~112 bytes. Arrays of
 * Particle fit in L1 cache for small local subsets (local_n ≤ ~1000 on this
 * hardware).
 */
struct Particle {

    Vector3D position;              ///< Current 3D position  [simulation length units]
    Vector3D velocity;              ///< Current 3D velocity  [length / time]
    Vector3D force;                 ///< Accumulated force     [mass × length / time²]
    double   mass{1.0};            ///< Body mass             [simulation mass units]
    int      id{-1};               ///< Globally unique particle index (0 … N-1)
    ParticleType type{ParticleType::STAR}; ///< Body classification

    // ── Physical helper methods ───────────────────────────────────────────────

    /**
     * @brief Resets the accumulated force to zero.
     * @details Must be called at the beginning of each force-computation step.
     */
    void resetForce() noexcept { force.zero(); }

    /**
     * @brief Computes the acceleration vector (Newton's 2nd law: a = F / m).
     * @return Force divided by mass.
     */
    [[nodiscard]] Vector3D acceleration() const noexcept {
        return force / mass;
    }

    /**
     * @brief Computes kinetic energy of this particle.
     * @return 0.5 × mass × |velocity|².
     */
    [[nodiscard]] double kineticEnergy() const noexcept {
        return 0.5 * mass * velocity.normSquared();
    }

    // ── MPI serialization ─────────────────────────────────────────────────────

    /// Number of doubles stored per particle in the MPI communication buffer.
    static constexpr int MPI_PACK_SIZE = 8;

    /**
     * @brief Packs the particle state into a flat double array for MPI transfer.
     *
     * @details The buffer must have room for at least MPI_PACK_SIZE doubles.
     * Layout: [px, py, pz, vx, vy, vz, mass, type].
     *
     * @param buf Destination buffer (caller owns the memory).
     */
    void pack(double* buf) const noexcept;

    /**
     * @brief Reconstructs a Particle from a flat double buffer.
     *
     * @param buf       Source buffer produced by pack().
     * @param particle_id Unique ID to assign to the restored particle.
     * @return A fully initialized Particle.
     */
    static Particle unpack(const double* buf, int particle_id) noexcept;
};
