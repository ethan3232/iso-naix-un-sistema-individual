#!/usr/bin/env bash
# Muestra comandos y su salida real en una CONSOLA de texto de una VM Linux, con letra grande,
# para capturarla después con scripts/captura.py. Se lanza por SSH (evita el teclado de la VM).
#   [TTY=tty3] scripts/muestra-tty.sh <host-ssh> "comando 1" ["comando 2" ...]
# Por defecto usa tty3, porque en algunas VMs tty1 es el escritorio gráfico.
set -euo pipefail
host=$1; shift
TTY=${TTY:-tty3}
PASS=$("$HOME/iso-lab/ssh/askpass.sh")
guion="T=/dev/$TTY; chvt ${TTY#tty}"'
export TERM=linux
setterm --blank poke > $T 2>/dev/null
setfont -C $T Lat15-TerminusBold24x12 2>/dev/null || true
clear > $T
P="$(id -un)@$(hostname):~# "'
for c in "$@"; do
  q=$(printf '%q' "$c")
  guion+="
printf '\033[1;32m%s\033[0m%s\n' \"\$P\" $q > \$T; sh -c $q > \$T 2>&1"
done
echo "$PASS" | ssh -F "$HOME/iso-lab/ssh/config" "$host" "sudo -S -p '' bash -c $(printf '%q' "$guion")"
