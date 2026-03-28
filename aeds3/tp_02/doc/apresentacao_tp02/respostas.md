## Respostas
>> Equipe Alpha (Dupla 1): Núcleo Algorítmico e DP

A Estratégia de Resposta:

    Sobre o Mismatch (-1) e a Subestrutura Ótima: "A essência da Programação Dinâmica é justamente não tomar decisões precipitadas. A equação de recorrência de Needleman-Wunsch, materializada na nossa função max3, avalia as três rotas possíveis simultaneamente. Aceitar um mismatch local (-1) não corrompe o estado futuro porque a matriz guarda o histórico de todas as sub-soluções. Se o mismatch no índice atual for o 'pedágio' necessário para alcançar uma sequência de 50 matches perfeitos logo adiante, a rota do mismatch será matematicamente coroada como a pontuação ótima."

    Sobre a Alocação Espacial O(N*M): "Professor, é verdade que para retornar apenas o valor long int final nós poderíamos ter otimizado o espaço para O(M) mantendo apenas as duas últimas linhas ativas na memória. Contudo, optamos pela matriz completa O(N*M) como uma decisão de design voltada à escalabilidade. Na bioinformática real, a pontuação sem o traçado do alinhamento é inútil. Manter a matriz inteira nos deixa a uma função de distância de implementar o backtracking para imprimir visualmente os gaps. Contornamos o peso espacial garantindo a integridade do sistema com liberações estritas via free() em cada laço."

>> Equipe Bravo (Dupla 2): Heurística e Integridade de Estado

A Estratégia de Resposta:

    Sobre o Limite do Lookahead (Janela Curta): "Nós reconhecemos as limitações da heurística. Um lookahead de 1 caractere é, por definição, míope e falhará em cadeias que exigem a inserção de múltiplos gaps consecutivos para sincronizar um bloco maior à frente. No entanto, esse é o preço consciente que pagamos. Aumentar a janela de observação para 2, 3 ou K caracteres faria nossa complexidade de tempo degenerar para O(N*K). O objetivo do Guloso era manter a letalidade do tempo linear O(N), sacrificando a otimalidade global em prol da velocidade extrema."

    Sobre a Manipulação de Ponteiros (A Armadilha do C): "As strings originais recebidas pela função, de acordo com a arquitetura que o senhor forneceu, são ponteiros para blocos de memória estáticos ou alocados à medida. Tentar injetar o caractere - usando métodos como memmove causaria um deslocamento no array. Se esse array não tivesse capacidade extra (padding) alocada previamente pela ler_arquivo, nós causaríamos uma invasão de memória ou um Segmentation Fault instantâneo. Por isso, nosso algoritmo opera de forma 100% passiva, usando apenas ponteiros de leitura i e j para simular os gaps mentalmente e calcular o score."

>> Equipe Charlie (Dupla 3): Benchmarking e Síntese

A Estratégia de Resposta:

    Sobre Cache Misses e Gargalos de Hardware: "Nós concordamos que a latência de acesso à memória RAM e os cache misses poluem o tempo bruto de CPU. O processador gasta mais tempo buscando blocos da nossa matriz O(N*M) na paginação do sistema operacional do que processando os cálculos. Porém, esse overhead não é uma 'sujeira' no teste; ele é o sintoma clínico do problema! O gargalo de paginação é inerente à complexidade espacial quadrática do algoritmo. Em um cenário real de produção, o tempo de alocação de memória faz parte da penalidade que o usuário paga por exigir a resposta ótima."

    O Veredito Final (Ponto de Abandono): "Baseado nos nossos testes empíricos cruzados com o hardware da agência, o limite de viabilidade é exato: N = 10.000 bases. Neste ponto de intersecção, a Programação Dinâmica consome cerca de 1 Gigabyte de RAM e leva 2.0 segundos apenas para duas fitas. Sabendo que o genoma humano possui bilhões de pares de bases, recomendamos formalmente que qualquer entrada superior a 104 seja redirecionada compulsoriamente para o Algoritmo Guloso. A perda de precisão biológica é imensa, mas a alternativa é o colapso estrutural do sistema."