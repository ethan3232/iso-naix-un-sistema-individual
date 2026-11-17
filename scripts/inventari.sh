#!/usr/bin/env bash
# =============================================================================
# inventari.sh — Inventario y diagnóstico del equipo (Tasca 2)
# Uso:   bash scripts/inventari.sh [nombre-equipo]            (sin sudo: casi todo)
#        sudo bash scripts/inventari.sh [nombre-equipo]       (añade SMART, dmidecode)
# Salida: evidencies/logs/inventari-<nombre>.txt
# Pensado para Linux (Mint/Ubuntu/Debian). En el PC de casa: copiar el repo y ejecutarlo igual.
# =============================================================================
NOM=${1:-$(hostname)}
DIR=$(cd "$(dirname "$0")/.." && pwd)/evidencies/logs
OUT="$DIR/inventari-$NOM.txt"; mkdir -p "$DIR"
s() { echo; echo "=================================================================="; echo "## $*"; echo "=================================================================="; }
c() { echo; echo "\$ $*"; bash -c "$*" 2>&1; }
TMP=$(mktemp -d)

{
echo "# INVENTARIO DEL EQUIPO: $NOM — $(date '+%d/%m/%Y %H:%M') — usuario $(id -un)$( [ $EUID -eq 0 ] && echo ' (root)')"

s "1. Sistema y firmware"
c "hostnamectl 2>/dev/null | grep -vE 'Machine ID|Boot ID'"
c "cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/product_name /sys/class/dmi/id/board_name /sys/class/dmi/id/bios_vendor /sys/class/dmi/id/bios_version /sys/class/dmi/id/bios_date 2>/dev/null | paste -sd' | '"
c "[ -d /sys/firmware/efi ] && echo 'Arranque: UEFI' || echo 'Arranque: BIOS (Legacy)'"
c "mokutil --sb-state 2>/dev/null || echo 'Secure Boot: N/C (mokutil no disponible)'"
[ $EUID -eq 0 ] && c "dmidecode -t system -t bios -t baseboard | grep -E 'Manufacturer|Product|Version|Release Date|Serial' | grep -v 'Not Specified'"

s "2. CPU y virtualización"
c "lscpu | grep -E 'Nombre del modelo|Model name|^CPU\(s\)|Núcleo|Core|Hilo|Thread|Socket|MHz máx|max MHz|Virtualiz|L2|L3'"
c "echo \"Flags de virtualización (vmx=Intel VT-x, svm=AMD-V): \$(grep -oE 'vmx|svm' /proc/cpuinfo | sort -u | tr '\n' ' ')\""
c "ls -l /dev/kvm 2>&1 | head -1"

s "3. Memoria RAM"
c "free -h"
c "grep -E 'MemTotal|SwapTotal' /proc/meminfo"
c "swapon --show"
[ $EUID -eq 0 ] && c "dmidecode -t memory | grep -E 'Size:|Type:|Speed:|Locator:|Maximum Capacity|Number Of Devices' | grep -v 'No Module'"

s "4. Discos y almacenamiento"
c "lsblk -o NAME,SIZE,TYPE,ROTA,TRAN,MODEL,FSTYPE,MOUNTPOINT"
c "df -h -x tmpfs -x devtmpfs -x squashfs -x efivarfs"
for d in /sys/block/sd* /sys/block/nvme*n*; do [ -e "$d" ] && echo "$(basename $d): rotacional=$(cat $d/queue/rotational) scheduler=$(cat $d/queue/scheduler 2>/dev/null)"; done
if [ $EUID -eq 0 ] && command -v smartctl >/dev/null; then
  for d in $(lsblk -dno NAME | grep -vE 'loop|zram|sr'); do c "smartctl -H -A /dev/$d | grep -E 'overall-health|SMART Health|Power_On_Hours|Reallocated|Wear_Leveling|Percentage Used|Temperature|Media_Wearout|Data Units Written'"; done
else echo; echo "(SMART: ejecutar con sudo y con smartmontools instalado)"; fi

s "5. Red"
c "ip -br link"; c "ip -br addr"; c "ip route"
for i in $(ls /sys/class/net | grep -vE 'lo|docker|vbox|virbr|veth'); do echo "$i: velocidad=$(cat /sys/class/net/$i/speed 2>/dev/null || echo N/C) Mb/s, MAC=$(cat /sys/class/net/$i/address)"; done
c "lspci | grep -iE 'ethernet|network|wireless'"

s "6. Gráfica, USB y otros periféricos"
c "lspci | grep -iE 'vga|3d|display|audio'"
c "lsusb 2>/dev/null | grep -viE 'root hub'"
c "cat /sys/class/power_supply/BAT*/capacity /sys/class/power_supply/BAT*/status 2>/dev/null | paste -sd' ' | sed 's/^/Batería: /' || echo 'Sin batería'"
c "cat /sys/class/power_supply/BAT*/energy_full_design /sys/class/power_supply/BAT*/energy_full 2>/dev/null | paste -sd' ' | awk '{if(\$1) printf \"Salud de la batería: %.0f%% de la capacidad original\n\", \$2/\$1*100}'"

s "7. Sensores y temperaturas"
c "for z in /sys/class/thermal/thermal_zone*; do echo \"\$(cat \$z/type): \$((\$(cat \$z/temp)/1000)) ºC\"; done 2>/dev/null | head -8"

s "8. Software de virtualización"
c "VBoxManage --version 2>/dev/null || echo 'VirtualBox no instalado'"
c "lsmod | grep -E '^(kvm|vbox)' | awk '{print \$1}' | paste -sd' '"

s "9. DIAGNÓSTICO — Disco (escritura y lectura secuencial, 1 GiB, sin caché)"
echo "Herramienta: dd con oflag=direct / iflag=direct · Fichero de prueba en \$HOME · Condiciones: equipo en reposo"
c "dd if=/dev/zero of=$HOME/.prueba-disco bs=1M count=1024 oflag=direct status=none conv=fdatasync; echo escritura: hecho" >/dev/null
W=$( { /usr/bin/time -f '%e' dd if=/dev/zero of=$HOME/.prueba-disco bs=1M count=1024 oflag=direct status=none conv=fdatasync; } 2>&1 | tail -1)
R=$( { /usr/bin/time -f '%e' dd if=$HOME/.prueba-disco of=/dev/null bs=1M iflag=direct status=none; } 2>&1 | tail -1)
rm -f $HOME/.prueba-disco
echo "Escritura secuencial: $(awk -v t=$W 'BEGIN{printf "%.0f MB/s (%.1f s)", 1024/t, t}')"
echo "Lectura secuencial:   $(awk -v t=$R 'BEGIN{printf "%.0f MB/s (%.1f s)", 1024/t, t}')"
echo "Escritura aleatoria 4K (2000 bloques, sync):"
T4=$( { /usr/bin/time -f '%e' dd if=/dev/zero of=$HOME/.prueba-4k bs=4k count=2000 oflag=direct,dsync status=none; } 2>&1 | tail -1); rm -f $HOME/.prueba-4k
echo "  $(awk -v t=$T4 'BEGIN{printf "%.0f IOPS (%.1f s)", 2000/t, t}')"

s "10. DIAGNÓSTICO — Memoria (ancho de banda y prueba de patrón)"
echo "Herramienta: python3 (copia de 512 MiB en memoria) · sin sudo. Para un test completo: memtest86+ desde GRUB."
c "python3 -c '
import time
n=512*1024*1024; a=bytearray(b\"\\x55\")*n
t=time.time(); b=bytes(a); d=time.time()-t
print(f\"Copia de 512 MiB: {d:.2f} s -> {n/d/1e9:.1f} GB/s\")
ok = b.count(b\"\\x55\")==n
print(\"Patrón 0x55 verificado sin errores\" if ok else \"ERROR: el patrón no coincide\")'"
command -v memtester >/dev/null && [ $EUID -eq 0 ] && c "memtester 256M 1 | tail -12"

s "11. DIAGNÓSTICO — Red"
echo "Herramientas: ping (latencia/pérdida al gateway y a Internet), curl (velocidad de descarga)"
GW=$(ip route | awk '/default/{print $3; exit}')
c "ping -c 10 -i 0.2 $GW | tail -2"
c "ping -c 5 1.1.1.1 | tail -2"
c "curl -s -o /dev/null -m 30 -w 'Descarga de 10 MB: %{speed_download} B/s (%{time_total} s)\n' http://speedtest.tele2.net/10MB.zip | awk '{printf \"%s %s %s %s %.1f MB/s %s %s\n\",\$1,\$2,\$3,\$4,\$5/1048576,\$7,\$8}'"
c "ip -s link show $(ip route | awk '/default/{print $5; exit}') | sed -n '3,6p'"
echo; echo "# FIN DEL INVENTARIO"
} > "$OUT" 2>&1
rm -rf "$TMP"
echo "Inventario guardado en: $OUT"
