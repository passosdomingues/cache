#ifndef ALGORITHMS_H
#define ALGORITHMS_H

#include <limits.h>
#include <stdbool.h>

#define INF INT_MAX

// Estrutura para o nó do heap
typedef struct {
    int v;
    double dist;
} HeapNode;

// Estrutura para o Min-Heap
typedef struct {
    int size;
    int capacity;
    int *pos; // Para rastrear a posição do nó no heap (opcional para Dijkstra padrão, mas útil)
    HeapNode **array;
} MinHeap;

// Funções para manipulação do heap
MinHeap* criar_min_heap(int capacity);
void min_heapify(MinHeap* minHeap, int idx);
HeapNode* extrair_minimo(MinHeap* minHeap);
void diminuir_chave(MinHeap* minHeap, int v, double dist);
bool esta_no_heap(MinHeap *minHeap, int v);
void liberar_heap(MinHeap *minHeap);

// Executa o algoritmo de Dijkstra a partir de um nó de origem
double dijkstra(int **matriz, int num_nos, int origem);

// Executa o algoritmo de Duan a partir de um nó de origem
double duan(int **matriz, int num_nos, int origem);

// Executa o terceiro algoritmo a partir de um nó de origem (Bellman-Ford)
double outro(int **matriz, int num_nos, int origem);

#endif
