/**
 * @file MPIManager.cpp
 * @brief Implementation of the MPI communication layer.
 *
 * @details
 * All MPI calls are centralised here to keep the rest of the codebase free
 * of MPI-specific details. Communication buffers are allocated once and
 * reused across timesteps to minimise allocation overhead.
 */

#include "MPIManager.hpp"
#include <stdexcept>
#include <cstring>
#include <iostream>

// ─────────────────────────────────────────────────────────────────────────────

MPIManager::MPIManager(int& argc, char**& argv) {
    if (MPI_Init(&argc, &argv) != MPI_SUCCESS) {
        throw std::runtime_error("MPI_Init failed.");
    }
    MPI_Comm_rank(MPI_COMM_WORLD, &m_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &m_worldSize);
}

// ─────────────────────────────────────────────────────────────────────────────

MPIManager::~MPIManager() {
    MPI_Finalize();
}

// ─────────────────────────────────────────────────────────────────────────────

int MPIManager::localCount(int totalParticles, int targetRank) const noexcept {
    if (targetRank < 0) targetRank = m_rank;

    const int base      = totalParticles / m_worldSize;
    const int remainder = totalParticles % m_worldSize;

    // Distribute remainder particles to the first `remainder` ranks
    return base + (targetRank < remainder ? 1 : 0);
}

// ─────────────────────────────────────────────────────────────────────────────

int MPIManager::globalOffset(int totalParticles, int targetRank) const noexcept {
    if (targetRank < 0) targetRank = m_rank;

    const int base      = totalParticles / m_worldSize;
    const int remainder = totalParticles % m_worldSize;

    // offset = sum of localCounts for ranks 0 .. targetRank-1
    return base * targetRank + std::min(targetRank, remainder);
}

// ─────────────────────────────────────────────────────────────────────────────

