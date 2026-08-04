#!/usr/bin/env bash
# ==============================================================================
# scripts/launch_rcmdr.sh
# Lança a interface gráfica do RCommander em background mantendo a sessão viva
# ==============================================================================

WORKDIR="/home/rafael/github/cache/estatistica"
export R_LIBS_USER="$HOME/R/x86_64-pc-linux-gnu-library/4.3"
mkdir -p "$R_LIBS_USER"

cd "$WORKDIR" || exit 1

# Lança a sessão R interativa em um processo desacoplado em background
x-terminal-emulator -title "RCommander" -e bash -c "R_PROFILE_USER=$WORKDIR/scripts/start_gui.R R --no-save" >/dev/null 2>&1 &

echo "RCommander iniciado! — terminal liberado."
