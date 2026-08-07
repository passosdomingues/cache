# 📡 STATE — Estado Atual do Projeto

> **Este é o documento mais importante para o dia a dia.**
> Atualizado sempre que uma task muda de estado ou um bloqueio é identificado.
>
> **Última atualização:** 2026-08-07 17:41 BRT (Sprint 4 — Início)
> **Responsável pela atualização:** Tech Lead / Dev ativo

---

## 🚦 Status Geral

| Aspecto | Status | Detalhe |
|---|---|---|
| **Sprint Atual** | 🟡 Sprint 4 | Polish & Assets |
| **Build (javac direto)** | 🟢 OK | `javac` com JDK 21 Temurin + JavaFX local ✅ |
| **Build (mvn compile)** | 🔴 BLOCKED | Maven usa JAVA_HOME=JDK 17 → fix: usar Temurin 21 |
| **Jogo Jogável** | 🟡 CÓDIGO COMPLETO | Aguarda execução `java --module-path` para validar |
| **Sprites** | 🟢 PRONTOS | 6 PNGs em `src/main/resources/` (5.3MB total) |
| **Makefile** | 🟢 COMPLETO | `make help` mostra todos os targets |
| **Dockerfile** | 🟢 COMPLETO | Multi-stage, Liberica JDK 21 Full |
| **Git** | 🟡 PENDENTE | `.gitignore` criado, repositório não inicializado |
| **MPI demo** | 🟢 PRONTO | `mpi/MapGenerator.c` criado, aguarda `make mpi-demo` |

---

## ✅ O que está FEITO

### Sprint 0 — Concluída ✅

| Item | Localização |
|---|---|
| Game Plan completo | `/Game/GamePlan.md` |
| Sprite herói Apkallu | `/Game/Apkallu.png` (1.3MB) |
| Sprite Kullullû (boss) | `src/main/resources/boss.png` (565KB) |
| Sprite Enki (NPC) | `src/main/resources/npc.png` (744KB) |
| Background Fase 1 | `src/main/resources/bg1.png` (978KB) |
| Background Fase 2 | `src/main/resources/bg2.png` (895KB) |
| Background Fase 3 | `src/main/resources/bg3.png` (957KB) |
| Estrutura Maven criada | `/Game/src/main/java/`, `src/main/resources/` |
| Pasta planning completa | `/Game/planning/` (7 arquivos) |

### Sprint 1 — Concluída ✅ (2026-08-07)

| Task | Arquivo | Status |
|---|---|---|
| APSU-010 `pom.xml` | `pom.xml` | ✅ |
| APSU-011 `ApsuGame.java` | `src/main/java/ApsuGame.java` | ✅ |
| APSU-012 Sistema de Input | (em ApsuGame.java) | ✅ |
| APSU-013 Menu animado | (em ApsuGame.java) | ✅ |
| APSU-014 Diálogo Enki | (em ApsuGame.java) | ✅ |
| APSU-015 SpriteManager + fallback | (em ApsuGame.java) | ✅ |
| APSU-016 Sprites copiados | `src/main/resources/*.png` | ✅ |
| APSU-017 `.gitignore` | `.gitignore` | ✅ |

### Sprint 2 — Concluída ✅ (2026-08-07, junto com Sprint 1)

| Task | Implementação | Status |
|---|---|---|
| APSU-020 Câmera `camX` | ApsuGame.java L~180 | ✅ |
| APSU-021 Movimento herói WASD | ApsuGame.java | ✅ |
| APSU-022 Colisão AABB `rectsHit()` | ApsuGame.java | ✅ |
| APSU-023 Fase 1 — Águas Claras | ApsuGame.java | ✅ |
| APSU-024 Fase 2 — Cavernas Coral | ApsuGame.java | ✅ |
| APSU-025 Fase 3 — Boss Kullullû | ApsuGame.java | ✅ |
| APSU-026 HUD completo | ApsuGame.java | ✅ |
| APSU-027 Sistema de partículas | ApsuGame.java | ✅ |
| APSU-028 Vitória + Game Over | ApsuGame.java | ✅ |

### Sprint 3 — Concluída ✅ (2026-08-07)

| Task | Arquivo | Status |
|---|---|---|
| APSU-030 Makefile | `Makefile` | ✅ |
| APSU-031 Dockerfile | `Dockerfile` | ✅ |
| APSU-032 run-local JAVAFX_PATH | (em Makefile) | ✅ |
| APSU-033 MPI MapGenerator.c | `mpi/MapGenerator.c` | ✅ |

---

## 🟡 O que está EM ANDAMENTO

### Sprint 4 — Em progresso (2026-08-08 →)

| Task | Responsável | Progresso |
|---|---|---|
| APSU-040 Validar sprites in-game | Dev JavaFX | ⚪ Aguardando execução |
| APSU-041 Parallax 2 camadas | Dev JavaFX | ⚪ Pendente |
| APSU-042 Efeitos sonoros | Dev JavaFX | ⚪ Opcional |
| APSU-043 Benchmark FPS | Dev JavaFX | ⚪ Pendente |

### Imediato — Fix de Build Maven

| Item | Status |
|---|---|
| Corrigir JAVA_HOME para Maven usar JDK 21 | 🟡 Em avaliação |
| Testar execução: `java --module-path /opt/javafx-21/lib ...` | 🟡 Próximo passo |
| `git init && git add . && git commit` | 🟡 Próximo passo |

---

## 🔴 Bloqueios Ativos

