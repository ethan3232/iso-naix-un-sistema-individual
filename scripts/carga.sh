#!/usr/bin/env bash
# =============================================================================
# carga.sh — Tasca 7: qué VM satura qué recurso del PC físico
# Requisitos: Mikrotik-IND + DEB13-SRV2 + DEB13-SRV3 encendidas, con iperf3 y stress-ng.
# Uso:  VMPW='contraseña-de-izan' bash scripts/carga.sh          (la contraseña NO se guarda)
# Cada prueba: 60 s de medida en el host (mide-vm.sh) con 50 s de carga dentro de la VM.
# =============================================================================
D=$(cd "$(dirname "$0")" && pwd); LOG=$D/../evidencies/logs/rend-carga.txt
r() { local h=$1; shift; echo "$VMPW" | ssh -F ~/iso-lab/ssh/config -o BatchMode=yes "$h" "sudo -S -p '' bash -c $(printf %q "$*")"; }
prueba() {   # prueba <etiqueta> <VM medida> <host ssh> <comando de carga>
  echo "== $1 ($(date +%T)) · carga en $3: $4" | tee -a "$LOG"
  ( sleep 4; r "$3" "$4" >/dev/null 2>&1 ) &
  bash "$D/mide-vm.sh" "$2" 60 "$1" | tee -a "$LOG"; wait; sleep 10
}
echo "### $(date '+%d/%m/%Y') — escenario: Mikrotik-IND + DEB13-SRV2 + DEB13-SRV3" | tee -a "$LOG"
r srv3 'pkill iperf3; iperf3 -s -D'
prueba reposo     DEB13-SRV2 srv2 'true'
prueba carga-cpu  DEB13-SRV3 srv3 'stress-ng --cpu 1 --cpu-method int64 --timeout 50s'
prueba carga-ram  DEB13-SRV2 srv2 'stress-ng --vm 1 --vm-bytes 700M --vm-keep --vm-method write64 --timeout 50s'
# Disco con fio y datos ALEATORIOS: con dd if=/dev/zero VirtualBox no escribe los bloques de ceros en el VDI y da cifras falsas (2,4 GB/s)
FIO='fio --name=sec --filename=/var/tmp/carga --size=2G --rw=write --bs=1M --direct=1 --runtime=45 --time_based --output-format=terse --terse-version=3 | cut -d";" -f48 > /var/tmp/fio.txt; rm -f /var/tmp/carga'
prueba carga-disco DEB13-SRV2 srv2 "$FIO"
echo "   fio escritura secuencial dentro de SRV2: $(( $(r srv2 'cat /var/tmp/fio.txt') / 1024 )) MB/s" | tee -a "$LOG"
prueba carga-red  DEB13-SRV2 srv2 'iperf3 -c 192.168.23.22 -t 45 > /var/tmp/iperf.txt'
echo "   iperf3 SRV2→SRV3: $(r srv2 'grep -E "receiver" /var/tmp/iperf.txt')" | tee -a "$LOG"
prueba carga-todo DEB13-SRV2 srv2 'stress-ng --cpu 1 --cpu-method int64 --vm 1 --vm-bytes 500M --vm-method write64 --timeout 50s & fio --name=t --filename=/var/tmp/c --size=1G --rw=write --bs=1M --direct=1 >/dev/null; rm -f /var/tmp/c; iperf3 -c 192.168.23.22 -t 20 >/dev/null; wait'
r srv3 'pkill iperf3'
