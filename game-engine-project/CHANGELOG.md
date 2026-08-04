# Changelog

Todas as mudanças relevantes do projeto são documentadas aqui.
Formato inspirado em [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.0.4] — Sprint 3
### Adicionado
- Biblioteca `assetc_lib` + executável `assetc` (`tools/assetc/`), módulo
  `engine::assetc` — primeira materialização concreta da arquitetura
  "compilador de jogos" (RFC 02):
  - `Hash` (FNV-1a 64 bits) — hash de conteúdo determinístico, sem
    dependências externas
  - `Manifest` — formato de blocos (`[id]` + `chave=valor`) para o que
    compilar, reaproveitado também no manifesto de cache
  - `Frontend`/`FrontendRegistry` — front-end "raw" (Sprint 3); pronto
    para receber Image (Sprint 4) e Audio (Sprint 5) sem mudar o núcleo
  - Dependency Graph — ordenação topológica com detecção de ciclo
  - `BuildCache` — cache incremental endereçado por hash de conteúdo,
    com propagação de invalidação pelo grafo de dependências (se uma
    dependência foi recompilada, quem depende dela também é)
  - `Package` — formato binário `game.pkg` (header + tabela + blobs),
    determinístico byte a byte (sem timestamps embutidos, por desenho)
  - CLI `assetc build` / `assetc inspect`, sobre
    `platform::CommandLineParser`
- `tests/assetc_tests.cpp` — 7 testes: hash, manifesto (round-trip),
  grafo de dependências (ordem + ciclo), build determinístico (dois
  builds produzem bytes idênticos), propagação de invalidação de cache,
  leitura de metadados via `inspect`.
- `tools/assetc/examples/` — manifesto e assets de exemplo prontos para
  rodar (`assetc build --manifest=... --out=...`).
- `CMakeLists.txt` raiz atualizado com `add_subdirectory(tools/assetc)`.

## [0.0.3] — Sprint 2
### Adicionado
- Biblioteca `jobs` (`src/jobs/`), módulo `engine::jobs`: `JobSystem`
  (thread pool + filas Critical/Normal/Background), Dependency Graph
  entre jobs, `Future<T>`/`submit_with_result`, `CancellationToken`
  (cancelamento cooperativo), `JobStats` (profiling de fila/execução).
  Construída sobre a Platform Layer (`Thread`, `Mutex`, `AtomicCounter`).
- Executável `job-benchmark` (entrega do Sprint 2): sustenta 100.000
  jobs (organizados em cadeias de dependência de 4) sem deadlock,
  validando o contador final e medindo throughput (~300k jobs/s no
  hardware de referência).
- `tests/job_tests.cpp` — 6 testes cobrindo execução básica,
  dependências, future com valor, cancelamento, `wait_all` e não-inanição
  de jobs de baixa prioridade.
- `Makefile` na raiz do projeto com atalhos `build`, `run`, `test`,
  `bench`, `clean`, `rebuild`.
- `CMakeLists.txt` raiz atualizado com `add_subdirectory(src/jobs)`.

### Corrigido
- `version.hpp` e `project(VERSION ...)` no CMake estavam travados em
  `0.0.1` desde o Sprint 0, sem acompanhar o `CHANGELOG.md` — `hello-engine`
  agora reporta a versão real (`0.0.3`).
- `job_system.hpp` passou a incluir `<mutex>` explicitamente, em vez de
  depender do include transitivo via `sync.hpp`.
- `scripts/build.sh` não reconfigura o CMake do zero em toda chamada
  (`make build`/`test`/`bench` encadeados evitavam trabalho redundante) e
  silencia o ruído de "Entering/Leaving directory" do make recursivo.

## [0.0.2] — Sprint 1
### Adicionado
- Biblioteca `platform` (`src/platform/`), módulo `engine::platform`:
  `Filesystem`, `Timer`/`DeltaClock`, `Logger` (níveis Debug/Info/Warn/Error),
  `Configuration` (chave=valor), `Sync` (`Mutex`, `ScopedLock`,
  `CountingSemaphore`, `BinarySemaphore`, `AtomicCounter`), `Thread`
  (wrapper nomeado), `TcpSocket` (POSIX/Linux), `CommandLineParser`,
  `ArenaAllocator`/`PoolAllocator`, `ENGINE_ASSERT`/`ENGINE_VERIFY`.
- Framework de testes próprio (`tests/test_framework.hpp`), sem
  dependências externas.
- Executável `platform-tests` (entrega do Sprint 1): 10 testes cobrindo
  todos os módulos da Platform Layer, incluindo um teste de loopback TCP
  real (client/server em threads separadas).
- `STATE.md` criado — snapshot rápido do estado do projeto, atualizado a
  cada sprint.
- `CMakeLists.txt` raiz atualizado com `add_subdirectory(src/platform)` e
  `add_subdirectory(tests)`; testes registrados via `add_test`/CTest.

## [0.0.1] — Sprint 0
### Adicionado
- Estrutura inicial de diretórios (`src/`, `docs/`, `tools/`, `tests/`, `assets/`, `scripts/`).
- Documentos de arquitetura (RFC): visão arquitetural, modelo de execução,
  asset pipeline, runtime, sistema de plugins, plataformas e plano de
  implementação.
- Architecture Decision Records (ADR) 0001–0003: padrão C++, sistema de
  build e convenções de projeto.
- `CMakeLists.txt` raiz configurando o projeto em C++20.
- Executável `hello-engine` (entrega do Sprint 0).
- `ROADMAP.md` com fases e sprints completos (0 a 23).
