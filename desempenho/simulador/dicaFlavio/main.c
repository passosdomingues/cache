#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<time.h>
#include<float.h>

#define MAX_HEAP_SIZE 1000000
#define SAMPLE_INTERVAL 10.0

typedef struct {
    double tempo_anterior;
    unsigned long int qt_requisicoes;
    double soma_area;
} medida_little;

typedef struct {
    double tempo;
    int tipo; // 0: chegada, 1: saída, 2: amostragem
} Evento;

typedef struct {
    Evento* eventos;
    int tamanho;
    int capacidade;
} HeapEventos;

double aleatorio() {
    double u = rand() / ((double) RAND_MAX + 1);
    u = 1.0 - u;
    return u;
}

double exponencial(double l) {
    return (-1.0/l) * log(aleatorio());
}

HeapEventos* criar_heap(int capacidade) {
    HeapEventos* heap = (HeapEventos*)malloc(sizeof(HeapEventos));
    heap->eventos = (Evento*)malloc(capacidade * sizeof(Evento));
    heap->tamanho = 0;
    heap->capacidade = capacidade;
    return heap;
}

void destruir_heap(HeapEventos* heap) {
    free(heap->eventos);
    free(heap);
}

void inserir_evento(HeapEventos* heap, Evento novo_evento) {
    if (heap->tamanho >= heap->capacidade) {
        printf("Erro: Heap cheio\n");
        exit(1);
    }
    
    int i = heap->tamanho++;
    while (i > 0) {
        int pai = (i - 1) / 2;
        if (heap->eventos[pai].tempo <= novo_evento.tempo) break;
        heap->eventos[i] = heap->eventos[pai];
        i = pai;
    }
    heap->eventos[i] = novo_evento;
}

Evento remover_evento(HeapEventos* heap) {
    if (heap->tamanho <= 0) {
        printf("Erro: Heap vazio\n");
        exit(1);
    }
    
    Evento resultado = heap->eventos[0];
    Evento ultimo = heap->eventos[--heap->tamanho];
    int i = 0;
    
    while (1) {
        int filho_esq = 2 * i + 1;
        int filho_dir = 2 * i + 2;
        int menor = i;
        
        if (filho_esq < heap->tamanho && heap->eventos[filho_esq].tempo < heap->eventos[menor].tempo)
            menor = filho_esq;
        if (filho_dir < heap->tamanho && heap->eventos[filho_dir].tempo < heap->eventos[menor].tempo)
            menor = filho_dir;
        
        if (menor == i) break;
        
        heap->eventos[i] = heap->eventos[menor];
        i = menor;
    }
    heap->eventos[i] = ultimo;
    return resultado;
}

void inicia_little(medida_little * medidas) {
    medidas->tempo_anterior = 0.0;
    medidas->qt_requisicoes = 0;
    medidas->soma_area = 0.0;
}

void atualizar_medidas(medida_little* E_N, medida_little* E_W_chegadas, medida_little* E_W_saidas, double tempo_atual) {
    E_N->soma_area += (tempo_atual - E_N->tempo_anterior) * E_N->qt_requisicoes;
    E_W_chegadas->soma_area += (tempo_atual - E_W_chegadas->tempo_anterior) * E_W_chegadas->qt_requisicoes;
    E_W_saidas->soma_area += (tempo_atual - E_W_saidas->tempo_anterior) * E_W_saidas->qt_requisicoes;
    
    E_N->tempo_anterior = tempo_atual;
    E_W_chegadas->tempo_anterior = tempo_atual;
    E_W_saidas->tempo_anterior = tempo_atual;
}

