# RFC 05 — Plataformas

## Status
Rascunho — Linux é a única plataforma até o Sprint 22 inclusive.

## Plataforma primária: Linux

- Distribuições alvo: Debian e derivados (Linux Mint).
- Hardware de referência de desenvolvimento:
  - CPU: Intel i7-8565U (8 threads), 2.0 GHz
  - RAM: 16 GB
  - GPU: Intel UHD (integrada) + AMD Radeon dedicada (dual GPU, notebook)
  - Resolução de referência: 1360×768
- Implicação de design: a engine deve rodar bem em hardware integrado
  modesto — batching agressivo, texturas comprimidas, orçamento de
  memória consciente desde o início, sem depender de GPU dedicada.
- Toda a Platform Layer (RFC 01, Sprint 1) é escrita contra uma interface
  abstrata; a implementação Linux é uma das possíveis, não a única
  assumida pelo core.

## Critérios para futura migração (Android — Sprint 23)

Migrar para Android **somente depois** do runtime estar sólido (pós
Sprint 22), porque:

- Input abstrato (RFC 03, Sprint 10) já precisa suportar touch como um
  cidadão de primeira classe, não um adaptador tardio.
- Renderização (OpenGL, Sprint 7) já é compatível com OpenGL ES com
  ajustes mínimos, se as extensões usadas forem escolhidas com isso em
  mente.
- Filesystem, Threads e Timer da Platform Layer precisam ter uma
  implementação Android sem alterar a interface pública.
- Empacotamento (`game.pkg`) e Asset Pipeline são agnósticos de
  plataforma por construção — não deve haver rework nessa camada.

## Não-objetivos

- Windows/macOS não são alvo neste momento; a Platform Layer não deve
  impedir uma implementação futura, mas nenhum esforço será investido
  nisso agora.
- Consoles: fora de escopo.
