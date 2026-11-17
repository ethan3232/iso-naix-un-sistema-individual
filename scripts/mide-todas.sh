#!/usr/bin/env bash
# mide-todas.sh — Tasca 7: línea base + cada VM sola (de una en una) con mide-vm.sh
# Uso: bash scripts/mide-todas.sh [segundos-por-vm] VM1 VM2 ...
# Apaga cada VM por ACPI antes de pasar a la siguiente. Si no se apaga en 180 s, PARA (no fuerza el apagado),
# salvo en los CLIENTES (*-CLI): la pantalla de login de GNOME ignora el ACPI y no hay nada que perder → apagado forzado a los 90 s.
# Variable BASE=no para no repetir la línea base.
D=$(cd "$(dirname "$0")" && pwd); SEG=${1:-120}; shift
LOG=$D/../evidencies/logs/rend-por-vm.txt
[ -n "$(VBoxManage list runningvms)" ] && { echo "Hay VMs encendidas: apágalas antes"; exit 1; }
[ "$BASE" != no ] && { echo "== base ($(date +%T))" | tee -a "$LOG"; bash "$D/mide-vm.sh" base 60 | tee -a "$LOG"; }
for vm in "$@"; do
  echo "== $vm ($(date +%T))" | tee -a "$LOG"
  bash "$D/mide-vm.sh" "$vm" "$SEG" solo | tee -a "$LOG"
  t0=$(date +%s); VBoxManage controlvm "$vm" acpipowerbutton
  while VBoxManage list runningvms | grep -q "\"$vm\""; do
    sleep 3
    if [[ $vm == *-CLI ]] && [ $(( $(date +%s)-t0 )) -gt 90 ]; then VBoxManage controlvm "$vm" poweroff; echo "  $vm: apagado forzado (cliente en la pantalla de login)" | tee -a "$LOG"; fi
    [ $(( $(date +%s)-t0 )) -gt 180 ] && { echo "  $vm NO se apaga por ACPI: paro" | tee -a "$LOG"; exit 1; }
  done
  echo "  $vm apagada (ACPI, $(( $(date +%s)-t0 )) s)" | tee -a "$LOG"; sleep 10
done
echo "== FIN ($(date +%T))" | tee -a "$LOG"
