#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

/**
 * Estrutura para armazenar métricas da Lei de Little
 */
typedef struct {
    double tempoAnterior;
    unsigned long int quantidadeRequisicoes;
    double somaArea;
} MetricasLittle;

/**
 * Gera um número pseudoaleatório entre 0 e 1
 */
double gerarNumeroAleatorio() {
    double numeroAleatorio = rand() / ((double) RAND_MAX + 1);
    numeroAleatorio = 1.0 - numeroAleatorio;
    return numeroAleatorio;
}

/**
 * Gera uma amostra da distribuição exponencial
 */
double distribuiçãoExponencial(double parametroTaxa) {
    return (-1.0 / parametroTaxa) * log(gerarNumeroAleatorio());
}

/**
 * Encontra o mínimo entre dois números
 */
double encontrarMinimo(double numero1, double numero2) {
    if (numero1 < numero2) return numero1;
    return numero2;
}

/**
 * Inicializa as métricas da Lei de Little
 */
void inicializarMetricasLittle(MetricasLittle* metricas) {
    metricas->tempoAnterior = 0.0;
    metricas->quantidadeRequisicoes = 0;
    metricas->somaArea = 0.0;
}

/**
 * Executa a simulação de fila para um cenário específico
 */
void executarSimulacao(double ocupacaoDesejada, double tempoTotalSimulacao, const char* nomeArquivo) {
    srand(time(NULL));

    // Abre arquivo para escrita dos dados
    FILE* arquivo = fopen(nomeArquivo, "w");
    if (arquivo == NULL) {
        printf("Erro ao abrir o arquivo %s\n", nomeArquivo);
        return;
    }
    
    // Escreve cabeçalho do arquivo
    fprintf(arquivo, "Tempo,Ocupacao,NumeroMedioRequisicoes,TempoMedioEspera,TamanhoFila\n");

    MetricasLittle metricasNumeroRequisicoesSistema;
    MetricasLittle metricasTempoEsperaChegadas;
    MetricasLittle metricasTempoEsperaSaidas;
    
    inicializarMetricasLittle(&metricasNumeroRequisicoesSistema);
    inicializarMetricasLittle(&metricasTempoEsperaChegadas);
    inicializarMetricasLittle(&metricasTempoEsperaSaidas);
    
    double tempoDecorrido = 0.0;
    double taxaServico = 1.0;
    double taxaChegada = ocupacaoDesejada * taxaServico;

    double proximaChegada = distribuiçãoExponencial(taxaChegada);
    double proximaSaida = 0.0;
    double tempoServicoAtual = 0.0;

    unsigned long int tamanhoFila = 0;
    unsigned long int tamanhoMaximoFila = 0;

    unsigned long int totalRequisicoes = 0;
    double somaIntervalosChegada = 0.0;
    unsigned long int totalAtendimentos = 0;
    double somaTemposServico = 0.0;

    double proximaMedicao = 10.0;
    int contadorMedicoes = 1;

    // Loop principal de simulação
    while (tempoDecorrido < tempoTotalSimulacao) {
        tempoDecorrido = tamanhoFila ? 
            encontrarMinimo(proximaChegada, proximaSaida) : 
            proximaChegada;

        // Realiza medições periódicas e escreve no arquivo
        while (tempoDecorrido >= proximaMedicao && proximaMedicao <= tempoTotalSimulacao) {
            double ocupacaoAtual = somaTemposServico / proximaMedicao;
            double numeroMedioRequisicoes = metricasNumeroRequisicoesSistema.somaArea / proximaMedicao;
            double tempoMedioEspera = (metricasTempoEsperaChegadas.somaArea - metricasTempoEsperaSaidas.somaArea) / 
                                     metricasTempoEsperaChegadas.quantidadeRequisicoes;
            
            // Escreve dados no arquivo
            fprintf(arquivo, "%.0f,%.6f,%.6f,%.6f,%lu\n", 
                   proximaMedicao, ocupacaoAtual, numeroMedioRequisicoes, tempoMedioEspera, tamanhoFila);
            
            proximaMedicao += 10.0;
            contadorMedicoes++;
        }

        // Processamento de eventos
        if (tempoDecorrido == proximaChegada) {
            tamanhoFila++;
            
            if (tamanhoFila > tamanhoMaximoFila) {
                tamanhoMaximoFila = tamanhoFila;
            }

            if (tamanhoFila == 1) {
                tempoServicoAtual = distribuiçãoExponencial(taxaServico);
                proximaSaida = tempoDecorrido + tempoServicoAtual;
                
                totalAtendimentos++;
                somaTemposServico += tempoServicoAtual;
            }

            double intervaloChegada = distribuiçãoExponencial(taxaChegada);
            proximaChegada = tempoDecorrido + intervaloChegada;
            
            totalRequisicoes++;
            somaIntervalosChegada += intervaloChegada;
            
            // Atualiza métricas
            metricasNumeroRequisicoesSistema.somaArea += 
                (tempoDecorrido - metricasNumeroRequisicoesSistema.tempoAnterior) * 
                metricasNumeroRequisicoesSistema.quantidadeRequisicoes;
            metricasNumeroRequisicoesSistema.quantidadeRequisicoes++;
            metricasNumeroRequisicoesSistema.tempoAnterior = tempoDecorrido;

            metricasTempoEsperaChegadas.somaArea += 
                (tempoDecorrido - metricasTempoEsperaChegadas.tempoAnterior) * 
                metricasTempoEsperaChegadas.quantidadeRequisicoes;
            metricasTempoEsperaChegadas.quantidadeRequisicoes++;
            metricasTempoEsperaChegadas.tempoAnterior = tempoDecorrido;
        } else {
            tamanhoFila--;

            if (tamanhoFila > 0) {
                tempoServicoAtual = distribuiçãoExponencial(taxaServico);
                proximaSaida = tempoDecorrido + tempoServicoAtual;
                
                totalAtendimentos++;
                somaTemposServico += tempoServicoAtual;
            }

            // Atualiza métricas
            metricasNumeroRequisicoesSistema.somaArea += 
                (tempoDecorrido - metricasNumeroRequisicoesSistema.tempoAnterior) * 
                metricasNumeroRequisicoesSistema.quantidadeRequisicoes;
            metricasNumeroRequisicoesSistema.quantidadeRequisicoes--;
            metricasNumeroRequisicoesSistema.tempoAnterior = tempoDecorrido;

            metricasTempoEsperaSaidas.somaArea += 
                (tempoDecorrido - metricasTempoEsperaSaidas.tempoAnterior) * 
                metricasTempoEsperaSaidas.quantidadeRequisicoes;
            metricasTempoEsperaSaidas.quantidadeRequisicoes++;
            metricasTempoEsperaSaidas.tempoAnterior = tempoDecorrido;
        }
    }

    // Ajuste final das métricas
    metricasTempoEsperaChegadas.somaArea += 
        (tempoDecorrido - metricasTempoEsperaChegadas.tempoAnterior) * 
        metricasTempoEsperaChegadas.quantidadeRequisicoes;

    metricasTempoEsperaSaidas.somaArea += 
        (tempoDecorrido - metricasTempoEsperaSaidas.tempoAnterior) * 
        metricasTempoEsperaSaidas.quantidadeRequisicoes;

    // Cálculo das métricas finais
    double numeroMedioRequisicoesSistema = metricasNumeroRequisicoesSistema.somaArea / tempoDecorrido;
    double tempoMedioEsperaSistema = 
        (metricasTempoEsperaChegadas.somaArea - metricasTempoEsperaSaidas.somaArea) / 
        metricasTempoEsperaChegadas.quantidadeRequisicoes;
    double taxaChegadaMedia = metricasTempoEsperaChegadas.quantidadeRequisicoes / tempoDecorrido;
    double erroLittle = numeroMedioRequisicoesSistema - taxaChegadaMedia * tempoMedioEsperaSistema;
    
    double ocupacaoCalculada = somaTemposServico / tempoDecorrido;
    
    // Exibição dos resultados finais
    printf("\n=== Resultados para ocupação %.3f ===\n", ocupacaoDesejada);
    printf("Tamanho máximo da fila: %lu\n", tamanhoMaximoFila);
    printf("Ocupação calculada: %.6f\n", ocupacaoCalculada);
    printf("E[N] (Número médio de requisições no sistema): %.6f\n", numeroMedioRequisicoesSistema);
    printf("E[W] (Tempo médio de espera no sistema): %.6f\n", tempoMedioEsperaSistema);
    printf("Erro na Lei de Little: %.6f\n", erroLittle);
    
    // Fecha o arquivo
    fclose(arquivo);
}

/**
 * Função principal
 */
int main() {
    double cenariosOcupacao[4] = {0.80, 0.90, 0.95, 0.999};
    const char* nomesArquivos[4] = {
        "data/dados_ocupacao_080.csv",
        "data/dados_ocupacao_090.csv", 
        "data/dados_ocupacao_095.csv",
        "data/dados_ocupacao_0999.csv"
    };
    
    double tempoSimulacao = 86400.0; // 24 horas em segundos

    for (int i = 0; i < 4; i++) {
        executarSimulacao(cenariosOcupacao[i], tempoSimulacao, nomesArquivos[i]);
        printf("Dados salvos em: %s\n", nomesArquivos[i]);
        printf("----------------------------------------\n");
    }

    printf("Simulação concluída. Use o script Python para visualizar os dados.\n");
    return 0;
}