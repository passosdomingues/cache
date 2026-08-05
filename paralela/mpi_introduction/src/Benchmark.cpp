/**
 * @file Benchmark.cpp
 * @brief Implementation of MPI latency and throughput benchmarks.
 */

#include "Benchmark.hpp"
#include "TableFormatter.hpp"
#include <iostream>
#include <fstream>
#include <vector>
#include <filesystem>
#include <cmath>

namespace DidacticMPI {

void Benchmark::runPingPongLatency(const MPILearningFramework& env) {
    if (env.isRoot()) {
        TableFormatter::printHeader(
            "Benchmark 1: Latência e Bandbanda MPI (Ping-Pong)",
            "Mede tempo de transmissão Ponto-a-Ponto (MPI_Send/MPI_Recv) de 1B a 1MB."
        );
    }
    env.barrier();

    const int rank = env.getRank();
    const int iterations = 1000;
    std::vector<int> payloadSizes = {1, 64, 1024, 1024 * 64, 1024 * 1024}; // bytes

    std::ofstream csv;
    if (env.isRoot()) {
        namespace fs = std::filesystem;
        fs::create_directories("data/output");
        csv.open("data/output/pingpong_benchmark.csv");
        csv << "size_bytes,latency_us,bandwidth_mbps\n";
    }

    for (int size : payloadSizes) {
        std::vector<char> buffer(size, 'a');

        env.barrier();
        double start = MPILearningFramework::getWtime();

        for (int i = 0; i < iterations; ++i) {
            if (rank == 0) {
                MPI_Send(buffer.data(), size, MPI_BYTE, 1, 99, MPI_COMM_WORLD);
                MPI_Recv(buffer.data(), size, MPI_BYTE, 1, 99, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            } else if (rank == 1) {
                MPI_Recv(buffer.data(), size, MPI_BYTE, 0, 99, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                MPI_Send(buffer.data(), size, MPI_BYTE, 0, 99, MPI_COMM_WORLD);
            }
        }

        double elapsed = MPILearningFramework::getWtime() - start;

        if (env.isRoot()) {
            double avgLatencyUs = (elapsed / (2.0 * iterations)) * 1e6;
            double bandwidthMBps = (static_cast<double>(size * 2 * iterations) / (1024.0 * 1024.0)) / elapsed;

            std::cout << "  • Payload: " << std::setw(10) << size << " Bytes | "
                      << "Latência Média: " << std::setw(8) << std::fixed << std::setprecision(2) << avgLatencyUs << " µs | "
                      << "Banda: " << std::setw(8) << std::setprecision(2) << bandwidthMBps << " MB/s\n";

            if (csv.is_open()) {
                csv << size << "," << avgLatencyUs << "," << bandwidthMBps << "\n";
            }
        }
    }

    env.barrier();
    if (env.isRoot()) {
        TableFormatter::printFooter();
    }
}

void Benchmark::runReduceScaling(const MPILearningFramework& env) {
    if (env.isRoot()) {
        TableFormatter::printHeader(
            "Benchmark 2: Redução Paralela (MPI_Reduce / MPI_Allreduce)",
            "Mede desempenho da soma reduzida sobre vetores de 1M inteiros."
        );
    }
    env.barrier();

    const int N = 1000000;
    const int localN = N / env.getSize();
    std::vector<int> localData(localN, 1);

    env.barrier();
    double start = MPILearningFramework::getWtime();

    long long localSum = 0;
    for (int v : localData) localSum += v;

    long long globalSum = 0;
    MPI_Reduce(&localSum, &globalSum, 1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    double elapsed = MPILearningFramework::getWtime() - start;

    if (env.isRoot()) {
        TableFormatter::printKeyValue("Tamanho do Vetor", std::to_string(N) + " elementos");
        TableFormatter::printKeyValue("Soma Global Calculada", std::to_string(globalSum));
        TableFormatter::printKeyValue("Tempo de Execução", std::to_string(elapsed * 1000.0) + " ms");
        TableFormatter::printFooter();
    }
}

} // namespace DidacticMPI
