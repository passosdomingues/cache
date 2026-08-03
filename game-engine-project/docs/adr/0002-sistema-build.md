# ADR 0002 — Sistema de Build

## Status
Aceito

## Contexto
O projeto precisa de um sistema de build capaz de organizar múltiplos
alvos (core, platform layer, toolchain, testes, benchmarks) com
dependências entre eles, com bom suporte a builds incrementais e
integração futura com CI.

## Alternativas consideradas
- **CMake**: padrão de facto em C++, ecossistema maduro, boa integração
  com Ninja, testes (CTest) e ferramentas de terceiros (ImageMagick,
  FFmpeg via `find_package`/`pkg-config`).
- **Meson**: sintaxe mais limpa e builds geralmente mais rápidos, porém
  ecossistema menor para bibliotecas específicas que a Toolchain vai
  precisar (ImageMagick, FFmpeg).

## Decisão
Adotar **CMake** (≥ 3.20), com Ninja como gerador recomendado.

## Consequências
- Cada módulo (`src/core`, `src/platform`, `tools/*`) é um alvo CMake
  próprio, com `CMakeLists.txt` local.
- Testes via CTest (Sprint 1 em diante).
- Scripts em `scripts/build.sh` e `scripts/run.sh` encapsulam os comandos
  CMake para uso do dia a dia.
