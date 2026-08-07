/*
 * =====================================================================================
 * PROGRAMA: Soma Paralela de Vetor com Threads (POSIX Pthreads)
 *
 * CONCEITO DE MEMÓRIA:
 * Threads pertencem ao MESMO processo. Elas compartilham o espaço de endereçamento,
 * o que significa que todas as threads conseguem ler diretamente o 'vetor' global.
 *
 * PARA EVITAR RACE CONDITIONS:
 * Em vez de usarmos uma variável global compartilhada com Mutex (que causaria gargalo
 * de sincronização), cada thread escreve seu resultado parcial em uma estrutura
 * individual (ThreadData). O processo principal lê esses dados após o 'pthread_join'.
 * =====================================================================================
 */

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#define TAM 8

// Vetor de dados compartilhado (acessível por todas as threads)
int vetor[TAM] = {1, 2, 3, 4, 5, 6, 7, 8};

/*
 * Estrutura de dados para passar parâmetros e receber resultados
 * de cada thread sem necessidade de sincronização via Locks/Mutexes.
 */
typedef struct {
    int id;           // Identificador lógico da thread (1, 2...)
    int inicio;       // Índice inicial do sub-vetor
    int fim;          // Índice final (exclusivo) do sub-vetor
    int soma_parcial; // Resultado da soma calculado por esta thread
} ThreadData;

/*
 * Função executada concorrentemente pelas threads.
 */
void* somar_metade(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    data->soma_parcial = 0;

    printf("  [Thread %d | TID: %lu] Iniciada. Processando índices [%d até %d]...\n",
           data->id, (unsigned long)pthread_self(), data->inicio, data->fim - 1);

    for (int i = data->inicio; i < data->fim; i++) {
        data->soma_parcial += vetor[i];
    }

    printf("  [Thread %d | TID: %lu] Concluída! Soma parcial calculada = %d\n",
           data->id, (unsigned long)pthread_self(), data->soma_parcial);

    pthread_exit(NULL);
}

int main() {
    pthread_t threads[2];
    ThreadData dados[2];
    int metade = TAM / 2;

    printf("=====================================================\n");
    printf("         EXECUÇÃO PARALELA: MULTI-THREADING          \n");
    printf("=====================================================\n");
    printf("[Main PID: %d] Vetor: { ", getpid());
    for (int i = 0; i < TAM; i++) printf("%d ", vetor[i]);
    printf("}\n\n");

    /*
     * CRIAÇÃO DAS THREADS:
     * Divide o trabalho em 2 metades e atribui uma faixa para cada thread.
     */
    for (int i = 0; i < 2; i++) {
        dados[i].id = i + 1;
        dados[i].inicio = i * metade;
        dados[i].fim = (i + 1) * metade;

        printf("[Main] Despachando Thread %d...\n", i + 1);
        if (pthread_create(&threads[i], NULL, somar_metade, &dados[i]) != 0) {
            perror("Erro ao criar a thread");
            return 1;
        }
    }

    /*
     * BARREIRA DE SINCRONIZAÇÃO (pthread_join):
     * O processo principal aguarda o término das duas threads e consolida o valor final.
     */
    int soma_total = 0;
    printf("\n[Main] Aguardando término das threads (pthread_join)...\n");

    for (int i = 0; i < 2; i++) {
        pthread_join(threads[i], NULL);
        printf("[Main] Thread %d finalizada. Coletando soma parcial: %d\n",
               i + 1, dados[i].soma_parcial);
        soma_total += dados[i].soma_parcial;
    }

    printf("\n-----------------------------------------------------\n");
    printf(" SOMA TOTAL (Threads): %d\n", soma_total);
    printf("-----------------------------------------------------\n\n");

    return 0;
}