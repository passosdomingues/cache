Analisando cuidadosamente o documento regrasProfessor.pdf, é possível identificar não apenas as regras do trabalho, mas também as armadilhas (pegadinhas) que o professor inseriu para testar se os alunos estão programando no "piloto automático" ou copiando códigos genéricos da internet e de IAs.

Aqui está a análise ponto a ponto e as armadilhas desmascaradas:

1. A Grande Pegadinha: A Definição de "Match" (Igualdade vs. Complementaridade)
A maior armadilha do documento está na definição do pareamento.

Como códigos genéricos funcionam: A maioria dos algoritmos clássicos de alinhamento (como Needleman-Wunsch para DNA) que você encontra online considera um "match" quando os caracteres são iguais (ex: A pareando com A).

A regra do professor: O professor definiu estritamente que um par perfeito ocorre apenas nas combinações biológicas complementares: A com T, T com A, C com G, e G com C.

A prova da armadilha: Se você olhar o Exemplo 2 do professor, a sequência CATCG contra TAGCC sem lacunas pontua -2. Na segunda posição, temos um A alinhado com um A. Pela biologia do trabalho, A com A é um mismatch (não pareado) e recebe -1. Se você usar um código genérico que dá +2 para caracteres iguais, seu algoritmo vai falhar em todos os testes do professor. 

2. A Pegadinha do Algoritmo Guloso no Relatório

Na seção do relatório, o professor diz: "O objetivo é verificar se o algoritmo guloso encontrou a mesma pontuação que o algoritmo de programação dinâmica". 

A armadilha: Ele escreve isso para induzir o aluno a achar que o Guloso deveria encontrar a mesma pontuação. Se uma IA ou um aluno desavisado tentar forçar o algoritmo guloso a dar o mesmo resultado que o dinâmico, vai estragar o código.

A realidade: O algoritmo guloso toma decisões baseadas apenas no cenário local e raramente encontrará a mesma pontuação máxima que a programação dinâmica em instâncias complexas. Na sua "Análise Crítica", você deve afirmar com convicção que o Guloso falha em encontrar a pontuação ótima justamente por sua natureza míope, o que causa o trade-off citado por ele.

3. A "Prova" Escondida nos Critérios de Avaliação

Preste muita atenção na seção de "Método de avaliação". O professor lista que irá avaliar a "Corretude da prova apresentada" tanto na apresentação oral quanto no documento PDF.
  
O que isso significa: Ele não quer apenas que você mostre o código rodando. A palavra "prova" em Ciência da Computação significa uma prova de corretude matemática/lógica.

Você precisará explicar (usando subestrutura ótima) por que a Programação Dinâmica garante a pontuação máxima.

Resumo das Regras Técnicas Rigorosas
Para não perder pontos de bobeira, fique atento a estas restrições inegociáveis da descrição.

Sistema de Pontuação: Deve ser estritamente +2 para bases complementares, -1 para bases não complementares (incluindo letras iguais), e -2 para Gaps (lacunas). 

Tamanho do Grupo: Sugiro dividir as responsabilidades em 3 duplas

Dupla A: Foco no código
Dupla B: Foco nos gráficos
Dupla C: Foco no relatório e apresentação
 
Arquivos Permitidos: O professor é explícito: Somente os arquivos algoritmos.c e algoritmos.h podem ser modificados.

– –
A Pegadinha Oculta no base.c (Shallow Copy)
Olhe atentamente para estas linhas no código do professor:

char *s1_copy = s1;
char *s2_copy = s2;

// ...
long int resultado_dinamico = programacao_dinamica(s1_copy, s2_copy);
// ...
long int resultado_guloso = guloso(s1, s2);

Qual é a armadilha aqui?

Em C, fazer char *s1_copy = s1; não copia a string. Ele apenas cria um novo ponteiro apontando para o mesmo endereço de memória da string original (isso se chama cópia rasa ou shallow copy).
Muitos alunos, ao tentarem implementar o alinhamento, tentam inserir os gaps (-) diretamente na string original durante a Programação Dinâmica para tentar "imprimir" o alinhamento depois. Se um grupo fizer isso, a string s1 será modificada permanentemente. Quando o base.c chamar a função guloso(s1, s2) logo em seguida, o algoritmo guloso vai receber uma string já destruída/modificada, gerando um resultado completamente errado e zerando a nota do grupo.
Por que nós estamos seguros?
Se você olhar o algoritmos.c que construímos juntos, nós usamos s1[i] e s2[j] de forma estritamente passiva (somente leitura). Nós não alteramos o conteúdo das strings originais em nenhum momento. Nós calculamos a pontuação usando variáveis independentes. Portanto, o nosso código vai rodar perfeitamente nesse base.c e passar liso pela armadilha.
– –

Distribuição de Notas: O código vale apenas 30%. A Apresentação vale a maior parte (40%), seguida do Relatório em PDF (30%). Isso mostra que o professor valoriza mais a sua capacidade de explicar o problema do que apenas entregar um código funcional.

Gráficos Exigidos: O PDF deve obrigatoriamente ter um gráfico de "Tamanho da entrada vs. Tempo" e outro de "Tamanho da entrada vs. Consumo de memória". Lembre-se de não cair na armadilha dos gráficos falsos (como tempo caindo para zero) discutidos anteriormente!

Faça o Gráfico

Pegue esses tempos que o base.c gerou para tamanhos diferentes de DNA (no script Python análise.py).

Você verá exatamente o comportamento que discutimos para a Análise Crítica:
O tempo da Programação Dinâmica vai crescer muito rápido (curva parabólica O(N \times M)).

O tempo do Guloso vai ser quase instantâneo e crescer muito devagar (linha reta O(N)).
A pontuação (Resultado) da Dinâmica será sempre maior ou igual à do Guloso.

