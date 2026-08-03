# STATE.md — Estado Atual do Projeto

Este arquivo é a fonte de verdade rápida sobre "onde o projeto está agora".
Atualizado a cada sprint concluído. Para o plano completo veja
`ROADMAP.md`; para o "porquê" das decisões, `docs/adr/`; para a
arquitetura, `docs/0N-*.md`.

## Sprint atual

**Sprint 1 — Platform Layer: concluído.**

## Sprints concluídos

| Sprint | Nome | Entrega | Status |
|--------|------|---------|--------|
| 0 | Fundamentos | `hello-engine` | ✅ Validado na máquina do usuário (Linux Mint, i7-8565U, 8 threads) |
| 1 | Platform Layer | `platform-tests` (10/10 testes) | ✅ Validado por compilação manual (g++ 13, C++20); pendente validar via CMake na máquina do usuário |

## O que existe hoje

- **`src/core/`** — executável `hello-engine` (Sprint 0), com benchmark
  inicial de threads.
- **`src/platform/`** — biblioteca `platform` (Sprint 1), módulo
  `engine::platform`, contendo:
  - `filesystem.hpp/.cpp` — leitura/escrita de arquivos, diretórios
  - `timer.hpp` — `Timer` e `DeltaClock`
  - `logger.hpp/.cpp` — logger com níveis (Debug/Info/Warn/Error)
  - `configuration.hpp/.cpp` — configuração chave=valor
  - `sync.hpp` — `Mutex`, `ScopedLock`, `CountingSemaphore`,
    `BinarySemaphore`, `AtomicCounter`
  - `thread.hpp` — `Thread` (wrapper nomeado sobre `std::thread`)
  - `socket.hpp/.cpp` — `TcpSocket` (POSIX, Linux)
  - `cli.hpp/.cpp` — `CommandLineParser`
  - `memory.hpp/.cpp` — `ArenaAllocator`, `PoolAllocator`
  - `assert.hpp` — `ENGINE_ASSERT` / `ENGINE_VERIFY`
- **`tests/`** — `platform_tests.cpp` com framework de testes próprio
  (`test_framework.hpp`, sem dependências externas) cobrindo os 10
  módulos acima.

## Próximo passo

**Sprint 2 — Job System**: Thread Pool, Job Queue, Task Scheduler,
Dependency Graph, Future, Cancellation, Priority, Profiling, Benchmark.
Entrega: sustentar 100.000 jobs.

## Fluxo de trabalho combinado com o usuário

- Cada sprint é entregue como um **zip incremental**: só arquivos novos
  ou alterados, para o usuário descompactar dentro do projeto existente,
  mesclando e substituindo o que for preciso, preservando o resto.
- Todo sprint atualiza `STATE.md` (este arquivo), `ROADMAP.md` (status)
  e `CHANGELOG.md`.
- Build/validação: `./scripts/build.sh && ./scripts/run.sh` para o
  hello-engine; testes via CTest (`ctest --test-dir build`) ou
  diretamente `./build/tests/platform-tests`.
