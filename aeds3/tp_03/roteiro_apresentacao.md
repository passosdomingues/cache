# Roteiro de Apresentação (TP 03 - SSSP)

Este documento serve como guia (script) para a apresentação do projeto. O tempo estimado é de 10 a 15 minutos, e a fala é dividida para evidenciar a colaboração *cross-functional* (matricial) entre as 3 duplas.

---

## 1. Introdução e Visão Geral
**Quem fala:** Integrante 1 (Dupla C - Relatoria)
**Duração Estimada:** 2 minutos
**Slide:** 1 a 3 (Sumário e Introdução)

* **Foco da Fala:**
  - "Bom dia/boa noite a todos. Somos a Equipe SSSP e hoje vamos apresentar nosso Trabalho Prático 03."
  - "O foco do nosso trabalho é o problema de *Single-Source Shortest Path* (Caminho Mínimo de Fonte Única). Classicamente, algoritmos como Dijkstra resolvem o problema maravilhosamente bem com o uso de um Min-Heap, porém ficam limitados pela barreira teórica da ordenação global ($O(m \log n)$)."
  - "Nosso objetivo aqui foi ir além: nós implementamos o algoritmo de Bellman-Ford como linha de base (força-bruta) e o revolucionário **BMSSP**, de Duan e outros, que consegue contornar a ordenação e entregar um tempo teórico de $O(m \log^{2/3} n)$."

---

## 2. Estrutura Matricial e Governança
**Quem fala:** Integrante 2 (Dupla C - Relatoria)
**Duração Estimada:** 1.5 minutos
**Slide:** 4 (Estrutura Matricial)

* **Foco da Fala:**
  - "Para desenvolvermos esse projeto sem criar gargalos, adotamos uma estrutura matricial, onde os 6 membros foram divididos em 3 duplas: Core Algorítmico, Python Pipeline e Documentação."
  - "O mais importante é que nossa interação ocorreu de **Ponta-a-Ponta**. Nós montamos a arquitetura de tal forma que o simples comando `make all` resolve, roda e compila todos os testes, os códigos em C e os relatórios em LaTeX. Qualquer dupla aqui é capaz de assumir o lugar da outra e rodar o pipeline sem depender da máquina do colega."

---

## 3. O Algoritmo BMSSP e a Complexidade Matemática
**Quem fala:** Integrante 3 (Dupla A - Core Algorítmico)
**Duração Estimada:** 3 minutos
**Slide:** 5 e 6 (Fundamentação Teórica e Pseudocódigo)

* **Foco da Fala:**
  - "Entrando agora na parte central da nossa implementação C. Enquanto o Dijkstra enfileira tudo em um Min-Heap, o BMSSP adota um particionamento inteligente."
  - "Nós usamos o que o artigo chama de amostragem de pivôs. Ao invés de pegar o menor absoluto, nós pegamos um subconjunto de vértices $S$ e comprimimos em um grupo de pivôs $P$, reduzindo a amostra usando um fator $k$ dependente de $\log n$."
  - *(Pode referenciar o pseudocódigo)* "Na nossa função recursiva `bmssp` no C, repare que passamos um limite de distância $B$. Se o limite for ultrapassado, ou se alcançarmos o caso base $l=0$, nós paramos e rodamos o relaxamento restrito. Foi isso que permitiu a Duan demonstrar a quebra do limite, rodando no nível ótimo $O(m \log^{2/3} n)$."

---

## 4. Orquestração, Engenharia e Pipeline (Zero-Noise)
**Quem fala:** Integrante 4 (Dupla B - Engenharia/Python)
**Duração Estimada:** 2.5 minutos
**Slide:** 7 (Implementação Computacional)

* **Foco da Fala:**
  - "Como engenheiros do projeto, nosso desafio não era só ter o código C rodando, mas garantir que a equipe conseguisse medir o tempo empiricamente sem sujar as máquinas."
  - "Montamos um pipeline Python usando `networkx` e `subprocess`. Nosso script injeta automaticamente grafos do modelo *Erdos-Renyi*, variando de 50 a 1000 vértices, direto na entrada padrão do executável C."
  - *(Opcional)* "Gostaria de adicionar que um dos maiores desafios foi lidar com um *Segmentation Fault* no código C na manipulação do array posicional da Min-Heap no caso do Duan. A Dupla B, junto com a Dupla A, revisou cruzado o código e nós implementamos a correção inicializando o array do heap dinâmico para os grafos enormes, permitindo que a simulação corresse lisa."

