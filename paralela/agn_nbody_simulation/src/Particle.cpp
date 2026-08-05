/**
 * @file Particle.cpp
 * @brief Implements MPI serialization for the Particle struct.
 */

#include "Particle.hpp"
#include <cstring>

// ─────────────────────────────────────────────────────────────────────────────

void Particle::pack(double* buf) const noexcept {
    buf[0] = position.x;
    buf[1] = position.y;
    buf[2] = position.z;
    buf[3] = velocity.x;
    buf[4] = velocity.y;
    buf[5] = velocity.z;
    buf[6] = mass;
    buf[7] = static_cast<double>(static_cast<int>(type));
}

// ─────────────────────────────────────────────────────────────────────────────

Particle Particle::unpack(const double* buf, int particle_id) noexcept {
    Particle p;
    p.position.x = buf[0];
    p.position.y = buf[1];
    p.position.z = buf[2];
    p.velocity.x = buf[3];
    p.velocity.y = buf[4];
    p.velocity.z = buf[5];
    p.mass        = buf[6];
    p.type        = static_cast<ParticleType>(static_cast<int>(buf[7]));
    p.id          = particle_id;
    return p;
}
