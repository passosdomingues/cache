# RFC 01 — Modelo de Execução

## Status
Rascunho — implementação começa no Sprint 1 (Platform Layer) e Sprint 2
(Job System).

## Objetivo

Definir como a engine executa em tempo real: loop principal, escalonamento
de trabalho, concorrência e sincronização.

## Loop principal

```
enquanto (rodando):
    coletar input
    atualizar timer / delta time
    processar jobs concluídos do frame anterior
    submeter jobs deste frame (update de sistemas ECS, IA, física)
    aguardar barreira de sincronização
    render (frame N-1 ou N, dependendo de pipelining)
    apresentar frame
```

O loop em si não conhece a lógica de jogo — ele apenas orquestra a
submissão de jobs e a barreira de sincronização entre simulação e
apresentação.

## Job System (Sprint 2)

- **Thread Pool** dimensionado por `hardware_concurrency()`, configurável.
- **Job Queue** com filas por prioridade (crítico / normal / background).
- **Task Scheduler** resolve o **Dependency Graph** entre jobs antes de
  despachá-los.
- **Future** para resultado assíncrono de um job.
- **Cancellation** cooperativa via token, não preemptiva.
- Critério de aceite: sustentar 100.000 jobs triviais sem deadlock e com
  overhead de escalonamento mensurável via benchmark.

## Concorrência e sincronização

- Primitivas na Platform Layer: `Mutex`, `Semaphore`, tipos `Atomic`.
- Regra geral: sistemas de jogo não compartilham estado mutável direto;
  comunicação entre sistemas via **Event System** (RFC futura, Sprint 16)
  ou resultados de jobs.
- Nenhuma alocação de memória dentro de uma job crítica de frame sem
  passar pelo alocador da engine (ver `03-runtime.md`).

## Determinismo de frame

- Delta time é *clampado* para evitar espirais de morte em frames longos.
- Ordem de execução de sistemas dentro de um frame é definida
  explicitamente pelo Dependency Graph, não por ordem de registro.

## Profiling

- Cada job registra tempo de fila e tempo de execução.
- Benchmark do Sprint 2 mede: jobs/segundo, latência p50/p99, overhead do
  scheduler.

## Fora de escopo aqui

- Renderização (RFC 03).
- Pipeline de assets (RFC 02).
