#!/usr/bin/env python3
"""Captura de pantalla de una VM de VirtualBox, recortada y legible.

Uso:  scripts/captura.py <vm> <ruta.png> [--escala N] [--sin-recorte] [--margen PX]

1. Hace `VBoxManage controlvm <vm> screenshotpng` (la pantalla real de la VM).
2. Recorta el fondo sobrante (el negro vacío de las consolas) dejando un margen.
   El fondo se toma del píxel de abajo a la derecha.
3. Opcional: escala ×N con vecino más próximo (consolas de texto de 720×400),
   para que se lea sin difuminar. No se altera el contenido.
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

p = argparse.ArgumentParser()
p.add_argument("vm")
p.add_argument("salida")
p.add_argument("--escala", type=int, default=1)
p.add_argument("--sin-recorte", action="store_true")
p.add_argument("--margen", type=int, default=16)
a = p.parse_args()

with tempfile.TemporaryDirectory() as tmp:
    bruto = Path(tmp) / "bruto.png"
    subprocess.run(["VBoxManage", "controlvm", a.vm, "screenshotpng", str(bruto)], check=True)
    img = Image.open(bruto).convert("RGB")

if not a.sin_recorte:
    fondo = Image.new("RGB", img.size, img.getpixel((img.width - 1, img.height - 1)))
    caja = ImageChops.difference(img, fondo).convert("L").point(lambda v: 255 if v > 24 else 0).getbbox()
    if caja:
        m = a.margen
        x0, y0, x1, y1 = caja
        img = img.crop((max(0, x0 - m), max(0, y0 - m), min(img.width, x1 + m), min(img.height, y1 + m)))

if a.escala > 1:
    img = img.resize((img.width * a.escala, img.height * a.escala), Image.NEAREST)

salida = Path(a.salida)
salida.parent.mkdir(parents=True, exist_ok=True)
img.save(salida, optimize=True)
print(f"{salida}  {img.width}x{img.height}")
