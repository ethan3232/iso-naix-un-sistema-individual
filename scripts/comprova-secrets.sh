#!/usr/bin/env bash
# Comprueba que el commit no contiene ninguna contraseña de CREDENCIALES-PRIVADAS.md.
# Lee las contraseñas de la columna "Contraseña" del archivo privado (no las escribe en ningún sitio).
# Uso: scripts/comprova-secrets.sh   (también se ejecuta solo como hook pre-commit)
set -euo pipefail
raiz=$(git rev-parse --show-toplevel)
priv="$raiz/CREDENCIALES-PRIVADAS.md"
[ -f "$priv" ] || { echo "Aviso: no existe $priv, no se puede comprobar"; exit 0; }

# 1) El archivo privado nunca puede estar en el índice
if git diff --cached --name-only | grep -qx 'CREDENCIALES-PRIVADAS.md'; then
  echo "❌ CREDENCIALES-PRIVADAS.md está en el commit. Sácalo con: git rm --cached CREDENCIALES-PRIVADAS.md"; exit 1
fi

# 2) Ninguna contraseña puede aparecer en las líneas añadidas
mapfile -t claves < <(awk -F'|' '/^\| /{gsub(/^ +| +$/,"",$6); print $6}' "$priv" \
  | grep -vE '^(Contraseña|-+|)$' | sort -u)
# Archivos de texto: líneas añadidas. Archivos binarios: no se miran sus bytes (comprimidos, darían falsos
# positivos con contraseñas cortas), pero de los PDF se extrae el TEXTO con pdftotext y se comprueba entero.
texto=$(git diff --cached --numstat | awk '$1!="-"{print $3}')
binarios=$(git diff --cached --numstat --diff-filter=AM | awk '$1=="-"{print $3}')
anadido=$( { [ -n "$texto" ] && git diff --cached -U0 -- $texto | grep -a '^+' | grep -av '^+++'
  for b in $binarios; do case "$b" in *.pdf) git show ":$b" | pdftotext - - ;; esac; done; } 2>/dev/null || true)
for c in "${claves[@]}"; do
  if grep -aqwF -- "$c" <<<"$anadido"; then
    echo "❌ El commit contiene una contraseña de CREDENCIALES-PRIVADAS.md. Cámbiala por ******** y vuelve a intentarlo."
    exit 1
  fi
done
echo "✅ Sin contraseñas en el commit (${#claves[@]} comprobadas)."
