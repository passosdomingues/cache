#include "algoritmos.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Preencher os campos abaixo
Participantes do grupo
Nome: Rafael Passos Domingues           Matrícula: 2023.1.08.036
Nome:                                   Matrícula:
Nome:                                   Matrícula:
Nome:                                   Matrícula:
Nome:                                   Matrícula:
*/

/* --- FUNÇÕES AUXILIARES --- */

/* Retorna a pontuação baseada estritamente na complementaridade do DNA */
long int calcular_score(char a, char b) {
    // Pegadinha evitada: Apenas bases biológicas complementares ganham +2
    if ((a == 'A' && b == 'T') || (a == 'T' && b == 'A') ||
        (a == 'C' && b == 'G') || (a == 'G' && b == 'C')) {
        return 2;
    }
    // Gaps inseridos
    if (a == '-' || b == '-') {
        return -2;
    }
    // Mismatch (inclui letras iguais como A com A, ou pares inválidos como A com C)
    return -1;
}

/* Retorna o maior de três valores long int */
long int max3(long int a, long int b, long int c) {
    if (a >= b && a >= c) return a;
    if (b >= a && b >= c) return b;
    return c;
}

/* --- ALGORITMOS PRINCIPAIS --- */

long int programacao_dinamica(char *s1, char *s2) {
    // Usamos size_t para lidar com instâncias gigantes sem risco de overflow
    size_t n = strlen(s1);
    size_t m = strlen(s2);
    size_t cols = m + 1; // Quantidade total de colunas na nossa "matriz"
    
    // Alocação de um único bloco de memória contíguo (Vetor 1D simulando 2D)
    // Tamanho total = (n + 1) * (m + 1)
    long int *dp = (long int *)malloc((n + 1) * cols * sizeof(long int));
    if (dp == NULL) {
        // Fallback de segurança caso a máquina não tenha RAM suficiente
        fprintf(stderr, "Erro de alocação de memória na DP\n");
        return 0; 
    }
    
    // Inicialização (acumulando a penalidade de gaps nas bordas)
    // dp[i][j] agora é acessado por dp[i * cols + j]
    dp[0 * cols + 0] = 0;
    for (size_t i = 1; i <= n; i++) {
        dp[i * cols + 0] = dp[(i - 1) * cols + 0] - 2;
    }
    for (size_t j = 1; j <= m; j++) {
        dp[0 * cols + j] = dp[0 * cols + (j - 1)] - 2;
    }
    
    // Preenchimento da matriz de Needleman-Wunsch adaptada
    for (size_t i = 1; i <= n; i++) {
        for (size_t j = 1; j <= m; j++) {
            long int match_mismatch = dp[(i - 1) * cols + (j - 1)] + calcular_score(s1[i - 1], s2[j - 1]);
            long int gap_s1 = dp[(i - 1) * cols + j] - 2; 
            long int gap_s2 = dp[i * cols + (j - 1)] - 2; 
            
            dp[i * cols + j] = max3(match_mismatch, gap_s1, gap_s2);
        }
    }
    
    // O resultado final fica na última célula: dp[n][m]
    long int pontuacao = dp[n * cols + m];
    
    // OBRIGATÓRIO: Liberação de memória (agora é apenas um free!)
    free(dp);

    return pontuacao;
}

long int guloso(char *s1, char *s2) {
    long int pontuacao = 0;

    size_t n = strlen(s1);
    size_t m = strlen(s2);
    size_t i = 0, j = 0;

    while (i < n && j < m) {
        // Cenário ideal: match complementar perfeito (+2)
        if (calcular_score(s1[i], s2[j]) == 2) {
            pontuacao += 2;
            i++; 
            j++;
        } 
        // Heurística gulosa: olhar 1 passo a frente para ver se compensa inserir um gap (-2)
        // para conseguir um match (+2) logo em seguida.
        else if (i + 1 < n && calcular_score(s1[i + 1], s2[j]) == 2) {
            pontuacao -= 2; // Insere gap penalizado
            i++; 
        } 
        else if (j + 1 < m && calcular_score(s1[i], s2[j + 1]) == 2) {
            pontuacao -= 2; // Insere gap penalizado
            j++; 
        } 
        // Se nada disso der certo, aceita o mismatch (-1), pois é menos ruim que um gap (-2)
        else {
            pontuacao -= 1;
            i++; 
            j++;
        }
    }
    
    // Tratamento para strings de tamanhos diferentes: 
    // Tudo que sobrar vira gap obrigatoriamente
    while (i < n) { pontuacao -= 2; i++; }
    while (j < m) { pontuacao -= 2; j++; }

    return pontuacao;
}

