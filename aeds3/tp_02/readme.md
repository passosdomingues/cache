-------------------------------------------------------------------------------
███████████████████████████████████████████████████████████████████████████████
█▄─▄███─▄▄─█▄─▄▄─█─▄▄▄▄█▄─▄▄─█▄─▄▄▀██▀▄─██▄─▀█▄─▄███─▄▄▄▄█▄─▄▄▀█▄─▄▄─█▄─▄▄─█
██─██▀█─██─██─▄█▀█▄▄▄▄─██─▄█▀██─██─██─▀─███─█▄▀─████─▄▄▄▄██─██─██─▄█▀██─▄▄▄█
▀▄▄▄▄▄▀▄▄▄▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▄▄▀▀▄▄▀▄▄▀▄▄▄▀▀▄▄▀▀▄▄▄▄▄▀▀▄▄▄▄▀▀▄▄▄▄▄▀▄▄▄▀▀
-------------------------------------------------------------------------------

# DOSSIÊ CONFIDENCIAL: OPERAÇÃO DUPLA HÉLICE
**NÍVEL DE ACESSO:** SIGILOSO (TIER 3 - AEDS III)
**AGÊNCIA:** UNIFAL (Universidade Federal de Alfenas)
**DIRETOR DA OPERAÇÃO:** Prof. Iago Augusto de Carvalho

Aviso: A divulgação não autorizada dos algoritmos aqui contidos resultará em 
falha imediata na missão e acionamento do protocolo de reprovação.

---

## 1. RESUMO DA MISSÃO (SITREP)

Nossa divisão foi encarregada de interceptar e decodificar fragmentos de DNA (Ácido Desoxirribonucleico). O objetivo tático é alinhar sequências genéticas (A, T, C, G) para encontrar a máxima correspondência possível entre elas, inserindo lacunas (gaps) estratégicas.

Para esta missão, desenvolvemos duas armas algorítmicas:
* **Projeto "Oráculo" (Programação Dinâmica):** Precisão absoluta, custo computacional elevado (Tempo O(N*M), Memória O(N*M)). Vasculha todas as possibilidades do multiverso antes de agir.
* **Projeto "Caçador" (Algoritmo Guloso):** Rápido, letal, mas míope. Toma decisões locais imediatas buscando a melhor vantagem no momento, sem calcular consequências a longo prazo (Tempo O(N), Memória O(1)).

### Parâmetros Biológicos de Engajamento:
* **Match (+2):** Emparelhamento perfeito validado (A-T, C-G).
* **Mismatch (-1):** Anomalia de emparelhamento.
* **Gap (-2):** Inserção tática de lacuna estrutural.

---

## 2. A DIRETRIZ PRIME E O PROTOCOLO FANTASMA (O CASO "bla")

O Alto Comando emitiu uma ordem inquebrável: **Os arquivos `Makefile` e `base.c` na pasta `codigo_base` são infraestruturas críticas intocáveis.** Qualquer adulteração resultará na anulação da operação. 

**A Anomalia:** O `Makefile` oficial possui uma regra de compilação cega. Ao acionar `make run`, ele exige ler os dados de um arquivo estático e inflexível chamado `../bla`. 

**A Solução (Protocolo Fantasma):** Em vez de alterar as regras, nós as contornamos. Todo o nosso sistema opera em quarentena na subpasta `/data`. Nosso orquestrador itera sobre as instâncias de teste e cria um **link simbólico dinâmico** (symlink) chamado `bla` na raiz do projeto. O corretor automático acredita estar lendo sempre o mesmo arquivo, enquanto secretamente injetamos novos alvos. Integridade da regra mantida em 100%.

---

## 3. INFRAESTRUTURA DE AUTOMAÇÃO E O "MAKEFILE ADAPTADOR"

Para evitar a contaminação do sistema operacional dos agentes com bibliotecas de terceiros, desenvolvemos um **Makefile Adaptador** operando restritamente dentro de `/data`. Ele é responsável por forjar um ambiente selado e garantir a reprodutibilidade da missão em qualquer máquina.

