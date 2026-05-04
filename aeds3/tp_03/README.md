# Análise Comparativa de Algoritmos SSSP (TP 03)

Este repositório contém o código, a orquestração e a documentação para a análise de desempenho empírico de três algoritmos para o problema *Single-Source Shortest Path* (SSSP):
1. **Dijkstra** com Min-Heap
2. **BMSSP** (Duan et al.) com Amostragem de Pivôs
3. **Bellman-Ford** (como *Baseline*)

O pipeline foi totalmente automatizado para gerar instâncias, medir os tempos, traçar gráficos de desempenho e compilar o relatório LaTeX, tudo orquestrado via `make`.

---

## Estrutura de Equipe Matricial (6 Membros / 3 Duplas)

Para evitar gargalos e silos de conhecimento, a equipe operará em uma **Estrutura Matricial de Ponta a Ponta**. As 3 duplas têm responsabilidades primárias focadas, mas devem ter domínio total para executar e reproduzir o trabalho das outras. 

### Papéis e Responsabilidades

* **Dupla A (Core Algorítmico & Desempenho):** Responsáveis pela manutenção, profilometria e corretude dos algoritmos em `codigo base/`. Devem assegurar que o C não apresente vazamentos de memória (uso de Valgrind) e respeite a complexidade teórica da *Referência* (BMSSP $O(m \log^{2/3} n)$).
* **Dupla B (Engenharia de Instâncias & Orquestração):** Responsáveis pela evolução de `gerador de instancias/` e `runner_and_plot.py`. Ajustam heurísticas de geração de grafos (ex: Barabasi, Watts-Strogatz) e garantem que o orquestrador lide com falhas e automatize o *Virtual Environment* corretamente.
* **Dupla C (Relatoria Científica & UX da Apresentação):** Focados no artefato final: `relatorio_tp03/sbc-template.tex` e `apresentacao/apresentacao.tex`. Consolidam os *insights* de performance em inferências teóricas sólidas, além de gerir a bibliografia (BibTeX).

### Dinâmica *Cross-Functional* (Sem Gargalos)
* **Revisão Cruzada:** A Dupla B revisa os *Pull Requests* da Dupla A (para validar como o código C lida com as matrizes de input); a Dupla C revisa a Dupla B (verificando se o gráfico reflete as restrições científicas); a Dupla A revisa a Dupla C (verificando se a matemática escrita bate com a heurística implementada).
* **Autonomia:** O comando `make all` garante que qualquer integrante, independente da dupla, possa simular todo o experimento em sua máquina e atuar como *backup* caso um gargalo crítico ocorra.

---

## Como Reproduzir o Experimento

O repositório foi construído com a filosofia "Zero-Noise". Não é necessário instalar bibliotecas complexas na máquina globalmente. A orquestração lida com o isolamento em *Virtual Environment* (`venv`).

### Pré-requisitos
* Sistema Linux/Unix
* Compilador GCC (ou compatível) e ferramenta `make`
* Python 3 e `pip`
* Distribuição LaTeX (`texlive`, `pdflatex`, `bibtex`)

### Passos de Execução

1. **Clone e entre no repositório:**
   ```bash
   cd tp_03
   ```
2. **Execute o Pipeline Completo:**
   ```bash
   make all
   ```
   **O que este comando faz?**
   - Compila o código C em `codigo base/base`.
   - Cria o ambiente virtual (`venv`) e instala os pacotes (`networkx`, `scipy`, `matplotlib`).
   - Roda o gerador variando $N$ (50 a 1000) e alimenta o executável C.
   - Extrai as métricas de tempo e salva o gráfico em P&B de 300 DPI (`relatorio_tp03/desempenho_algoritmos_pb.png`).
   - Compila o relatório PDF.
   
3. **Gerar a Apresentação Beamer:**
   ```bash
   make apresentacao
   ```
   Isso compilará o PDF da apresentação na respectiva pasta.

4. **Limpeza do Projeto:**
   Para resetar o projeto e apagar todos os artefatos temporários e de compilação:
   ```bash
   make clean
   ```

## Referência Bibliográfica
Conformidade teórica e estrutural baseada em: Duan, R., Mao, J., Shu, X., & Yin, L. (2023). *A randomized algorithm for single-source shortest path on undirected real-weighted graphs* (FOCS 2023).
