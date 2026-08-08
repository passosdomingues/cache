# ADR 0005 — GLFW para Janela e Contexto OpenGL

## Status
Aceito

## Contexto
O Sprint 7 precisa criar uma janela, um contexto OpenGL e processar
eventos básicos de input (Sprint 10 trata input "de verdade"; aqui só
precisamos de poll_events para a janela não travar). RFC 00 permite
bibliotecas de terceiros na Toolchain; para o runtime, a única exceção
já aberta é zlib (ADR 0004). Criar janela/contexto é território
diferente: não existe alternativa razoável sem depender de uma
biblioteca de sistema de janelas (GLFW, SDL2) ou escrever bindings
diretos com Xlib/Wayland/Win32 por plataforma — isso teria custo alto e
não agrega nada ao objetivo do projeto (que é validar a arquitetura de
engine, não reimplementar um windowing toolkit).

## Alternativas consideradas
- **GLFW**: biblioteca pequena e focada — janela, contexto OpenGL/Vulkan,
  input básico. Não faz mais que isso.
- **SDL2**: framework multimídia mais amplo (áudio, input avançado,
  gamepads, etc.) — mas o projeto já tem FFmpeg cobrindo áudio (Sprint 5)
  e não precisa da superfície extra do SDL2 agora.

## Decisão
Adotar **GLFW** para janela + contexto OpenGL.

## Consequências
- `src/render/` depende de GLFW e OpenGL (`find_package(glfw3 REQUIRED)`,
  `find_package(OpenGL REQUIRED)`) — nova dependência de sistema:
  `sudo apt install libglfw3-dev libgl-dev` (ver `README.md`).
- GLFW não carrega os ponteiros de função OpenGL modernos (>= 1.5/3.0)
  sozinho — `engine::render::gl` implementa um loader mínimo próprio via
  `glfwGetProcAddress`, carregando só o que a engine efetivamente usa
  (VAOs/VBOs, shaders, framebuffers). Deliberadamente não se usa uma
  biblioteca de loader de terceiros (GLAD/GLEW) — o conjunto de funções
  necessário é pequeno o bastante para não justificar mais uma
  dependência.
- Input "de verdade" (Sprint 10) continua usando GLFW como fonte de
  eventos, mas por trás de uma abstração própria (Platform/Input) — o
  restante da engine nunca chama a API do GLFW diretamente.
