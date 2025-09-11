#include<stdio.h>
#include<stdlib.h>
#include<math.h>

/**
 * @struct medida_little
 * Estrutura usada para computar integrais temporais e contagens necessárias
 * para aplicar e validar a Lei de Little na simulação.
 *
 * @param tempo_anterior Marca o último instante em que a área foi atualizada
 * @param qt_requisicoes Contador de requisições (chegadas ou saídas)
 * @param soma_area      Integral acumulada de quantidade × tempo
 */
typedef struct {
    double tempo_anterior;
    unsigned long int qt_requisicoes;
    double soma_area;
} medida_little;

/**
 * @brief Gera número aleatório uniforme (0,1]
 */
double aleatorio() {
    double u = rand() / ((double) RAND_MAX + 1);
    u = 1.0 - u;
    return u;
}

/**
 * @brief Gera variável exponencial com taxa l
 * @param l taxa (lambda ou mu)
 */
double exponencial(double l){
    double x = (-1.0/l)*log(aleatorio());
    //printf("[DEBUG] exponencial(%.6lf) -> %.6lf\n", l, x);
    return x;
}

/**
 * @brief Retorna o menor entre dois valores
 */
double minimo(double n1, double n2){
    return (n1 < n2) ? n1 : n2;
}

/**
 * @brief Inicializa estrutura de medida_little
 */
void inicia_little(medida_little * medidas){
    medidas->tempo_anterior = 0.0;
    medidas->qt_requisicoes = 0;
    medidas->soma_area = 0.0;
}

