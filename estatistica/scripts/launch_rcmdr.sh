#!/usr/bin/env bash
# ==============================================================================
# scripts/launch_rcmdr.sh
# Abre a interface gráfica do RCommander em background e mantém a janela aberta
# ==============================================================================

WORKDIR="$(cd "$(dirname "$0")/.." && pwd)"
export R_LIBS_USER="$HOME/R/x86_64-pc-linux-gnu-library/4.3"
mkdir -p "$R_LIBS_USER"

TMPFILE=$(mktemp /tmp/rcmdr_start_XXXXXX.R)
cat > "$TMPFILE" << RSCRIPT
options(repos = c(CRAN = "https://cloud.r-project.org"))
setwd("$WORKDIR")

options(Rcmdr = list(
  console.output = FALSE,
  log.width = 80,
  log.height = 25,
  output.height = 30,
  messages.height = 3,
  quit.R.on.close = TRUE,
  ask.to.exit = FALSE
))

suppressMessages(library(Rcmdr))

# Garantir que a janela permaneça aberta aguardando ação do usuário
if (exists("CommanderWindow", envir = Rcmdr:::RcmdrEnv())) {
  tcltk::tkwait.window(Rcmdr:::CommanderWindow())
}
RSCRIPT

export R_PROFILE_USER="$TMPFILE"
nohup R --no-save --no-restore > /tmp/rcmdr.log 2>&1 &
RPID=$!
disown "$RPID"

(sleep 5 && rm -f "$TMPFILE") &

echo "RCommander iniciado! (PID: $RPID) — terminal liberado."
