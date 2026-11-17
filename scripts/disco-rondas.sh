#!/usr/bin/env bash
# disco-rondas.sh <etiqueta> — 3 rondas de fio-disco.sh en DEB13-SRV2 con 60 s de descanso entre rondas
# Uso: VMPW='…' bash scripts/disco-rondas.sh antes-sin-cache
D=$(cd "$(dirname "$0")" && pwd); OUT=$D/../evidencies/logs/optim-disco-$1.txt
r() { local h=$1; shift; echo "$VMPW" | ssh -F ~/iso-lab/ssh/config -o BatchMode=yes "$h" "sudo -S -p '' bash -c $(printf %q "$*")"; }
{ echo "### $1 · $(date '+%d/%m/%Y %H:%M') · useHostIOCache=$(grep -oP 'name="SATA"[^>]*useHostIOCache="\K[^"]+' "$(VBoxManage showvminfo DEB13-SRV2 --machinereadable | grep -oP '^CfgFile="\K[^"]+')")"
  for i in 1 2 3; do echo "-- ronda $i"; r srv2 "$(cat "$D/fio-disco.sh")"; [ $i -lt 3 ] && sleep 60; done; } | tee "$OUT"
