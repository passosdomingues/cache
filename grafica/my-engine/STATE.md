# STATE.md — Estado Atual do Projeto

Este arquivo é a fonte de verdade rápida sobre "onde o projeto está agora".
Atualizado a cada sprint concluído. Para o plano completo veja
`ROADMAP.md`; para o "porquê" das decisões, `docs/adr/`; para a
arquitetura, `docs/0N-*.md`.

## Sprint atual

**Sprint 7 — OpenGL: concluído.**

## Sprints concluídos

| Sprint | Nome | Entrega | Status |
|--------|------|---------|--------|
| 0 | Fundamentos | `hello-engine` | ✅ Validado na máquina do usuário |
| 1 | Platform Layer | `platform-tests` (10/10) | ✅ Validado na máquina do usuário via CMake/CTest |
| 2 | Job System | `job-benchmark` (100.000 jobs) | ✅ Validado na máquina do usuário via CMake/CTest |
| 3 | Asset Compiler | `assetc` (build/inspect) | ✅ Validado na máquina do usuário via CMake/CTest |
| 4 | Image Pipeline | `assetc` com `image`/`atlas` | ✅ Validado na máquina do usuário via CMake/CTest |
| 5 | Audio Pipeline | `assetc` com `audio` | ✅ Validado na máquina do usuário via CMake/CTest |
| 6 | Resource Manager | `resource-demo` | ✅ Validado na máquina do usuário via CMake/CTest |
| 7 | OpenGL | `moving-sprite-demo` | ✅ Validado por compilação manual (g++ 13, C++20 + GLFW + Mesa/llvmpipe via Xvfb): sprite renderizado corretamente (pixel a pixel), atlas UV mapping correto, framebuffer render-to-texture funcional; `render-tests` 7/7; pendente validar via CMake com display real na máquina do usuário |

## O que existe hoje

- **`src/core/`** — `hello-engine` (Sprint 0), benchmark inicial de threads.

- **`src/platform/`** — biblioteca `platform` (Sprint 1), `engine::platform`:
  `Filesystem`, `Timer`/`DeltaClock`, `Logger` (níveis), `Configuration`
  (chave=valor), `Sync` (`Mutex`, `ScopedLock`, `CountingSemaphore`,
  `BinarySemaphore`, `AtomicCounter`), `Thread` (wrapper nomeado),
  `TcpSocket` (POSIX), `CommandLineParser`, `ArenaAllocator`/`PoolAllocator`,
  `ENGINE_ASSERT`/`ENGINE_VERIFY`. `tests/platform_tests.cpp` — 10 testes.

- **`src/jobs/`** — biblioteca `jobs` (Sprint 2), `engine::jobs`, sobre
  `platform`: `JobSystem` (thread pool + filas Critical/Normal/Background),
  Dependency Graph entre jobs, `Future<T>`/`submit_with_result`,
  `CancellationToken`, `JobStats`. Executável `job-benchmark`: 100.000
  jobs em cadeias de dependência. `tests/job_tests.cpp` — 6 testes.

- **`src/pkg/`** (Sprint 6) — biblioteca compartilhada entre Toolchain e
  runtime, extraída de `tools/assetc/` para eliminar duplicação:
  - `format.hpp/.cpp` — `write_package`/`read_package_info`/
    `read_package_payload`, o binário `game.pkg` v2. `PackageEntry` é a
    forma "achatada" que vai pro disco (separada do Asset IR do
    compilador — ver `compiler.hpp` em `tools/assetc`).
  - `compression.hpp/.cpp` — deflate/zlib. `docs/adr/0004-*.md` justifica
    por que zlib é a única dependência externa permitida no runtime
    (diferente de ImageMagick/FFmpeg, restritos à Toolchain).

- **`src/resources/`** (Sprint 6) — `ResourceManager`, `engine::resources`,
  sobre `pkg`+`jobs`+`platform`:
  - Streaming — payload de um asset só é descomprimido no primeiro `acquire()`
  - Cache + Reference Counting — `release()` evita o payload da memória
    ao chegar a refcount 0 (mantém metadata; pode readquirir depois)
  - `ResourceHandle` — índice + geração, detecta handles "stale"
  - `acquire_async()` — carregamento via `JobSystem` (Sprint 2)
  - Hot Reload — `poll_hot_reload()` relê o `.pkg` do disco e substitui
    o payload de recursos residentes cujo `content_hash` mudou
  - `resource-demo` (entrega do sprint) — demonstra tudo isso sobre um
    `game.pkg` real gerado pelo `assetc`
  - `tests/resources_tests.cpp` — 8 testes (incluindo hot reload real:
    reescreve o pacote em disco, chama poll, confirma bytes atualizados)

