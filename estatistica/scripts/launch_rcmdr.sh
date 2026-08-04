#!/usr/bin/env bash
# ==============================================================================
# scripts/launch_rcmdr.sh
# Abre o RCommander em background — libera o terminal imediatamente
# ==============================================================================

# Mudar para a pasta da workstation
cd "$(dirname "$0")/.." || exit 1

# Criar script R temporário com as configurações
TMPFILE=$(mktemp /tmp/rcmdr_start_XXXXXX.R)
cat > "$TMPFILE" << 'EOF'
options(repos = c(CRAN = "https://cloud.r-project.org"))
options(Rcmdr = list(
  console.output = FALSE,
  log.width = 80,
  log.height = 25,
  output.height = 30,
  messages.height = 3,
  quit.R.on.close = TRUE,
  ask.to.exit = FALSE
))
library(Rcmdr)
EOF

# Abrir o R com esse script de perfil — totalmente em background, sem travar o terminal
nohup R --no-save --no-restore --profile="$TMPFILE" > /tmp/rcmdr.log 2>&1 &
disown

# Limpar
sleep 2 && rm -f "$TMPFILE" &

echo "RCommander iniciado! (PID: $!)"
