# Metodologia Cascata - Desvantagens Principais

## Contexto
Esta nota detalha os **[[Desafios e Limitações]]** inerentes à [[Metodologia Cascata (Waterfall)]], explicando como sua [[Rigidez Estrutural]] pode criar dificuldades significativas, especialmente em [[Ambientes Dinâmicos e Incertezas|ambientes dinâmicos]]. Complementa a compreensão iniciada em [[Metodologia Cascata - Vantagens]].

## Desvantagens Críticas

### 1. [[Mudanças Difíceis e Custosas]]
- **Complexidade de Alterações**: [[Mudanças no Escopo]] após o início do projeto exigem [[Revisitar Fases Concluídas]]
- **Custo de Retrabalho Alto**: Cada alteração desencadeia [[Revisão em Cascata]] de fases anteriores
- **Processos Burocráticos**: Requer [[Processos Formais de Controle de Alterações]] complexos
- **Conexão**: Resultado direto do [[Processo Sequencial]] e da [[Pouca Flexibilidade]]

### 2. [[Descoberta Tardia de Problemas]]
- **Identificação no Final do Ciclo**: [[Problemas e Erros]] muitas vezes só detectados na [[Fase de Testes]]
- **Correção Onerosa**: [[Retrabalho]] se torna mais [[Caro e Demorado]] quando descoberto tardiamente
- **Risco Técnico Acumulado**: [[Defeitos de Concepção]] podem permanecer ocultos por longos períodos
- **Conexão**: Consequência direta das [[Entregas ao Final]] do modelo

### 3. [[Visibilidade Limitada para o Cliente]]
- **Produto Só no Final**: O [[Cliente]] só visualiza o [[Produto Finalizado]] no [[Encerramento do Projeto]]
- **Risco de Desalinhamento**: Aumenta a probabilidade de o [[Resultado Não Atender Expectativas]]
- **Feedback Tardio**: [[Validação do Usuário]] ocorre apenas quando mudanças são mais difíceis
- **Conexão**: Relaciona-se com a característica de [[Entregas ao Final]]

## Conexões com a Ontologia Existente

### Relação com [[Metodologia Cascata (Waterfall): Características Principais]]
- Estas desvantagens são o **lado negativo** das características apresentadas
- [[Mudanças Difíceis]] é o reverso da [[Estrutura Rígida]]
- [[Visibilidade Limitada]] contrasta com a [[Forte Documentação]]

### Relação com [[Metodologia Cascata - Fases Típicas do Processo]]
- O [[Fluxo Linear]] cria a [[Propagação de Erros]] entre fases
- A [[Sequência Fixa]] impede [[Feedback Contínuo]] durante o desenvolvimento
- Os [[Gate Reviews]] formais podem criar falsa sensação de segurança

### Relação com [[Visão Geral de Gestão]]
- Estas desvantagens explicam porque [[Cascata]] pode não ser adequada para [[Ambientes Dinâmicos]]
- Justificam a necessidade de [[Seleção Estratégica de Metodologia]]
- Contrapõem-se às vantagens de ser [[Linear e Previsível]]

### Relação com [[Processo Fundamental de Gestão]]
- Dificulta o [[Controlar]] proativo durante a execução
- Limita a capacidade de [[Dirigir]] ajustes baseados em feedback
- Torna o [[Planejar]] inicial extremamente crítico e arriscado

### Relação com [[Características Distintivas de Projetos]]
- Pode comprometer o [[Alcance de Metas]] se requisitos mudarem
- Dificulta o [[Gerenciamento Eficiente de Recursos]] em cenários de mudança
- Afeta negativamente a [[Governança e Acompanhamento]] quando flexibilidade é necessária

## Implicações Práticas

### Para [[Gestão de Riscos]]
- **[[Risco de Escopo]]**: Alta probabilidade de mudanças não antecipadas
- **[[Risco Técnico]]**: Problemas arquiteturais detectados tardiamente
- **[[Risco de Qualidade]]**: Comprometimento por testes insuficientes no ciclo

### Para [[Relação com Clientes]]
- **[[Expectativas Não Gerenciadas]]**: Cliente não vê progresso até o final
- **[[Insatisfação Pós-Entrega]]**: Produto pode não atender necessidades evolutivas
- **[[Conflitos Contratuais]]**: Mudanças geram disputas sobre custos adicionais

### Para [[Custos e Prazos]]
- **[[Estouro de Orçamento]]**: Correções tardias são extremamente custosas
- **[[Atrasos Significativos]]**: Retrabalho impacta cronograma de forma severa
- **[[Custo de Oportunidade]]**: Recursos imobilizados em soluções potencialmente obsoletas

## Contextos onde Desvantagens se Tornam Críticas

### [[Projetos de Software Moderno]]
- **[[Requisitos Voláteis]]**: Norma em desenvolvimento de software atual
- **[[Mercados Dinâmicos]]**: Necessidade de adaptação rápida a mudanças
- **[[Tecnologias Emergentes]]**: Incerteza técnica requer abordagem iterativa

### [[Projetos Inovadores]]
- **[[Inovação por Descoberta]]**: Solução emerge durante o desenvolvimento
- **[[Aprendizado Contínuo]]**: Equipe descobre requisitos ao implementar
- **[[Validação de Mercado]]**: Necessidade de testar hipóteses com usuários reais

## Mitigações Possíveis (mas Limitadas)

### [[Controle de Mudanças Formal]]
- **[[Processo de Change Request]]**: Para gerenciar alterações necessárias
- **[[Análise de Impacto]]**: Avaliação rigorosa antes de aprovar mudanças
- **[[Revisão de Contrato]]**: Ajustes nos acordos comerciais

### [[Prototipagem nas Fases Iniciais]]
- **[[Mockups e Protótipos]]**: Para validar conceitos antes do desenvolvimento completo
- **[[Testes de Conceito]]**: Verificações técnicas antecipadas
- **[[Validação com Usuários]]**: Feedback limitado, mas melhor que nenhum

### [[Fases Sobrepostas Controladas]]
- **[[Início Antecipado]]**: Começar fases subsequentes antes da conclusão formal
- **[[Paralelismo Limitado]]**: Atividades que não dependem totalmente da fase anterior
- **[[Revisões Contínuas]]**: Checkpoints informais durante o desenvolvimento

## Comparação com [[Metodologias Ágeis]]
- **[[Feedback vs. Documentação]]**: Ágil prioriza feedback contínuo sobre documentação completa
- **[[Adaptabilidade vs. Previsibilidade]]**: Trade-off fundamental entre as abordagens
- **[[Risco Distribuído vs. Risco Concentrado]]**: Ágil distribui risco ao longo do projeto

---
**Palavras-chave:** `Inflexibilidade` `Risco` `Feedback-Tardio`