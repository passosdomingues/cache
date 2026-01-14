# Métricas e Tomada de Decisão - Indicadores no Monitoramento

## A Governança Baseada em Dados
O **[[Monitoramento Baseado em Métricas]]** transforma a gestão de projetos de uma prática subjetiva em uma **[[Disciplina Orientada por Dados]]**. Indicadores-chave de desempenho (KPIs) fornecem uma **[[Visão Objetiva e Quantificada]]** da saúde do projeto, permitindo **[[Tomada de Decisão Proativa e Informada]]**. Estas métricas atuam como o **[[Painel de Instrumentos do Projeto]]**, alertando sobre desvios antes que se tornem críticos e validando a eficácia das ações corretivas.

## Os Cinco Pilares das Métricas de Monitoramento

### 1. **[[Métricas de Prazo (Desempenho Temporal)]]**
- **Indicador Primário**: **[[Índice de Desempenho de Prazo (SPI)]]**
    - **Fórmula**: SPI = Valor Agregado (VA) / Valor Planejado (VP)
    - **Interpretação**:
        - **SPI = 1.0** (SV = 0): Projeto **[[Exatamente no Prazo]]**.
        - **SPI < 1.0** (ex: 0.85): Projeto **[[Atrasado]]**. Para cada dia planejado, menos de um dia de valor foi agregado.
        - **SPI > 1.0** (ex: 1.15): Projeto **[[Adiantado]]**.
- **Métrica Complementar**: **[[Variação de Prazo (SV)]]**: SV = VA - VP. Valor monetário do atraso ou adiantamento.
- **Implicação Gerencial**: Um SPI < 1 requer análise do **[[Caminho Crítico]]** e possíveis ações de **[[Aceleração (Crashing)]]** ou **[[Paralelismo (Fast Tracking)]]**.

### 2. **[[Métricas de Custo (Desempenho Financeiro)]]**
- **Indicador Primário**: **[[Índice de Desempenho de Custo (CPI)]]**
    - **Fórmula**: CPI = Valor Agregado (VA) / Custo Real (CR)
    - **Interpretação**:
        - **CPI = 1.0** (CV = 0): Projeto **[[Exatamente no Orçamento]]**.
        - **CPI < 1.0** (ex: 0.90): **[[Estouro de Orçamento]]**. Para cada R$1 gasto, menos de R$1 em valor foi agregado.
        - **CPI > 1.0** (ex: 1.05): **[[Custo Abaixo do Orçamento]]**.
- **Métrica Complementar**: **[[Variação de Custo (CV)]]**: CV = VA - CR. Valor monetário do desvio orçamentário.
- **Implicação Gerencial**: Um CPI < 1 exige revisão de **[[Estimativas]]**, análise de **[[Causas de Desperdício]]** e possivelmente **[[Reserva de Contingência]]**.

### 3. **[[Métricas de Qualidade (Conformidade e Eficiência)]]**
- **Indicadores Típicos**:
    - **[[Taxa de Defeitos por Entregável]]**: Número de não-conformidades identificadas.
    - **[[Percentual de Retrabalho]]**: Tempo/custo gasto corrigindo defeitos vs. trabalho novo. **Meta: < 5%**.
    - **[[Custo da Má Qualidade (COPQ)]]**: Custos de retrabalho, reteste, garantia e falhas externas.
- **Interpretação**: **[[Baixa Taxa de Defeitos e Retrabalho]]** indica processos controlados. **[[Alto Retrabalho]]** impacta diretamente **[[Prazo e Custo]]** e sinaliza falhas no **[[Controle de Processos]]**.
- **Fonte**: Dados do **[[Plano de Gestão da Qualidade]]** e atividades de **[[Garantia e Controle da Qualidade]]**.

### 4. **[[Métricas de Riscos e Problemas (Exposição e Resolução)]]**
- **Indicadores de Risco**:
    - **[[Exposição ao Risco Total]]**: Soma (Probabilidade x Impacto) dos riscos ativos. **Nível "Médio"** requer atenção contínua.
    - **[[Eficácia das Respostas]]**: % de respostas a riscos implementadas conforme planejado.
- **Indicadores de Problemas (Issues)**:
    - **[[Issues Ativos]]**: Número de problemas não resolvidos. Alto volume indica ambiente caótico.
    - **[[Tempo Médio de Resolução (MTTR)]]**: Velocidade da equipe em resolver issues.
- **Implicação**: Issues são **[[Riscos que se Materializaram]]**; seu gerenciamento ágil é crítico para evitar desvios maiores.

### 5. **[[Métricas de Comunicação e Engajamento]]**
- **Indicadores de Processo**:
    - **[[Conformidade do Plano de Comunicacão]]**: % de relatórios (reports) entregues **["Em Dia"]**.
    - **[[Cobertura de Stakeholders]]**: % do registro de stakeholders que recebe comunicações adequadas.
