# 📝 CHANGELOG — As Águas de Apsu

> Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)
> Versionamento seguindo [Semantic Versioning](https://semver.org/lang/pt-BR/) — `MAJOR.MINOR.PATCH`
>
> - **MAJOR**: mudança que quebra compatibilidade (ex: novo engine, refactor completo)
> - **MINOR**: nova feature ou fase adicionada
> - **PATCH**: bugfix, ajuste de balance, correção visual

---

## [Unreleased] — Sprint 4 em andamento

### Pendente para próxima versão
- Validação de sprites in-game (proporção, transparência) — APSU-040
- Parallax de 2 camadas — APSU-041
- Benchmark de FPS — APSU-043
- Fix: JAVA_HOME apontando para JDK 21 Temurin para `make run` funcionar
- `git init && git commit` — inicializar repositório

---

## [0.2.0] — 2026-08-07 — Sprints 1, 2 e 3 Concluídas

> **Sprint 1: Core Engine & Menu**  
> **Sprint 2: Game Phases & HUD**  
> **Sprint 3: Build System & DevOps**  
> Implementação completa do jogo em uma única sessão intensiva.
> Compilação validada: `javac` + JDK 21 Temurin + JavaFX `/opt/javafx-21/lib` → **0 erros**.

### Adicionado
- `pom.xml` — Maven + JavaFX 21.0.3 linux, javafx-maven-plugin 0.0.8, assembly fat JAR (APSU-010)
- `src/main/java/ApsuGame.java` — jogo completo monolítico ~600 linhas (APSU-011–028):
  - Input `Set<KeyCode>` + eventos pontuais `onKey()`
  - Menu oceânico animado (bolhas, gradiente, seleção ↑↓)
  - Diálogo Enki 7 linhas + avatar PNG/fallback
  - Câmera `camX` deadzone 35%, herói WASD flip horizontal
  - **Fase 1** — Águas Claras: 4 inimigos senoidal, Tabuleta, portal
  - **Fase 2** — Cavernas Coral: obstulos sólidos, Easter Egg baú, Tabuleta
  - **Fase 3** — Boss Kullullû: HP bar 5 hits, bolhas leque, feixes guiados, Tabuleta
  - HUD: corações, tabuletas 0/3→3/3, fase, dificuldade
  - Partículas: 14/evento (dourado/vermelho/ciano), fade
  - Vitória (orbital dourado) + Game Over (vermelho, restart R)
  - SpriteManager fallback geométrico — zero NPE
- `src/main/resources/` — 6 sprites: hero(1.3MB) boss(565KB) npc(744KB) bg1(978KB) bg2(895KB) bg3(957KB) (APSU-016)
- `Makefile` — build/run/run-local/package/docker-build/docker-run/mpi-demo/clean/help, JAVAFX_PATH configurável (APSU-030/032)
- `Dockerfile` — multi-stage Maven builder + Liberica JDK 21 Full + X11 libs (APSU-031)
- `mpi/MapGenerator.c` — MPI_Scatter/Gather 8 processos, mapa colorido ANSI 3 fases (APSU-033)
- `.gitignore` — Java/Maven/JavaFX/Docker/MPI/IDEs/OS (APSU-017)
- `planning/ARCHITECTURE.md` — ADR-008: FXGL avaliado e rejeitado para v1.0

### Corrigido
- BLOCK-001: `pom.xml` não existia → criado
- BLOCK-002: sprites fora de `src/main/resources/` → copiados

### Notas
- **Build Maven bloqueado:** Maven usa JDK 17 (JAVA_HOME). Fix: `export JAVA_HOME=/opt/java-temurin-21`
- **Build direto OK:** `javac` JDK 21 Temurin + JAVAFX_PATH → 4 .class gerados sem erro
- **FXGL avaliado:** Rejeitado (ADR-008) — migrar seria reescrever o projeto

---

## [0.1.0] — 2026-08-07 — Sprint 0 Concluída

> **Sprint 0: Kickoff & Game Plan**
> Primeira versão registrada. Apenas assets e planejamento — sem código executável ainda.

### Adicionado
- `GamePlan.md` — documento de design completo com mecânicas, fases e requisitos técnicos
- `Apkallu.png` — sprite base do herói Adapa fornecido pelo designer
- Sprites gerados por IA com estilo coerente ao Apkallu:
  - `boss_kullullu_*.png` — Boss: Kullullû corrompido (visual sombrio, tons roxo/preto)
  - `npc_enki_*.png` — NPC: Enki deus das águas (tons dourado/azul, cetro)
  - `bg1_aguas_claras_*.png` — Background Fase 1: águas azuis claras tropicais
  - `bg2_cavernas_coral_*.png` — Background Fase 2: cavernas escuras com corais
  - `bg3_templo_submerso_*.png` — Background Fase 3: templo mesopotâmico submerso
- `implementation_plan.md` — plano técnico de implementação aprovado pelo Tech Lead

### Decisões Técnicas
- Stack definida: JavaFX 21 + Maven 3.9 + Docker (Liberica) + GNU Make + OpenMPI
- Resolução alvo: 1366×768 fullscreen adaptativo
- Dificuldades: Sábio (5❤, inimigos lentos) e Ira de Enki (3❤, inimigos rápidos)
- Colisão: AABB simples (suficiente para side-scroller)
- Sprite fallback: formas geométricas quando PNG não encontrado (resiliência)

---

## [0.0.1] — 2026-07-28 — Projeto Iniciado

### Adicionado
- Repositório criado em `/home/rafael/github/cache/grafica/Game/`
- Reunião inicial de kickoff: tema mesopotâmico aprovado
- Personagem principal definido: Adapa, o Apkallu (homem-peixe sábio)

---

## Convenção de Tipos de Mudança

| Tag | Descrição |
|---|---|
| `Adicionado` | Nova funcionalidade ou arquivo |
| `Modificado` | Mudança em funcionalidade existente |
| `Depreciado` | Funcionalidade que será removida em breve |
| `Removido` | Funcionalidade removida |
| `Corrigido` | Correção de bug |
| `Segurança` | Correção de vulnerabilidade |
| `Balance` | Ajuste em valores de gameplay (HP, velocidade, etc.) |
| `Visual` | Mudança cosmética sem impacto em gameplay |

---

## Template para Nova Entrada

```markdown
## [X.Y.Z] — YYYY-MM-DD — Título da Release

> **Sprint N: Nome da Sprint**
> Breve descrição do que foi entregue.

### Adicionado
- Item adicionado (APSU-XXX)

### Modificado
- Item modificado (APSU-XXX)

### Corrigido
- Bug corrigido — descrição do problema e solução (APSU-XXX)

### Balance
- Velocidade dos inimigos ajustada: 2.2 → 2.5 (Modo Sábio)

### Notas para Próxima Versão
- Lista de débitos técnicos identificados
```
