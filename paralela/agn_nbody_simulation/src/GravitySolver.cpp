/**
 * @file GravitySolver.cpp
 * @brief Direct-summation O(N²/P) gravitational force computation.
 *
 * @details
 * This is the hottest code path in the entire simulation. Every timestep,
 * each MPI rank calls computeForces() for its local_n particles against all
 * N global particles — total work per rank: O(local_n × N).
 *
 * Compiler auto-vectorisation: with -O3 -march=native, GCC/Clang recognise
 * the inner loop pattern and emit AVX2 256-bit FMA instructions, processing
 * 4 doubles per cycle on the i7-8565U.
 */

#include "GravitySolver.hpp"
#include <cmath>

// ─────────────────────────────────────────────────────────────────────────────

GravitySolver::GravitySolver(const SimulationConfig& config)
    : m_config(config) {}

// ─────────────────────────────────────────────────────────────────────────────

void GravitySolver::computeForces(
    std::vector<Particle>&     localParticles,
    const std::vector<double>& allPosX,
    const std::vector<double>& allPosY,
    const std::vector<double>& allPosZ,
    const std::vector<double>& allMass,
    int                        globalOffset,
    int                        totalN) const noexcept {

    const double G    = m_config.G;
    const double eps2 = m_config.softeningEps * m_config.softeningEps;

    const int localN = static_cast<int>(localParticles.size());

    // ── Outer loop: iterate over this rank's local particles ─────────────────
    for (int i = 0; i < localN; ++i) {
        Particle& pi = localParticles[i];

        const double xi = pi.position.x;
        const double yi = pi.position.y;
        const double zi = pi.position.z;
        const double mi = pi.mass;

        double fx = 0.0, fy = 0.0, fz = 0.0;

        // ── Inner loop: sum force contribution from all N global particles ───
        // This loop is the primary target for AVX2 auto-vectorisation.
        // Variables are kept as scalars to allow the compiler full freedom.
        const int globalI = globalOffset + i; // global index of local particle i

        for (int j = 0; j < totalN; ++j) {
            if (j == globalI) continue; // skip self-interaction

            const double dx   = allPosX[j] - xi;
            const double dy   = allPosY[j] - yi;
            const double dz   = allPosZ[j] - zi;
            const double dist2 = dx*dx + dy*dy + dz*dz + eps2;

            // Inverse distance cubed:  1 / (r² + ε²)^(3/2)
            // Written as:  dist2^(-3/2) = 1 / (dist2 * sqrt(dist2))
            // rsqrt approximation would be faster but less accurate — using sqrt for correctness.
            const double inv_dist  = 1.0 / std::sqrt(dist2);
            const double inv_dist3 = inv_dist * inv_dist * inv_dist;

            // G * m_j / |r_ij|^3  (scalar factor for this pair)
            const double factor = G * allMass[j] * inv_dist3;

            fx += factor * dx;
            fy += factor * dy;
            fz += factor * dz;
        }

        // Accumulate into the particle (F = m_i * a, and factor already
        // encodes G*m_j/r³; multiplying by m_i gives F on particle i)
        pi.force.x += mi * fx;
        pi.force.y += mi * fy;
        pi.force.z += mi * fz;
    }
}
