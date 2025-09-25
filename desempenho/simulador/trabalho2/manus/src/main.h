/**
 * @file main.h
 * @brief Definições e protótipos para o simulador de filas C.
 *
 * Este arquivo contém as definições de estruturas de dados, constantes e protótipos de funções
 * para o simulador de filas event-driven. Ele suporta múltiplas filas lógicas, políticas de decisão
 * configuráveis e coleta de métricas detalhadas para análise.
 *
 * Autor: Rafael Passos Domingues
 * Última Atualização: 2025 Sep 25 14h36
 */

#ifndef MAIN_H
#define MAIN_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

// Constantes de simulação
#define TEMPO_SIMULACAO_PADRAO 86400.0 // 24 horas em segundos
#define INTERVALO_AMOSTRAGEM 10.0     // Amostragem a cada 10 segundos
#define NUM_FILAS 3                   // Número de filas lógicas

// Estrutura para métricas da Lei de Little
typedef struct {
    double tempoAnterior;       ///< @brief Tempo do evento anterior para cálculo de área.
    unsigned long int qtRequisicoes; ///< @brief Quantidade de requisições no sistema/fila.
    double somaArea;            ///< @brief Soma das áreas para cálculo de média.
} MedidaLittle;

// Estrutura para uma requisição (cliente)
typedef struct {
    double tempoChegada;        ///< @brief Tempo de chegada da requisição na fila.
    int idFilaOrigem;           ///< @brief ID da fila de onde a requisição veio.
} Requisicao;

// Estrutura para uma fila lógica
typedef struct {
    int id;                     ///< @brief Identificador único da fila.
    double mediaTempoServico;   ///< @brief Média do tempo de serviço para esta fila.
    double mediaInterRequisicoes; ///< @brief Média do tempo entre requisições para esta fila.
    unsigned long int tamanhoAtual; ///< @brief Número atual de requisições na fila.
    unsigned long int maxTamanho;   ///< @brief Tamanho máximo atingido pela fila.
    Requisicao *fila;           ///< @brief Array dinâmico de requisições na fila.
    int capacidadeFila;         ///< @brief Capacidade atual do array da fila.
    double somaTemposEspera;    ///< @brief Soma dos tempos de espera das requisições atendidas.
    unsigned long int qtRequisicoesAtendidas; ///< @brief Quantidade de requisições atendidas.
    MedidaLittle littleEN;      ///< @brief Métricas Little para E[N] (fila + servidor).
    MedidaLittle littleEWChegadas; ///< @brief Métricas Little para E[W] (chegadas).
    MedidaLittle littleEWSaidas;   ///< @brief Métricas Little para E[W] (saídas).
    double ultimaAmostragemTempo; ///< @brief Tempo da última amostragem para esta fila.
    double lambdaMedido;        ///< @brief Taxa de chegada medida para esta fila.
    double ocupacaoMedida;      ///< @brief Ocupação medida para esta fila.
    double somaInterChegadas;   ///< @brief Soma dos intervalos entre chegadas para lambda medido.
    unsigned long int qtChegadas; ///< @brief Quantidade de chegadas para lambda medido.
} FilaLogica;

// Estrutura para o estado geral do simulador
typedef struct {
    double tempoAtual;          ///< @brief Tempo atual da simulação.
    double proximaRequisicaoTempo[NUM_FILAS]; ///< @brief Tempo da próxima requisição para cada fila.
    double tempoServicoFim;     ///< @brief Tempo de término do serviço atual no servidor.
    int filaEmAtendimento;      ///< @brief ID da fila atualmente em atendimento (-1 se ocioso).
    FilaLogica filas[NUM_FILAS]; ///< @brief Array de filas lógicas.
    double tempoProximaAmostragem; ///< @brief Tempo da próxima amostragem global.
    FILE *arquivoSaidaCSV;      ///< @brief Ponteiro para o arquivo CSV de saída.
} EstadoSimulador;

// Ponteiro para função de política de decisão
typedef int (*PoliticaDecisao)(EstadoSimulador *estado);

// Protótipos de funções utilitárias
double aleatorio();
double exponencial(double lambda);
double minimo(double n1, double n2);

// Protótipos de funções de inicialização e gerenciamento
void inicializaMedidaLittle(MedidaLittle *medidas);
void inicializaFila(FilaLogica *fila, int id, double mediaInterRequisicoes, double mediaTempoServico);
void inicializaEstadoSimulador(EstadoSimulador *estado, double muGlobal, double rhos[NUM_FILAS], unsigned int seed, const char *nomeArquivoSaida);
void adicionaRequisicaoFila(FilaLogica *fila, double tempoChegada);
Requisicao removeRequisicaoFila(FilaLogica *fila);

// Protótipos de funções de eventos
void eventoChegada(EstadoSimulador *estado, int idFila, PoliticaDecisao politica);
void eventoSaida(EstadoSimulador *estado, PoliticaDecisao politica);
void eventoAmostragem(EstadoSimulador *estado);

// Protótipos de políticas de decisão
int politicaMaiorFila(EstadoSimulador *estado);
int politicaMaiorTempoEsperaMedio(EstadoSimulador *estado);
int politicaClienteMaisAntigo(EstadoSimulador *estado);

// Protótipos de funções de simulação
void executaSimulacao(EstadoSimulador *estado, PoliticaDecisao politica);

// Protótipos de funções de validação e saída
void calculaMetricasFinais(EstadoSimulador *estado);
void escreveCabecalhoCSV(FILE *arquivo);
void escreveAmostraCSV(FILE *arquivo, EstadoSimulador *estado, int sampleIndex);

#endif // MAIN_H


