# Roadmap

> Status atual: veja `STATE.md` para o resumo rápido de onde o projeto
> está agora. Sprints concluídos estão marcados com ✅ abaixo.

Cada sprint deve produzir um **executável funcional**. Nunca uma biblioteca
sem demonstração. O jogo (JRPG orientado a dados, temática de física /
astrofísica / exploração espacial) existe apenas para validar Core Engine,
Asset Pipeline e Toolchain.

## Fases

| Fase | Nome         |
|------|--------------|
| 0    | Fundamentos  |
| 1    | Toolchain    |
| 2    | Runtime      |
| 3    | Rendering    |
| 4    | Assets       |
| 5    | Gameplay     |
| 6    | Performance  |
| 7    | Engine       |
| 8    | Publicação   |

## Sprints

### Sprint 0 — Fundamentos ✅
Construir a fundação: padrão C++, compilador, sistema de build, estrutura
de diretórios, convenções, documentação, ADRs, roadmap, changelog,
arquitetura inicial, benchmark inicial.
**Entrega:** `hello-engine`

### Sprint 1 — Platform Layer ✅
Filesystem, Timer, Logger, Configuration, Threads, Mutex, Semaphore,
Atomic, Socket, CLI, Memory, Assertions.
**Entrega:** Platform Tests

### Sprint 2 — Job System ✅
Thread Pool, Job Queue, Task Scheduler, Dependency Graph, Future,
Cancellation, Priority, Profiling, Benchmark.
**Entrega:** 100.000 jobs

### Sprint 3 — Asset Compiler ✅
Pipeline, Hash, Manifest, Dependency Graph, Incremental Build, Cache,
Binary Package, Metadata.
**Entrega:** `assetc`

### Sprint 4 — Image Pipeline ✅
ImageMagick, Resize, Crop, Padding, Atlas, Compression, Mipmaps, Metadata,
Sprite Compiler.
**Entrega:** `atlas.pkg`

### Sprint 5 — Audio Pipeline ✅
FFmpeg, Normalize, Trim, Fade, Loop, Compress, Metadata, Package.
**Entrega:** `audio.pkg`

### Sprint 6 — Resource Manager ✅
Streaming, Cache, Hot Reload, Reference Counting, Handle, Package Loader.
**Entrega:** Resource Demo

### Sprint 7 — OpenGL
Window, Context, Shader, Texture, Camera, Sprite, Batch, Framebuffer,
Render Queue.
**Entrega:** Moving Sprite

### Sprint 8 — ECS
Entity, Component, Systems, Events, Commands, Serialization.
**Entrega:** 10.000 entities

### Sprint 9 — Scene Graph
Hierarchy, Transform, Camera, Viewport, Layers, Culling.
**Entrega:** Multiple scenes

### Sprint 10 — Input
Keyboard, Mouse, Gamepad, Touch abstraction, Action Mapping.

### Sprint 11 — UI
Fonts, Widgets, Layout, Theme, Animation.

### Sprint 12 — Tile Engine
Tilemap, Chunk, Collision, Layers, Animation, Streaming.

### Sprint 13 — Animation
Sprite Animation, Blend, State Machine, Events.

### Sprint 14 — Physics
AABB, Raycast, Collision, Triggers.

### Sprint 15 — Save System
Binary, JSON, Versioning, Migration, Compression.

### Sprint 16 — Event System
Publish, Subscribe, Signals, Commands.

### Sprint 17 — AI
FSM, Behavior Tree, Navigation, Pathfinding.

### Sprint 18 — Scripting
Evitar incorporar uma linguagem logo de início. Primeiro construir uma
representação intermediária (IR) para eventos do jogo; depois decidir se
ela será alimentada por JSON, YAML, Lua ou outra sintaxe.

### Sprint 19 — Gameplay Prototype
Somente agora. Sem gênero definido além do necessário para validar:
Mapa, NPC, Inventário, Interação, Salvar, Carregar.

### Sprint 20 — Performance
Profiler, Memory, CPU, GPU, Frame Time, Asset Loading, Parallelism.

### Sprint 21 — Distribuição
Asset Server, Cache, HTTP, Mirror, Versionamento, Manifest.

### Sprint 22 — Ferramentas
Map Compiler, Dialogue Compiler, Package Viewer, Asset Inspector,
Benchmark Viewer.

### Sprint 23 — Android
Somente aqui, porque o runtime já estará sólido.
