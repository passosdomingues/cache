# STATE.md — Estado Atual do Projeto

Este arquivo é a fonte de verdade rápida sobre "onde o projeto está agora".
Atualizado a cada sprint concluído. Para o plano completo veja
`ROADMAP.md`; para o "porquê" das decisões, `docs/adr/`; para a
arquitetura, `docs/0N-*.md`.

## Sprint atual

**Sprint 3 — Asset Compiler: concluído.**

## Sprints concluídos

| Sprint | Nome | Entrega | Status |
|--------|------|---------|--------|
| 0 | Fundamentos | `hello-engine` | ✅ Validado na máquina do usuário (Linux Mint, i7-8565U, 8 threads) |
| 1 | Platform Layer | `platform-tests` (10/10 testes) | ✅ Validado na máquina do usuário via CMake/CTest |
| 2 | Job System | `job-benchmark` (100.000 jobs) | ✅ Validado na máquina do usuário via CMake/CTest (100.000/100.000, `job-tests` 6/6) |
| 3 | Asset Compiler | `assetc` (build/inspect) | ✅ Validado por compilação manual (g++ 13, C++20): build determinístico byte-a-byte, cache incremental com propagação de invalidação, `assetc-tests` 7/7; pendente validar via CMake na máquina do usuário |

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

- **`src/jobs/`** — biblioteca `jobs` (Sprint 2), módulo `engine::jobs`,
  construída sobre `platform` (`Thread`, `Mutex`, `AtomicCounter`):
  - `JobSystem` — thread pool + filas por prioridade (Critical/Normal/Background)
  - Dependency Graph — jobs só entram na fila quando as dependências terminam
  - `Future<T>` / `submit_with_result` — resultado assíncrono tipado
  - `CancellationToken` — cancelamento cooperativo
  - `JobStats` — tempo em fila vs. tempo de execução por job
  - Executável `job-benchmark` (entrega do Sprint 2): 100.000 jobs (em
    cadeias de dependência de 4), valida contador final e mede throughput
  - `tests/job_tests.cpp` — 6 testes (execução básica, dependências,
    future com valor, cancelamento, wait_all, não-inanição por prioridade)
- **`Makefile`** na raiz — atalhos `make build/run/test/bench/clean`.

- **`tools/assetc/`** — biblioteca `assetc_lib` + executável `assetc`
  (Sprint 3), módulo `engine::assetc`, primeira materialização concreta
  da analogia "compilador" do RFC 02:
  - `Hash` — FNV-1a 64 bits, hash de conteúdo determinístico
  - `Manifest` — formato de blocos (`[id]` + `chave=valor`) para descrever
    o que compilar; mesmo formato reusado para o manifesto de cache
  - `Frontend`/`FrontendRegistry` — front-end "raw" (Sprint 3); Image
    (Sprint 4) e Audio (Sprint 5) se registram aqui sem mudar o núcleo
  - `Dependency Graph` — ordenação topológica + detecção de ciclo
  - `BuildCache` — cache incremental endereçado por hash de conteúdo
    (manifesto + object store), com propagação de invalidação pelo grafo
    de dependências
  - `Package` — escreve/lê o binário `game.pkg` (header + tabela +
    blobs), determinístico byte a byte (sem timestamps embutidos)
  - CLI `assetc build`/`assetc inspect`, usando `platform::CommandLineParser`
  - `tests/assetc_tests.cpp` — 7 testes (hash, manifesto, grafo de
    dependências, build determinístico, propagação de invalidação de
    cache, leitura de metadados via inspect)
  - `tools/assetc/examples/` — manifesto e assets de exemplo prontos pra
    rodar

## Próximo passo

**Sprint 4 — Image Pipeline**: ImageMagick, Resize, Crop, Padding, Atlas,
Compression, Mipmaps, Metadata, Sprite Compiler. Entrega: `atlas.pkg`.
Primeiro front-end "de verdade" a se registrar no `FrontendRegistry` do
Sprint 3, sem alterar o núcleo do asset compiler.

## Fluxo de trabalho combinado com o usuário

- Cada sprint é entregue como um **zip incremental**: só arquivos novos
  ou alterados, para o usuário descompactar dentro do projeto existente,
  mesclando e substituindo o que for preciso, preservando o resto.
- Todo sprint atualiza `STATE.md` (este arquivo), `ROADMAP.md` (status)
  e `CHANGELOG.md`.
- Build/validação: `./scripts/build.sh && ./scripts/run.sh` para o
  hello-engine; testes via CTest (`ctest --test-dir build`) ou
  diretamente `./build/tests/platform-tests`.
