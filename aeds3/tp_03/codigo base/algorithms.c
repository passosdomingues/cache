#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "algorithms.h"

// --- Implementação do Min-Heap ---

HeapNode* novo_no_heap(int v, double dist) {
    HeapNode* no = (HeapNode*)malloc(sizeof(HeapNode));
    no->v = v;
    no->dist = dist;
    return no;
}

MinHeap* criar_min_heap(int capacity) {
    MinHeap* minHeap = (MinHeap*)malloc(sizeof(MinHeap));
    minHeap->pos = (int*)malloc(capacity * sizeof(int));
    for (int i = 0; i < capacity; i++) {
        minHeap->pos[i] = capacity;
    }
    minHeap->size = 0;
    minHeap->capacity = capacity;
    minHeap->array = (HeapNode**)malloc(capacity * sizeof(HeapNode*));
    return minHeap;
}

void trocar_nos_heap(HeapNode** a, HeapNode** b) {
    HeapNode* t = *a;
    *a = *b;
    *b = t;
}

void min_heapify(MinHeap* minHeap, int idx) {
    int menor = idx;
    int esquerda = 2 * idx + 1;
    int direita = 2 * idx + 2;

    if (esquerda < minHeap->size && minHeap->array[esquerda]->dist < minHeap->array[menor]->dist)
        menor = esquerda;

    if (direita < minHeap->size && minHeap->array[direita]->dist < minHeap->array[menor]->dist)
        menor = direita;

    if (menor != idx) {
        HeapNode* noMenor = minHeap->array[menor];
        HeapNode* noIdx = minHeap->array[idx];

        minHeap->pos[noMenor->v] = idx;
        minHeap->pos[noIdx->v] = menor;

        trocar_nos_heap(&minHeap->array[menor], &minHeap->array[idx]);
        min_heapify(minHeap, menor);
    }
}

HeapNode* extrair_minimo(MinHeap* minHeap) {
    if (minHeap->size == 0) return NULL;

    HeapNode* raiz = minHeap->array[0];
    HeapNode* ultimoNo = minHeap->array[minHeap->size - 1];
    minHeap->array[0] = ultimoNo;

    minHeap->pos[raiz->v] = minHeap->size - 1;
    minHeap->pos[ultimoNo->v] = 0;

    --minHeap->size;
    min_heapify(minHeap, 0);

    return raiz;
}

void diminuir_chave(MinHeap* minHeap, int v, double dist) {
    int i = minHeap->pos[v];
    minHeap->array[i]->dist = dist;

    while (i && minHeap->array[i]->dist < minHeap->array[(i - 1) / 2]->dist) {
        minHeap->pos[minHeap->array[i]->v] = (i - 1) / 2;
        minHeap->pos[minHeap->array[(i - 1) / 2]->v] = i;
        trocar_nos_heap(&minHeap->array[i], &minHeap->array[(i - 1) / 2]);
        i = (i - 1) / 2;
    }
}

bool esta_no_heap(MinHeap *minHeap, int v) {
    return minHeap->pos[v] < minHeap->size;
}

void liberar_heap(MinHeap *minHeap) {
    for (int i = 0; i < minHeap->size; i++) free(minHeap->array[i]);
    free(minHeap->array);
    free(minHeap->pos);
    free(minHeap);
}

// --- Algoritmos SSSP ---

// Algoritmo de Dijkstra usando Min-Heap
double dijkstra(int **matriz, int num_nos, int origem) {
    double* distancias = (double*)malloc(num_nos * sizeof(double));
    MinHeap* minHeap = criar_min_heap(num_nos);

    for (int v = 0; v < num_nos; v++) {
        distancias[v] = (double)INF;
        minHeap->array[v] = novo_no_heap(v, distancias[v]);
        minHeap->pos[v] = v;
    }

    distancias[origem] = 0;
    diminuir_chave(minHeap, origem, distancias[origem]);
    minHeap->size = num_nos;

    while (minHeap->size != 0) {
        HeapNode* minHeapNode = extrair_minimo(minHeap);
        int u = minHeapNode->v;

        for (int v = 0; v < num_nos; v++) {
            if (matriz[u][v] != 0 && distancias[u] != (double)INF && matriz[u][v] + distancias[u] < distancias[v]) {
                distancias[v] = distancias[u] + matriz[u][v];
                diminuir_chave(minHeap, v, distancias[v]);
            }
        }
        free(minHeapNode);
    }

    double soma_custo = 0;
    for (int i = 0; i < num_nos; i++) {
        if (distancias[i] != (double)INF) soma_custo += distancias[i];
    }

    free(distancias);
    // Note: minHeap nodes were already freed during extraction or loop
    free(minHeap->array);
    free(minHeap->pos);
    free(minHeap);

    return soma_custo;
}

// Algoritmo de Duan (BMSSP - Bounded Multi-Source Shortest Path)
// Esta é uma implementação estruturada baseada na descrição da referência.
// O algoritmo usa recursão e amostragem de pivôs.

typedef struct {
    int* vertices;
    int size;
} VertexSet;

