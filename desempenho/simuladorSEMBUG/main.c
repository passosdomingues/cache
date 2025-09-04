#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<time.h>

// Estrutura para medições da Lei de Little
typedef struct {
    double tempoAnterior;      // Tempo do último evento
    unsigned long int quantidadeRequisicoes; // Número de requisições no sistema
    double somaArea;           // Soma acumulada da área sob a curva
} MedidaLittle;

// Estrutura para armazenar métricas da simulação
typedef struct {
    unsigned long int maxFila;
    unsigned long int totalRequisicoes;
    unsigned long int totalAtendimentos;
    double somaIntervaloRequisicoes;
    double somaTempoServico;
    double tempoDecorrido;
} MetricasSimulacao;

// Gera um número aleatório entre 0 e 1 (exclusivo)
double aleatorio() {
    double u = rand() / ((double) RAND_MAX + 1);
    return 1.0 - u;  // Limitando entre (0,1]
}

// Gera um valor da distribuição exponencial
double exponencial(double taxa) {
    return (-1.0 / taxa) * log(aleatorio());
}

// Retorna o mínimo entre dois números
double minimo(double n1, double n2) {
    return (n1 < n2) ? n1 : n2;
}

// Inicializa a estrutura de medição da Lei de Little
void iniciaLittle(MedidaLittle *medida) {
    medida->tempoAnterior = 0.0;
    medida->quantidadeRequisicoes = 0;
    medida->somaArea = 0.0;
}

// Atualiza a medição da Lei de Little (VERSÃO COM BUG)
void atualizaLittleComBug(MedidaLittle *medida, double tempoAtual, int variacao) {
    // Calcula a área desde a última atualização
    medida->somaArea += (tempoAtual - medida->tempoAnterior) * medida->quantidadeRequisicoes;
    
    // Atualiza o tempo da última medição
    medida->tempoAnterior = tempoAtual;
    
    // Ajusta a quantidade de requisições (BUG: esta lógica está incorreta)
    if (variacao > 0) {
        medida->quantidadeRequisicoes++;
    } else {
        medida->quantidadeRequisicoes--;
    }
}

// Atualiza a medição da Lei de Little (VERSÃO CORRIGIDA)
void atualizaLittle(MedidaLittle *medida, double tempoAtual, unsigned long int quantidadeAtual) {
    // Calcula a área desde a última atualização
    medida->somaArea += (tempoAtual - medida->tempoAnterior) * medida->quantidadeRequisicoes;
    
    // Atualiza o tempo e a quantidade para a próxima iteração
    medida->tempoAnterior = tempoAtual;
    medida->quantidadeRequisicoes = quantidadeAtual;
}

