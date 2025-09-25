/**
 * @file test_harness.c
 * @brief Test harness para validação do simulador de filas C.
 *
 * Este programa executa o simulador de filas para múltiplos cenários e sementes,
 * coleta os resultados de littleError e calcula estatísticas (média, desvio padrão,
 * mínimo, máximo) para validar a correção da implementação da Lei de Little.
 *
 * Autor: Rafael Passos Domingues
 * Última Atualização: 2025 Sep 25 14h36
 */

#include "main.h"
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>

#define MAX_SEEDS 10
#define MAX_RHOS 10
#define MAX_LITTLE_ERRORS 100000 // Número máximo de littleErrors a serem armazenados

// Estrutura para armazenar os resultados de littleError para um cenário
typedef struct {
    double errors[MAX_LITTLE_ERRORS];
    int count;
    double mean;
    double stdDev;
    double min;
    double max;
} LittleErrorStats;

/**
 * @brief Calcula estatísticas (média, desvio padrão, min, max) para um array de littleErrors.
 * @param stats Ponteiro para a estrutura LittleErrorStats onde os resultados serão armazenados.
 */
void calculateLittleErrorStats(LittleErrorStats *stats) {
    if (stats->count == 0) {
        stats->mean = 0.0;
        stats->stdDev = 0.0;
        stats->min = 0.0;
        stats->max = 0.0;
        return;
    }

    double sum = 0.0;
    stats->min = stats->errors[0];
    stats->max = stats->errors[0];

    for (int i = 0; i < stats->count; i++) {
        sum += stats->errors[i];
        if (stats->errors[i] < stats->min) stats->min = stats->errors[i];
        if (stats->errors[i] > stats->max) stats->max = stats->errors[i];
    }
    stats->mean = sum / stats->count;

    double sumSqDiff = 0.0;
    for (int i = 0; i < stats->count; i++) {
        sumSqDiff += (stats->errors[i] - stats->mean) * (stats->errors[i] - stats->mean);
    }
    stats->stdDev = sqrt(sumSqDiff / stats->count);
}

/**
 * @brief Lê os littleErrors de um arquivo CSV gerado pela simulação.
 * @param filePath Caminho para o arquivo CSV.
 * @param stats Ponteiro para a estrutura LittleErrorStats onde os erros serão armazenados.
 * @return EXIT_SUCCESS em caso de sucesso, EXIT_FAILURE em caso de erro.
 */
int readLittleErrorsFromCSV(const char *filePath, LittleErrorStats *stats) {
    FILE *file = fopen(filePath, "r");
    if (file == NULL) {
        fprintf(stderr, "Erro: Não foi possível abrir o arquivo CSV %s.\n", filePath);
        return EXIT_FAILURE;
    }

    char line[1024];
    // Pula o cabeçalho
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return EXIT_FAILURE;
    }

    stats->count = 0;
    while (fgets(line, sizeof(line), file) != NULL && stats->count < MAX_LITTLE_ERRORS) {
        // Encontra a coluna littleError. Assume que é a 8ª coluna (índice 7) no cabeçalho base.
        // Timestamp,SampleIndex,EN,EW,QueueSizes,MeasuredLambda,MeasuredOccupancy,LittleError
        char *token;
        char *rest = line;
        for (int i = 0; i < 7; i++) { // Pula as primeiras 7 colunas
            token = strtok_r(rest, ",", &rest);
            if (token == NULL) break;
        }
        token = strtok_r(rest, ",", &rest); // littleError
        if (token != NULL) {
            stats->errors[stats->count++] = atof(token);
        }
    }

    fclose(file);
    return EXIT_SUCCESS;
}

/**
 * @brief Função principal do test harness.
 * @param argc Número de argumentos da linha de comando.
 * @param argv Array de strings com os argumentos da linha de comando.
 * @return EXIT_SUCCESS em caso de sucesso, EXIT_FAILURE em caso de erro.
 */
