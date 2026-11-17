#!/usr/bin/env bash
# Cambia el gateway activo de los clientes Linux de LAN23 (solo uno hace de gateway a la vez).
#   scripts/canvi-gw.sh 1   -> MikroTik  192.168.23.1 (por defecto)
#   scripts/canvi-gw.sh 2   -> OPNsense  192.168.23.2
#   scripts/canvi-gw.sh 3   -> Debian    192.168.23.3
# DNS: MikroTik y OPNsense hacen de DNS para la LAN. Debian SRV no tiene DNS,
# así que con .3 se usa un DNS público (1.1.1.1) que sale por el propio Debian.
# Vuelta atrás: scripts/canvi-gw.sh 1
set -euo pipefail
gw=${1:?Uso: $0 1|2|3}
case $gw in 1) dns=192.168.23.1;; 2) dns=192.168.23.2;; 3) dns=1.1.1.1;; *) echo "Gateway no valido"; exit 1;; esac
SSHCFG="$HOME/iso-lab/ssh/config"
PASS=$("$HOME/iso-lab/ssh/askpass.sh")
for cli in cli-info; do
  echo ">> $cli: gateway 192.168.23.$gw, DNS $dns"
  ssh -F "$SSHCFG" -o BatchMode=yes "$cli" "echo '$PASS' | sudo -S -p '' sh -c \
    'nmcli con mod LAN23 ipv4.gateway 192.168.23.$gw ipv4.dns $dns && nmcli con up LAN23 >/dev/null && ip route | head -1'"
done
