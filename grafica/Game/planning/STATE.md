# 📡 STATE — Estado Atual do Projeto

> **Este é o documento mais importante para o dia a dia.**
> Atualizado sempre que uma task muda de estado ou um bloqueio é identificado.
>
> **Última atualização:** 2026-08-07 (Sprint 4 — gameplay e pipeline 3D)
> **Responsável pela atualização:** Tech Lead / Dev ativo

---

## 🚦 Status Geral

| Aspecto | Status | Detalhe |
|---|---|---|
| **Sprint Atual** | 🟡 Sprint 4 | Polish & Assets |
| **Build (`make build-local`)** | 🟢 OK | javac JDK 21 Temurin + JAVAFX_PATH ✅ |
| **Build (`make run` via Maven)** | 🟢 OK | JAVA_HOME=JDK21 definido no Makefile ✅ |
| **MPI (`make mpi-demo`)** | 🟢 OK | 8 processos, mapa 96×16 gerado ✅ |
| **Jogo Jogável** | 🟡 COMPILADO | Progressão de mundo corrigida; aguarda validação manual com display X11 |
| **Pipeline Hunyuan3D** | 🟡 PRONTA | API local indisponível neste host; cache idempotente implementado |
| **Sprites** | 🟢 PRONTOS | 6 PNGs em `src/main/resources/` (5.3MB) |
| **Makefile** | 🟢 COMPLETO | Todos os targets funcionando |
| **Dockerfile** | 🟢 PRONTO | Multi-stage, aguarda `docker build` |
| **Git** | 🟢 INICIALIZADO | 2 commits no `main` |
| **MPI** | 🟢 TESTADO | `make mpi-demo` ✅ |

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
| APSU-044 Progressão e balanceamento | Dev JavaFX | 🟢 Corrigido; precisa playtest |
| APSU-045 Pipeline personagem 3D idempotente | Asset/DevOps | 🟡 Cliente pronto; servidor Hunyuan pendente |

### Imediato — Fix de Build Maven

| Item | Status |
|---|---|
| Corrigir JAVA_HOME para Maven usar JDK 21 | 🟡 Em avaliação |
| Testar execução: `java --module-path /opt/javafx-21/lib ...` | 🟡 Próximo passo |
| `git init && git add . && git commit` | 🟡 Próximo passo |

---

### Bloqueios Resolvidos

| Bloqueio | Resolução | Data |
|---|---|---|
| BLOCK-001: `pom.xml` não existia | Criado com JavaFX 21 + assembly plugin | 2026-08-07 |
| BLOCK-002: sprites fora de `resources/` | Copiados via script | 2026-08-07 |
| BLOCK-003: Maven usava JDK 17 | Makefile define `MVN := JAVA_HOME=$(JDK21) mvn` | 2026-08-07 |

### Bloqueios ativos

| Bloqueio | Impacto | Próxima ação |
|---|---|---|
| Hunyuan3D local não está instalado/servido em `127.0.0.1:8080` | Não gera GLB neste host ainda | Instalar/rodar uma instância compatível ou apontar `HUNYUAN3D_URL` para ela |
| GPU disponível é Intel integrada (sem CUDA) | Hunyuan3D 2.1 com textura não é viável nesta máquina | Usar servidor com GPU NVIDIA/CUDA, ou geração somente de malha em máquina externa |

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

> Sprint 4 iniciada. Execute nesta ordem:

1. **[Dev JavaFX]** `make run-local` — fazer playtest completo; agora a coleta e os portais usam coordenadas de mundo consistentes
2. **[Asset]** Para trocar Adapa: `make character-reference CHARACTER=adapa FILE=/caminho/imagem.png`
3. **[Asset/ML]** Subir a API Hunyuan3D e rodar `make character-3d CHARACTER=adapa`
4. **[Dev JavaFX]** Ajustar proporção dos sprites se necessário (ImageMagick `convert`)
4. **[Dev DevOps]** Testar `make docker-build && make docker-run`
5. **[Dev JavaFX]** Benchmark FPS com `AnimationTimer` (APSU-043)
6. **[Sprint 5]** Gerar fat JAR: `make package` e testar
7. **[Sprint 5]** README.md final com screenshots e instruções
8. **[Sprint 5]** Tag v1.0.0: `git tag -a v1.0.0 -m "Release v1.0.0"`

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
