/*
 * =====================================================================================
 * PROGRAMA: Soma Paralela de Vetor com Processos Isolados (fork + pipe)
 *
 * CONCEITO DE MEMÓRIA:
 * Diferente das threads, quando chamamos fork(), o Kernel do Linux cria um novo
 * processo com espaço de memória ISOLADO (via Copy-on-Write).
 * O filho ganha uma cópia do 'vetor', mas alterações ou variáveis locais dele NÃO
 * são visíveis para o processo pai.
 *
 * MECANISMO DE IPC (Inter-Process Communication):
 * Para transmitir os dados calculados pelos filhos de volta ao pai, usamos um Pipe.
 * Um Pipe é um buffer unidirecional gerenciado pelo Kernel:
 *   - fd[1]: ponta de ESCRITA (usada pelos filhos)
 *   - fd[0]: ponta de LEITURA (usada pelo pai)
 * =====================================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

#define TAM 8

int main() {
    int vetor[TAM] = {1, 2, 3, 4, 5, 6, 7, 8};
    int fd[2]; // fd[0] = leitura, fd[1] = escrita

    printf("=====================================================\n");
    printf("         EXECUÇÃO PARALELA: MULTI-PROCESSOS          \n");
    printf("=====================================================\n");
    printf("[Pai - PID: %d] Vetor inicial: { ", getpid());
    for (int i = 0; i < TAM; i++) printf("%d ", vetor[i]);
    printf("}\n\n");

    /*
     * CRIAÇÃO DO PIPE:
     * O canal IPC deve ser criado ANTES do fork() para que os processos filhos
     * herdem os descritores de arquivo (fd[0] e fd[1]) abertos.
     */
    if (pipe(fd) == -1) {
        perror("Erro ao criar o pipe de comunicação");
        return 1;
    }

    int metade = TAM / 2;

    /*
     * MULTIPLICAÇÃO DE PROCESSOS VIA FORK:
     */
    for (int i = 0; i < 2; i++) {
        pid_t pid = fork();

        if (pid < 0) {
            perror("Erro ao executar o fork");
            return 1;
        }

        if (pid == 0) {
            /*
             * -----------------------------------------------------------------
             * BLOCO DO PROCESSO FILHO
             * -----------------------------------------------------------------
             */
            // O processo filho só irá escrever, então deve fechar a leitura do pipe
            close(fd[0]);

            int inicio = i * metade;
            int fim = inicio + metade;
            int soma_parcial = 0;

            printf("  [Filho %d | PID: %d] Calculando sub-vetor índices [%d até %d]...\n",
                   i + 1, getpid(), inicio, fim - 1);

            for (int j = inicio; j < fim; j++) {
                soma_parcial += vetor[j];
            }

            printf("  [Filho %d | PID: %d] Soma parcial = %d. Escrevendo no Pipe...\n",
                   i + 1, getpid(), soma_parcial);

            /*
             * Gravando o dado no Pipe IPC.
             * Tratamos o retorno de 'write' para evitar alertas do compilador.
             */
            ssize_t bytes_escritos = write(fd[1], &soma_parcial, sizeof(soma_parcial));
            if (bytes_escritos < 0) {
                perror("Erro ao escrever no pipe");
                exit(1);
            }

            // Fecha a ponta de escrita e encerra o processo filho de forma limpa
            close(fd[1]);
            printf("  [Filho %d | PID: %d] Finalizado e destruído.\n", i + 1, getpid());
            exit(0);
        }
    }

    /*
     * -------------------------------------------------------------------------
     * BLOCO DO PROCESSO PAI
     * -------------------------------------------------------------------------
     */
    // O Pai apenas lê os dados, portanto deve FECHAR seu descritor de escrita.
    // Isso é vital: se mantido aberto, chamadas de 'read' podem bloquear indefinidamente.
    close(fd[1]);

    int soma_total = 0;
    int soma_parcial = 0;

    printf("\n[Pai - PID: %d] Aguardando e lendo dados do Pipe IPC...\n", getpid());

    for (int i = 0; i < 2; i++) {
        // Lê os dados trafegados pelo canal IPC enviado por cada filho
        ssize_t bytes_lidos = read(fd[0], &soma_parcial, sizeof(soma_parcial));
        if (bytes_lidos > 0) {
            printf("[Pai - PID: %d] Recebeu %ld bytes do Pipe -> Parcial %d: %d\n",
                   getpid(), bytes_lidos, i + 1, soma_parcial);
            soma_total += soma_parcial;
        } else if (bytes_lidos < 0) {
            perror("Erro ao ler do pipe");
        }
    }

    // Fecha a ponta de leitura do pai
    close(fd[0]);

    /*
     * RECOLHIMENTO DE PROCESSOS (wait):
     * Evita que os filhos fiquem no estado "Zombie" na tabela de processos do SO.
     */
    for (int i = 0; i < 2; i++) {
        wait(NULL);
    }

    printf("\n-----------------------------------------------------\n");
    printf(" SOMA TOTAL (Processos): %d\n", soma_total);
    printf("-----------------------------------------------------\n\n");

    return 0;
}