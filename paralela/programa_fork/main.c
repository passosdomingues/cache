#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h> // Necessário para a função wait()

int main() {
    pid_t pid;

    // A chamada fork() cria um processo filho idêntico ao pai
    pid = fork();

    if (pid < 0) {
        // Erro na criação do processo
        perror("Falha ao executar o fork");
        exit(EXIT_FAILURE);
    } 
    else if (pid == 0) {
        // O valor de retorno 0 indica que estamos no PROCESSO FILHO
        printf("[Filho] Executando...\n");
        printf("[Filho] PID do Filho: %d\n", getpid());
        printf("[Filho] PPID do Filho (ID do Pai): %d\n\n", getppid());
        
        exit(EXIT_SUCCESS); // Encerra o filho corretamente
    } 
    else {
        // O valor de retorno positivo é o PID do filho, indicando o PROCESSO PAI
        printf("[Pai] Executando...\n");
        printf("[Pai] PID do Pai: %d\n", getpid());
        printf("[Pai] PPID do Pai (ID do shell que rodou o programa): %d\n", getppid());
        printf("[Pai] PID do Filho criado: %d\n\n", pid);

        // Boa prática: o pai aguarda o filho terminar a execução
        wait(NULL);
        printf("[Pai] O processo filho finalizou com sucesso.\n");
    }

    return 0;
}