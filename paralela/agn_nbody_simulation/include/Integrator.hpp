/**
 * @file Integrator.hpp
 * @brief Leapfrog (Störmer–Verlet) symplectic integrator for the N-body system.
 *
 * @details
 * The Leapfrog method is the standard integrator for N-body gravitational
 * simulations because it is:
 *   - Symplectic  : preserves phase-space volume (Liouville's theorem)
 *   - Time-reversible : reduces secular energy drift
 *   - Second-order accurate in time  O(dt²)
 *   - Cheap: only one force evaluation per timestep
 *
 * The Kick-Drift-Kick (KDK) variant is implemented:
 *
 *   1. KICK  : v(t + dt/2) = v(t) + a(t) * (dt/2)
 *   2. DRIFT : x(t + dt)   = x(t) + v(t + dt/2) * dt
 *   3. [MPI_Allgather new positions]
 *   4. [Compute new forces: a(t + dt)]
 *   5. KICK  : v(t + dt)   = v(t + dt/2) + a(t + dt) * (dt/2)
 *
 * This is implemented as two separate methods (halfKick and drift) so the
 * caller (main loop) can interleave MPI communication between them.
 *
 * @note
 * Do NOT use a simple Euler or RK4 integrator for long-running N-body
 * simulations: both accumulate energy drift. Leapfrog energy error is
 * bounded (oscillating), not growing — the hallmark of a symplectic method.
 */

#pragma once

#include "Particle.hpp"
#include <vector>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Stateless Leapfrog integrator for a list of Particle objects.
 *
 * @details
 * All methods operate in-place on the provided particle list.
 * GravitySolver must be called between halfKick() and the second halfKick()
 * to refresh forces at the new positions.
 */
class Integrator {
public:

    Integrator() = default;

    /**
     * @brief Performs a half-step velocity kick: v += a * (dt/2).
     *
     * @details
     * Uses the current `particle.force` to compute acceleration (F/m)
     * and advances the velocity by half a timestep.
     *
     * Called BEFORE drift (first half-kick) and AFTER force update (second half-kick).
     *
     * @param particles [in/out] Particle list whose velocities are updated.
     * @param dt        Full timestep size (method applies dt/2 internally).
     */
    void halfKick(std::vector<Particle>& particles, double dt) const noexcept;

    /**
     * @brief Advances positions by one full timestep: x += v * dt.
     *
     * @details
     * Called after the first halfKick(). Uses the half-stepped velocity
     * computed by halfKick(), which is why the KDK scheme is more accurate
     * than a naive full-step Euler drift.
     *
     * @param particles [in/out] Particle list whose positions are updated.
     * @param dt        Full timestep size.
     */
    void drift(std::vector<Particle>& particles, double dt) const noexcept;
};
