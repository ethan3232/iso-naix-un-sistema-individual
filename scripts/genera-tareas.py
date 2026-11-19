#!/usr/bin/env python3
"""Prepara la entrega de Aules tarea por tarea a partir de Proyecto-por-Tareas/.

Uso:  ~/iso-lab/pdf-venv/bin/python scripts/genera-tareas.py [Tasca-5 ...]

Para cada ficha genera en entrega/tareas/:
  <Tarea>/<Tarea>.md   el Markdown autónomo (imágenes en <Tarea>/img/, sin enlaces al resto del repo)
  <Tarea>.zip          la carpeta comprimida, lista para subir a Aules
  <Tarea>.pdf          la misma ficha en PDF (versión corta, para leerla o imprimirla)
"""
import importlib.util
import re
import shutil
import sys
import zipfile
from pathlib import Path

from pypdf import PdfReader

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("memoria", RAIZ / "scripts" / "genera-memoria.py")
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

FICHAS = RAIZ / "Proyecto-por-Tareas"
SALIDA = RAIZ / "entrega" / "tareas"

TAREAS = {  # nombre de la entrega: (ficha, color)
    "Tasca-0-entorno-de-pruebas": ("Tasca-0-entorno-de-pruebas.md", "lan"),
    "Tasca-2-equipos-y-perifericos": ("Tasca-2-equipos-y-perifericos.md", "nas"),
    "Tasca-4-diseno-fisico-y-logico": ("Tasca-4-diseno-fisico-y-logico.md", "lan"),
    "Tasca-5-instalacion-y-comunicaciones": ("Tasca-5-instalacion-y-comunicaciones.md", "com"),
    "Tasca-6-almacenamiento": ("Tasca-6-almacenamiento.md", "srv"),
    "Tasca-7-rendimiento": ("Tasca-7-rendimiento.md", "pve"),
    "Tasca-8-caso-practico": ("Tasca-8-caso-practico.md", "drbd"),
    "Transversal-predicciones-y-contingencia": ("Transversal.md", "suave"),
}

CABECERA = "**Alumno:** izan · 1.º ASIX · Puesto 23 · Red `192.168.23.0/24` · Dominio `asix23.lan` · CIP FP Batoi · Curso 2026-2027"


def quita_seccion(texto, titulo):
    return re.sub(rf"^## +{titulo}.*?(?=^## |\Z)", "", texto, flags=re.M | re.S)


def md_autonomo(nombre, ficha):
    """Devuelve el Markdown autónomo y la lista de imágenes (origen, nombre en img/)."""
    texto = ficha.read_text(encoding="utf-8")
    texto = M.limpia_emojis(texto)
    texto = quita_seccion(texto, "Evidencias")
    texto = texto.replace("## Preguntas probables de la defensa", "## Por qué lo he hecho así")
    imagenes = []

    def img(m):
        alt, ruta = m.group(1), m.group(2)
        if ruta.startswith("http"):
            return m.group(0)
        origen = (ficha.parent / ruta).resolve()
        partes = origen.parts
        destino = f"{partes[-2]}-{partes[-1]}" if "captures" in partes else partes[-1]
        imagenes.append((origen, destino))
        return f"![{alt}](img/{destino})"

    texto = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, texto)
    # Enlaces internos del repositorio → solo el texto (fuera del repo no funcionarían)
    texto = re.sub(r"(?<!!)\[([^\]]+)\]\((?!https?:)[^)\s]+\)", r"\1", texto)
    # Cabecera con los datos del alumno debajo del título
    texto = re.sub(r"^(# .+\n)", rf"\1\n{CABECERA}\n", texto, count=1)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip() + "\n"
    return texto, imagenes


CSS_CORTO = """
.ficha > h1 { font-size: 20pt; margin: 0 0 4pt; padding-bottom: 6pt; border-bottom: 4px solid var(--c); color: #0f172a; }
.ficha > p:first-of-type { color: var(--suave); font-size: 8.5pt; }
img { max-height: 95mm; }
"""


def pdf(nombre, texto_md, carpeta, color):
    texto = re.sub(r"!\[([^\]]*)\]\(img/([^)]+)\)", lambda m: f"![{m.group(1)}]({(carpeta / 'img' / m.group(2)).as_uri()})", texto_md)
    cuerpo = M.markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"])
    titulo = re.search(r"^# +(.+)$", texto_md, flags=re.M).group(1)
    doc = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>'
           f'<style>{M.CSS}{CSS_CORTO}</style></head><body>'
           f'<section class="ficha" style="--c:{M.COLOR[color]}">{cuerpo}</section></body></html>')
    original = M.IMPRIME
    M.IMPRIME = original.replace("Naix un sistema · Memoria técnica", f"Naix un sistema · {titulo.split(' · ')[0]}")
    salida = SALIDA / f"{nombre}.pdf"
    M.imprime(doc, salida)
    M.IMPRIME = original
    return len(PdfReader(str(salida)).pages)


def genera(nombre):
    ficha_nombre, color = TAREAS[nombre]
    texto, imagenes = md_autonomo(nombre, FICHAS / ficha_nombre)
    carpeta = SALIDA / nombre
    if carpeta.exists():
        shutil.rmtree(carpeta)
    (carpeta / "img").mkdir(parents=True)
    for origen, destino in imagenes:
        shutil.copy2(origen, carpeta / "img" / destino)
    (carpeta / f"{nombre}.md").write_text(texto, encoding="utf-8")

    zip_ruta = SALIDA / f"{nombre}.zip"
    with zipfile.ZipFile(zip_ruta, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(carpeta.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(SALIDA))
    paginas = pdf(nombre, texto, carpeta, color)
    print(f"{nombre}: {len(imagenes)} imágenes · PDF {paginas} páginas")


if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(TAREAS)
    SALIDA.mkdir(parents=True, exist_ok=True)
    for n in TAREAS:
        if any(n.startswith(p) for p in pedidas):
            genera(n)