int main(void){
    // Seed fixa para reprodutibilidade
    srand(0);

    /** @param cenarios Ocupações a serem testadas */
    double cenarios[] = {0.80, 0.90, 0.95, 0.999};
    int qtd_cenarios = 4;

    for(int c = 0; c < qtd_cenarios; c++){
        /** @param E_N Estrutura usada para calcular o valor médio de N(t) */
        medida_little E_N;
        /** @param E_W_chegadas Estrutura para acumular áreas relacionadas às chegadas */
        medida_little E_W_chegadas;
        /** @param E_W_saidas Estrutura para acumular áreas relacionadas às saídas */
        medida_little E_W_saidas;
        inicia_little(&E_N);
        inicia_little(&E_W_chegadas);
        inicia_little(&E_W_saidas);

        /** @param tempo_decorrido Relógio global da simulação */
        double tempo_decorrido = 0.0;
        /** @param tempo_simulacao Tempo total de simulação em segundos */
        double tempo_simulacao = 86400.0;
        /** @param media_inter_requisicoes Média entre chegadas (informada pelo usuário, convertida para taxa λ) */
        double media_inter_requisicoes;
        /** @param media_tempo_servico Média de tempo de serviço (informada pelo usuário, convertida para taxa μ) */
        double media_tempo_servico;
        /** @param proxima_requisicao Tempo agendado para a próxima chegada */
        double proxima_requisicao;
        /** @param tempo_servico Tempo agendado para conclusão do serviço em andamento */
        double tempo_servico;
        /** @param fila Número atual de clientes na fila (inclui o em serviço) */
        unsigned long int fila = 0;
        /** @param max_fila Maior valor observado de fila durante a simulação */
        unsigned long int max_fila = 0;

        /** @param qtd_requisicoes Número de chegadas geradas */
        unsigned long int qtd_requisicoes = 0;
        /** @param soma_inter_requisicoes Soma acumulada dos intervalos entre chegadas */
        double soma_inter_requisicoes;
        /** @param qtd_servicos Número de serviços iniciados */
        unsigned long int qtd_servicos = 0;
        /** @param soma_tempo_servico Soma acumulada dos tempos de serviço realizados */
        double soma_tempo_servico = 0.0;

        /**
         * Neste ponto, mantemos os mesmos printf/scanf
         * mas os valores são apenas para debug e consistência.
         */
        printf("Informe a media de tempo entre requisicoes: ");
        scanf("%lf", &media_inter_requisicoes);
        media_inter_requisicoes = 1.0/media_inter_requisicoes;
        //printf("[DEBUG] taxa de chegada (lambda): %.6lf\n", media_inter_requisicoes);

        printf("Informe a media de tempo para atendimentos: ");
        scanf("%lf", &media_tempo_servico);
        media_tempo_servico = 1.0/media_tempo_servico;
        //printf("[DEBUG] taxa de servico (mu): %.6lf\n", media_tempo_servico);

        /**
         * Ajusta parâmetros para o cenário de ocupação específico.
         * Ocupação = lambda/mu. Mantemos mu fixo (do scanf) e ajustamos lambda.
         */
        double ocupacao = cenarios[c];
        media_inter_requisicoes = media_tempo_servico * ocupacao;

        proxima_requisicao = exponencial(media_inter_requisicoes);
        qtd_requisicoes++;
        soma_inter_requisicoes = proxima_requisicao;

        /** @param proximo_checkpoint Marca próximo instante de checkpoint */
        double proximo_checkpoint = 10.0;

        /** Cria arquivo de saída para este cenário */
        char nome_arquivo[64];
        sprintf(nome_arquivo, "data/ocupacao_%03d.dat", (int)(ocupacao*1000));
        FILE *fout = fopen(nome_arquivo, "w");

        while(tempo_decorrido < tempo_simulacao){
            if(fila)
                tempo_decorrido = minimo(proxima_requisicao, tempo_servico);
            else
                tempo_decorrido = proxima_requisicao;

            if(fabs(tempo_decorrido - proxima_requisicao) < 1e-9){
                // Chegada
                fila++;
                max_fila = (fila > max_fila) ? fila : max_fila;

                if(fila == 1){
                    tempo_servico = tempo_decorrido + exponencial(media_tempo_servico);
                    qtd_servicos++;
                    soma_tempo_servico += tempo_servico - tempo_decorrido;
                }

                proxima_requisicao = tempo_decorrido + exponencial(media_inter_requisicoes);
                qtd_requisicoes++;
                soma_inter_requisicoes += proxima_requisicao - tempo_decorrido;

                E_N.soma_area += (tempo_decorrido - E_N.tempo_anterior) * E_N.qt_requisicoes;
                E_N.qt_requisicoes++;
                E_N.tempo_anterior = tempo_decorrido;

                E_W_chegadas.soma_area += (tempo_decorrido - E_W_chegadas.tempo_anterior) * E_W_chegadas.qt_requisicoes;
                E_W_chegadas.qt_requisicoes++;
                E_W_chegadas.tempo_anterior = tempo_decorrido;
            }else{
                // Saída
                fila--;

                if(fila){
                    tempo_servico = tempo_decorrido + exponencial(media_tempo_servico);
                    qtd_servicos++;
                    soma_tempo_servico += tempo_servico - tempo_decorrido;
                }

                E_N.soma_area += (tempo_decorrido - E_N.tempo_anterior) * E_N.qt_requisicoes;
                E_N.qt_requisicoes--;
                E_N.tempo_anterior = tempo_decorrido;

                E_W_saidas.soma_area += (tempo_decorrido - E_W_saidas.tempo_anterior) * E_W_saidas.qt_requisicoes;
                E_W_saidas.qt_requisicoes++;
                E_W_saidas.tempo_anterior = tempo_decorrido;
            }

            /** Checkpoints a cada 10s */
            while(tempo_decorrido >= proximo_checkpoint && proximo_checkpoint <= tempo_simulacao){
                double E_N_parcial = E_N.soma_area / tempo_decorrido;
                double E_W_parcial = (E_W_chegadas.soma_area - E_W_saidas.soma_area) / E_W_chegadas.qt_requisicoes;
                fprintf(fout, "%.0lf %.6lf %.6lf\n", proximo_checkpoint, E_N_parcial, E_W_parcial);
                proximo_checkpoint += 10.0;
            }
        }

        E_W_chegadas.soma_area += (tempo_decorrido - E_W_chegadas.tempo_anterior) * E_W_chegadas.qt_requisicoes;
        E_W_saidas.soma_area += (tempo_decorrido - E_W_saidas.tempo_anterior) * E_W_saidas.qt_requisicoes;

        printf("\n---=== Métricas e Validações ===---\n");
        printf("Cenário ocupacao: %.3lf\n", ocupacao);
        printf("max fila: %lu\n", max_fila);
        printf("media entre requisicoes: %.6lf\n", soma_inter_requisicoes/qtd_requisicoes);
        printf("media tempos de servico: %.6lf\n", soma_tempo_servico/qtd_servicos);
        printf("ocupacao esperada: %.6lf\n", media_inter_requisicoes/media_tempo_servico);
        printf("ocupacao calculada: %.6lf\n", soma_tempo_servico/tempo_decorrido);

        double E_N_final = E_N.soma_area/tempo_decorrido;
        double E_W_final = (E_W_chegadas.soma_area - E_W_saidas.soma_area)/E_W_chegadas.qt_requisicoes;
        double lambda = (double)E_W_chegadas.qt_requisicoes/tempo_decorrido;
        double erro_little = E_N_final - lambda * E_W_final;

        printf("E[N]: %.6lf\n", E_N_final);
        printf("E[W]: %.6lf\n", E_W_final);
        printf("Erro little: %.16lf\n", erro_little);

        fclose(fout);
    }

    return 0;
}