// Função para calcular e exibir resultados
void exibeResultados(MetricasSimulacao metricas, MedidaLittle E_N, 
                    MedidaLittle E_W_chegadas, MedidaLittle E_W_saidas,
                    int usarVersaoCorrigida) {
    printf("\n---=== Métricas e Validações ===---\n");
    printf("Tempo total de simulação: %lF segundos\n", metricas.tempoDecorrido);
    printf("Máximo de clientes na fila: %ld\n", metricas.maxFila);
    printf("Total de requisições: %ld\n", metricas.totalRequisicoes);
    printf("Total de atendimentos: %ld\n", metricas.totalAtendimentos);
    printf("Média entre requisições: %lF\n", 
           metricas.somaIntervaloRequisicoes / metricas.totalRequisicoes);
    printf("Média de tempo de serviço: %lF\n", 
           metricas.somaTempoServico / metricas.totalAtendimentos);
    
    double ocupacaoEsperada = (1.0 / (metricas.somaIntervaloRequisicoes / metricas.totalRequisicoes)) / 
                              (1.0 / (metricas.somaTempoServico / metricas.totalAtendimentos));
    double ocupacaoCalculada = metricas.somaTempoServico / metricas.tempoDecorrido;
    
    printf("Ocupação esperada: %lF\n", ocupacaoEsperada);
    printf("Ocupação calculada: %lF\n", ocupacaoCalculada);
    
    printf("\n---=== Lei de Little ===---\n");
    
    if (usarVersaoCorrigida) {
        // Cálculo correto usando a versão sem bug
        double E_N_final = E_N.somaArea / metricas.tempoDecorrido;
        double lambda = metricas.totalRequisicoes / metricas.tempoDecorrido;
        double E_W_final = E_N.somaArea / metricas.totalRequisicoes;
        double erroLittle = E_N_final - lambda * E_W_final;
        
        printf("(VERSÃO CORRIGIDA)\n");
        printf("E[N]: %lF\n", E_N_final);
        printf("λ: %lF\n", lambda);
        printf("E[W]: %lF\n", E_W_final);
        printf("Erro de Little: %lF\n", erroLittle);
        printf("λ * E[W]: %lF\n", lambda * E_W_final);
    } else {
        // Cálculo original com bug
        double E_N_final = E_N.somaArea / metricas.tempoDecorrido;
        double E_W_final = (E_W_chegadas.somaArea - E_W_saidas.somaArea) / E_W_chegadas.quantidadeRequisicoes;
        double lambda = E_W_chegadas.quantidadeRequisicoes / metricas.tempoDecorrido;
        double erroLittle = E_N_final - lambda * E_W_final;
        
        printf("(VERSÃO COM BUG)\n");
        printf("E[N]: %lF\n", E_N_final);
        printf("λ: %lF\n", lambda);
        printf("E[W]: %lF\n", E_W_final);
        printf("Erro de Little: %lF\n", erroLittle);
        printf("λ * E[W]: %lF\n", lambda * E_W_final);
    }
}

