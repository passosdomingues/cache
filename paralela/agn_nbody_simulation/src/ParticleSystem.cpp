/**
 * @file ParticleSystem.cpp
 * @brief Local particle management: energy computation and CSV snapshots.
 */

#include "ParticleSystem.hpp"
#include <cmath>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <stdexcept>
#include <iomanip>

// ─────────────────────────────────────────────────────────────────────────────

ParticleSystem::ParticleSystem(const SimulationConfig& config)
    : m_config(config) {}

// ─────────────────────────────────────────────────────────────────────────────

void ParticleSystem::setParticles(std::vector<Particle> particles) {
    m_particles = std::move(particles);
}

// ─────────────────────────────────────────────────────────────────────────────

void ParticleSystem::resetForces() noexcept {
    for (auto& p : m_particles) {
        p.resetForce();
    }
}

// ─────────────────────────────────────────────────────────────────────────────

double ParticleSystem::localKineticEnergy() const noexcept {
    double ke = 0.0;
    for (const auto& p : m_particles) {
        ke += p.kineticEnergy();
    }
    return ke;
}

// ─────────────────────────────────────────────────────────────────────────────

double ParticleSystem::localPotentialEnergy(
    const std::vector<double>& allPosX,
    const std::vector<double>& allPosY,
    const std::vector<double>& allPosZ,
    const std::vector<double>& allMass,
    int                        totalN) const noexcept {

    const double G   = m_config.G;
    const double eps = m_config.softeningEps;
    const double eps2 = eps * eps;
    double pe = 0.0;

    for (const auto& p : m_particles) {
        const double xi = p.position.x;
        const double yi = p.position.y;
        const double zi = p.position.z;
        const double mi = p.mass;

        for (int j = 0; j < totalN; ++j) {
            if (j == p.id) continue; // skip self

            const double dx = allPosX[j] - xi;
            const double dy = allPosY[j] - yi;
            const double dz = allPosZ[j] - zi;
            const double dist2 = dx*dx + dy*dy + dz*dz + eps2;
            const double dist  = std::sqrt(dist2);

            // Potential: -G * m_i * m_j / r  (softened)
            pe -= G * mi * allMass[j] / dist;
        }
    }

    // Factor 0.5 is applied globally after MPI_Reduce to avoid double-counting
    return pe;
}

// ─────────────────────────────────────────────────────────────────────────────

void ParticleSystem::writeSnapshot(int step, int rank) const {
    if (m_particles.empty()) return;

    // Ensure output directory exists
    namespace fs = std::filesystem;
    fs::create_directories(m_config.outputDir);

    // File name: output/snap_step0050_rank0.csv
    std::ostringstream fname;
    fname << m_config.outputDir
          << "/snap_step"  << std::setfill('0') << std::setw(6) << step
          << "_rank"       << std::setfill('0') << std::setw(2) << rank
          << ".csv";

    std::ofstream out(fname.str());
    if (!out.is_open()) {
        return; // silently skip on I/O error to not disrupt the simulation
    }

    // CSV header
    out << "id,type,x,y,z,vx,vy,vz,mass\n";
    out << std::fixed << std::setprecision(8);

    for (const auto& p : m_particles) {
        const char* typeStr = (p.type == ParticleType::BLACK_HOLE)
                              ? "BH" : (p.type == ParticleType::GAS ? "GAS" : "STAR");
        out << p.id      << ','
            << typeStr   << ','
            << p.position.x << ',' << p.position.y << ',' << p.position.z << ','
            << p.velocity.x << ',' << p.velocity.y << ',' << p.velocity.z << ','
            << p.mass    << '\n';
    }
}
