#!/usr/bin/env bash
# ==============================================================================
# scripts/launch_rcmdr.sh
# Lança o RCommander em background — libera o terminal instantaneamente
# ==============================================================================

WORKDIR="/home/rafael/github/cache/estatistica"
export R_LIBS_USER="$HOME/R/x86_64-pc-linux-gnu-library/4.3"
mkdir -p "$R_LIBS_USER"

cd "$WORKDIR" || exit 1

R_PROFILE_USER="$WORKDIR/scripts/start_gui.R" nohup R --interactive > /tmp/rcmdr.log 2>&1 &
RPID=$!
disown "$RPID" 2>/dev/null || true

echo "RCommander iniciado! (PID: $RPID) — terminal liberado."
