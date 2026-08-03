# Changelog

Todas as mudanças relevantes do projeto são documentadas aqui.
Formato inspirado em [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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
