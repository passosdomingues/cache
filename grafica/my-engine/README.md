# Game Engine Project — "Compilador de Jogos"

Uma engine de jogos organizada com a mesma filosofia de um compilador:
assets fonte são transformados por front-ends, reduzidos a uma representação
intermediária (Asset IR), otimizados e linkados em um pacote binário
(`game.pkg`) que o runtime apenas executa — nunca interpreta arquivos brutos.

```
Assets Fonte (PNG, WAV, TMX, JSON, SVG, TTF)
        │
   Front-end (por tipo de asset)
        │
     Asset IR
        │
Otimizações Paralelas (dead asset elimination, constant folding, etc.)
        │
   Linker de Assets
        │
     game.pkg
        │
     Runtime
```

O jogo de validação é um JRPG orientado a dados (NPCs, skills, missões e
batalhas descritos em JSON — a engine nunca conhece o conteúdo específico,
apenas interpreta esquemas), com temática de física, astrofísica e
exploração espacial, estética minimalista e paleta de cores inspirada em
Chrono Trigger e Zelda: A Link to the Past.

**Este repositório existe para validar o Core Engine, o Asset Pipeline e o
Toolchain. O jogo em si é apenas o critério de aceite.**

## Estrutura

```
.
├── docs/              RFC de arquitetura (leia isto antes de mexer no código)
│   ├── 00-visao-arquitetural.md
│   ├── 01-modelo-execucao.md
│   ├── 02-asset-pipeline.md
│   ├── 03-runtime.md
│   ├── 04-sistema-plugins.md
│   ├── 05-plataformas.md
│   ├── 06-plano-implementacao.md
│   └── adr/            Architecture Decision Records
├── src/
│   ├── core/           Núcleo da engine (Sprint 0: hello-engine)
│   ├── platform/       Camada de abstração de plataforma (Sprint 1)
│   ├── jobs/            Job System (Sprint 2)
│   ├── pkg/             Formato de pacote (game.pkg) + compressão,
│   │                    compartilhado entre Toolchain e runtime (Sprint 6)
│   ├── resources/       Resource Manager + Resource Demo (Sprint 6)
│   └── render/          Window/Context/Shader/Texture/Camera/Sprite/
│                         Batch/Framebuffer + Moving Sprite Demo (Sprint 7)
├── tools/
│   └── assetc/          Asset Compiler: front-ends raw/image/atlas/audio
│                         (Sprints 3-5)
├── tools/              Toolchain (asset compiler, etc. — Sprint 3+)
├── tests/              Testes automatizados
├── assets/             Assets fonte (vazio por enquanto)
├── scripts/            Scripts utilitários de build/run
├── ROADMAP.md          Fases e sprints completos
├── CHANGELOG.md
└── CMakeLists.txt
```

## Requisitos

- Linux (testado para Debian/Linux Mint)
- CMake ≥ 3.20
- GCC ≥ 12 ou Clang ≥ 15 (suporte a C++20)
- Ninja (opcional, recomendado)
- ImageMagick (`sudo apt install imagemagick`) — front-end de imagem do
  assetc (Sprint 4)
- zlib (`sudo apt install zlib1g-dev`, geralmente já vem instalado) —
  compressão do payload de assets no assetc (Sprint 4)
- FFmpeg (`sudo apt install ffmpeg`) — front-end de áudio do assetc
  (Sprint 5)
- GLFW e OpenGL (`sudo apt install libglfw3-dev libgl-dev`) — janela e
  contexto gráfico do runtime (Sprint 7). Requer um display (X11/Wayland)
  para rodar de verdade; `docs/adr/0005-*.md` documenta a escolha.

## Build

Via Makefile (recomendado):

```bash
make build   # configura e compila
make run     # roda o hello-engine
make test    # roda todos os testes (CTest)
make bench   # roda o job-benchmark (100.000 jobs, Sprint 2)
make clean   # limpa o build
```

Ou via scripts diretamente:

```bash
./scripts/build.sh
./scripts/run.sh
```

Ou manualmente:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
./build/src/core/hello-engine
```

## Estado atual

Sprint 0 — Fundamentos. Veja `ROADMAP.md` para o plano completo e
`docs/06-plano-implementacao.md` para critérios de aceite de cada sprint.