int main() {
    srand(time(NULL));
    
    // Variáveis para medições da Lei de Little
    MedidaLittle E_N;
    MedidaLittle E_W_chegadas;  // Para medição com bug
    MedidaLittle E_W_saidas;    // Para medição com bug
    
    // Inicializando variáveis de Little
    iniciaLittle(&E_N);
    iniciaLittle(&E_W_chegadas);
    iniciaLittle(&E_W_saidas);
    
    // Variáveis para métricas da simulação
    MetricasSimulacao metricas;
    metricas.maxFila = 0;
    metricas.totalRequisicoes = 0;
    metricas.totalAtendimentos = 0;
    metricas.somaIntervaloRequisicoes = 0.0;
    metricas.somaTempoServico = 0.0;
    metricas.tempoDecorrido = 0.0;
    
    // Tempo total de simulação (24 horas)
    double tempoSimulacao = 86400.0;
    
    // Variáveis de taxa
    double mediaIntervaloRequisicoes;
    double mediaTempoServico;
    
    // Variáveis de evento
    double proximaRequisicao;
    double tempoServico = 0.0;
    
    // Fila
    unsigned long int fila = 0;
    
    printf("Informe a média de tempo entre requisições: ");
    scanf("%lF", &mediaIntervaloRequisicoes);
    mediaIntervaloRequisicoes = 1.0 / mediaIntervaloRequisicoes;
    
    printf("Informe a média de tempo para atendimentos: ");
    scanf("%lF", &mediaTempoServico);
    mediaTempoServico = 1.0 / mediaTempoServico;
    
    // Gerando o tempo de chegada da primeira requisição
    proximaRequisicao = exponencial(mediaIntervaloRequisicoes);
    metricas.totalRequisicoes++;
    metricas.somaIntervaloRequisicoes = proximaRequisicao;
    
    // Loop principal de simulação
    while (metricas.tempoDecorrido < tempoSimulacao) {
        // Determina o próximo evento
        metricas.tempoDecorrido = fila ? 
            minimo(proximaRequisicao, tempoServico) : 
            proximaRequisicao;
        
        // Verifica se é um evento de chegada
        if (metricas.tempoDecorrido == proximaRequisicao) {
            // Evento de chegada
            fila++;
            
            // Atualiza o máximo da fila
            if (fila > metricas.maxFila) {
                metricas.maxFila = fila;
            }
            
            // Se o sistema estava vazio, inicia o atendimento
            if (fila == 1) {
                double tempoAtendimento = exponencial(mediaTempoServico);
                tempoServico = metricas.tempoDecorrido + tempoAtendimento;
                metricas.totalAtendimentos++;
                metricas.somaTempoServico += tempoAtendimento;
            }
            
            // Agenda a próxima requisição
            double intervalo = exponencial(mediaIntervaloRequisicoes);
            proximaRequisicao = metricas.tempoDecorrido + intervalo;
            metricas.totalRequisicoes++;
            metricas.somaIntervaloRequisicoes += intervalo;
            
            // Atualiza medições de Little (VERSÃO COM BUG)
            atualizaLittleComBug(&E_N, metricas.tempoDecorrido, 1);
            atualizaLittleComBug(&E_W_chegadas, metricas.tempoDecorrido, 1);
            
            // Atualiza medições de Little (VERSÃO CORRIGIDA)
            // atualizaLittle(&E_N, metricas.tempoDecorrido, fila);
            
        } else {
            // Evento de saída
            fila--;
            
            // Se ainda há clientes na fila, agenda a próxima saída
            if (fila > 0) {
                double tempoAtendimento = exponencial(mediaTempoServico);
                tempoServico = metricas.tempoDecorrido + tempoAtendimento;
                metricas.totalAtendimentos++;
                metricas.somaTempoServico += tempoAtendimento;
            }
            
            // Atualiza medições de Little (VERSÃO COM BUG)
            atualizaLittleComBug(&E_N, metricas.tempoDecorrido, -1);
            atualizaLittleComBug(&E_W_saidas, metricas.tempoDecorrido, 1);
            
            // Atualiza medições de Little (VERSÃO CORRIGIDA)
            atualizaLittle(&E_N, metricas.tempoDecorrido, fila);
        }
    }
    
    // Exibe resultados com a versão com bug
    exibeResultados(metricas, E_N, E_W_chegadas, E_W_saidas, 0);
    
    // Reinicializa as medições para a versão corrigida
    iniciaLittle(&E_N);
    
    // Reseta variáveis para executar a simulação novamente com a versão corrigida
    metricas.tempoDecorrido = 0.0;
    fila = 0;
    proximaRequisicao = exponencial(mediaIntervaloRequisicoes);
    
    // Executa a simulação novamente com a versão corrigida
    while (metricas.tempoDecorrido < tempoSimulacao) {
        metricas.tempoDecorrido = fila ? 
            minimo(proximaRequisicao, tempoServico) : 
            proximaRequisicao;
        
        if (metricas.tempoDecorrido == proximaRequisicao) {
            fila++;
            
            if (fila == 1) {
                double tempoAtendimento = exponencial(mediaTempoServico);
                tempoServico = metricas.tempoDecorrido + tempoAtendimento;
            }
            
            proximaRequisicao = metricas.tempoDecorrido + exponencial(mediaIntervaloRequisicoes);
            
            // Atualiza medições de Little (VERSÃO CORRIGIDA)
            atualizaLittle(&E_N, metricas.tempoDecorrido, fila);
            
        } else {
            fila--;
            
            if (fila > 0) {
                double tempoAtendimento = exponencial(mediaTempoServico);
                tempoServico = metricas.tempoDecorrido + tempoAtendimento;
            }
            
            // Atualiza medições de Little (VERSÃO CORRIGIDA)
            atualizaLittle(&E_N, metricas.tempoDecorrido, fila);
        }
    }
    
    // Exibe resultados com a versão corrigida
    exibeResultados(metricas, E_N, E_W_chegadas, E_W_saidas, 1);
    
    return 0;
}
