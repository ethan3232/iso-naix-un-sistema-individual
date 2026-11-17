#!/usr/bin/env bash
# red-iperf.sh <etiqueta> — 3 rondas de iperf3 (20 s) DEB13-SRV2 → DEB13-SRV3 midiendo la CPU del host a la vez
# Uso: VMPW='…' bash scripts/red-iperf.sh antes-e1000
D=$(cd "$(dirname "$0")" && pwd); OUT=$D/../evidencies/logs/optim-red-$1.txt
r() { local h=$1; shift; echo "$VMPW" | ssh -F ~/iso-lab/ssh/config -o BatchMode=yes "$h" "sudo -S -p '' bash -c $(printf %q "$*")"; }
cpu() { awk '/^cpu /{print $2+$3+$4+$7+$8, $2+$3+$4+$5+$6+$7+$8}' /proc/stat; }
r srv3 'pkill iperf3; iperf3 -s -D'; sleep 2
{ echo "### $1 · $(date '+%d/%m/%Y %H:%M') · NIC: $(VBoxManage showvminfo DEB13-SRV2 --machinereadable | grep -oP '^nictype1="\K[^"]+')"
  for i in 1 2 3; do
    read b1 t1 <<<"$(cpu)"
    g=$(r srv2 'iperf3 -c 192.168.23.22 -t 20 -f g | grep receiver' | awk '{print $7}')
    read b2 t2 <<<"$(cpu)"
    awk -v i=$i -v g=$g -v c=$(( (b2-b1)*1000/(t2-t1) )) 'BEGIN{printf "ronda %d: %s Gbit/s · CPU del host %.1f %% · %.1f %% de CPU por cada Gbit/s\n", i, g, c/10, (c/10)/g}'
    sleep 5
  done; } | tee "$OUT"
r srv3 'pkill iperf3'
