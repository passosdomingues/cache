#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

// ============================================================================
// ESTRUTURAS DE DADOS
// ============================================================================

/**
 * @brief Estrutura para medições da Lei de Little
 * 
 * Utilizada para calcular métricas relacionadas ao número de requisições
 * no sistema e validar a Lei de Little durante a simulação.
 */
typedef struct {
    double tempoAnterior;                 // Momento do último evento registrado
    unsigned long int quantidadeRequisicoesSistema;  // Nº atual de requisições no sistema
    double somaAreaIntervalo;             // Soma acumulada da área sob a curva
} MedicaoLeiLittle;

// ============================================================================
// FUNÇÕES UTILITÁRIAS
// ============================================================================

/**
 * @brief Gera número aleatório entre 0 e 1 (exclusive)
 * @return double Valor aleatório no intervalo (0,1)
 */
double gerarAleatorio() {
    double numeroAleatorio = rand() / ((double) RAND_MAX + 1);
    return 1.0 - numeroAleatorio;
}

/**
 * @brief Gera valor da distribuição exponencial
 * @param taxa Taxa de ocorrência do evento (λ)
 * @return double Valor da distribuição exponencial
 */
double gerarExponencial(double taxa) {
    return (-1.0 / taxa) * log(gerarAleatorio());
}

/**
 * @brief Retorna o menor entre dois valores
 * @param valor1 Primeiro valor
 * @param valor2 Segundo valor
 * @return double Menor valor
 */
double obterMinimo(double valor1, double valor2) {
    return (valor1 < valor2) ? valor1 : valor2;
}

/**
 * @brief Inicializa estrutura de medição da Lei de Little
 * @param medicao Ponteiro para estrutura de medição
 */
void inicializarMedicaoLittle(MedicaoLeiLittle* medicao) {
    medicao->tempoAnterior = 0.0;
    medicao->quantidadeRequisicoesSistema = 0;
    medicao->somaAreaIntervalo = 0.0;
}

// ============================================================================
// FUNÇÃO PRINCIPAL
// ============================================================================

/**
 * @brief Simulador de sistema de filas M/M/1 com validação da Lei de Little
 * 
 * Este programa simula um sistema de filas com chegadas e atendimentos
 * exponencialmente distribuídos. O objetivo é calcular métricas de desempenho
 * e validar a Lei de Little, mostrando tanto a versão com bug quanto a versão
 * corrigida dos cálculos.
 * 
 * @return int Status de execução
 */
