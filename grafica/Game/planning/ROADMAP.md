# 🗺️ ROADMAP — As Águas de Apsu: A Lenda dos Apkallu

> **Versão do documento:** 1.0.0
> **Última atualização:** 2026-08-07
> **Autor:** Equipe de Desenvolvimento
> **Status geral:** 🟡 IN_PROGRESS

---

## 🎯 Visão do Produto

> *"Um jogo 2D de nado livre com tema de Mitologia Mesopotâmica, onde o herói Adapa — um Apkallu (homem-peixe) — nada pelas profundezas do oceano primordial Apsu para recuperar as 3 Tabuletas da Sabedoria e derrotar o boss corrompido Kullullû."*

**Plataforma alvo:** Desktop Linux (Intel i7-8565U / 16GB RAM)
**Runtime:** Java 21 LTS + JavaFX 21
**Build:** Maven 3.9+ / Docker / GNU Make

---

## 🏁 Milestones

```
v0.1.0 ── Sprint 0 ── [✅ DONE]       Estrutura inicial + Game Plan
v0.2.0 ── Sprint 1 ── [🟡 ACTIVE]    Core Engine + Menu + Dialogue
v0.3.0 ── Sprint 2 ── [⚪ TODO]       Fases 1, 2, 3 + HUD completo
v0.4.0 ── Sprint 3 ── [⚪ TODO]       Build System (Maven+Docker+MPI)
v0.5.0 ── Sprint 4 ── [⚪ TODO]       Polish + Assets + Animações
v1.0.0 ── Sprint 5 ── [⚪ TODO]       QA + Release + Documentação final
```

---

## 📅 Fases do Projeto

### Fase 1 — Fundação (Sprints 0–1)
**Objetivo:** Ter o jogo rodando com menu e game loop funcional.

| Entregável | Status |
|---|---|
| Estrutura de pastas Maven | ✅ DONE |
| `GamePlan.md` definido | ✅ DONE |
| Sprites gerados por IA (hero, boss, npc, bg1-3) | ✅ DONE |
| `ApsuGame.java` — esqueleto da classe | 🟡 IN_PROGRESS |
| Menu com seleção de dificuldade | 🟡 IN_PROGRESS |
| Diálogo Enki funcional | 🟡 IN_PROGRESS |
| `pom.xml` configurado | 🟡 IN_PROGRESS |

---

### Fase 2 — Conteúdo (Sprint 2)
**Objetivo:** As 3 fases jogáveis com mecânicas completas.

| Entregável | Status |
|---|---|
| Fase 1 — As Águas Claras (scroll + 3 inimigos + tabuleta) | ⚪ TODO |
| Fase 2 — Cavernas de Coral (corais + easter egg + tabuleta) | ⚪ TODO |
| Fase 3 — Templo Submerso (Boss Fight Kullullû) | ⚪ TODO |
| Sistema de colisão (Bounding Box) | ⚪ TODO |
| HUD completo (vida + tabuletas + fase) | ⚪ TODO |
| Telas de Vitória e Game Over | ⚪ TODO |
| Sistema de partículas | ⚪ TODO |

---

### Fase 3 — DevOps (Sprint 3)
**Objetivo:** Automatização completa do build e deploy.

| Entregável | Status |
|---|---|
| `Makefile` com targets: build, run, docker-build, docker-run, mpi-demo | 🟡 IN_PROGRESS |
| `Dockerfile` (Liberica JDK 21 Full com JavaFX) | 🟡 IN_PROGRESS |
| `.gitignore` completo | 🟡 IN_PROGRESS |
| Suporte a JavaFX local (`/opt/javafx-21/lib`) | ⚪ TODO |
| Demo MPI com 8 cores (i7-8565U) | ⚪ TODO |
| CI/CD básico via script | ⚪ TODO |

---

### Fase 4 — Polish & Performance (Sprint 4)
**Objetivo:** Jogo visualmente impressionante e performático.

| Entregável | Status |
|---|---|
| Sprites PNG integrados ao classpath Maven | ⚪ TODO |
| Animações de sprite sheet (swimming cycle) | ⚪ TODO |
| Sistema de câmera paralax (múltiplas camadas) | ⚪ TODO |
| Efeitos sonoros (JavaFX AudioClip) | ⚪ TODO |
| Benchmark 60 FPS estável | ⚪ TODO |
| Profiling com VisualVM | ⚪ TODO |

---

### Fase 5 — Release (Sprint 5)
**Objetivo:** Produto finalizável e documentado.

| Entregável | Status |
|---|---|
| Testes de regressão manual | ⚪ TODO |
| Fat JAR executável (`mvn package`) | ⚪ TODO |
| README completo com instruções de instalação | ⚪ TODO |
| Avaliação de viabilidade Hunyuan3D local | ⚪ TODO |
| Tag v1.0.0 no Git | ⚪ TODO |

---

## 🔮 Futuro / Backlog (pós v1.0.0)

> Ideias aprovadas para versões futuras. **Não implementar antes da v1.0.0.**

- [ ] **v1.1.0** — Sistema de save/load com serialização JSON
- [ ] **v1.2.0** — Fase bônus: O Abismo de Nammu (boss alternativo)
- [ ] **v1.3.0** — Multiplayer local (2 Apkallus)
- [ ] **v1.4.0** — Editor de fases com JavaFX Scene Builder
- [ ] **v2.0.0** — Port para LibGDX para mobile (Android)

---

## ⚠️ Riscos e Dependências

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| JavaFX incompatível com Docker headless | Média | Alto | Usar Xvfb ou VNC no container |
| Performance < 60 FPS em cenas densas | Baixa | Médio | Profiling com AnimationTimer + Canvas clipping |
| MPI não instalado localmente | Baixa | Baixo | Incluir instalação no Makefile (apt-get) |
| Hunyuan3D não roda na GPU AMD | Alta | Baixo | CPU-only mode ou Cloud API |

---

## 👥 Time (Roles)

| Role | Responsabilidade |
|---|---|
| **Tech Lead / Sênior** | Arquitetura, revisão de código, decisões técnicas |
| **Dev JavaFX** | `ApsuGame.java`, game loop, rendering |
| **Dev DevOps** | Makefile, Dockerfile, MPI, CI |
| **Game Designer** | Balanceamento de dificuldade, mecânicas |
| **Asset Designer** | Sprites, backgrounds, animações |