void MPIManager::broadcastConfig(SimulationConfig& config) {
    // Pack all numeric config fields into a double array for a single Bcast
    // Layout: [numParticles, numSteps, dt, G, softeningEps, blackHoleMass,
    //          starMass, diskRadiusMin, diskRadiusMax, diskThickness,
    //          reportInterval, writeOutput, benchmarkMode, randomSeed]
    constexpr int NFIELDS = 14;
    double buf[NFIELDS];

    if (m_rank == 0) {
        buf[0]  = static_cast<double>(config.numParticles);
        buf[1]  = static_cast<double>(config.numSteps);
        buf[2]  = config.dt;
        buf[3]  = config.G;
        buf[4]  = config.softeningEps;
        buf[5]  = config.blackHoleMass;
        buf[6]  = config.starMass;
        buf[7]  = config.diskRadiusMin;
        buf[8]  = config.diskRadiusMax;
        buf[9]  = config.diskThickness;
        buf[10] = static_cast<double>(config.reportInterval);
        buf[11] = config.writeOutput   ? 1.0 : 0.0;
        buf[12] = config.benchmarkMode ? 1.0 : 0.0;
        buf[13] = static_cast<double>(config.randomSeed);
    }

    MPI_Bcast(buf, NFIELDS, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    if (m_rank != 0) {
        config.numParticles   = static_cast<int>(buf[0]);
        config.numSteps       = static_cast<int>(buf[1]);
        config.dt             = buf[2];
        config.G              = buf[3];
        config.softeningEps   = buf[4];
        config.blackHoleMass  = buf[5];
        config.starMass       = buf[6];
        config.diskRadiusMin  = buf[7];
        config.diskRadiusMax  = buf[8];
        config.diskThickness  = buf[9];
        config.reportInterval = static_cast<int>(buf[10]);
        config.writeOutput    = (buf[11] > 0.5);
        config.benchmarkMode  = (buf[12] > 0.5);
        config.randomSeed     = static_cast<unsigned>(buf[13]);
    }
}

// ─────────────────────────────────────────────────────────────────────────────

void MPIManager::scatterParticles(const std::vector<Particle>& allParticles,
                                   std::vector<Particle>&        localParticles,
                                   int                           totalN) {

    // Each particle is packed into Particle::MPI_PACK_SIZE doubles.
    // We use MPI_Scatterv because localCounts may differ by ±1 for non-divisible N.

    const int PACK = Particle::MPI_PACK_SIZE;

    // ── Build send buffer on rank 0 ──────────────────────────────────────────
    std::vector<double> sendBuf;
    std::vector<int> sendCounts(m_worldSize, 0);
    std::vector<int> sendDispls(m_worldSize, 0);

    if (m_rank == 0) {
        sendBuf.resize(static_cast<size_t>(totalN) * PACK);
        for (int i = 0; i < totalN; ++i) {
            allParticles[i].pack(sendBuf.data() + static_cast<size_t>(i) * PACK);
        }
        for (int r = 0; r < m_worldSize; ++r) {
            sendCounts[r] = localCount(totalN, r) * PACK;
            sendDispls[r] = globalOffset(totalN, r) * PACK;
        }
    }

    // ── Receive buffer ────────────────────────────────────────────────────────
    const int myLocalN = localCount(totalN);
    std::vector<double> recvBuf(static_cast<size_t>(myLocalN) * PACK);

    MPI_Scatterv(
        sendBuf.data(), sendCounts.data(), sendDispls.data(), MPI_DOUBLE,
        recvBuf.data(), myLocalN * PACK, MPI_DOUBLE,
        0, MPI_COMM_WORLD
    );

    // ── Unpack into Particle objects ──────────────────────────────────────────
    const int myOffset = globalOffset(totalN);
    localParticles.resize(static_cast<size_t>(myLocalN));
    for (int i = 0; i < myLocalN; ++i) {
        localParticles[i] = Particle::unpack(
            recvBuf.data() + static_cast<size_t>(i) * PACK,
            myOffset + i
        );
    }
}

// ─────────────────────────────────────────────────────────────────────────────

void MPIManager::allgatherPositions(const std::vector<Particle>& localParticles,
                                     std::vector<double>&          allPosX,
                                     std::vector<double>&          allPosY,
                                     std::vector<double>&          allPosZ,
                                     int                           totalN) {

    // ── Pack local positions into flat arrays ─────────────────────────────────
    const int myLocalN = static_cast<int>(localParticles.size());

    std::vector<double> localX(myLocalN), localY(myLocalN), localZ(myLocalN);
    for (int i = 0; i < myLocalN; ++i) {
        localX[i] = localParticles[i].position.x;
        localY[i] = localParticles[i].position.y;
        localZ[i] = localParticles[i].position.z;
    }

    // ── Build counts and displacements for MPI_Allgatherv ────────────────────
    std::vector<int> recvCounts(m_worldSize), recvDispls(m_worldSize);
    for (int r = 0; r < m_worldSize; ++r) {
        recvCounts[r] = localCount(totalN, r);
        recvDispls[r] = globalOffset(totalN, r);
    }

    allPosX.resize(totalN);
    allPosY.resize(totalN);
    allPosZ.resize(totalN);

    MPI_Allgatherv(localX.data(), myLocalN, MPI_DOUBLE,
                   allPosX.data(), recvCounts.data(), recvDispls.data(),
                   MPI_DOUBLE, MPI_COMM_WORLD);

    MPI_Allgatherv(localY.data(), myLocalN, MPI_DOUBLE,
                   allPosY.data(), recvCounts.data(), recvDispls.data(),
                   MPI_DOUBLE, MPI_COMM_WORLD);

    MPI_Allgatherv(localZ.data(), myLocalN, MPI_DOUBLE,
                   allPosZ.data(), recvCounts.data(), recvDispls.data(),
                   MPI_DOUBLE, MPI_COMM_WORLD);
}

// ─────────────────────────────────────────────────────────────────────────────

void MPIManager::buildMassArray(const std::vector<Particle>& localParticles,
                                 std::vector<double>&          allMass,
                                 int                           totalN) {

    const int myLocalN = static_cast<int>(localParticles.size());

    std::vector<double> localMass(myLocalN);
    for (int i = 0; i < myLocalN; ++i) {
        localMass[i] = localParticles[i].mass;
    }

    std::vector<int> recvCounts(m_worldSize), recvDispls(m_worldSize);
    for (int r = 0; r < m_worldSize; ++r) {
        recvCounts[r] = localCount(totalN, r);
        recvDispls[r] = globalOffset(totalN, r);
    }

    allMass.resize(totalN);
    MPI_Allgatherv(localMass.data(), myLocalN, MPI_DOUBLE,
                   allMass.data(), recvCounts.data(), recvDispls.data(),
                   MPI_DOUBLE, MPI_COMM_WORLD);
}

// ─────────────────────────────────────────────────────────────────────────────

void MPIManager::reduceEnergy(double  localKE,  double  localPE,
                               double& totalKE,  double& totalPE) {
    MPI_Reduce(&localKE, &totalKE, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
    MPI_Reduce(&localPE, &totalPE, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
}

// ─────────────────────────────────────────────────────────────────────────────

void MPIManager::barrier() {
    MPI_Barrier(MPI_COMM_WORLD);
}

// ─────────────────────────────────────────────────────────────────────────────

double MPIManager::wallTime() noexcept {
    return MPI_Wtime();
}