void run_simulation(double media_inter_requisicoes, double media_tempo_servico, const char* filename) {
    medida_little E_N, E_W_chegadas, E_W_saidas;
    inicia_little(&E_N);
    inicia_little(&E_W_chegadas);
    inicia_little(&E_W_saidas);
    
    double tempo_decorrido = 0.0;
    double tempo_simulacao = 86400.0;
    
    // Criar heap de eventos
    HeapEventos* heap = criar_heap(MAX_HEAP_SIZE);
    
    // Variáveis do sistema
    unsigned long int fila = 0;
    unsigned long int max_fila = 0;
    double proxima_requisicao = exponencial(media_inter_requisicoes);
    
    // Inserir eventos iniciais
    Evento evento_chegada = {proxima_requisicao, 0};
    Evento evento_amostragem = {SAMPLE_INTERVAL, 2};
    inserir_evento(heap, evento_chegada);
    inserir_evento(heap, evento_amostragem);
    
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        printf("Erro ao abrir arquivo %s\n", filename);
        exit(1);
    }

    while (heap->tamanho > 0 && tempo_decorrido < tempo_simulacao) {
        Evento proximo_evento = remover_evento(heap);
        tempo_decorrido = proximo_evento.tempo;
        
        // Atualizar medidas de Little
        atualizar_medidas(&E_N, &E_W_chegadas, &E_W_saidas, tempo_decorrido);
        
        switch (proximo_evento.tipo) {
            case 0: // Chegada
                fila++;
                max_fila = fila > max_fila ? fila : max_fila;
                
                // Agendar próxima chegada
                proxima_requisicao = tempo_decorrido + exponencial(media_inter_requisicoes);
                Evento nova_chegada = {proxima_requisicao, 0};
                inserir_evento(heap, nova_chegada);
                
                // Se era o primeiro na fila, agendar serviço
                if (fila == 1) {
                    double tempo_servico = tempo_decorrido + exponencial(media_tempo_servico);
                    Evento nova_saida = {tempo_servico, 1};
                    inserir_evento(heap, nova_saida);
                }
                
                // Atualizar medidas
                E_N.qt_requisicoes++;
                E_W_chegadas.qt_requisicoes++;
                break;
                
            case 1: // Saída
                fila--;
                
                // Se ainda há pessoas na fila, agendar próxima saída
                if (fila > 0) {
                    double tempo_servico = tempo_decorrido + exponencial(media_tempo_servico);
                    Evento nova_saida = {tempo_servico, 1};
                    inserir_evento(heap, nova_saida);
                }
                
                // Atualizar medidas
                E_N.qt_requisicoes--;
                E_W_saidas.qt_requisicoes++;
                break;
                
            case 2: // Amostragem
                // Calcular e registrar métricas
                double E_N_sample = E_N.soma_area / tempo_decorrido;
                double E_W_sample = (E_W_chegadas.soma_area - E_W_saidas.soma_area) / E_W_chegadas.qt_requisicoes;
                fprintf(file, "%lf %lf %lf\n", tempo_decorrido, E_N_sample, E_W_sample);
                
                // Agendar próxima amostragem
                if (tempo_decorrido + SAMPLE_INTERVAL <= tempo_simulacao) {
                    Evento nova_amostragem = {tempo_decorrido + SAMPLE_INTERVAL, 2};
                    inserir_evento(heap, nova_amostragem);
                }
                break;
        }
    }
    
    fclose(file);
    destruir_heap(heap);
}

int main() {
    srand(time(NULL));
    double occupancies[] = {0.8, 0.9, 0.95, 0.999};
    int num_occupancies = sizeof(occupancies) / sizeof(occupancies[0]);

    for (int i = 0; i < num_occupancies; i++) {
        double occupancy = occupancies[i];
        double mean_service_time = 1.0;
        double mean_inter_arrival_time = mean_service_time / occupancy;

        double media_inter_requisicoes = 1.0 / mean_inter_arrival_time;
        double media_tempo_servico = 1.0 / mean_service_time;

        char filename[100];
        sprintf(filename, "data/ocupacao_%.1f.dat", occupancy * 100);
        printf("Simulando ocupacao %.1f%%...\n", occupancy * 100);
        run_simulation(media_inter_requisicoes, media_tempo_servico, filename);
    }
    
    printf("Simulacoes concluidas.\n");
    return 0;
}
