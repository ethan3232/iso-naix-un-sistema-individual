#!/usr/bin/env bash
# generar.sh — Regenera todos los esquemas: cada diagrames/<nombre>.py → <nombre>.svg → <nombre>.png
# Requisitos: python3 y google-chrome (se usa sin ventana para pasar el SVG a PNG a 1,5×).
set -euo pipefail
cd "$(dirname "$0")"
for py in *.py; do
  [ "$py" = estilo.py ] && continue
  python3 "$py"
  svg="${py%.py}.svg"
  W=$(grep -om1 'width="[0-9]*"' "$svg" | tr -dc 0-9); H=$(grep -om1 'height="[0-9]*"' "$svg" | tr -dc 0-9)
  google-chrome --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1.5 \
    --window-size="$W,$H" --screenshot="$PWD/${py%.py}.png" "file://$PWD/$svg" 2>/dev/null
  echo "  → ${py%.py}.png"
done
