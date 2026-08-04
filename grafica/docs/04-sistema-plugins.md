# RFC 04 — Sistema de Plugins

## Status
Rascunho — princípios valem desde o Sprint 0; scripting concreto no
Sprint 18.

## Objetivo

Definir como adicionar gêneros, módulos e ferramentas **sem alterar o
núcleo** da engine.

## Princípio central

O núcleo não conhece conteúdo de jogo. Tudo que é "regra de gênero"
(fórmula de dano, condição de vitória, comportamento de NPC específico)
vive fora do core, como dado interpretado ou como módulo plugável.

## Camadas de extensão

1. **Dados puros** (JSON/IR) — a forma mais comum. NPCs, skills, missões,
   fórmulas de batalha. Não requer nenhum mecanismo de plugin: é apenas
   conteúdo consumido por sistemas genéricos já existentes no runtime.
2. **Representação Intermediária de eventos (Event IR)** — introduzida no
   Sprint 18. Antes de incorporar qualquer linguagem de script, a engine
   define um IR para eventos de jogo (condição → ação). Só depois se
   decide qual sintaxe alimenta esse IR (JSON, YAML, Lua, etc.).
3. **Módulos nativos (plugins em C++)** — para sistemas que precisam de
   desempenho ou acesso a APIs de baixo nível (ex.: um novo tipo de
   renderer, um novo front-end de asset). Carregados por interface
   estável, nunca por inclusão direta no core.

## Regras

- Um plugin nunca modifica o core; ele registra sistemas, componentes ou
  front-ends de asset através de pontos de extensão explícitos.
- Nenhum plugin pode introduzir uma dependência circular com o core.
- Scripting (Sprint 18) é tratado como *consumidor* do Event IR, não como
  substituto dele — trocar de Lua para outra linguagem no futuro não deve
  exigir reescrever a lógica de jogo, só o front-end que alimenta o IR.

## Sobre geração de conteúdo por IA

Quando IA (ex.: LLMs) for usada para gerar conteúdo, ela **gera dados
(JSON), nunca código**. O fluxo é:

```
Prompt → IA → JSON → Asset Compiler → game.pkg
```

Isso mantém a mesma garantia de segurança e validação que qualquer outro
asset fonte: passa pelo Asset Pipeline (RFC 02), é validado, tem hash e
metadados de origem.

## Fora de escopo aqui

- Qual linguagem de script será escolhida (decisão adiada para quando o
  Event IR já existir e houver necessidade real).