int main(int argc, char *argv[]) {
    // Argumentos esperados: <mu_global> <politica_id> <num_rhos> [rhos...] <num_seeds> [seeds...] <output_dir> <tolerance>
    if (argc < 8) {
        fprintf(stderr, "Uso: %s <mu_global> <politica_id> <num_rhos> [rho1 rho2 ...] <num_seeds> [seed1 seed2 ...] <output_dir> <tolerance>\n", argv[0]);
        fprintf(stderr, "Politicas: 0=MaiorFila, 1=MaiorTempoEsperaMedio, 2=ClienteMaisAntigo\n");
        return EXIT_FAILURE;
    }

    double muGlobal = atof(argv[1]);
    int politicaId = atoi(argv[2]);

    PoliticaDecisao politicaAtual;
    switch (politicaId) {
        case 0:
            politicaAtual = politicaMaiorFila;
            break;
        case 1:
            politicaAtual = politicaMaiorTempoEsperaMedio;
            break;
        case 2:
            politicaAtual = politicaClienteMaisAntigo;
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
    double rhos[MAX_RHOS][NUM_FILAS];
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
    double tolerance = atof(argv[argIndex++]);

    // Cria o diretório de saída se não existir
    struct stat st = {0};
    if (stat(outputDir, &st) == -1) {
        mkdir(outputDir, 0700);
    }

    printf("Iniciando Test Harness...\n");
    printf("Tolerância para littleError: %.6f\n", tolerance);

    int overallSuccess = EXIT_SUCCESS;

    for (int i = 0; i < numRhos; i++) {
        LittleErrorStats scenarioStats = { .count = 0 };
        printf("\n--- Cenário Rho: %.3f ---\n", rhos[i][0]);

        for (int j = 0; j < numSeeds; j++) {
            char simOutputFile[256];
            snprintf(simOutputFile, sizeof(simOutputFile), "%s/results_rho_%.3f_seed_%u.csv", 
                     outputDir, rhos[i][0], seeds[j]);
            
            // Executa a simulação para gerar o arquivo CSV
            printf("  Executando simulação para rho=%.3f, seed=%u...\n", rhos[i][0], seeds[j]);
            runSingleSimulation(muGlobal, rhos[i], seeds[j], simOutputFile, politicaAtual);

            // Lê os littleErrors do arquivo gerado
            LittleErrorStats currentRunStats = { .count = 0 };
            if (readLittleErrorsFromCSV(simOutputFile, &currentRunStats) == EXIT_SUCCESS) {
                // Agrega os littleErrors para o cenário
                for (int k = 0; k < currentRunStats.count; k++) {
                    if (scenarioStats.count < MAX_LITTLE_ERRORS) {
                        scenarioStats.errors[scenarioStats.count++] = currentRunStats.errors[k];
                    } else {
                        fprintf(stderr, "Aviso: Limite de littleErrors excedido para o cenário. Ignorando.\n");
                        break;
                    }
                }
            }
        }

        // Calcula estatísticas para o cenário e gera o arquivo de prova
        calculateLittleErrorStats(&scenarioStats);

        char proofFile[256];
        snprintf(proofFile, sizeof(proofFile), "%s/proof_rho_%.3f.txt", outputDir, rhos[i][0]);
        FILE *pf = fopen(proofFile, "w");
        if (pf == NULL) {
            fprintf(stderr, "Erro: Não foi possível criar o arquivo de prova %s.\n", proofFile);
            overallSuccess = EXIT_FAILURE;
            continue;
        }

        fprintf(pf, "--- Prova de Validação para Rho: %.3f ---\n", rhos[i][0]);
        fprintf(pf, "Média Absoluta do littleError: %.10f\n", fabs(scenarioStats.mean));
        fprintf(pf, "Desvio Padrão do littleError: %.10f\n", scenarioStats.stdDev);
        fprintf(pf, "Mínimo do littleError: %.10f\n", scenarioStats.min);
        fprintf(pf, "Máximo do littleError: %.10f\n", scenarioStats.max);
        fprintf(pf, "Tolerância: %.10f\n", tolerance);

        if (fabs(scenarioStats.mean) < tolerance) {
            fprintf(pf, "Resultado: SUCESSO - A média absoluta do littleError está abaixo da tolerância.\n");
            printf("  Cenário Rho %.3f: SUCESSO (Média Absoluta littleError: %.10f)\n", rhos[i][0], fabs(scenarioStats.mean));
        } else {
            fprintf(pf, "Resultado: FALHA - A média absoluta do littleError está acima da tolerância.\n");
            printf("  Cenário Rho %.3f: FALHA (Média Absoluta littleError: %.10f)\n", rhos[i][0], fabs(scenarioStats.mean));
            overallSuccess = EXIT_FAILURE;
        }
        fclose(pf);
    }

    printf("Test Harness concluído. Resultado geral: %s\n", overallSuccess == EXIT_SUCCESS ? "SUCESSO" : "FALHA");

    return overallSuccess;
}