---

## 5. Resultados Empíricos (O Gráfico)
**Quem fala:** Integrante 5 (Dupla A ou Dupla B)
**Duração Estimada:** 2 minutos
**Slide:** 8 (Resultados Empíricos e Gráfico)

* **Foco da Fala:**
  - "Os resultados práticos, gerados via Matplotlib (300 DPI) para o nosso relatório, trazem uma conclusão fascinante."
  - "Observem o gráfico. A curva pontilhada lá no alto é o nosso Bellman-Ford explodindo rapidamente como previsto. Já as curvas de baixo são o Dijkstra e o BMSSP de Duan."
  - "Na prática, para instâncias até 1000 vértices, o algoritmo BMSSP se mostrou mais custoso que o Dijkstra. Por que isso acontece se a complexidade assintótica do Duan é menor? Devido à constante estrutural. O `overhead` de chamar funções recursivas, de alocar listas de pivôs dinamicamente na memória RAM, acaba sendo muito superior ao simples *array swapping* no Min-Heap linear do Dijkstra Clássico."

---

## 6. Conclusões Finais
**Quem fala:** Integrante 6 (Qualquer membro, idealmente Dupla C fechando)
**Duração Estimada:** 1.5 minutos
**Slide:** 9 e 10 (Conclusões)

* **Foco da Fala:**
  - "Para concluir, nós tiramos dois grandes aprendizados do TP 03."
  - "O primeiro é sobre Teoria vs Prática. Teoricamente, quebrar o $O(m \log n)$ é um marco histórico. Mas, como desenvolvedores, percebemos que o Dijkstra Clássico continua sendo a escolha pragmática, pois o hardware de hoje é altamente otimizado para predição de saltos (branch prediction) e localidade de cache em *arrays* nativos."
  - "O segundo é sobre cultura técnica. Trabalhar com integração contínua (Makefiles gerando instâncias, Python, e PDFs do Beamer do zero) erradica gargalos de comunicação. Todos nós tivemos visibilidade plena sobre o funcionamento ponta-a-ponta."
  - "Muito obrigado pela atenção. Estamos abertos a perguntas."

---

## 7. Preparação para Sabatina (Q&A Nível Doutorado)

Esta seção prepara a equipe para possíveis questionamentos da banca avaliadora. Cada dupla deve dominar as respostas de sua área. As respostas já estão estruturadas como um **roteiro falado**.

### Sabatina para a Dupla A (Core Algorítmico)

**Pergunta Matadora 1:** *"Se o algoritmo BMSSP alcança o assintótico $O(m \log^{2/3} n)$, quebrando o limite de Dijkstra ($O(m \log n)$), por que os dados empíricos demonstram Dijkstra operando mais rapidamente nestas instâncias? Onde está a 'ilusão' da notação assintótica?"*
**Roteiro de Resposta (Dupla A):** 
> "Excelente pergunta, professor. A notação \textit{Big-O} abstrai as constantes ocultas do hardware. O ganho do BMSSP exige que o grafo seja massivo o suficiente para que a economia no particionamento compense os sucessivos *cache misses* e a pesada sobrecarga do *call stack* na recursão e alocação dinâmica do \texttt{FindPivots}. Em contraste, a \textit{Min-Heap} do Dijkstra reside contiguamente na memória cache L2/L3. A 'ilusão' não é matemática, mas arquitetural: o hardware moderno beneficia saltos previsíveis em *arrays* nativos, tornando o Dijkstra imbatível em cenários sub-quadráticos práticos."

**Pergunta Matadora 2:** *"Como vocês garantem a corretude da amostragem de pivôs ($P$) no BMSSP? Existe a possibilidade do particionamento induzir a exploração de um caminho subótimo antes do ótimo?"*
**Roteiro de Resposta (Dupla A):**
> "Esta é uma preocupação estocástica válida. Nós garantimos a corretude limitando rigidamente a busca através do parâmetro de \textit{bound} ($B$). O \texttt{FindPivots} não elege origens exclusivas definitivas; ele apenas atua como guia para relaxamentos temporários. Se um caminho subótimo é explorado, a chamada subsequente que cobre todo o conjunto $S$ atua como mecanismo de correção exaustiva até o limite $B$, garantindo que, quando a árvore recursiva retorna ($l=0$), o estado da fronteira está estritamente correto."

