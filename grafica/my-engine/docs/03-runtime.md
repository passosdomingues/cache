# RFC 03 — Runtime

## Status
Rascunho — implementação distribuída entre os Sprints 6 a 17.

## Objetivo

Especificar como o runtime consome `game.pkg` e executa o jogo: gestão de
recursos, renderização, áudio, entrada, eventos e memória. O runtime
**nunca interpreta arquivos fonte** — apenas pacotes já compilados pelo
Asset Pipeline (RFC 02).

## Resource Manager (Sprint 6)

- **Package Loader** lê `game.pkg` e expõe assets por handle opaco.
- **Streaming**: assets grandes (mapas, texturas) carregados sob demanda.
- **Cache** com **Reference Counting**: asset é liberado quando nenhum
  handle o referencia.
- **Hot Reload** em builds de desenvolvimento: recompila e substitui um
  asset sem reiniciar o processo.

## Renderização (Sprint 7 — OpenGL)

- Abstração mínima: Window, Context, Shader, Texture, Camera, Sprite,
  Batch, Framebuffer, Render Queue.
- Batching agressivo de sprites — coerente com um jogo 2D orientado a
  performance em hardware modesto.
- Render Queue ordena por material/textura para minimizar trocas de
  estado de GPU.

## ECS (Sprint 8)

- Entity = identificador opaco.
- Component = dado puro (sem lógica).
- System = função pura sobre um conjunto de componentes.
- Events/Commands para comunicação entre sistemas sem acoplamento direto.
- Critério de aceite: 10.000 entidades ativas sem degradação perceptível
  de frame time no hardware de referência.

## Scene Graph (Sprint 9)

- Hierarchy, Transform, Camera, Viewport, Layers, Culling.
- Múltiplas cenas simultâneas (ex.: mapa + HUD) sem acoplamento entre si.

## Entrada (Sprint 10)

- Abstração única para Keyboard, Mouse, Gamepad e Touch.
- Action Mapping: binds lógicos ("interagir", "mover") desacoplados de
  tecla/botão físico.

## UI (Sprint 11)

- Fonts, Widgets, Layout, Theme, Animation — suficiente para diálogo,
  inventário e menus do JRPG de validação.

## Tile Engine (Sprint 12)

- Tilemap, Chunk (streaming de mundo grande), Collision, Layers,
  Animation.

## Animação (Sprint 13)

- Sprite Animation, Blend, State Machine, Events — dirigido por dados
  (arquivo de animação, não código).

## Física simples (Sprint 14)

- AABB, Raycast, Collision, Triggers — o suficiente para um JRPG 2D, sem
  motor de física rígida completo.

## Save System (Sprint 15)

- Formatos binário e JSON, com versionamento e migração entre versões de
  save, e compressão opcional.

## Event System (Sprint 16)

- Publish/Subscribe, Signals, Commands — espinha dorsal de comunicação
  entre sistemas de gameplay.

## IA (Sprint 17)

- FSM e Behavior Tree para NPCs; Navigation/Pathfinding sobre o Tilemap.

## Memória

- Alocador central da engine (arena/pool, definido na Platform Layer,
  Sprint 1); nenhum sistema de runtime aloca via `new`/`malloc` cru no
  caminho crítico de frame.

## Fora de escopo aqui

- Como assets chegam a `game.pkg` (RFC 02).
- Scripting/linguagem de eventos (RFC 04, Sprint 18).
