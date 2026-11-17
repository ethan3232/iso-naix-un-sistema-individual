#!/usr/bin/env bash
# Utilidades para controlar VMs por consola desde el host (VBoxManage).
#   scripts/vm.sh type  <vm> "texto"     -> escribe el texto y pulsa Enter
#   scripts/vm.sh raw   <vm> "texto"     -> escribe el texto sin Enter
#   scripts/vm.sh key   <vm> enter|esc|tab|up|down|f2|y|n
#   scripts/vm.sh shot  <vm> <ruta.png>  -> captura de pantalla
set -euo pipefail
acc=$1; vm=$2; shift 2
case $acc in
  type) VBoxManage controlvm "$vm" keyboardputstring "$1"; VBoxManage controlvm "$vm" keyboardputscancode 1c 9c ;;
  raw)  VBoxManage controlvm "$vm" keyboardputstring "$1" ;;
  key)  case $1 in
          enter) c="1c 9c";; esc) c="01 81";; tab) c="0f 8f";; up) c="e0 48 e0 c8";; down) c="e0 50 e0 d0";;
          f2) c="3c bc";; y) c="15 95";; n) c="31 b1";; space) c="39 b9";; left) c="e0 4b e0 cb";; right) c="e0 4d e0 cd";;
          *) echo "tecla desconocida"; exit 1;; esac
        VBoxManage controlvm "$vm" keyboardputscancode $c ;;
  shot) mkdir -p "$(dirname "$1")"; VBoxManage controlvm "$vm" screenshotpng "$1" ;;
esac