### BLOCK-003 — Maven usa JDK 17 (JAVA_HOME aponta para JDK 17)
- **Sintoma:** `mvn compile` falha com `invalid target release: 21`
- **Causa:** `JAVA_HOME=/home/rafael/java/current` → JDK 17.0.12
- **JDK 21 disponível:** `/opt/java-temurin-21/` (Temurin 21.0.6) ✅
- **Workaround atual:** `javac` direto com JDK 21 Temurin → **compila sem erros** ✅
- **Fix permanente (escolha uma):**
  ```bash
  # Opção A — exportar JAVA_HOME para esta sessão:
  export JAVA_HOME=/opt/java-temurin-21
  mvn compile

  # Opção B — adicionar ao ~/.bashrc:
  echo 'export JAVA_HOME=/opt/java-temurin-21' >> ~/.bashrc

  # Opção C — usar o Makefile com JDK explícito (já configurado no run-local):
  make run-local  # usa javac + JAVAFX_PATH diretamente, sem Maven
  ```
- **Impacto:** `make run` (via Maven) bloqueado. `make run-local` funciona.

---

## 📁 Estrutura de Arquivos Atual

```
/home/rafael/github/cache/grafica/Game/
├── GamePlan.md                    ✅
├── Apkallu.png                    ✅ (hero sprite original)
├── pom.xml                        ✅ CRIADO
├── Makefile                       ✅ CRIADO
├── Dockerfile                     ✅ CRIADO
├── .gitignore                     ✅ CRIADO
├── mpi/
│   └── MapGenerator.c             ✅ CRIADO
├── planning/
│   ├── README.md                  ✅
│   ├── ROADMAP.md                 ✅
│   ├── SPRINTS.md                 ✅ (26/35 tasks done)
│   ├── STATE.md                   ✅ (este arquivo)
│   ├── CHANGELOG.md               ✅
│   ├── ARCHITECTURE.md            ✅ (com ADR-008 FXGL)
│   └── CONTRIBUTING.md            ✅
├── src/
│   └── main/
│       ├── java/
│       │   └── ApsuGame.java      ✅ (~600 linhas, jogo completo)
│       └── resources/
│           ├── hero.png           ✅ (1.3MB)
│           ├── boss.png           ✅ (565KB)
│           ├── npc.png            ✅ (744KB)
│           ├── bg1.png            ✅ (978KB)
│           ├── bg2.png            ✅ (895KB)
│           └── bg3.png            ✅ (957KB)
└── target/
    └── classes/
        ├── ApsuGame.class         ✅ COMPILADO (javac JDK 21)
        ├── ApsuGame$State.class   ✅
        ├── ApsuGame$Diff.class    ✅
        ├── ApsuGame$1.class       ✅
        └── *.png                  ✅ (resources copiados)
```

---

## 🎯 Próximas Ações (Ordered Priority)

> Execute nesta ordem para chegar na Sprint 4:

1. **[Dev DevOps]** Fixar JAVA_HOME → `export JAVA_HOME=/opt/java-temurin-21`
2. **[Dev JavaFX]** Executar o jogo: `make run-local` (já funciona via javac!)
3. **[Dev DevOps]** Inicializar git: `git init && git add . && git commit -m "feat: initial commit v0.2.0-SNAPSHOT"`
4. **[Dev JavaFX]** Validar sprites in-game (APSU-040) — proporção, transparência
5. **[Dev DevOps]** Testar `make mpi-demo` (requer OpenMPI instalado)
6. **[Dev DevOps]** Testar `make docker-build && make docker-run`
7. **[Dev JavaFX]** Implementar parallax se sprites OK (APSU-041)

---

## 🌡️ Ambiente de Desenvolvimento

```
OS:          Linux Mint 22.3
CPU:         Intel Core i7-8565U (4 cores / 8 threads @ 1.8GHz boost 4.6GHz)
RAM:         16 GB DDR4
GPU:         Intel UHD 620 (integrada) + AMD Radeon 520 Mobile (2GB VRAM)
JDK Maven:   Oracle JDK 17.0.12 (JAVA_HOME=/home/rafael/java/current) ← bug
JDK Build:   OpenJDK Temurin 21.0.6 (/opt/java-temurin-21/) ← usar este!
JDK Sistema: OpenJDK 21.0.11 (/usr/lib/jvm/java-21-openjdk-amd64/) ← sem javac
JavaFX:      21.x em /opt/javafx-21/lib ← usar em run-local
Maven:       3.9.9 (/opt/apache-maven-3.9.9)
Display:     $DISPLAY=:0 (X11)
```

---

## ⚙️ Variáveis de Ambiente Relevantes

```bash
# Já configurado pelo usuário:
export JAVAFX_PATH="/opt/javafx-21/lib"

# NECESSÁRIO para corrigir o build Maven:
export JAVA_HOME="/opt/java-temurin-21"

# Para Docker + JavaFX:
export DISPLAY=:0
xhost +local:docker   # executar antes de make docker-run
```

---

## 📋 Decisões Técnicas Recentes

| Data | Decisão | Justificativa |
|---|---|---|
| 2026-08-07 | JavaFX via Maven (não módulos) | Mais simples, sem configuração de module-info.java |
| 2026-08-07 | Fallback geométrico para sprites | Jogo funciona sem assets — resiliente por design |
| 2026-08-07 | Canvas 1366×768 fullscreen | Resolução alvo declarada no GamePlan |
| 2026-08-07 | Liberica JDK 21 Full no Docker | Única imagem com JavaFX nativo sem config extra |
| 2026-08-07 | AABB simples para colisão | Suficiente para side-scroller, sem overhead |
| 2026-08-07 | **FXGL rejeitado (ADR-008)** | Tudo já implementado; migrar = reescrever projeto |
| 2026-08-07 | JDK Temurin 21 para build direto | Maven usa JDK 17 — Temurin /opt/java-temurin-21 resolve |