- **`tools/assetc/`** — biblioteca `assetc_lib` + executável `assetc`
  (Sprints 3-6), `engine::assetc`, agora consumindo `src/pkg/` em vez de
  ter cópia própria do formato/compressão:
  - `Hash` — FNV-1a 64 bits + `hash_combine` (fonte + parâmetros do manifesto)
  - `Manifest` — formato de blocos, com `params` genéricos por asset
  - `FrontendRegistry` — front-ends `raw` (Sprint 3), `image`/`atlas`
    (Sprint 4, Sprite Compiler), `audio` (Sprint 5)
  - `FrontendContext` — acesso de um front-end aos nós de IR já
    compilados nesta build (usado pelo `atlas` para ler dependências)
  - `process_utils` (interno) — subprocessos compartilhados entre
    `image_codec` (ImageMagick) e `audio_codec` (FFmpeg)
  - `atlas_packer` — shelf packing determinístico
  - Dependency Graph — ordenação topológica + detecção de ciclo
  - `BuildCache` — cache incremental por hash (fonte+params), metadata
    persistida entre builds, propagação de invalidação pelo grafo
  - CLI `assetc build`/`assetc inspect`
  - `tests/assetc_tests.cpp` — 14 testes
  - `tools/assetc/examples/` — `assets.manifest`, `atlas.manifest`,
    `audio.manifest`, todos com fontes de exemplo prontas

- **`Makefile`** na raiz — `make build/run/test/bench/clean/rebuild/
  assetc-example/atlas-example/audio-example/resource-demo/
  moving-sprite-demo`.

- **`docs/adr/0004-zlib-runtime-dependency.md`** — decisão de permitir
  zlib (só zlib) como dependência de runtime.

- **`src/render/`** (Sprint 7) — `engine::render`, primeira saída
  gráfica de verdade, sobre `platform`+GLFW+OpenGL 3.3 core:
  - `Window` — janela + contexto, via GLFW (`docs/adr/0005-*.md`)
  - `gl` — loader mínimo próprio das funções OpenGL >= 1.5/3.0 não
    presentes no `GL/gl.h` legado do sistema (via `glfwGetProcAddress`)
  - `ShaderProgram` — compila/linka, lança com o log em caso de erro
  - `Texture2D` — upload de RGBA8 cru
  - `Framebuffer` — render-to-texture básico
  - `OrthographicCamera2D` + `math.hpp` (Mat4/Vec2 mínimos)
  - `Sprite` + `SpriteBatch` — batching por textura É a Render Queue
    neste contexto 2D (sem estrutura de fila separada)
  - `image_payload`/`atlas_payload` — lê, do lado do runtime, o layout
    binário que `tools/assetc`'s `image`/`atlas` front-ends escrevem
    (Sprint 4), a partir dos bytes já descomprimidos pelo
    `ResourceManager` (Sprint 6)
  - `moving-sprite-demo` (entrega do sprint) — carrega um atlas real via
    `game.pkg`, recorta o UV do sprite escolhido, anima e desenha
  - `tests/render_tests.cpp` — 7 testes (2 de payload sem GL; 5 com
    contexto GL headless: window+loader, shader válido/inválido,
    textura, framebuffer com leitura de pixel real, sprite batch)

## Próximo passo

**Sprint 8 — ECS**: Entity, Component, Systems, Events, Commands,
Serialization. Entrega: 10.000 entities.

## Fluxo de trabalho combinado com o usuário

- Cada sprint é entregue como **zip incremental** (só arquivos novos/
  alterados), para descompactar dentro do projeto existente, mesclando e
  preservando o resto.
- Todo sprint atualiza `STATE.md`, `ROADMAP.md` e `CHANGELOG.md`, e
  mantém `version.hpp`/`project(VERSION ...)` sincronizados.
- Rafa gosta de `Makefile` para os atalhos do dia a dia.