VertexSet* criar_set(int capacity) {
    VertexSet* s = (VertexSet*)malloc(sizeof(VertexSet));
    s->vertices = (int*)malloc(capacity * sizeof(int));
    s->size = 0;
    return s;
}

void add_to_set(VertexSet* s, int v) {
    s->vertices[s->size++] = v;
}

void liberar_set(VertexSet* s) {
    free(s->vertices);
    free(s);
}

// FindPivots: Seleciona um subconjunto de pivôs proporcional a |S|/k
VertexSet* find_pivots(VertexSet* S, int k) {
    VertexSet* P = criar_set(S->size);
    if (S->size == 0) return P;
    
    int num_pivots = S->size / k;
    if (num_pivots == 0) num_pivots = 1;
    
    // Amostragem simples para demonstração do conceito de pivôs
    for (int i = 0; i < num_pivots; i++) {
        int idx = rand() % S->size;
        add_to_set(P, S->vertices[idx]);
    }
    return P;
}

// Procedimento recursivo BMSSP
void bmssp(int **matriz, int num_nos, int level, double B, VertexSet* S, double* distancias) {
    if (level == 0 || S->size == 0) {
        // Caso base: Dijkstra simplificado
        MinHeap* mh = criar_min_heap(num_nos);
        for (int i = 0; i < S->size; i++) {
            int u = S->vertices[i];
            mh->array[mh->size] = novo_no_heap(u, distancias[u]);
            mh->pos[u] = mh->size;
            mh->size++;
        }
        // Build heap
        for (int i = (mh->size/2)-1; i >= 0; i--) min_heapify(mh, i);

        while (mh->size > 0) {
            HeapNode* minNode = extrair_minimo(mh);
            int u = minNode->v;
            if (distancias[u] >= B) { free(minNode); continue; }

            for (int v = 0; v < num_nos; v++) {
                if (matriz[u][v] != 0) {
                    double new_dist = distancias[u] + matriz[u][v];
                    if (new_dist < B && new_dist < distancias[v]) {
                        distancias[v] = new_dist;
                        if (esta_no_heap(mh, v)) {
                            diminuir_chave(mh, v, new_dist);
                        } else {
                            mh->array[mh->size] = novo_no_heap(v, new_dist);
                            mh->pos[v] = mh->size;
                            mh->size++;
                            int cur = mh->size - 1;
                            while (cur && mh->array[cur]->dist < mh->array[(cur-1)/2]->dist) {
                                mh->pos[mh->array[cur]->v] = (cur-1)/2;
                                mh->pos[mh->array[(cur-1)/2]->v] = cur;
                                trocar_nos_heap(&mh->array[cur], &mh->array[(cur-1)/2]);
                                cur = (cur-1)/2;
                            }
                        }
                    }
                }
            }
            free(minNode);
        }
        liberar_heap(mh);
        return;
    }

    int k = (int)pow(log10(num_nos + 1.0), 1.0/3.0);
    if (k < 1) k = 1;

    VertexSet* P = find_pivots(S, k);
    bmssp(matriz, num_nos, level - 1, B, P, distancias);
    bmssp(matriz, num_nos, level - 1, B, S, distancias);
    liberar_set(P);
}

// Algoritmo de Duan usando matriz de adjacência
double duan(int **matriz, int num_nos, int origem) {
    double* distancias = (double*)malloc(num_nos * sizeof(double));
    for (int i = 0; i < num_nos; i++) distancias[i] = (double)INF;
    distancias[origem] = 0;

    double log_n = log10(num_nos + 1.0);
    double t = pow(log_n, 2.0/3.0);
    if (t < 1) t = 1;
    int max_l = (int)ceil(log_n / t);
    if (max_l < 1) max_l = 1;

    VertexSet* S = criar_set(1);
    add_to_set(S, origem);
    bmssp(matriz, num_nos, max_l, (double)INF, S, distancias);

    double soma_custo = 0;
    for (int i = 0; i < num_nos; i++) {
        if (distancias[i] != (double)INF) soma_custo += distancias[i];
    }
    liberar_set(S);
    free(distancias);
    return soma_custo;
}

// Implementação do terceiro usando matriz de adjacência (Bellman-Ford)
double outro(int **matriz, int num_nos, int origem) {
    double* distancias = (double*)malloc(num_nos * sizeof(double));
    for (int i = 0; i < num_nos; i++) distancias[i] = (double)INF;
    distancias[origem] = 0;

    for (int i = 1; i < num_nos; i++) {
        bool trocou = false;
        for (int u = 0; u < num_nos; u++) {
            if (distancias[u] == (double)INF) continue;
            for (int v = 0; v < num_nos; v++) {
                if (matriz[u][v] != 0) {
                    if (distancias[u] + matriz[u][v] < distancias[v]) {
                        distancias[v] = (double)distancias[u] + matriz[u][v];
                        trocou = true;
                    }
                }
            }
        }
        if (!trocou) break;
    }

    double soma_custo = 0;
    for (int i = 0; i < num_nos; i++) {
        if (distancias[i] != (double)INF) soma_custo += distancias[i];
    }
    free(distancias);
    return soma_custo;
}