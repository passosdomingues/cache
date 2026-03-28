Preparação para perguntas

Arguição para a Dupla 1 (Núcleo Algorítmico Exato e Fidelidade Biológica)

A Pergunta:

"Vocês afirmam que a Programação Dinâmica garante a otimalidade global da pontuação. Contudo, a função de avaliação biológica de vocês pune a igualdade não-complementar (como um 'A' alinhado com um 'A') com -1. Do ponto de vista da subestrutura ótima da matriz de Needleman-Wunsch adaptada, como o algoritmo garante que a aceitação de um mismatch neste passo não corrompe a viabilidade de blocos ótimos futuros?

Além disso, já que o objetivo final exigido pelo edital é apenas devolver a pontuação máxima em um tipo long int (e não o traçado/alinhamento impresso das strings), justifiquem matematicamente por que vocês optaram por alocar uma matriz inteira de complexidade de espaço O(N \times M) em vez de usar uma técnica de otimização de espaço mantendo apenas duas linhas ativas em memória?"

—-

O que esta pergunta avalia (O Ponto Frágil):

Compreensão Teórica: Testa se eles sabem como a matriz guarda a memória das decisões passadas para não corromper o futuro (a essência do DP).
Defesa de Design: A pergunta sobre otimização de espaço é uma clássica pegadinha de doutorado. Em DP, se você só quer a nota final, você realmente só precisa de duas linhas da matriz O(M). Como vocês alocaram a matriz inteira O(N \times M).


A dupla precisa ter a resposta na ponta da língua:

"Alocamos a matriz completa visando flexibilidade futura para realizar o rastreamento (backtracking) do alinhamento, mas contornamos o custo espacial garantindo a liberação estrita da memória (free) para evitar vazamentos, conforme projetado em nosso modelo.”

– – –

Arguição para a Dupla 2 (Núcleo Heurístico e Integridade de Estado)

A Pergunta:

"A abordagem Gulosa de vocês baseia-se numa heurística de lookahead de um único caractere para decidir a inserção de um gap penalizado em -2. Qual é o embasamento teórico que garante que uma janela de observação tão curta é suficiente para justificar a inserção de um gap em cadeias altamente repetitivas?

E, no âmbito da Engenharia de Software, vocês defenderam que o algoritmo opera de forma 'estritamente passiva' para manter a integridade do estado. Expliquem, no nível de manipulação de ponteiros em C, o que aconteceria com a memória alocada dinamicamente pela função ler_arquivo do base.c se o código de vocês tentasse injetar o caractere de lacuna '-' diretamente nas strings originais fornecidas."

—

O que esta pergunta avalia (O Ponto Frágil):

Limites da Heurística: Força a dupla a admitir as fraquezas do próprio código. Um lookahead de tamanho 1 é cego para padrões que precisam de 2 ou 3 gaps consecutivos para alinhar um bloco enorme lá na frente. Eles precisam admitir isso com naturalidade e explicar que esse é o preço pago para manter a complexidade de tempo linear O(\min(N, M)).

Proficiência em C e Shallow Copy: A segunda parte da pergunta testa se eles realmente entendem a armadilha do professor. Eles devem explicar que as variáveis s1 e s2 do base.c são ponteiros para blocos de memória exatos. Inserir um caractere modificaria a string permanentemente para a próxima função ou, pior, causaria uma invasão de memória (segmentation fault) se a string excedesse o tamanho alocado pelo bloco iterativo do professor.

– – –

Arguição para a Dupla 3 (Integração, Benchmarking e Síntese)

A Pergunta:

"Como responsáveis pelo benchmarking e síntese da pesquisa, vocês concluíram que existe um trade-off claro entre exatidão biológica e tempo de execução. Porém, em testes empíricos rodando em C com <sys/time.h>, a alocação maciça da matriz O(N \times M) da Dupla 1 pode gerar altíssimas taxas de cache misses no processador, o que polui o tempo medido em relação ao tempo real de CPU.

Como vocês garantem que a diferença brutal de tempo entre o método Guloso e o Dinâmico não é majoritariamente um gargalo de paginação de memória do sistema operacional em vez de um gargalo estritamente algorítmico? Em posse dessa análise, a partir de qual tamanho de cadeia de DNA o projeto de vocês recomendaria formalmente o abandono da solução exata em favor do modelo subótimo?"

—

O que esta pergunta avalia (O Ponto Frágil):

Compreensão de Arquitetura de Computadores: Testa se quem fez o benchmarking sabe a diferença entre complexidade teórica (Big-O) e o comportamento real na máquina. A alocação da matriz grande da Programação Dinâmica realmente gera gargalos de RAM e cache (paginação). A dupla precisa demonstrar domínio dizendo algo como: "Temos ciência do overhead de hardware. O tempo aferido inclui o custo de alocação de memória, o que reflete o cenário de produção real, e é exatamente por esse custo acoplado que a diferença se torna tão gritante."

VRAU !

Poder de Decisão (A Consolidação):

A pergunta exige um limite exato. Eles não podem fugir com "depende".

Com base nos testes que vocês vão rodar (como orientei antes), eles precisam ter um número na cabeça:

"Pelos nossos testes, a partir de N = 10.000 bases, o consumo de RAM e o tempo da solução Dinâmica tornam o processo inviável para triagens em tempo real, ponto onde a heurística Gulosa se torna imperativa.”
