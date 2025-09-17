#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<time.h>

typedef struct {
    double tempo_anterior;
    unsigned long int qt_requisicoes;
    double soma_area;
} medida_little;

double aleatorio() {
    double u = rand() / ((double) RAND_MAX + 1);
    //limitando entre (0,1]
    u = 1.0 - u;
    return (u);
}

double exponencial(double l){
    return (-1.0/l)*log(aleatorio());
}

double minimo(double n1, double n2){
    if(n1 < n2) return n1;
    return n2;
}

void inicia_little(medida_little * medidas){
    medidas->tempo_anterior = 0.0;
    medidas->qt_requisicoes = 0;
    medidas->soma_area = 0.0;
}

int main(void){
    srand(time(NULL));

    // NOVO: Array com os cenários de ocupação desejados
    double ocupacoes[] = {0.80, 0.90, 0.95, 0.999};
    int num_cenarios = sizeof(ocupacoes) / sizeof(ocupacoes[0]);

    // NOVO: Laço para executar a simulação para cada cenário
    for (int i = 0; i < num_cenarios; i++) {
        double ocupacao_alvo = ocupacoes[i];
        printf("\n======================================================\n");
        printf("=== INICIANDO SIMULACAO PARA OCUPACAO DE %.3f ===\n", ocupacao_alvo);
        printf("======================================================\n");

        // NOVO: Todas as variáveis da simulação são inicializadas aqui dentro
        // para garantir que cada cenário comece do zero.
        medida_little E_N;
        medida_little E_W_chegadas;
        medida_little E_W_saidas;
        inicia_little(&E_N);
        inicia_little(&E_W_chegadas);
        inicia_little(&E_W_saidas);
        
        double tempo_decorrido = 0.0;
        double tempo_simulacao = 86400.0;
        double media_inter_requisicoes;
        double media_tempo_servico;
        double proxima_requisicao;
        double tempo_servico = tempo_simulacao * 2; 

        unsigned long int fila = 0;
        unsigned long int max_fila = 0;

        unsigned long int qtd_requisicoes = 0;
        double soma_inter_requisicoes = 0.0; 
        unsigned long int qtd_servicos = 0;
        double soma_tempo_servico = 0.0;
        
        // NOVO: Definir parâmetros para atingir a ocupação alvo
        // Vamos fixar o tempo médio de serviço e calcular o tempo entre chegadas necessário.
        double tempo_medio_servico_base = 10.0; // Ex: serviço leva 10 segundos em média
        
        // Ocupação = tempo_medio_servico / tempo_medio_chegadas
        // Logo, tempo_medio_chegadas = tempo_medio_servico / ocupacao_alvo
        double tempo_medio_chegadas_base = tempo_medio_servico_base / ocupacao_alvo;

        // O código usa as TAXAS (1/tempo), então calculamos o inverso
        media_inter_requisicoes = 1.0 / tempo_medio_chegadas_base;
        media_tempo_servico = 1.0 / tempo_medio_servico_base;

        proxima_requisicao = exponencial(media_inter_requisicoes);
        qtd_requisicoes++;
        soma_inter_requisicoes = proxima_requisicao;
        
        // NOVO: Gerar nome do arquivo de saída dinamicamente
        char nome_arquivo[100];
        sprintf(nome_arquivo, "relatorio_ocupacao_%.3f.csv", ocupacao_alvo);
        
        FILE *arquivo_saida = fopen(nome_arquivo, "w");
        if (arquivo_saida == NULL) {
            printf("Erro ao abrir o arquivo de saída %s!\n", nome_arquivo);
            return 1; 
        }
        fprintf(arquivo_saida, "Tempo(s),Fila,E[N],E[W]\n");
        double proximo_ponto_relatorio = 10.0;

        while(tempo_decorrido < tempo_simulacao){
            double tempo_proximo_evento = minimo(proxima_requisicao, proximo_ponto_relatorio);
            if (fila > 0) {
                tempo_proximo_evento = minimo(tempo_proximo_evento, tempo_servico);
            }

            tempo_decorrido = tempo_proximo_evento;

            if (tempo_decorrido > tempo_simulacao) {
                break;
            }

            if(tempo_decorrido == proxima_requisicao){ // --- EVENTO DE CHEGADA ---
                E_N.soma_area += (tempo_decorrido - E_N.tempo_anterior) * E_N.qt_requisicoes;
                E_W_chegadas.soma_area += (tempo_decorrido - E_W_chegadas.tempo_anterior) * E_W_chegadas.qt_requisicoes;
                
                fila++;
                max_fila = fila > max_fila ? fila : max_fila;
                E_N.qt_requisicoes++;
                E_W_chegadas.qt_requisicoes++;
                E_N.tempo_anterior = tempo_decorrido;
                E_W_chegadas.tempo_anterior = tempo_decorrido;

                if(fila == 1){ 
                    tempo_servico = tempo_decorrido + exponencial(media_tempo_servico);
                    qtd_servicos++;
                    soma_tempo_servico += tempo_servico - tempo_decorrido;
                }

                proxima_requisicao = tempo_decorrido + exponencial(media_inter_requisicoes);
                qtd_requisicoes++;
                soma_inter_requisicoes += proxima_requisicao - tempo_decorrido;

            } else if (fila > 0 && tempo_decorrido == tempo_servico) { // --- EVENTO DE SAÍDA ---
                E_N.soma_area += (tempo_decorrido - E_N.tempo_anterior) * E_N.qt_requisicoes;
                E_W_saidas.soma_area += (tempo_decorrido - E_W_saidas.tempo_anterior) * E_W_saidas.qt_requisicoes;
                
                fila--;
                E_N.qt_requisicoes--;
                E_W_saidas.qt_requisicoes++;
                E_N.tempo_anterior = tempo_decorrido;
                E_W_saidas.tempo_anterior = tempo_decorrido;

                if(fila > 0){ 
                    tempo_servico = tempo_decorrido + exponencial(media_tempo_servico);
                    qtd_servicos++;
                    soma_tempo_servico += tempo_servico - tempo_decorrido;
                } else { 
                    tempo_servico = tempo_simulacao * 2;
                }

            } else { // --- EVENTO DE RELATÓRIO ---
                E_N.soma_area += (tempo_decorrido - E_N.tempo_anterior) * E_N.qt_requisicoes;
                E_W_chegadas.soma_area += (tempo_decorrido - E_W_chegadas.tempo_anterior) * E_W_chegadas.qt_requisicoes;
                E_W_saidas.soma_area += (tempo_decorrido - E_W_saidas.tempo_anterior) * E_W_saidas.qt_requisicoes;
                
                E_N.tempo_anterior = tempo_decorrido;
                E_W_chegadas.tempo_anterior = tempo_decorrido;
                E_W_saidas.tempo_anterior = tempo_decorrido;

                double E_N_atual = E_N.soma_area / tempo_decorrido;
                double E_W_atual = 0.0;
                if (E_W_chegadas.qt_requisicoes > 0) {
                    E_W_atual = (E_W_chegadas.soma_area - E_W_saidas.soma_area) / E_W_chegadas.qt_requisicoes;
                }

                printf("Tempo: %.0fs | Fila: %lu | E[N] parcial: %f\n", tempo_decorrido, fila, E_N_atual);

                fprintf(arquivo_saida, "%.0f,%lu,%f,%f\n", tempo_decorrido, fila, E_N_atual, E_W_atual);
                fflush(arquivo_saida);

                proximo_ponto_relatorio += 10.0;
            }
        }

        tempo_decorrido = tempo_simulacao;
        E_N.soma_area += (tempo_decorrido - E_N.tempo_anterior) * E_N.qt_requisicoes;
        E_W_chegadas.soma_area += (tempo_decorrido - E_W_chegadas.tempo_anterior) * E_W_chegadas.qt_requisicoes;
        E_W_saidas.soma_area += (tempo_decorrido - E_W_saidas.tempo_anterior) * E_W_saidas.qt_requisicoes;

        printf("\n---=== Métricas e Validações Finais (Ocupacao %.3f) ===---\n", ocupacao_alvo);
        printf("max fila: %ld\n", max_fila);
        printf("media entre requisicoes: %f\n", soma_inter_requisicoes/qtd_requisicoes);
        printf("media tempos de sevico: %f\n", soma_tempo_servico/qtd_servicos);
        // NOVO: Uso das variáveis base para mostrar a ocupação esperada
        printf("Ocupação esperada: %f\n", tempo_medio_servico_base / tempo_medio_chegadas_base);
        printf("Ocupação calculada: %f\n", soma_tempo_servico/tempo_decorrido);
            
        printf("\n---=== Lei de Little ===---\n");

        double E_N_final = E_N.soma_area / tempo_decorrido;
        double E_W_final = (E_W_chegadas.soma_area - E_W_saidas.soma_area) / E_W_chegadas.qt_requisicoes;
        double lambda = (double)E_W_chegadas.qt_requisicoes / tempo_decorrido;
        double erro_little = E_N_final - lambda * E_W_final;  

        printf("E[N]: %f\n", E_N_final);
        printf("E[W]: %f\n", E_W_final);
        printf("Erro Little: %e\n", erro_little);

        fclose(arquivo_saida);
        printf("Arquivo '%s' gerado com sucesso.\n", nome_arquivo);
    } // NOVO: Fim do laço dos cenários

    return 0;
}
