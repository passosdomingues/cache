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

O Alto Comando emitiu uma ordem inquebrável: **Os arquivos `Makefile` e `base.c` são infraestruturas críticas intocáveis.** Qualquer adulteração resultará na anulação da operação. Nossa inteligência só tem permissão para operar nos arquivos `algoritmos.c` e `algoritmos.h`.

**A Anomalia:** O `Makefile` original possui uma regra de compilação cega. Ao acionar `make run`, ele exige ler os dados de um arquivo estático e inflexível chamado `../bla`. 

**A Solução (Protocolo Fantasma):** Para testar milhares de instâncias sem modificar a infraestrutura crítica, desenvolvemos uma ferramenta de orquestração na pasta `/data`. O script `testador.sh` opera nas sombras: ele itera sobre a pasta de instâncias e cria um **link simbólico dinâmico** (symlink) chamado `bla` na raiz do projeto. 

O `Makefile` acredita estar lendo sempre o mesmo arquivo, enquanto nós secretamente injetamos uma nova matriz de testes a cada ciclo. Sistema contornado com sucesso. Integridade mantida em 100%.

---

## 3. MANUAL DE EXECUÇÃO TÁTICA

A operação requer o interpretador Python 3 para renderização de relatórios visuais. Instale as dependências criptográficas antes de prosseguir:

> $ pip install numpy matplotlib seaborn

Toda a operação de testes foi isolada na subpasta `/data`. Navegue até o perímetro seguro e inicie a interface de comando:

> $ cd tp_02/data
> $ chmod +x testador.sh
> $ ./testador.sh

### Módulos do Sistema:
* **[1-N] Teste Isolado:** Seleciona um fragmento específico de DNA para análise minuciosa. O sistema reportará o Score e o Tempo de Execução no terminal.
* **[99] Orquestrador Global (Bateria de Testes):** Inicia a varredura completa. O script criará symlinks sucessivos, extrairá os dados brutos de tempo via `awk` e os compilará em um documento de texto não formatado (`resultados.csv`). Em seguida, o submódulo Python será acionado automaticamente.
* **[0] Abortar Missão:** Encerra a operação e destrói o arquivo `bla` (symlink), não deixando rastros no sistema de arquivos da agência.

---

## 4. RELATÓRIOS DESCLASSIFICADOS (OUTPUT)

Ao final da execução do Orquestrador Global [99], o sistema gerará evidências visuais provando a discrepância assintótica entre a Programação Dinâmica e o Algoritmo Guloso.

Os gráficos serão gerados em escala de cinza de alto contraste (padrão Tufte, 300 DPI), prontos para serem anexados a artigos científicos e relatórios impressos da agência sem perda de legibilidade.

**Destino dos relatórios:** `data/graficos/desempenho_algoritmos_pb.png`

## 5. Equipes

Equipe Alpha: "Setor de Engenharia de Baixo Nível"

Codinome da Dupla: Os Escovadores de Bit
Foco de Atuação: Código, Otimização e Automação (30% da nota)

Esta é a equipe que opera nas trincheiras do terminal. Eles são responsáveis por garantir que o código fonte não apenas funcione, mas seja uma obra de arte da engenharia de software.

Responsabilidades Estratégicas:

    Limpeza e Comentários: Garantir que o algoritmos.c esteja impecável, com variáveis bem nomeadas e comentários explicativos detalhados (exigência direta do professor).

    Gerenciamento de Memória: Rodar o Valgrind e assegurar que o algoritmo de Programação Dinâmica aloque e libere a matriz perfeitamente. Zero vazamentos.

    Manutenção do Orquestrador: Cuidar do testador.sh e do gerador_graficos.py, garantindo que rodem sem falhas no ambiente de entrega.

    Suporte Técnico: Fornecer os dados brutos e os gráficos gerados com precisão absoluta para o Setor de Inteligência.

Equipe Bravo: "Setor de Inteligência de Dados"

Codinome da Dupla: Os Analistas do Arquivo X
Foco de Atuação: Documentação, Dossiê PDF e Análise Crítica (30% da nota)

Esta dupla é o cérebro analítico da operação. Eles pegam os dados crus gerados pela Equipe Alpha e os transformam em conhecimento científico. O professor avaliará rigorosamente o português e a corretude da prova apresentada por eles.

Responsabilidades Estratégicas:

    Redação do Dossiê: Escrever o documento PDF final seguindo o template exigido, garantindo gramática perfeita e formatação acadêmica.

    Análise de Trade-off: Redigir a "Análise Crítica" exigida, discutindo profundamente o sacrifício de otimalidade pelo tempo de execução ao comparar o Algoritmo Guloso com a Programação Dinâmica.

    Integração Visual: Inserir e explicar os gráficos gerados em tons de cinza no documento, tornando a leitura fluida e irrefutável.

    Registro de Operações: Documentar exatamente a divisão de tarefas ("quem fez o quê") dentro do relatório, conforme as regras do trabalho.

Equipe Charlie: "Divisão de Operações Psicológicas"

Codinome da Dupla: A Linha de Frente (PsyOps)
Foco de Atuação: Apresentação de Slides e Defesa Oral (40% da nota)

O código pode ser perfeito e o relatório brilhante, mas é esta dupla que vai garantir a maior fatia da nota nos dias 13 e 14 de abril. Eles são os diplomatas e os porta-vozes da operação.

Responsabilidades Estratégicas:

    Design do Briefing (Slides): Criar uma apresentação em PDF altamente visual, com pouco texto e uso inteligente de imagens e diagramas (conforme encorajado pelo professor).

    Gestão do Tempo: Roteirizar a fala para garantir que a apresentação dure rigorosamente entre 7 e 12 minutos. O relógio é o maior inimigo aqui.

    Treinamento de Postura: Ensaiar a "assertividade na fala" e a postura, itens que o professor explicitou que serão avaliados.

    Tradução do Tecniquês: Explicar a corretude da prova e o funcionamento dos algoritmos de forma que a turma inteira compreenda, conectando o código da Equipe Alpha com a análise da Equipe Bravo.

---
"A verdade está nos dados."
- Fim da transmissão.

[ALERTA DO SISTEMA]
Protocolo de contenção fantasma acionado.
Limpando rastros em memória e sobrescrevendo logs de acesso...

Esta mensagem vai se autodestruir em 10... 9... 8...

Connection to host closed by remote server.
Segmentation fault (core dumped)