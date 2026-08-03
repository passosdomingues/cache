# RFC 02 — Asset Pipeline

## Status
Rascunho — implementação começa no Sprint 3 (Asset Compiler).

## Objetivo

Especificar o pipeline que transforma assets fonte em `game.pkg`, seguindo
a analogia com um compilador tradicional:

```
Assets Fonte (PNG, WAV, TMX, JSON, SVG, TTF)
        │
   Front-end (por tipo)
        │
     Asset IR
        │
Otimizações Paralelas
        │
   Linker de Assets
        │
     game.pkg
```

## Front-ends

Um front-end por tipo de asset, cada um responsável apenas por traduzir o
formato fonte para o Asset IR — nunca por decidir política de runtime.

| Front-end | Entrada | Sprint |
|-----------|---------|--------|
| Image     | PNG (via ImageMagick) | 4 |
| Audio     | WAV/OGG (via FFmpeg)  | 5 |
| Map       | TMX (Tiled)           | 22 |
| Dialogue  | JSON/YAML             | 18/22 |
| Font      | TTF                   | 11 |

## Asset IR

Representação intermediária comum, independente do formato de origem.
Cada nó do IR carrega:

- tipo do asset
- metadados de origem (caminho, hash de conteúdo, timestamp)
- dependências explícitas (ex.: um atlas depende das imagens que o compõem)
- payload transformável pelas otimizações

## Otimizações paralelas

Executadas sobre o IR, independentes entre si sempre que o Dependency
Graph permitir:

- **Dead Asset Elimination** — remove assets não referenciados por
  nenhuma cena/pacote alvo.
- **Constant Folding** em scripts/fórmulas de dados (ex.: fórmulas de dano
  pré-calculáveis).
- **Atlas packing** e **mipmaps** (imagens).
- **Compressão e normalização** (áudio).
- Cada otimização é uma função pura sobre o IR: entrada imutável, nova
  versão do IR como saída — facilita paralelismo e cache.

## Cache e build incremental

- Cache por **hash de conteúdo**, não por timestamp de arquivo.
- Manifest registra, para cada asset final, quais fontes e quais versões
  de front-end/otimização o geraram — qualquer mudança invalida apenas o
  necessário.
- Build incremental: apenas assets cujo hash (ou dependências) mudou são
  recompilados.

## Linker de assets

- Resolve o Dependency Graph final entre todos os assets do pacote alvo.
- Gera `game.pkg`: formato binário com header (versão, hash global),
  tabela de assets e blobs.
- Build determinístico: mesma entrada + mesma versão da toolchain =
  mesmo `game.pkg` byte a byte.

## Ferramentas da Toolchain

- `assetc` — compilador de assets (Sprint 3).
- `Map Compiler`, `Dialogue Compiler`, `Package Viewer`, `Asset Inspector`,
  `Benchmark Viewer` (Sprint 22).

## Fora de escopo aqui

- Como o runtime consome `game.pkg` (RFC 03).
- Distribuição de pacotes pela rede (RFC 05 / Sprint 21).
