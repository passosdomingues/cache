#!/usr/bin/env bash
# ==============================================================================
# scripts/launch_rcmdr.sh
# Abre o RCommander em background — libera o terminal imediatamente
# ==============================================================================

# Diretório da workstation
WORKDIR="$(cd "$(dirname "$0")/.." && pwd)"

# Biblioteca pessoal do R (evita perguntas sobre permissão de escrita)
export R_LIBS_USER="$HOME/R/x86_64-pc-linux-gnu-library/4.3"
mkdir -p "$R_LIBS_USER"

# Script de inicialização temporário
TMPFILE=$(mktemp /tmp/rcmdr_start_XXXXXX.R)
cat > "$TMPFILE" << RSCRIPT
# Repositório fixo — nunca pede para escolher mirror
options(repos = c(CRAN = "https://cloud.r-project.org"))

# Definir pasta de trabalho como a workstation de estatística
setwd("$WORKDIR")

# Configurações da interface conforme Nota de Aula (Prof. Luiz Alberto Beijo)
options(Rcmdr = list(
  console.output = FALSE,   # Resultados na janela Output da GUI (não no terminal)
  log.width = 80,
  log.height = 25,
  output.height = 30,
  messages.height = 3,
  quit.R.on.close = TRUE,   # Ao fechar a janela do RCommander, fecha o R também
  ask.to.exit = FALSE       # Sem confirmação ao sair
))

# Carregar RCommander
suppressMessages(library(Rcmdr))
RSCRIPT

# Lançar R em modo interativo, em background total — terminal fica livre
nohup R --no-save --no-restore --profile="$TMPFILE" > /tmp/rcmdr.log 2>&1 &
RPID=$!
disown "$RPID"

# Remover script temporário após carregamento
(sleep 5 && rm -f "$TMPFILE") &

echo "RCommander iniciado! (PID: $RPID) — terminal liberado."
echo "Log em: /tmp/rcmdr.log"
