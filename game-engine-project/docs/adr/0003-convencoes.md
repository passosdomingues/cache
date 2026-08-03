# ADR 0003 — Convenções de Projeto

## Status
Aceito

## Contexto
Um projeto de longo prazo, com muitos módulos independentes (core,
platform, toolchain), precisa de convenções consistentes desde o
Sprint 0 para evitar retrabalho de estilo mais tarde.

## Decisão

### Nomenclatura
- Namespaces: `engine::<módulo>` (ex.: `engine::core`, `engine::platform`).
- Classes/Structs: `PascalCase`.
- Funções e métodos: `snake_case`.
- Membros privados: sufixo `_` (ex.: `frame_count_`).
- Constantes: `kPascalCase`.
- Arquivos: `snake_case.hpp` / `snake_case.cpp`.

### Estrutura de diretórios
- Um diretório por módulo em `src/`, cada um com seu próprio
  `CMakeLists.txt`.
- Headers públicos de um módulo ficam em `include/` dentro do módulo
  quando o módulo expõe uma API para outros; headers internos ficam
  junto ao `.cpp`.

### Documentação
- Toda decisão de arquitetura relevante vira um ADR em `docs/adr/`,
  numerado sequencialmente.
- RFCs de arquitetura (`docs/0N-*.md`) são atualizadas quando a decisão
  de um ADR as afeta — ADRs não substituem as RFCs, apenas registram o
  "porquê" de uma escolha pontual.

### Commits e versionamento
- `CHANGELOG.md` atualizado a cada sprint concluído.
- Versionamento semântico informal durante a fase de fundamentos
  (0.0.x por sprint), formal (`1.0.0`) a partir da primeira release
  jogável.

### Testes e benchmarks
- Todo módulo que expõe um critério de aceite mensurável (RFC 06) tem um
  benchmark em `tests/` ou `tools/benchmarks/`.

## Consequências
- Consistência entre módulos escritos em sprints diferentes.
- Menor custo de revisão ao longo do projeto.
