# 🌌 AGN N-Body Simulation — Parallel Gravitational Direct-Summation

> Simulação paralela de um **Núcleo Galático Ativo (AGN)** — um buraco negro
> supermassivo rodeado por um disco de estrelas em órbitas Keplerianas.
> Implementado em **C++17** com **Open MPI**, integrador **Leapfrog (KDK)**
> e força gravitacional com suavização (*gravitational softening*).

---

## Hardware Target

| Componente | Detalhe |
|---|---|
| CPU | Intel Core i7-8565U — 4 cores físicos / 8 threads (Whiskey Lake) |
| SIMD | AVX2 + FMA — vetorização automática do loop de forças |
| Cache L3 | 8 MB — cabe ~500k doubles (todas as posições de N=16k partículas) |
| RAM | 16 GB — suporta facilmente N=500k partículas |
| MPI ótimo | `--np 8` (um processo por thread lógica) |

---

## Física: o que está sendo simulado

```
       ★  ★   ★
    ★           ★
  ★    ●●●●●    ★        ●●● = Buraco Negro Supermassivo (BH)
    ★   ●●●   ★          ★   = Estrelas em disco Kepleriano
  ★    ●●●●●    ★
    ★           ★
       ★  ★   ★
```

- **Força gravitacional** com suavização: `F = G·m₁·m₂·Δr / (|r|² + ε²)^(3/2)`
- **Integrador Leapfrog (KDK)**: simpléctco, conserva energia a longo prazo
- **Velocidade Kepleriana inicial**: `v_k = √(G·M_BH / r)` — órbitas circulares estáveis
- **MPI**: cada processo gerencia N/P partículas; posições compartilhadas via `MPI_Allgather`

---

## Estrutura do Projeto

```
paralela/
├── CMakeLists.txt          # Build com CMake + MPI
├── Makefile                # Targets: build, run, benchmark, docker-*
├── Dockerfile              # Multi-stage: builder + runtime mínimo
├── docker-compose.yml      # Run via Docker com 1 comando
├── README.md
├── include/
│   ├── Vector3D.hpp        # Vetor 3D alinhado para AVX2 (alignas 32)
│   ├── Particle.hpp        # Corpo gravitacional + serialização MPI
│   ├── SimulationConfig.hpp # Parâmetros + parser CLI
│   ├── MPIManager.hpp      # Abstração MPI (scatter/allgather/reduce)
│   ├── ParticleSystem.hpp  # Subconjunto local de partículas por rank
│   ├── GravitySolver.hpp   # Loop O(N²/P) de forças gravitacionais
│   ├── Integrator.hpp      # Leapfrog Kick-Drift-Kick
│   ├── AGNInitializer.hpp  # Condições iniciais do AGN
│   └── StatsReporter.hpp   # Output formatado + ANSI colorido
└── src/
    ├── *.cpp               # Implementações correspondentes
    └── main.cpp            # Loop principal + orquestração MPI
```

---

## Instalação das Dependências

```bash
# Open MPI + CMake + build tools (provavelmente já instalados)
sudo apt install -y libopenmpi-dev openmpi-bin cmake build-essential
```

---

## Build e Execução (local)

```bash
# Compilar com -O3 -march=native (AVX2 automático)
make build

# Rodar com 8 processos MPI (padrão)
make run

# Customizar
make run NP=4 N=2000 STEPS=1000

# Benchmark de speedup: 1 → 2 → 4 → 8 processos
make benchmark N=500
```

---

## Docker

```bash
# Build da imagem (multi-stage, runtime mínimo)
make docker-build

# Rodar a simulação em container
make docker-run NP=8 N=1000

# Shell interativo para explorar
make docker-shell

# Via docker-compose (tudo em 1 comando)
NP=8 N=1000 STEPS=500 docker compose up --build
```

---

## Flags CLI

```
--particles  <int>    Total de partículas (padrão: 1000)
--steps      <int>    Número de passos de tempo (padrão: 500)
--dt         <float>  Tamanho do passo [unidades sim.] (padrão: 0.02)
--bh-mass    <float>  Massa do buraco negro (padrão: 50000)
--eps        <float>  Suavização gravitacional ε (padrão: 0.5)
--seed       <int>    Semente aleatória (padrão: 42)
--benchmark           Modo benchmark: saída mínima, sem CSV
--no-output           Desativa escrita de CSVs
--help                Ajuda
```

---

## Saída Esperada

```
════════════════════════════════════════════════════════════════════════════════
  🌌  AGN N-Body Simulation — Active Galactic Nucleus
       Parallel gravitational direct-summation with Leapfrog/KDK

  CPU   : Intel Core i7-8565U  (4 cores / 8 HT threads  |  AVX2 + FMA)
  MPI   : 8 processes  │  Particles: 1000  │  Steps: 500  │  dt = 0.02
════════════════════════════════════════════════════════════════════════════════
   Step  │     Time    │   Kin. Energy    │   Pot. Energy    │  Total Energy   │ Drift (%)
────────────────────────────────────────────────────────────────────────────────
      0  │   0.0000   │  4.83745e+05    │ -9.67490e+05    │ -4.83745e+05   │    0.0000
     50  │   1.0000   │  4.83902e+05    │ -9.67804e+05    │ -4.83902e+05   │    0.0033
────────────────────────────────────────────────────────────────────────────────
  ✔  Simulation complete
     Wall time   : 8.421 s
     Throughput  : 59.37 M·(part×step)/s
     MPI ranks   : 8
```

---

## Conceitos MPI Demonstrados

| Operação | Uso | Frequência |
|---|---|---|
| `MPI_Bcast` | Distribui a configuração de rank 0 → todos | 1x (init) |
| `MPI_Scatterv` | Distribui partículas de rank 0 → todos | 1x (init) |
| `MPI_Allgatherv` | Compartilha posições entre todos os ranks | **toda iteração** |
| `MPI_Reduce` | Soma energia local → rank 0 | a cada `reportInterval` |
| `MPI_Wtime` | Medição de tempo de parede | timing |

---

## Algoritmo: Leapfrog Kick-Drift-Kick

```
Início do passo t:
  particles têm: x(t), v(t), F(t)

  1. KICK½   v(t + dt/2) = v(t)        + F(t)/m × (dt/2)
  2. DRIFT   x(t + dt)   = x(t)        + v(t + dt/2) × dt
  3. COMM    MPI_Allgather(posições)
  4. FORCE   F(t + dt)   = Σ G·m·Δx/r³  (sobre todas as partículas)
  5. KICK½   v(t + dt)   = v(t + dt/2) + F(t+dt)/m × (dt/2)

Fim do passo: particles têm x(t+dt), v(t+dt), F(t+dt)
```

> O Leapfrog é **simpléctco**: o erro de energia é *bounded* (oscila),
> não cresce. Após 1000 steps, o drift deve ser < 0.1%.

---

## Referências

- **GADGET-2**: Springel V. (2005) — simulador N-body/SPH para cosmologia
- **Millennium Simulation**: 10^10 partículas DM, mesmo princípio MPI
- **Leapfrog integrador**: Hockney & Eastwood, *Computer Simulation Using Particles* (1988)
- **AGN physics**: Krolik, *Active Galactic Nuclei* (1999)
