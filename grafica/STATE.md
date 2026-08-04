# STATE.md — Estado Atual do Projeto

Este arquivo é a fonte de verdade rápida sobre "onde o projeto está agora".
Atualizado a cada sprint concluído. Para o plano completo veja
`ROADMAP.md`; para o "porquê" das decisões, `docs/adr/`; para a
arquitetura, `docs/0N-*.md`.

## Sprint atual

**Sprint 4 — Image Pipeline: concluído.**

## Sprints concluídos

| Sprint | Nome | Entrega | Status |
|--------|------|---------|--------|
| 0 | Fundamentos | `hello-engine` | ✅ Validado na máquina do usuário (Linux Mint, i7-8565U, 8 threads) |
| 1 | Platform Layer | `platform-tests` (10/10 testes) | ✅ Validado na máquina do usuário via CMake/CTest |
| 2 | Job System | `job-benchmark` (100.000 jobs) | ✅ Validado na máquina do usuário via CMake/CTest (100.000/100.000, `job-tests` 6/6) |
| 3 | Asset Compiler | `assetc` (build/inspect) | ✅ Validado na máquina do usuário via CMake/CTest (build determinístico, `assetc-tests` 3/3 na época) |
| 4 | Image Pipeline | `assetc` com front-ends `image`/`atlas` (`atlas.pkg`) | ✅ Validado por compilação manual (g++ 13, C++20 + ImageMagick + zlib): mipmaps corretos, atlas 64x26 com 2 sprites sem overlap, pixels verificados, cache incremental com propagação, pacotes idênticos byte a byte; `assetc-tests` 11/11; pendente validar via CMake na máquina do usuário |

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
  (Sprints 3-4), módulo `engine::assetc`:
  - `Hash` — FNV-1a 64 bits + `hash_combine` (fonte + parâmetros do manifesto)
  - `Manifest` — formato de blocos, com `params` genéricos por asset
    (resize=, crop=, max_width=, padding=, mips=, ...)
  - `FrontendRegistry` — front-ends `raw` (Sprint 3), `image` e `atlas`
    (Sprint 4); Audio (Sprint 5) se registra aqui sem mudar o núcleo
  - `FrontendContext` — dá a um front-end acesso aos nós de IR já
    compilados nesta build (dependências), usado pelo `atlas`
  - `image_codec` — decodifica/transforma via ImageMagick CLI
    (resize/crop/pad) para RGBA8 cru; `generate_mipmaps` por box filter
  - `atlas_packer` — shelf packing determinístico (ordena por altura
    desc., desempate por id) + Sprite Compiler (tabela de UV/posições)
  - `compression` — deflate/zlib do payload final (Toolchain-only, como
    ImageMagick — nunca no runtime)
  - `Dependency Graph` — ordenação topológica + detecção de ciclo
  - `BuildCache` — cache incremental por hash (fonte+params), com
    metadata persistida entre builds e propagação de invalidação pelo
    grafo de dependências
  - `Package` (formato v2) — `game.pkg` com tabela de metadata por asset,
    determinístico byte a byte
  - CLI `assetc build`/`assetc inspect`, mostrando metadata
  - `tests/assetc_tests.cpp` — 11 testes (Sprint 3: 7; Sprint 4: +4 —
    compressão, packer sem overlap, metadata de imagem, atlas com
    verificação de pixels reais)
  - `tools/assetc/examples/` — `assets.manifest` (raw) e `atlas.manifest`
    (image+atlas, com PNGs de exemplo prontos)

## Próximo passo

**Sprint 5 — Audio Pipeline**: FFmpeg, Normalize, Trim, Fade, Loop,
Compress, Metadata, Package. Entrega: `audio.pkg`. Segundo front-end
"de verdade" a se registrar no `FrontendRegistry`, seguindo o mesmo
padrão do `image` (Sprint 4): ferramenta de terceiro via CLI (FFmpeg) +
payload estruturado + compressão + metadata.

## Fluxo de trabalho combinado com o usuário

- Cada sprint é entregue como um **zip incremental**: só arquivos novos
  ou alterados, para o usuário descompactar dentro do projeto existente,
  mesclando e substituindo o que for preciso, preservando o resto.
- Todo sprint atualiza `STATE.md` (este arquivo), `ROADMAP.md` (status)
  e `CHANGELOG.md`.
- Build/validação: `./scripts/build.sh && ./scripts/run.sh` para o
  hello-engine; testes via CTest (`ctest --test-dir build`) ou
  diretamente `./build/tests/platform-tests`.
