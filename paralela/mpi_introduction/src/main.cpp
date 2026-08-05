/**
 * @file main.cpp
 * @brief Entry point for the Didactic MPI C++ Framework.
 */

#include "MPILearningFramework.hpp"
#include "Lessons.hpp"
#include "Benchmark.hpp"
#include "TableFormatter.hpp"
#include <iostream>
#include <string>

using namespace DidacticMPI;

int main(int argc, char* argv[]) {
    MPILearningFramework env(argc, argv);

    bool runAll = true;
    bool runBench = false;

    if (argc > 1) {
        std::string flag(argv[1]);
        if (flag == "--benchmark") {
            runAll = false;
            runBench = true;
        } else if (flag == "--lessons") {
            runAll = true;
            runBench = false;
        } else if (flag == "--all") {
            runAll = true;
            runBench = true;
        }
    }

    if (env.isRoot()) {
        std::cout << TableFormatter::BOLD << TableFormatter::GREEN << R"(
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║        🎓 CURSO DE COMPUTAÇÃO PARALELA E DISTRIBUÍDA — MPI EM C++17      ║
 ║        Baseado no Roteiro de Aulas do Prof. Paulo Bressan                  ║
 ╚═══════════════════════════════════════════════════════════════════════════╝
)" << TableFormatter::RESET << "\n";
        TableFormatter::printKeyValue("Número de Processos MPI", std::to_string(env.getSize()));
        TableFormatter::printKeyValue("Processador / Host", env.getProcessorName());
    }

    if (runAll) {
        Lessons::runHelloWorld(env);
        Lessons::runPointToPoint(env);
        Lessons::runGreetingsAndRankSquaredSum(env);
        Lessons::runVectorProcessingAndEcho(env);
        Lessons::runBroadcastConfig(env);
    }

    if (runBench) {
        Benchmark::runPingPongLatency(env);
        Benchmark::runReduceScaling(env);
    }

    return 0;
}