int main() {
    srand(time(NULL));
    
    // Variáveis para medições da Lei de Little (versão com bug)
    MedicaoLeiLittle medicaoNumeroRequisicoes;
    MedicaoLeiLittle medicaoChegadas;
    MedicaoLeiLittle medicaoSaidas;
    
    // Inicialização das medições
    inicializarMedicaoLittle(&medicaoNumeroRequisicoes);
    inicializarMedicaoLittle(&medicaoChegadas);
    inicializarMedicaoLittle(&medicaoSaidas);
    
    // Variáveis de controle da simulação
    double tempoDecorrido = 0.0;
    double tempoTotalSimulacao = 86400.0; // 24 horas em segundos
    
    // Variáveis de taxa (convertidas de médias fornecidas pelo usuário)
    double mediaIntervaloRequisicoes;
    double mediaTempoServico;
    
    // Variáveis de evento
    double tempoProximaRequisicao;
    double tempoProximoServico = 0.0;
    
    // Métricas da fila
    unsigned long int tamanhoFila = 0;
    unsigned long int tamanhoMaximoFila = 0;
    
    // Métricas de desempenho
    unsigned long int totalRequisicoes = 0;
    double somaIntervalosRequisicoes = 0.0;
    unsigned long int totalAtendimentos = 0;
    double somaTemposServico = 0.0;
    
    // Entrada de parâmetros
    printf("==================================================\n");
    printf("        SIMULADOR DE SISTEMA DE FILAS M/M/1\n");
    printf("==================================================\n");
    
    printf("\nInforme a média de tempo entre requisições: ");
    scanf("%lf", &mediaIntervaloRequisicoes);
    mediaIntervaloRequisicoes = 1.0 / mediaIntervaloRequisicoes;
    
    printf("Informe a média de tempo para atendimentos: ");
    scanf("%lf", &mediaTempoServico);
    mediaTempoServico = 1.0 / mediaTempoServico;
    
    // Inicialização da simulação
    tempoProximaRequisicao = gerarExponencial(mediaIntervaloRequisicoes);
    totalRequisicoes++;
    somaIntervalosRequisicoes = tempoProximaRequisicao;
    
    // ========================================================================
    // EXECUÇÃO DA SIMULAÇÃO
    // ========================================================================
    
    printf("\n>>>>>> Executando simulação...\n");
    
    while (tempoDecorrido < tempoTotalSimulacao) {
        // Determina o próximo evento
        tempoDecorrido = tamanhoFila ? 
            obterMinimo(tempoProximaRequisicao, tempoProximoServico) : 
            tempoProximaRequisicao;
        
        if (tempoDecorrido == tempoProximaRequisicao) {
            // Evento de chegada
            tamanhoFila++;
            
            // Atualiza o máximo da fila
            if (tamanhoFila > tamanhoMaximoFila) {
                tamanhoMaximoFila = tamanhoFila;
            }
            
            // Se o sistema estava vazio, inicia o atendimento
            if (tamanhoFila == 1) {
                double tempoAtendimento = gerarExponencial(mediaTempoServico);
                tempoProximoServico = tempoDecorrido + tempoAtendimento;
                totalAtendimentos++;
                somaTemposServico += tempoAtendimento;
            }
            
            // Agenda a próxima requisição
            double intervalo = gerarExponencial(mediaIntervaloRequisicoes);
            tempoProximaRequisicao = tempoDecorrido + intervalo;
            totalRequisicoes++;
            somaIntervalosRequisicoes += intervalo;
            
            // Atualiza medições de Little (VERSÃO COM BUG)
            medicaoNumeroRequisicoes.somaAreaIntervalo += 
                (tempoDecorrido - medicaoNumeroRequisicoes.tempoAnterior) * 
                medicaoNumeroRequisicoes.quantidadeRequisicoesSistema;
            medicaoNumeroRequisicoes.quantidadeRequisicoesSistema++;
            medicaoNumeroRequisicoes.tempoAnterior = tempoDecorrido;
            
            medicaoChegadas.somaAreaIntervalo += 
                (tempoDecorrido - medicaoChegadas.tempoAnterior) * 
                medicaoChegadas.quantidadeRequisicoesSistema;
            medicaoChegadas.quantidadeRequisicoesSistema++;
            medicaoChegadas.tempoAnterior = tempoDecorrido;
            
        } else {
            // Evento de saída
            tamanhoFila--;
            
            // Se ainda há clientes na fila, agenda a próxima saída
            if (tamanhoFila > 0) {
                double tempoAtendimento = gerarExponencial(mediaTempoServico);
                tempoProximoServico = tempoDecorrido + tempoAtendimento;
                totalAtendimentos++;
                somaTemposServico += tempoAtendimento;
            }
            
            // Atualiza medições de Little (VERSÃO COM BUG)
            medicaoNumeroRequisicoes.somaAreaIntervalo += 
                (tempoDecorrido - medicaoNumeroRequisicoes.tempoAnterior) * 
                medicaoNumeroRequisicoes.quantidadeRequisicoesSistema;
            medicaoNumeroRequisicoes.quantidadeRequisicoesSistema--;
            medicaoNumeroRequisicoes.tempoAnterior = tempoDecorrido;
            
            medicaoSaidas.somaAreaIntervalo += 
                (tempoDecorrido - medicaoSaidas.tempoAnterior) * 
                medicaoSaidas.quantidadeRequisicoesSistema;
            medicaoSaidas.quantidadeRequisicoesSistema++;
            medicaoSaidas.tempoAnterior = tempoDecorrido;
        }
    }
    
    // ========================================================================
    // CÁLCULO DAS MÉTRICAS E RESULTADOS
    // ========================================================================
    
    printf("\n==================================================\n");
    printf("            RESULTADOS DA SIMULAÇÃO\n");
    printf("==================================================\n");
    
    // Métricas básicas
    printf("\n---------------- Métricas da Fila ----------------\n");
    printf("Tempo total de simulação: %.2f segundos\n", tempoDecorrido);
    printf("Tamanho máximo da fila: %lu\n", tamanhoMaximoFila);
    printf("Total de requisições: %lu\n", totalRequisicoes);
    printf("Total de atendimentos: %lu\n", totalAtendimentos);
    
    // Métricas de tempo
    double mediaIntervalo = somaIntervalosRequisicoes / totalRequisicoes;
    double mediaServico = somaTemposServico / totalAtendimentos;
    printf("\n---------------- Métricas de Tempo ----------------\n");
    printf("Média entre requisições: %.6f segundos\n", mediaIntervalo);
    printf("Média de tempo de serviço: %.6f segundos\n", mediaServico);
    
    // Métricas de utilização
    double taxaChegada = 1.0 / mediaIntervalo;
    double taxaServico = 1.0 / mediaServico;
    double ocupacaoTeorica = taxaChegada / taxaServico;
    double ocupacaoCalculada = somaTemposServico / tempoDecorrido;
    printf("\n---------------- Métricas de Utilização ----------------\n");
    printf("Taxa de chegada (λ): %.6f req/segundo\n", taxaChegada);
    printf("Taxa de serviço (μ): %.6f req/segundo\n", taxaServico);
    printf("Ocupação teórica: %.6f\n", ocupacaoTeorica);
    printf("Ocupação calculada: %.6f\n", ocupacaoCalculada);
    
    // ========================================================================
    // VALIDAÇÃO DA LEI DE LITTLE (VERSÃO COM BUG)
    // ========================================================================
    
    printf("\n============== Lei de Little (VERSÃO COM BUG) ==============\n");
    
    double numeroMedioRequisicoes = medicaoNumeroRequisicoes.somaAreaIntervalo / tempoDecorrido;
    double tempoMedioResidencia = (medicaoChegadas.somaAreaIntervalo - medicaoSaidas.somaAreaIntervalo) / 
                                   medicaoChegadas.quantidadeRequisicoesSistema;
    double lambda = medicaoChegadas.quantidadeRequisicoesSistema / tempoDecorrido;
    double produtoLittle = lambda * tempoMedioResidencia;
    double erroLittle = fabs(numeroMedioRequisicoes - produtoLittle);
    
    printf("E[N] (número médio de requisições): %.6f\n", numeroMedioRequisicoes);
    printf("λ (taxa de chegada): %.6f\n", lambda);
    printf("E[W] (tempo médio de residência): %.6f\n", tempoMedioResidencia);
    printf("λ * E[W]: %.6f\n", produtoLittle);
    printf("Erro de Little: %.6f\n", erroLittle);
    
    // ========================================================================
    // VALIDAÇÃO DA LEI DE LITTLE (VERSÃO CORRIGIDA)
    // ========================================================================
    
    printf("\n============ Lei de Little (VERSÃO CORRIGIDA) =============\n");
    
    // Para a versão corrigida, precisamos recalcular a área com a lógica correta
    MedicaoLeiLittle medicaoCorrigida;
    inicializarMedicaoLittle(&medicaoCorrigida);
    
    // Reinicializa variáveis para nova simulação
    tempoDecorrido = 0.0;
    tamanhoFila = 0;
    tempoProximaRequisicao = gerarExponencial(mediaIntervaloRequisicoes);
    totalRequisicoes = 1;
    somaIntervalosRequisicoes = tempoProximaRequisicao;
    totalAtendimentos = 0;
    somaTemposServico = 0.0;
    
    // Executa a simulação novamente com a versão corrigida
    while (tempoDecorrido < tempoTotalSimulacao) {
        tempoDecorrido = tamanhoFila ? 
            obterMinimo(tempoProximaRequisicao, tempoProximoServico) : 
            tempoProximaRequisicao;
        
        if (tempoDecorrido == tempoProximaRequisicao) {
            tamanhoFila++;
            
            if (tamanhoFila == 1) {
                double tempoAtendimento = gerarExponencial(mediaTempoServico);
                tempoProximoServico = tempoDecorrido + tempoAtendimento;
                totalAtendimentos++;
                somaTemposServico += tempoAtendimento;
            }
            
            tempoProximaRequisicao = tempoDecorrido + gerarExponencial(mediaIntervaloRequisicoes);
            totalRequisicoes++;
            
            // Atualiza medições de Little (VERSÃO CORRIGIDA)
            medicaoCorrigida.somaAreaIntervalo += 
                (tempoDecorrido - medicaoCorrigida.tempoAnterior) * 
                medicaoCorrigida.quantidadeRequisicoesSistema;
            medicaoCorrigida.quantidadeRequisicoesSistema = tamanhoFila;
            medicaoCorrigida.tempoAnterior = tempoDecorrido;
            
        } else {
            tamanhoFila--;
            
            if (tamanhoFila > 0) {
                double tempoAtendimento = gerarExponencial(mediaTempoServico);
                tempoProximoServico = tempoDecorrido + tempoAtendimento;
                totalAtendimentos++;
                somaTemposServico += tempoAtendimento;
            }
            
            // Atualiza medições de Little (VERSÃO CORRIGIDA)
            medicaoCorrigida.somaAreaIntervalo += 
                (tempoDecorrido - medicaoCorrigida.tempoAnterior) * 
                medicaoCorrigida.quantidadeRequisicoesSistema;
            medicaoCorrigida.quantidadeRequisicoesSistema = tamanhoFila;
            medicaoCorrigida.tempoAnterior = tempoDecorrido;
        }
    }
    
    // Cálculos para a versão corrigida
    numeroMedioRequisicoes = medicaoCorrigida.somaAreaIntervalo / tempoDecorrido;
    tempoMedioResidencia = medicaoCorrigida.somaAreaIntervalo / totalRequisicoes;
    lambda = totalRequisicoes / tempoDecorrido;
    produtoLittle = lambda * tempoMedioResidencia;
    erroLittle = fabs(numeroMedioRequisicoes - produtoLittle);
    
    printf("E[N] (número médio de requisições): %.6f\n", numeroMedioRequisicoes);
    printf("λ (taxa de chegada): %.6f\n", lambda);
    printf("E[W] (tempo médio de residência): %.6f\n", tempoMedioResidencia);
    printf("λ * E[W]: %.6f\n", produtoLittle);
    printf("Erro de Little: %.6f\n", erroLittle);
    
    printf("\n==================================================\n");
    printf("    SIMULAÇÃO CONCLUÍDA COM SUCESSO!\n");
    printf("==================================================\n");
    
    return 0;
}
