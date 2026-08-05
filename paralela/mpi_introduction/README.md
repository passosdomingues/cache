# 🎓 Roteiro Didático de MPI em C++17

> Projeto estruturado e orientado a objetos desenvolvido com base no notebook de **Computação Paralela e Distribuída** do **Prof. Paulo Bressan** (`Introducao_MPI_Colab.ipynb`).

---

## 🎯 Objetivos Cobertos

Este projeto abstrai e expande em C++17 todas as lições e exercícios propostos pelo professor:

1. **Hello World & Identificação de Processos**: `MPI_Init`, `MPI_Comm_rank`, `MPI_Comm_size`, `MPI_Get_processor_name`.
2. **Comunicação Ponto a Ponto Bloqueante**: `MPI_Send` e `MPI_Recv` com verificação de tipo e filtro por tags.
3. **Exercício 1 — Soma dos Ranks Quadrados**: Múltiplos workers calculam $rank^2$ e enviam para o rank 0 agregar a soma total.
4. **Exercício 2 — Vetor e Ring Echo**: Envio de vetores de inteiros, cálculo de soma distribuída e resposta para o mestre.
5. **Comunicação Coletiva com Broadcast**: `MPI_Bcast` transmitindo estruturas de parâmetros para todos os nós.
6. **Medição de Desempenho & Gráficos**: Benchmark de latência (Ping-Pong) e banda de comunicação exportados para gráficos com Python.

---

## 🛠️ Estrutura do Projeto

```
mpi_didatico_cpp/
├── CMakeLists.txt              # Sistema de Build com C++17 e suporte a MPI
├── Makefile                    # Automação de tarefas (make run, make simulate, etc.)
├── Dockerfile                  # Ambiente reproduzível multi-stage
├── docker-compose.yml          # Containerização com 1 comando
├── include/
│   ├── MPILearningFramework.hpp # Classe Wrapper OO do MPI
│   ├── Lessons.hpp              # Implementação modular das lições e exercícios
│   ├── TableFormatter.hpp       # Formatador de tabelas ANSI para terminal
│   └── Benchmark.hpp            # Módulo de medição de latência e banda
├── src/
│   ├── MPILearningFramework.cpp
│   ├── Lessons.cpp
│   ├── TableFormatter.cpp
│   ├── Benchmark.cpp
│   └── main.cpp                 # Runner principal interativo
└── scripts/
    ├── generate_charts.py       # Script Python para plotagem de latência/banda
    └── requirements.txt
```

---

## 🚀 Como Executar

### 1. Compilar e Rodar o Roteiro Didático

```bash
cd /home/rafael/github/cache/paralela/mpi_didatico_cpp

# Compila e roda todas as lições e exercícios com 4 processos MPI
make run NP=4
```

### 2. Executar os Benchmarks e Gerar os Gráficos

```bash
# Executa as lições, benchmarks de latência e gera os gráficos
make simulate NP=4
```

Os gráficos de latência e banda serão salvos em `plots/mpi_performance.png`.

### 3. Rodar via Docker

```bash
make docker-run NP=4
```
ou
```bash
docker compose up --build
```
