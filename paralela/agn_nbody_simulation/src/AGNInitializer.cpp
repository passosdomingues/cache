/**
 * @file AGNInitializer.cpp
 * @brief Keplerian disk initial conditions for the AGN N-body simulation.
 *
 * @details
 * Stars are placed in circular Keplerian orbits around the central BH.
 * The orbital speed for a body at radius r is:
 *
 *   v_k = sqrt(G * M_BH / r)
 *
 * which balances the gravitational centripetal force exactly (in the limit
 * where stellar self-gravity is negligible — valid here since M_BH >> m_star).
 *
 * The disk lies in the XY plane with a small random Z perturbation to prevent
 * perfect 2D degeneracy (which can cause numerical artifacts).
 *
 * Azimuthal angle is sampled uniformly in [0, 2π] using a Mersenne Twister,
 * seeded by config.randomSeed for reproducibility.
 */

#include "AGNInitializer.hpp"
#include <cmath>
#include <random>
#include <stdexcept>

// ─────────────────────────────────────────────────────────────────────────────

AGNInitializer::AGNInitializer(const SimulationConfig& config)
    : m_config(config) {

    if (m_config.numParticles < 2) {
        throw std::invalid_argument(
            "AGNInitializer: numParticles must be >= 2 (1 BH + at least 1 star).");
    }
}

// ─────────────────────────────────────────────────────────────────────────────

std::vector<Particle> AGNInitializer::generate() const {
    std::vector<Particle> particles;
    particles.reserve(static_cast<size_t>(m_config.numParticles));

    // ── Particle 0: central supermassive black hole ───────────────────────────
    particles.push_back(createBlackHole());

    // ── Particles 1 … N-1: stars in Keplerian disk ───────────────────────────
    std::mt19937_64 rng(m_config.randomSeed);

    // Uniform radius in [r_min, r_max]
    std::uniform_real_distribution<double> radiusDist(
        m_config.diskRadiusMin, m_config.diskRadiusMax);

    // Uniform azimuthal angle φ in [0, 2π]
    std::uniform_real_distribution<double> angleDist(0.0, 2.0 * M_PI);

    // Uniform vertical displacement in [-h, +h]
    std::uniform_real_distribution<double> zDist(
        -m_config.diskThickness, m_config.diskThickness);

    const int numStars = m_config.numParticles - 1;
    for (int i = 0; i < numStars; ++i) {
        const double r     = radiusDist(rng);
        const double angle = angleDist(rng);
        const double z     = zDist(rng);

        particles.push_back(createKeplerianStar(i + 1, r, angle, z));
    }

    return particles;
}

// ─────────────────────────────────────────────────────────────────────────────

Particle AGNInitializer::createBlackHole() const {
    Particle bh;
    bh.id       = 0;
    bh.type     = ParticleType::BLACK_HOLE;
    bh.mass     = m_config.blackHoleMass;
    bh.position = {0.0, 0.0, 0.0};
    bh.velocity = {0.0, 0.0, 0.0};
    bh.force    = {0.0, 0.0, 0.0};
    return bh;
}

// ─────────────────────────────────────────────────────────────────────────────

Particle AGNInitializer::createKeplerianStar(int    id,
                                              double radius,
                                              double angle,
                                              double z) const {
    Particle star;
    star.id   = id;
    star.type = ParticleType::STAR;
    star.mass = m_config.starMass;

    // Position on disk plane + small Z offset
    star.position.x = radius * std::cos(angle);
    star.position.y = radius * std::sin(angle);
    star.position.z = z;

    // Keplerian circular speed: v_k = sqrt(G * M_BH / r)
    const double vk = std::sqrt(m_config.G * m_config.blackHoleMass / radius);

    // Velocity is perpendicular to the radial direction (tangential):
    //   v_x = -v_k * sin(φ)
    //   v_y = +v_k * cos(φ)
    //   v_z =  0 (no vertical velocity for circular orbits)
    star.velocity.x = -vk * std::sin(angle);
    star.velocity.y =  vk * std::cos(angle);
    star.velocity.z =  0.0;

    star.force = {0.0, 0.0, 0.0};
    return star;
}
