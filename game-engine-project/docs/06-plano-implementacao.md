# RFC 06 — Plano de Implementação

## Status
Rascunho — este documento é o elo entre a arquitetura (RFCs 00–05) e o
`ROADMAP.md` sprint a sprint.

## Backlog priorizado

A ordem dos sprints em `ROADMAP.md` já reflete a priorização: primeiro
fundamentos e toolchain (Sprints 0–5), depois runtime mínimo (6–10),
depois camadas de conteúdo (11–17), scripting só depois de haver um IR
(18), gameplay só depois de tudo isso validado (19), performance e
distribuição por último (20–22), mobile por último de todos (23).

## Dependências entre sprints

```
0 (Fundamentos)
 └─ 1 (Platform Layer)
     ├─ 2 (Job System)
     │   └─ 3 (Asset Compiler)
     │       ├─ 4 (Image Pipeline)
     │       ├─ 5 (Audio Pipeline)
     │       └─ 6 (Resource Manager)
     │           └─ 7 (OpenGL)
     │               ├─ 8 (ECS)
     │               │   └─ 9 (Scene Graph)
     │               │       └─ 10 (Input)
     │               │           ├─ 11 (UI)
     │               │           ├─ 12 (Tile Engine)
     │               │           ├─ 13 (Animation)
     │               │           ├─ 14 (Physics)
     │               │           ├─ 15 (Save System)
     │               │           ├─ 16 (Event System)
     │               │           └─ 17 (AI)
     │                               └─ 18 (Scripting / Event IR)
     │                                   └─ 19 (Gameplay Prototype)
     │                                       └─ 20 (Performance)
     │                                           └─ 21 (Distribuição)
     │                                               └─ 22 (Ferramentas)
     │                                                   └─ 23 (Android)
```

## Critérios de aceite por sprint

Cada sprint só é considerado concluído quando:

1. O executável de entrega (ver `ROADMAP.md`) compila e roda no hardware
   de referência (`05-plataformas.md`).
2. Existe um benchmark ou teste automatizado que comprova a capacidade
   central do sprint (ex.: 100.000 jobs no Sprint 2, 10.000 entidades no
   Sprint 8).
3. O `CHANGELOG.md` é atualizado.
4. Nenhuma regressão nos critérios de aceite de sprints anteriores.

## Riscos conhecidos

| Risco | Mitigação |
|-------|-----------|
| Escopo do JRPG crescer além do necessário para validar a arquitetura | Sprint 19 explicitamente "sem gênero definido", apenas mecânicas mínimas |
| Scripting virar dependência prematura | Sprint 18 constrói o IR antes de qualquer linguagem concreta |
| Hardware modesto limitar renderização | Batching agressivo e orçamento de memória desde o Sprint 7 |
| Builds não-determinísticos quebrarem cache | Cache por hash de conteúdo desde o Sprint 3, testado no CI |
| Migração Android forçar retrabalho | Input/Renderização já desenhados com touch/GLES em mente desde os Sprints 7 e 10 |

## Benchmarks obrigatórios

- Sprint 0: benchmark inicial (baseline de compilação/execução).
- Sprint 2: 100.000 jobs.
- Sprint 8: 10.000 entidades.
- Sprint 20: profiler completo (CPU, GPU, memória, frame time, asset
  loading, paralelismo).
