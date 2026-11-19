#!/usr/bin/env python3
"""Comprueba los enlaces de los .md del repositorio.
- Enlaces e imágenes relativos que apuntan a archivos que no existen.
- Capturas de evidencies/captures/ que no están enlazadas en ningún .md.
Uso: scripts/comprova-enllacos.py   (sale con código 1 si hay enlaces rotos)
"""
import re, sys
from pathlib import Path
from urllib.parse import unquote

raiz = Path(__file__).resolve().parent.parent
mds = [p for p in raiz.rglob('*.md') if '.git' not in p.parts and 'build' not in p.parts and 'CREDENCIALES' not in p.name]
patron = re.compile(r'!?\[[^\]]*\]\(([^)\s]+)')
rotos, usadas = [], set()
for md in mds:
    texto = re.sub(r'```.*?```', '', md.read_text(), flags=re.S)
    for destino in patron.findall(texto):
        if re.match(r'^(https?:|mailto:|#)', destino):
            continue
        ruta = (md.parent / unquote(destino.split('#')[0])).resolve()
        usadas.add(ruta)
        if not ruta.exists():
            rotos.append(f'{md.relative_to(raiz)} -> {destino}')
sin_usar = [p.relative_to(raiz) for p in sorted((raiz / 'evidencies/captures').rglob('*.png')) if p.resolve() not in usadas]
print(f'Enlaces rotos: {len(rotos)}'); print(*rotos, sep='\n') if rotos else None
print(f'Capturas sin enlazar: {len(sin_usar)}'); print(*sin_usar, sep='\n') if sin_usar else None
sys.exit(1 if rotos else 0)