### Sabatina para a Dupla B (Python Pipeline e Engenharia)

**Pergunta Matadora 3:** *"A geração dos grafos via modelo de Erdős-Rényi (com densidade uniforme $0.5$) captura de maneira fidedigna a topologia de gargalos que os algoritmos de particionamento como o BMSSP exploram? Ou o modelo de dados mascarou a vantagem teórica?"*
**Roteiro de Resposta (Dupla B):**
> "Sua observação é precisa. A topologia afeta a distribuição de custos de caminhos mínimos. O modelo Erdős-Rényi gera grafos com baixo diâmetro e conectividade altamente redundante (densos). Essa redundância de caminhos quase de mesmo custo prejudica o particionamento do BMSSP, que brilharia em grafos de grande diâmetro com métricas não triviais (como \textit{Bounded-UDG} ou Redes \textit{Scale-Free} estendidas). Optamos por ele para estabelecer uma linha base empírica, mas é um viés métrico assumido na orquestração: a vantagem de quebrar a barreira de ordenação se mostra pífia em grafos rasos e densos."

**Pergunta Matadora 4:** *"Observando o \textit{overhead} do subprocesso no Pipeline, os desvios padrões (error bars) no gráfico capturam variações da carga do Sistema Operacional ou são genuinamente variações inerentes aos algoritmos operando sob ruído topológico?"*
**Roteiro de Resposta (Dupla B):**
> "Para isolar o ruído do SO (\textit{context switching}), o nosso orquestrador injeta instâncias completas no \textit{stdin} via binário puro e captura apenas o perfil interno devolvido pelo binário via chamada à biblioteca C nativa \texttt{clock()}. Logo, os tempos medidos desconsideram o tempo de \textit{bootstrap} ou do \textit{subprocess.run}. Os \textit{error bars} medem estritamente a assimetria na travessia das arestas (ruído topológico) a cada geração randômica de instâncias."

### Sabatina para a Dupla C (LaTeX e Relatoria Científica)

**Pergunta Matadora 5:** *"A apresentação das complexidades temporais desconsidera as constantes, porém as tabelas evidenciam saltos exponenciais do Bellman-Ford. Como a documentação valida o distanciamento entre $O(mn)$ e o limite imposto pela Min-Heap?"*
**Roteiro de Resposta (Dupla C):**
> "Professor, no nosso documento relatamos o fenômeno através de uma ótica empírica: a complexidade de tempo não reflete o pior caso nas instâncias geradas aleatoriamente para o Bellman-Ford se houvesse parada precoce acentuada, porém a densidade Erdős-Rényi manteve a média global alta. A Min-Heap estabiliza as extrações em limite \textit{upper-bound} determinístico de $\log n$, o que traduz a estabilidade quase linear das nossas tabelas para o Dijkstra. O relatório foi construído exatamente para provar que $O(mn)$ destoa gravemente de operações baseadas em prioridade para arestas uniformes positivas."

**Pergunta Matadora 6:** *"O artigo base (Duan et al. 2023) introduziu o BMSSP resolvendo teias em tempo quase-linear. Como vocês extrapolam os achados desta pesquisa (TP 03) sob uma ótica de aplicação no mundo real, como Sistemas de Navegação?"*
**Roteiro de Resposta (Dupla C):**
> "A nossa conclusão consolida um alerta fundamental para a engenharia de \textit{software}: inovações de limite inferior assintótico (como a quebra da barreira de ordenação de Duan) não implicam adesão imediata de mercado. Sistemas de navegação como Google Maps sofrem mutações constantes e a topologia tem dimensões logísticas massivas, mas hierárquicas. O BMSSP custaria \textit{terabytes} em partições de memória recursiva ineficiente na nuvem, enquanto otimizações de Dijkstra espacialmente coerentes (A*) dão conta do recado usando apenas uma minúscula \textit{cache}. Essa é a tese principal que consolidamos como fechamento deste trabalho de ponta a ponta."
