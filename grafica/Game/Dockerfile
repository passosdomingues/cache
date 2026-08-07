# ============================================================
# Dockerfile — As Águas de Apsu
# Multi-stage: build com Maven → runtime com Liberica JDK Full
# (Liberica Full inclui JavaFX nativamente — sem config extra)
# ============================================================

# ── STAGE 1: BUILD ──────────────────────────────────────────
FROM maven:3.9-eclipse-temurin-21 AS builder

LABEL stage="builder"

WORKDIR /app

# Copiar pom.xml primeiro para aproveitar cache de layers do Docker
# (dependências só são baixadas novamente se o pom.xml mudar)
COPY pom.xml .
RUN mvn dependency:go-offline -q

# Copiar código-fonte e recursos
COPY src/ ./src/

# Compilar e gerar fat JAR
RUN mvn package -q -DskipTests

# ── STAGE 2: RUNTIME ────────────────────────────────────────
# bellsoft/liberica-openjdk-debian:21-full inclui JavaFX 21 nativo
# É a escolha padrão para rodar JavaFX em container (ver ADR-006)
FROM bellsoft/liberica-openjdk-debian:21-full

LABEL maintainer="Equipe As Águas de Apsu"
LABEL version="0.2.0"
LABEL description="As Águas de Apsu — Jogo 2D JavaFX de Mitologia Mesopotâmica"

# Instalar dependências X11 para renderização gráfica
# Necessário para JavaFX via X11 socket forwarding
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libxtst6 \
        libxi6 \
        libxrandr2 \
        fonts-liberation \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar o fat JAR do stage de build
COPY --from=builder /app/target/apsu-game-*.jar ./apsu-game.jar

# Variável de ambiente para display X11
# Sobrescreva com: docker run -e DISPLAY=:0 ...
ENV DISPLAY=:0

# Porta não necessária (jogo desktop), mas documentada
# EXPOSE 8080

# Executar o jogo
# O -Dprism.order=sw força software rendering se OpenGL não disponível
ENTRYPOINT ["java", \
    "-Dprism.order=sw,es2,j2d", \
    "-Dprism.verbose=false", \
    "-jar", "apsu-game.jar"]

# ============================================================
# COMO USAR:
#
#   # Build:
#   docker build -t apsu-game .
#   # ou via Makefile:
#   make docker-build
#
#   # Run (requer X11 no host):
#   xhost +local:docker
#   docker run --rm \
#     -e DISPLAY=$DISPLAY \
#     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
#     apsu-game
#   # ou via Makefile:
#   make docker-run
# ============================================================
