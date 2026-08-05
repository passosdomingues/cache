/**
 * @file Benchmark.hpp
 * @brief Performance benchmarking and latency measurement module for MPI routines.
 */

#pragma once

#include "MPILearningFramework.hpp"

namespace DidacticMPI {

/**
 * @brief Benchmarking suite measuring MPI communication latencies and throughputs.
 */
class Benchmark {
public:
    /**
     * @brief Measures point-to-point roundtrip latency (ping-pong) for different payload sizes.
     * Export data to CSV for plotting.
     */
    static void runPingPongLatency(const MPILearningFramework& env);

    /**
     * @brief Measures execution time scaling for parallel reduction.
     */
    static void runReduceScaling(const MPILearningFramework& env);
};

} // namespace DidacticMPI
