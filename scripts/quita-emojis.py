#!/usr/bin/env python3
"""Quita los emojis de la documentación (estilo formal) conservando el significado.
✅ → ✓, ❌ → ✗, ⚠️ → «Atención:», 🧪 → «simulado», flechas de subida/bajada → texto.
Uso: scripts/quita-emojis.py <archivo.md> ...   (modifica los archivos)
"""
import re, sys
CAMBIOS = [
    ("⬆️⬆️ N discos en paralelo", "Muy alta: N discos en paralelo"), ("| ⬆️⬆️ |", "| Muy alta |"),
    ("⬆️ puede leer de los dos", "Mejor: puede leer de los dos"), ("⬆️ de N discos", "Mejor: lee de N discos"),
    ("⬇️ *penalización", "Peor: *penalización"),
    ("¿Probado o 🧪 simulado?", "¿Probado o simulado?"), ("🧪 Simulado", "Simulado"), ("🧪 Solo diseño", "Solo diseño"),
    ("🧪 Diseño:", "Diseño:"), ("🧪 diseño", "solo diseño"), ("(🧪)", "(simulado)"), (" 🧪 |", " (*) |"), ("> 🧪 ", "> (*) "),
    ("· 🧪", "· simulado"), ("🧪 ", ""),
    ("⚠️ ", "Atención: "), ("⚠ ", "Atención: "), ("✍️ ", ""), ("👉 ", ""), ("➕ ", ""), ("| ➖ grupo |", "| De grupo |"),
    ("✅", "✓"), ("❌", "✗"), ("🟡 en curso", "en curso"), ("⬜ pendiente", "pendiente"), ("🚫 ", ""),
]
resto = re.compile('[\U0001F000-\U0001FAFF☀-⛿⬀-⯿️]\\s?')
for ruta in sys.argv[1:]:
    texto = open(ruta, encoding='utf-8').read()
    nuevo = texto
    for a, b in CAMBIOS:
        nuevo = nuevo.replace(a, b)
    nuevo = resto.sub('', nuevo)
    if nuevo != texto:
        open(ruta, 'w', encoding='utf-8').write(nuevo)
        print('modificado:', ruta)
