# RFC 00 — Visão Arquitetural

## Status
Rascunho — válido a partir do Sprint 0.

## Objetivo

Construir uma engine de jogos 2D cuja arquitetura é modelada como um
**compilador**, não como um "motor que interpreta arquivos". Assets fonte
(PNG, WAV, TMX, JSON, SVG, TTF) passam por front-ends específicos, são
reduzidos a uma representação intermediária comum (Asset IR), otimizados e
linkados em um pacote binário (`game.pkg`). O runtime nunca lê arquivos
brutos de conteúdo — ele carrega e executa pacotes já compilados.

O jogo de validação é um JRPG orientado a dados, com temática de física,
astrofísica e exploração espacial, para garantir que a engine nasça "rica"
(tilemaps, diálogo, IA, save system, áudio, scripting, UI, física simples)
sem se tornar um projeto de jogo em si — o jogo é apenas o critério de
aceite da arquitetura.

## Princípios

1. **Tudo é transformação.** Texto → Parser → Objeto. Imagem → Atlas →
   Textura. Áudio → FFmpeg → Asset. Mapa → Compiler → Binário. Cada
   estágio tem entrada e saída bem definidas, sem estado escondido.
2. **Data-driven até o limite razoável.** NPCs, skills, missões, fórmulas
   de dano e diálogos são dados (JSON/IR), não código. A engine interpreta
   esquemas, nunca conhece conteúdo específico.
3. **Nenhuma biblioteca sem demonstração.** Cada sprint entrega um
   executável funcional que prova a capacidade construída.
4. **Builds determinísticos e incrementais.** Mesma entrada produz sempre
   o mesmo `game.pkg`, byte a byte. Cache por hash evita recompilar assets
   inalterados.
5. **Paralelismo por padrão.** Compilação de assets, jobs de runtime e
   pipelines de otimização são desenhados para escalar em múltiplos
   núcleos desde o início (Job System no Sprint 2).
6. **Plataforma abstrata desde o Sprint 1.** O núcleo nunca chama APIs de
   SO diretamente; sempre através da Platform Layer.
7. **Minimalismo estético e técnico.** Prefere-se o menor conjunto de
   conceitos que resolve o problema — coerente com a estética visual
   pretendida do jogo (paleta inspirada em Chrono Trigger / Zelda: A Link
   to the Past).

## Requisitos não funcionais

- **Portabilidade:** Linux (Debian/Mint) como plataforma primária; Android
  como alvo tardio (Sprint 23), só depois do runtime estar sólido.
- **Desempenho:** hardware de referência é uma máquina modesta (ver
  `05-plataformas.md`); a engine deve ser leve o suficiente para rodar bem
  nela.
- **Rastreabilidade:** todo asset compilado carrega metadados de origem
  (hash, timestamp, versão do compilador que o gerou).
- **Determinismo:** builds reproduzíveis, importantes para cache e CI.
- **Extensibilidade sem modificar o núcleo:** novos gêneros/módulos via
  sistema de plugins (RFC 04), não via fork do core.

## Restrições

- C++20, compilado com GCC ou Clang no Linux.
- CMake como sistema de build (ADR 0002).
- Sem motor de terceiros (Unity, Unreal, Godot) — a engine é o produto.
- Bibliotecas externas usadas apenas na Toolchain (ex: ImageMagick,
  FFmpeg) para pipelines de assets, não no runtime.

## Fora de escopo (por enquanto)

- 3D.
- Multiplayer/rede além de um Socket básico na Platform Layer.
- Motor de física rígida completo (apenas AABB/raycast/triggers, Sprint 14).
- Definição de gênero final do jogo — o Sprint 19 valida mecânicas
  mínimas, sem comprometer a arquitetura com decisões de gameplay
  específicas cedo demais.

## Documentos relacionados

- `01-modelo-execucao.md`
- `02-asset-pipeline.md`
- `03-runtime.md`
- `04-sistema-plugins.md`
- `05-plataformas.md`
- `06-plano-implementacao.md`
