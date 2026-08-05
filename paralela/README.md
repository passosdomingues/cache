# 🚀 Repositório de Computação Paralela e Distribuída (MPI)

Este repositório contém os projetos e exercícios práticos da disciplina de **Computação Paralela e Distribuída**, organizados de forma modular e independente.

---

## 📁 Estrutura de Projetos

### 1. 🌌 [`agn_nbody_simulation`](file:///home/rafael/github/cache/paralela/agn_nbody_simulation)
Simulação de **Núcleo Galático Ativo (AGN)** em C++17 e MPI.
- **Caso de uso**: Buraco Negro Supermassivo com 2.000+ estrelas em órbita Kepleriana.
- **Física**: Integrador Leapfrog KDK simpléctco (drift de energia < 0.0001%).
- **Gráficos**: Análise de evolução do disco, conservação de energia e benchmarks de speedup.
- **Como rodar**:
  ```bash
  cd agn_nbody_simulation
  make simulate NP=4 N=2000 STEPS=500
  ```

---

### 2. 🎓 [`mpi_didatico_cpp`](file:///home/rafael/github/cache/paralela/mpi_didatico_cpp)
Roteiro didático completo baseado no notebook do professor Paulo Bressan ([`Introducao_MPI_Colab.ipynb`](file:///home/rafael/github/cache/paralela/Introducao_MPI_Colab.ipynb)).
- **Abordagem**: C++17 orientado a objetos, formatado com tabelas ANSI no terminal.
- **Lições & Exercícios**:
  - `Hello World` & Nomes dos nós (`MPI_Init`, `MPI_Comm_rank`, `MPI_Get_processor_name`)
  - Envio e recebimento ponto a ponto (`MPI_Send`, `MPI_Recv`)
  - Exercício 1: Soma dos Ranks Quadrados ($\sum rank^2$)
  - Exercício 2: Processamento e Echo de Vetores
  - Transmissão de configurações (`MPI_Bcast`)
  - Benchmarks de Latência Ping-Pong (1B até 1MB) e Redução Paralela
- **Como rodar**:
  ```bash
  cd mpi_didatico_cpp
  make simulate NP=4
  ```

---

## 📄 Material de Apoio
- **`Introducao_MPI_Colab.ipynb`**: Notebook original fornecido no curso.