### As 3 Camadas de Defesa:
1. **Ambiente de Contenção (VENV):** Isola as dependências analíticas do Python (`numpy`, `matplotlib`, `seaborn`) do resto do sistema.
2. **Instalação Idempotente:** O sistema possui sensores embutidos. Ele só baixa e instala as dependências táticas uma única vez. Execuções subsequentes são instantâneas.
3. **Camuflagem Anti-Rastreio (`.gitignore`):** O adaptador injeta automaticamente regras de ofuscação no `.gitignore` raiz, garantindo que logs de teste, symlinks fantasma e as bibliotecas pesadas do VENV nunca subam para o repositório principal acidentalmente.

---

## 4. MANUAL DE EXECUÇÃO TÁTICA

Navegue até o perímetro seguro para iniciar a operação:
```bash
cd tp_02/data

Uma vez dentro do perímetro, você possui três comandos diretos através do nosso Makefile Adaptador:

======================================================================
      TERMINAL DE CONTROLE - OPERACAO DUPLA HELICE (SETOR DATA)       
======================================================================
Comandos de engajamento disponiveis:

  make setup      : Prepara o ambiente de contencao (VENV) e camuflagem.
  make run        : Aciona o Orquestrador Bash para a bateria de testes.
  make clean_venv : Protocolo Terra Arrasada. Oblitera o ambiente virtual.
  make help       : Exibe este manual de operacoes.
======================================================================

🔵 Comando de Preparação: make setup

Cria o ambiente seguro, instala as bibliotecas cripto-visuais e ativa a camuflagem.

```bash
make setup

🟢 Comando de Engajamento: make run

Aciona a interface colorida do Orquestrador Tático (Bash). É aqui que a mágica acontece. O painel exibirá as seguintes opções:

    [1-N] Ataque Focado: Testa um fragmento genético específico (Score e Tempo no terminal).

    [99] Varredura Global (AUTO): Automatização total. Compila o código C ➔ Cria os symlinks iterativamente ➔ Roda todas as instâncias ➔ Extrai tempos via awk ➔ Salva os dados brutos ➔ Aciona o Python VENV ➔ Plota os relatórios em alta resolução. Você só precisa cruzar os braços e assistir aos indicadores de progresso.

    [0] Abortar Missão: Destrói o symlink atual e recua em segurança.

```bash
make run

🔴 Protocolo Terra Arrasada: make clean_venv

Caso o ambiente seja comprometido, este comando oblitera o campo de contenção (VENV), apagando todas as dependências isoladas.

```bash
make clean_venv

5. DIVISÃO DE OPERAÇÕES ESPECIAIS (ROSTER)

Para garantir a máxima eficiência (e cobrir todos os 100% da avaliação), a força-tarefa foi dividida em três frentes de inteligência:

>> Equipe Alpha: "Setor de Engenharia de Baixo Nível"

Codinome: Os Escovadores de Bit

    Foco: Código, Otimização e Automação (30% da nota).

    Missão: Garantir eficiência O(N*M) na DP e O(N) no Guloso, zerar vazamentos de memória (Valgrind), comentar o código impecavelmente e manter o Orquestrador Bash operacional.

>> Equipe Bravo: "Setor de Inteligência de Dados"

Codinome: Os Analistas do Arquivo X

    Foco: Documentação, Dossiê PDF e Análise Crítica (30% da nota).

    Missão: Redigir o dossiê final validando o trade-off de Tempo vs. Otimalidade, inserir os relatórios gráficos em P&B e garantir o verniz acadêmico exigido pelo Alto Comando.

>> Equipe Charlie: "Divisão de Operações Psicológicas"

Codinome: A Linha de Frente (PsyOps)

    Foco: Apresentação de Slides e Defesa Oral (40% da nota).

    Missão: Conduzir o briefing presencial. Roteirizar a fala tática (janela estrita de 7 a 12 minutos), produzir slides limpos e assertivos, e defender a corretude algorítmica perante o esquadrão completo.

"A verdade está nos dados."

    Fim da transmissão.

[ALERTA DO SISTEMA]
Protocolo de contenção fantasma acionado.
Limpando rastros em memória e sobrescrevendo logs de acesso...

Esta mensagem vai se autodestruir em 10... 9... 8...

Connection to host closed by remote server.
Segmentation fault (core dumped)
