/**
 * @file Lessons.cpp
 * @brief Implementation of educational modules and exercises.
 */

#include "Lessons.hpp"
#include "TableFormatter.hpp"
#include <iostream>
#include <vector>
#include <numeric>
#include <string>

namespace DidacticMPI {

// ─────────────────────────────────────────────────────────────────────────────
// LESSON 1: HELLO WORLD
// ─────────────────────────────────────────────────────────────────────────────
void Lessons::runHelloWorld(const MPILearningFramework& env) {
    if (env.isRoot()) {
        TableFormatter::printHeader(
            "Lição 1: Hello World & Identificação de Processos",
            "Conceitos: MPI_Init, MPI_Comm_rank, MPI_Comm_size, MPI_Get_processor_name"
        );
    }
    env.barrier();

    std::string msg = " Processo [" + std::to_string(env.getRank()) + "/" +
                      std::to_string(env.getSize()) + "] executando no host: " + env.getProcessorName();

    if (env.isRoot()) {
        std::cout << TableFormatter::GREEN << "[ROOT 0]" << TableFormatter::RESET << msg << "\n";
    } else {
        std::cout << "         " << msg << "\n";
    }

    env.barrier();
    if (env.isRoot()) {
        TableFormatter::printFooter();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// LESSON 2: POINT TO POINT (MPI_Send / MPI_Recv)
// ─────────────────────────────────────────────────────────────────────────────
void Lessons::runPointToPoint(const MPILearningFramework& env) {
    if (env.isRoot()) {
        TableFormatter::printHeader(
            "Lição 2: Comunicação Ponto a Ponto Bloqueante",
            "Conceitos: MPI_Send (envio) e MPI_Recv (recebimento com tag e filtro)"
        );
    }
    env.barrier();

    const int rank = env.getRank();
    const int tag = 11;

    if (rank == 0) {
        std::string msg = "Olá do processo 0!";
        int valor = 42;

        std::cout << TableFormatter::YELLOW << " [RANK 0] " << TableFormatter::RESET
                  << "Enviando mensagem '" << msg << "' e valor " << valor << " para Rank 1...\n";

        // Envia tamanho da string + string
        int msgLen = static_cast<int>(msg.size()) + 1;
        MPI_Send(&msgLen, 1, MPI_INT, 1, tag, MPI_COMM_WORLD);
        MPI_Send(msg.c_str(), msgLen, MPI_CHAR, 1, tag, MPI_COMM_WORLD);
        MPI_Send(&valor, 1, MPI_INT, 1, tag, MPI_COMM_WORLD);

    } else if (rank == 1) {
        int msgLen = 0;
        MPI_Recv(&msgLen, 1, MPI_INT, 0, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        std::vector<char> buffer(msgLen);
        MPI_Recv(buffer.data(), msgLen, MPI_CHAR, 0, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        int valorRecebido = 0;
        MPI_Recv(&valorRecebido, 1, MPI_INT, 0, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        std::cout << TableFormatter::GREEN << " [RANK 1] " << TableFormatter::RESET
                  << "Recebido com Sucesso! Texto: '" << buffer.data() << "' | Valor: " << valorRecebido << "\n";
    } else {
        std::cout << " [RANK " << rank << "] Aguardando em espera passiva (não participa da troca).\n";
    }

    env.barrier();
    if (env.isRoot()) {
        TableFormatter::printFooter();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// LESSON 3 / EXERCISE 1: GREETINGS & RANK SQUARED SUM
// ─────────────────────────────────────────────────────────────────────────────
void Lessons::runGreetingsAndRankSquaredSum(const MPILearningFramework& env) {
    if (env.isRoot()) {
        TableFormatter::printHeader(
            "Lição 3 / Exercício 1: Coleta de Mensagens & Soma dos Ranks Quadrados",
            "Múltiplos workers enviam rank^2 para o Rank 0, que agrega o resultado."
        );
    }
    env.barrier();

    const int rank = env.getRank();
    const int size = env.getSize();

    if (rank != 0) {
        int rankSquared = rank * rank;
        MPI_Send(&rankSquared, 1, MPI_INT, 0, 100, MPI_COMM_WORLD);
    } else {
        int totalSum = 0; // rank 0^2 = 0
        std::cout << TableFormatter::CYAN << " [RANK 0] " << TableFormatter::RESET
                  << "Coletando dados de " << (size - 1) << " processos workers...\n";

        for (int q = 1; q < size; ++q) {
            int valorRecebido = 0;
            MPI_Recv(&valorRecebido, 1, MPI_INT, q, 100, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            std::cout << "   <- Recebido do Rank " << q << ": " << q << "^2 = " << valorRecebido << "\n";
            totalSum += valorRecebido;
        }

        TableFormatter::printKeyValue("Soma Total (Σ rank^2)", std::to_string(totalSum));
    }

    env.barrier();
    if (env.isRoot()) {
        TableFormatter::printFooter();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// LESSON 4 / EXERCISE 2: VECTOR PROCESSING & ECHO
// ─────────────────────────────────────────────────────────────────────────────
void Lessons::runVectorProcessingAndEcho(const MPILearningFramework& env) {
    if (env.isRoot()) {
        TableFormatter::printHeader(
            "Lição 4 / Exercício 2: Processamento Distribuído de Vetor",
            "Rank 0 gera vetor de 10 elementos -> Rank 1 calcula a soma e devolve o resultado."
        );
    }
    env.barrier();

    const int rank = env.getRank();

    if (rank == 0) {
        std::vector<int> vetor = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
        std::cout << TableFormatter::YELLOW << " [RANK 0] " << TableFormatter::RESET
                  << "Vetor gerado: [";
        for (size_t i = 0; i < vetor.size(); ++i) {
            std::cout << vetor[i] << (i + 1 < vetor.size() ? ", " : "");
        }
        std::cout << "]\n";

        std::cout << " [RANK 0] Enviando vetor de 10 inteiros para o Rank 1...\n";
        MPI_Send(vetor.data(), 10, MPI_INT, 1, 200, MPI_COMM_WORLD);

        int somaResultado = 0;
        MPI_Recv(&somaResultado, 1, MPI_INT, 1, 201, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        std::cout << TableFormatter::GREEN << " [RANK 0] " << TableFormatter::RESET
                  << "Resultado final recebido do Rank 1: " << TableFormatter::BOLD << somaResultado << TableFormatter::RESET << "\n";

    } else if (rank == 1) {
        std::vector<int> vetorRecebido(10);
        MPI_Recv(vetorRecebido.data(), 10, MPI_INT, 0, 200, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        int soma = std::accumulate(vetorRecebido.begin(), vetorRecebido.end(), 0);
        std::cout << TableFormatter::CYAN << " [RANK 1] " << TableFormatter::RESET
                  << "Vetor recebido! Soma dos 10 elementos calculada = " << soma << "\n";

        MPI_Send(&soma, 1, MPI_INT, 0, 201, MPI_COMM_WORLD);
    }

    env.barrier();
    if (env.isRoot()) {
        TableFormatter::printFooter();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// LESSON 5: BROADCAST CONFIGURATION
// ─────────────────────────────────────────────────────────────────────────────
void Lessons::runBroadcastConfig(const MPILearningFramework& env) {
    if (env.isRoot()) {
        TableFormatter::printHeader(
            "Lição 5: Comunicação Coletiva com Broadcast (MPI_Bcast)",
            "Rank 0 transmite hiperparâmetros de configuração para TODOS os ranks em 1 comando."
        );
    }
    env.barrier();

    struct ConfigParams {
        char paramName[32];
        double learningRate;
        int maxEpochs;
    } config;

    if (env.isRoot()) {
        snprintf(config.paramName, sizeof(config.paramName), "Adam_Optimizer");
        config.learningRate = 0.001;
        config.maxEpochs = 500;
        std::cout << TableFormatter::YELLOW << " [RANK 0] " << TableFormatter::RESET
                  << "Configuração original criada na raiz.\n";
    }

    // Transmite a struct completa para todos os processos
    MPI_Bcast(&config, sizeof(ConfigParams), MPI_BYTE, 0, MPI_COMM_WORLD);

    std::cout << " [RANK " << env.getRank() << "] Config Sincronizada: "
              << "Nome='" << config.paramName << "' | LR=" << config.learningRate
              << " | Epochs=" << config.maxEpochs << "\n";

    env.barrier();
    if (env.isRoot()) {
        TableFormatter::printFooter();
    }
}

} // namespace DidacticMPI
