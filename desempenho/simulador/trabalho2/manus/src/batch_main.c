/**
 * @file batch_main.c
 * @brief Executa o simulador de filas em modo batch para múltiplos cenários e sementes.
 *
 * Este programa orquestra a execução do simulador de filas para diferentes valores de ocupação (rho)
 * e sementes de números aleatórios. Ele gera arquivos CSV de saída para cada execução e, opcionalmente,
 * pode agregar os resultados e executar validações.
 *
 * Autor: Rafael Passos Domingues
 * Última Atualização: 2025 Sep 25 14h36
 */

#include "main.h"
#include <dirent.h>

#define MAX_SEEDS 10
#define MAX_RHOS 10

// Estrutura para armazenar os resultados de uma execução
typedef struct {
    double littleErrorMean;
    double littleErrorStdDev;
    double littleErrorMin;
    double littleErrorMax;
} BatchResult;

/**
 * @brief Executa uma única simulação com os parâmetros fornecidos.
 * @param muGlobal Taxa de serviço global.
 * @param rhos Array de ocupações para cada fila.
 * @param seed Semente para o gerador de números aleatórios.
 * @param nomeArquivoSaida Nome do arquivo CSV de saída.
 * @param politica Ponteiro para a função de política de decisão.
 * @return EXIT_SUCCESS em caso de sucesso, EXIT_FAILURE em caso de erro.
 */
int runSingleSimulation(double muGlobal, double rhos[NUM_FILAS], unsigned int seed, const char *nomeArquivoSaida, PoliticaDecisao politica) {
    EstadoSimulador estado;
    inicializaEstadoSimulador(&estado, muGlobal, rhos, seed, nomeArquivoSaida);
    executaSimulacao(&estado, politica);
    calculaMetricasFinais(&estado);

    for (int i = 0; i < NUM_FILAS; i++) {
        free(estado.filas[i].fila);
    }
    fclose(estado.arquivoSaidaCSV);
    return EXIT_SUCCESS;
}

/**
 * @brief Função principal para o modo batch.
 * @param argc Número de argumentos da linha de comando.
 * @param argv Array de strings com os argumentos da linha de comando.
 * @return EXIT_SUCCESS em caso de sucesso, EXIT_FAILURE em caso de erro.
 */
int main(int argc, char *argv[]) {
    // Argumentos esperados: <mu_global> <politica_id> <num_rhos> [rhos...] <num_seeds> [seeds...] <output_dir>
    if (argc < 7) {
        fprintf(stderr, "Uso: %s <mu_global> <politica_id> <num_rhos> [rho1 rho2 ...] <num_seeds> [seed1 seed2 ...] <output_dir>\n", argv[0]);
        fprintf(stderr, "Politicas: 0=MaiorFila, 1=MaiorTempoEsperaMedio, 2=ClienteMaisAntigo\n");
        return EXIT_FAILURE;
    }

    double muGlobal = atof(argv[1]);
    int politicaId = atoi(argv[2]);

    PoliticaDecisao politicaAtual;
    switch (politicaId) {
        case 0:
            politicaAtual = politicaMaiorFila;
            printf("Política de decisão: Maior Fila\n");
            break;
        case 1:
            politicaAtual = politicaMaiorTempoEsperaMedio;
            printf("Política de decisão: Maior Tempo de Espera Médio\n");
            break;
        case 2:
            politicaAtual = politicaClienteMaisAntigo;
            printf("Política de decisão: Cliente Mais Antigo\n");
            break;
        default:
            fprintf(stderr, "Erro: Política de decisão inválida. Usando Maior Fila por padrão.\n");
            politicaAtual = politicaMaiorFila;
            break;
    }

    int argIndex = 3;
    int numRhos = atoi(argv[argIndex++]);
    if (numRhos > MAX_RHOS) {
        fprintf(stderr, "Erro: Número de rhos excede o máximo permitido (%d).\n", MAX_RHOS);
        return EXIT_FAILURE;
    }
    double rhos[MAX_RHOS][NUM_FILAS]; // Supondo que cada rho é aplicado a todas as 3 filas
    for (int i = 0; i < numRhos; i++) {
        double currentRho = atof(argv[argIndex++]);
        for (int j = 0; j < NUM_FILAS; j++) {
            rhos[i][j] = currentRho;
        }
    }

    int numSeeds = atoi(argv[argIndex++]);
    if (numSeeds > MAX_SEEDS) {
        fprintf(stderr, "Erro: Número de seeds excede o máximo permitido (%d).\n", MAX_SEEDS);
        return EXIT_FAILURE;
    }
    unsigned int seeds[MAX_SEEDS];
    for (int i = 0; i < numSeeds; i++) {
        seeds[i] = (unsigned int)atoi(argv[argIndex++]);
    }

    const char *outputDir = argv[argIndex++];

    // Cria o diretório de saída se não existir
    struct stat st = {0};
    if (stat(outputDir, &st) == -1) {
        mkdir(outputDir, 0700);
    }

    printf("Iniciando simulações em modo batch...\n");

    for (int i = 0; i < numRhos; i++) {
        for (int j = 0; j < numSeeds; j++) {
            char nomeArquivoSaida[256];
            snprintf(nomeArquivoSaida, sizeof(nomeArquivoSaida), "%s/results_rho_%.3f_seed_%u.csv", 
                     outputDir, rhos[i][0], seeds[j]);
            printf("  Executando rho=%.3f, seed=%u -> %s\n", rhos[i][0], seeds[j], nomeArquivoSaida);
            runSingleSimulation(muGlobal, rhos[i], seeds[j], nomeArquivoSaida, politicaAtual);
        }
    }

    printf("Simulações em modo batch concluídas.\n");

    return EXIT_SUCCESS;
}