- **Indicadores de Percepção**:
    - **[[Nível de Engajamento dos Stakeholders]]**: Medido via pesquisas de satisfação ou percepção. **"Engajados"** é o estado desejado.
    - **[[Clareza e Utilidade da Informação]]**: Feedback sobre relatórios.
- **Implicação**: Comunicação eficaz é o **[[Lubrificante do Projeto]]**; métricas ruins aqui predizem problemas de alinhamento e suporte.

## Integração das Métricas para Tomada de Decisão

As métricas não devem ser analisadas isoladamente. A **[[Análise Integrada]]** é poderosa:
- **[[Cenário: SPI < 1, CPI > 1]]**: Projeto atrasado mas sob orçamento. Decisão: Usar recursos financeiros salvos para acelerar o cronograma (ex: hora extra).
- **[[Cenário: SPI > 1, CPI < 1, Retrabalho Alto]]**: Projeto adiantado mas com estouro de custo e má qualidade. Decisão: Investigar se a aceleração está causando retrabalho, sacrificando qualidade e custo.

Estas análises alimentam diretamente o **[[Processo de Controle de Mudanças]]** e as **[[Reuniões de Status com a Governança (CCB)]]**.

## Conexões com a Ontologia Existente

### Relação com [[Gestão de Desempenho - Monitoramento e Controle]]
- Estes indicadores são os **[[Sinais Vitais Concretos]]** que o processo de Monitoramento coleta e analisa. O SPI e CPI são o núcleo da **[[Análise de Valor Agregado (EVA)]]**.
- As **[[Ações Corretivas e Preventivas]]** são disparadas pelos alertas gerados por essas métricas.

### Relação com [[Definição de Caminhos e Estratégias - Fase de Planejamento]]
- As métricas comparam o **[[Real vs. as Linhas de Base]]** (escopo, cronograma, custo) definidas no planejamento.
- Os **[[Planos Subsidiários]]** (Qualidade, Riscos, Comunicação) definem as métricas específicas a serem coletadas (ex: padrões de qualidade, matriz de rastreabilidade de riscos).

### Relação com [[Base de Planejamento - Importância do Planejamento]]
- A utilidade das métricas depende da **[[Existência de um Plano Clara e Mensurável]]**. Sem baseline, não há SPI ou CPI significativos.
- O planejamento estabelece os **[[Valores-Alvo (Targets)]]** contra os quais as métricas são comparadas.

### Relação com [[1-Projeto]] (Restrições Concorrentes)
- Estas métricas quantificam diretamente o estado das **[[Restrições Concorrentes]]**:
    - **SPI** → Prazo
    - **CPI** → Custo
    - **Métricas de Qualidade** → Qualidade
    - **Métricas de Escopo** (não listadas mas implícitas) → % da EAP concluída.
- A **[[Tomada de Decisão]]** baseada em métricas é essencialmente o ato de **[[Reequilibrar essas Restrições]]**.

### Relação com [[Governança e Acompanhamento]]
- Estes indicadores formam o **[[Conteúdo Central dos Relatórios de Status para a Governança]]**.
- Permitem que o patrocinador e o CCB tomem decisões **[[Baseadas em Fatos, Não em Opiniões]]** sobre a continuidade do projeto.
- Um dashboard consolidado com SPI, CPI, status de riscos e engajamento é a ferramenta ideal para **[[Revisões de Governança]]**.

## Riscos e Boas Práticas no Uso de Métricas

### **[[Riscos no Uso de Métricas]]**
1.  **[[Paralisia por Análise]]**: Coletar muitas métricas e não agir.
2.  **[[Jogo de Métricas (Gaming)]]**: A equipe otimiza localmente o indicador em detrimento do objetivo global (ex: sacrificar qualidade para melhorar SPI).
3.  **[[Métricas Vanidosas (Vanity Metrics)]]**: Medir o que é fácil, não o que importa.
4.  **[[Falta de Contexto]]**: Interpretar um número isoladamente sem entender a história por trás.

### **[[Boas Práticas Recomendadas]]**
1.  **[[Menos é Mais]]**: Escolher um conjunto pequeno (5-7) de **[[Métricas Acionáveis]]** diretamente ligadas aos objetivos.
2.  **[[Visualização Clara]]**: Usar dashboards e gráficos de tendência (ex: SPI/CPI ao longo do tempo).
3.  **[[Revisões Periódicas]]**: Analisar métricas em ciclos regulares (semanal/quinzenal) com a equipe.
4.  **[[Foco em Tendências, Não em Pontos Isolados]]**: Um CPI de 0.98 é preocupante? Depende se está caindo (de 1.05) ou subindo (de 0.90).
5.  **[[Complementar com Narrativa]]**: Atrás de todo número há uma história. Relatórios devem misturar dados com explicações qualitativas.

---
**Palavras-chave:** `Métricas-Projeto` `SPI` `CPI` `Indicadores-Qualidade` `Gestão-Riscos-Métricas` `Engajamento-Stakeholders` `Tomada-Decição-Dados` `KPIs-Projeto`