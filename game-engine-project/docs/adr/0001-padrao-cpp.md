# ADR 0001 — Padrão de C++

## Status
Aceito

## Contexto
A engine precisa de um padrão de C++ moderno o suficiente para suportar
concepts (validação de interfaces do asset pipeline em tempo de
compilação), `std::span`, inicializadores designados (úteis para structs
data-driven que espelham os JSONs consumidos em runtime) e um caminho de
evolução até coroutines para o Job System.

## Alternativas consideradas
- **C++17**: maduro, suporte universal, mas sem concepts nativos nem
  coroutines — exigiria bibliotecas/patterns alternativos para o Job
  System e para validação de templates do asset pipeline.
- **C++20**: concepts, ranges (parcial), coroutines, `std::span`,
  designated initializers, `std::format` (parcial). Suporte sólido em
  GCC ≥ 10/Clang ≥ 10, maduro em GCC ≥ 12.
- **C++23**: recursos adicionais interessantes, mas suporte ainda
  irregular nos compiladores disponíveis em Debian stable no momento
  desta decisão.

## Decisão
Adotar **C++20**.

## Consequências
- Compilador mínimo: GCC 12 ou Clang 15 (ver ADR 0002 / RFC 05).
- Concepts serão usados para restringir templates do Asset IR e do
  sistema de otimizações (RFC 02).
- Coroutines ficam disponíveis para uma eventual revisão do Job System,
  sem necessidade de reescrever a base em C++23 depois.
