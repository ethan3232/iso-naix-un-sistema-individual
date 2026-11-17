#!/usr/bin/env bash
# =============================================================================
# mide-vm.sh — Tasca 7: qué recursos del PC físico consume cada VM
# Uso:  bash scripts/mide-vm.sh base <segundos>            línea base del host (sin arrancar nada)
#       bash scripts/mide-vm.sh <VM> <segundos> [etiqueta]  arranca la VM (si está apagada) y la mide
# Lee /proc (no necesita sudo ni sysstat). Muestra cada 2 s:
#   host: CPU usada %, iowait % (CPU esperando al disco), RAM disponible, swap usada
#   VM:   CPU del proceso VBoxHeadless (100 % = 1 hilo entero), RAM real (RSS), lectura/escritura de disco MB/s
# Salida: evidencies/logs/rend-<VM>[-etiqueta].csv  +  resumen en pantalla
# "Arranque calmado": primer momento en que la CPU de la VM se queda < 15 % durante 10 s seguidos.
# =============================================================================
export LC_ALL=C
VM=$1; DUR=${2:-120}; TAG=${3:+-$3}
DIR=$(cd "$(dirname "$0")/.." && pwd)/evidencies/logs; mkdir -p "$DIR"
OUT="$DIR/rend-${VM}${TAG}.csv"; HZ=$(getconf CLK_TCK); NCPU=$(nproc)

cpu_host() { awk '/^cpu /{print $2+$3+$4+$7+$8, $6, $2+$3+$4+$5+$6+$7+$8}' /proc/stat; }   # ocupado iowait total
mem_host() { awk '/MemAvailable/{a=$2} /SwapTotal/{t=$2} /SwapFree/{f=$2} END{printf "%d %d", a/1024, (t-f)/1024}' /proc/meminfo; }
vm_pid()   { local uuid; uuid=$(VBoxManage showvminfo "$VM" --machinereadable 2>/dev/null | grep -oP '^UUID="\K[^"]+')
             pgrep -f "VBoxHeadless.*($VM|$uuid)" | head -1; }
vm_stat()  { [ -n "$1" ] && [ -r /proc/$1/stat ] || { echo "0 0 0 0"; return; }
             local t r w; t=$(awk '{print $14+$15}' /proc/$1/stat); r=$(awk '/^read_bytes/{print $2}' /proc/$1/io 2>/dev/null)
             w=$(awk '/^write_bytes/{print $2}' /proc/$1/io 2>/dev/null); echo "$t $(awk '/VmRSS/{print int($2/1024)}' /proc/$1/status) ${r:-0} ${w:-0}"; }

if [ "$VM" != base ]; then
  st=$(VBoxManage showvminfo "$VM" --machinereadable | grep -oP 'VMState="\K[^"]+')
  [ "$st" = running ] || VBoxManage startvm "$VM" --type headless >/dev/null || exit 1
fi
T0=$(date +%s.%N); read hb hw ht <<<"$(cpu_host)"; pid=$(vm_pid); read vt vr vrd vwr <<<"$(vm_stat "$pid")"
echo "seg,host_cpu_pct,host_iowait_pct,host_ram_disp_mb,host_swap_mb,vm_cpu_pct,vm_rss_mb,vm_lee_mbs,vm_escribe_mbs" > "$OUT"
calma=""; calm_n=0
for ((i=0; i<DUR; i+=2)); do
  sleep 2
  read hb2 hw2 ht2 <<<"$(cpu_host)"; [ "$VM" != base ] && [ -z "$pid" ] && pid=$(vm_pid) && read vt vr vrd vwr <<<"$(vm_stat "$pid")"
  read vt2 vr2 vrd2 vwr2 <<<"$(vm_stat "$pid")"; read ma sw <<<"$(mem_host)"
  dt=$((ht2-ht)); [ $dt -eq 0 ] && dt=1
  l=$(awk -v hb=$((hb2-hb)) -v hw=$((hw2-hw)) -v dt=$dt -v vt=$((vt2-vt)) -v hz=$HZ -v rd=$((vrd2-vrd)) -v wr=$((vwr2-vwr)) \
      -v s=$((i+2)) -v ma=$ma -v sw=$sw -v rss=$vr2 \
      'BEGIN{printf "%d,%.1f,%.1f,%d,%d,%.1f,%d,%.1f,%.1f", s, hb/dt*100, hw/dt*100, ma, sw, vt/hz/2*100, rss, rd/2/1048576, wr/2/1048576}')
  echo "$l" >> "$OUT"
  vc=$(echo "$l" | cut -d, -f6)
  if [ "$VM" != base ] && [ -z "$calma" ]; then
    if awk -v c=$vc 'BEGIN{exit !(c<15)}'; then calm_n=$((calm_n+1)); [ $calm_n -ge 5 ] && calma=$((i+2-8)); else calm_n=0; fi
  fi
  hb=$hb2; hw=$hw2; ht=$ht2; vt=$vt2; vrd=$vrd2; vwr=$vwr2
done

awk -F, -v vm="$VM$TAG" -v ncpu=$NCPU -v calma="${calma:-no se calmó en ${DUR} s}" 'NR>1{
  n++; hc+=$2; if($2>hcM)hcM=$2; if($3>iwM)iwM=$3; iw+=$3; if(ramm==""||$4<ramm)ramm=$4; if($5>swM)swM=$5
  vc+=$6; if($6>vcM)vcM=$6; if($7>rssM)rssM=$7; rd+=$8*2; wr+=$9*2; if($8+$9>ioM)ioM=$8+$9 }
  END{ printf "%-24s | host CPU media %4.1f%% (máx %4.1f%%) · iowait medio %4.1f%% (máx %4.1f%%) · RAM disp. mín %5d MB · swap máx %d MB\n", vm, hc/n, hcM, iw/n, iwM, ramm, swM
       if (vm !~ /^base/) printf "%-24s | VM CPU media %5.1f%% (máx %5.1f%% = %.1f hilos de %d) · RSS máx %5d MB · disco: %6.0f MB leídos, %6.0f MB escritos (pico %.0f MB/s) · arranque calmado: %s s\n", "", vc/n, vcM, vcM/100, ncpu, rssM, rd, wr, ioM, calma }' "$OUT" | tee -a "$DIR/rend-resumen.txt"
