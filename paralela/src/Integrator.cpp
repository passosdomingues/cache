/**
 * @file Integrator.cpp
 * @brief Leapfrog Kick-Drift-Kick (KDK) integrator implementation.
 *
 * @details
 * The KDK Leapfrog is a symplectic (phase-space preserving) integration scheme.
 * Energy conservation error is bounded (oscillating) rather than growing,
 * making it far superior to Euler or RK4 for long N-body runs.
 *
 * Full timestep sequence (coordinated with MPIManager in main.cpp):
 *
 *   halfKick(dt)                   ← v(t) → v(t + dt/2)
 *   drift(dt)                      ← x(t) → x(t + dt)
 *   [MPIManager::allgatherPositions]  ← communicate new positions
 *   [GravitySolver::computeForces]   ← compute F(t + dt)
 *   halfKick(dt)                   ← v(t + dt/2) → v(t + dt)
 */

#include "Integrator.hpp"

// ─────────────────────────────────────────────────────────────────────────────

void Integrator::halfKick(std::vector<Particle>& particles,
                           double                  dt) const noexcept {
    const double half_dt = 0.5 * dt;

    for (auto& p : particles) {
        // a = F / m  (acceleration from current force)
        const double inv_mass = 1.0 / p.mass;
        const double ax = p.force.x * inv_mass;
        const double ay = p.force.y * inv_mass;
        const double az = p.force.z * inv_mass;

        // v += a * (dt/2)
        p.velocity.x += ax * half_dt;
        p.velocity.y += ay * half_dt;
        p.velocity.z += az * half_dt;
    }
}

// ─────────────────────────────────────────────────────────────────────────────

void Integrator::drift(std::vector<Particle>& particles,
                        double                  dt) const noexcept {
    for (auto& p : particles) {
        // x += v * dt
        p.position.x += p.velocity.x * dt;
        p.position.y += p.velocity.y * dt;
        p.position.z += p.velocity.z * dt;
    }
}
