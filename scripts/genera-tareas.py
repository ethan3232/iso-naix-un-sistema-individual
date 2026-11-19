#!/usr/bin/env python3
"""Prepara la entrega de Aules tarea por tarea a partir de Proyecto-por-Tareas/.

Uso:  ~/iso-lab/pdf-venv/bin/python scripts/genera-tareas.py [Tasca-5 ...]

Para cada ficha genera en entrega/tareas/:
  <Tarea>.md    Markdown de una sola pieza: las imágenes y los enlaces apuntan al repositorio de GitHub
  <Tarea>.pdf   la misma ficha en PDF, con las imágenes incrustadas y el enlace al repositorio
"""
import importlib.util
import re
import sys
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

REPO = "https://github.com/ethan3232/iso-naix-un-sistema-individual"
CABECERA = ("**Alumno:** izan · 1.º ASIX · Puesto 23 · Red `192.168.23.0/24` · Dominio `asix23.lan` · CIP FP Batoi · Curso 2026-2027\n\n"
            "**Repositorio del proyecto:** [{repo}]({repo}) · **Esta tarea en GitHub:** [{url}]({url})")


def quita_seccion(texto, titulo):
    return re.sub(rf"^## +{titulo}.*?(?=^## |\Z)", "", texto, flags=re.M | re.S)


def a_github(ficha, ruta, crudo=False):
    """Convierte una ruta relativa del repositorio en su URL de GitHub."""
    ruta, _, ancla = ruta.partition("#")
    destino = (ficha.parent / ruta).resolve().relative_to(RAIZ).as_posix()
    tipo = "raw" if crudo else ("tree" if (RAIZ / destino).is_dir() else "blob")
    return f"{REPO}/{tipo}/main/{destino}" + (f"#{ancla}" if ancla else "")


def md_autonomo(nombre, ficha):
    """Markdown de una sola pieza: imágenes y enlaces apuntan al repositorio de GitHub.
    Devuelve también la lista de imágenes locales (para el PDF)."""
    texto = ficha.read_text(encoding="utf-8")
    texto = M.limpia_emojis(texto)
    texto = quita_seccion(texto, "Evidencias")
    texto = texto.replace("## Preguntas probables de la defensa", "## Por qué lo he hecho así")
    locales = {}

    def img(m):
        alt, ruta = m.group(1), m.group(2)
        if ruta.startswith("http"):
            return m.group(0)
        url = a_github(ficha, ruta, crudo=True)
        locales[url] = (ficha.parent / ruta).resolve()
        return f"![{alt}]({url})"

    texto = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, texto)
    texto = re.sub(r"(?<!!)\[([^\]]+)\]\((?!https?:|#)([^)\s]+)\)",
                   lambda m: f"[{m.group(1)}]({a_github(ficha, m.group(2))})", texto)
    url = f"{REPO}/blob/main/Proyecto-por-Tareas/{ficha.name}"
    texto = re.sub(r"^(# .+\n)", lambda m: f"{m.group(1)}\n{CABECERA.format(repo=REPO, url=url)}\n", texto, count=1)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip() + "\n"
    texto += (f"\n---\n\n**Documentación completa, capturas, salidas de los comandos, configuraciones y scripts:** "
              f"[{REPO}]({REPO})\n")
    return texto, locales


CSS_CORTO = """
.ficha > h1 { font-size: 20pt; margin: 0 0 4pt; padding-bottom: 6pt; border-bottom: 4px solid var(--c); color: #0f172a; }
.ficha > h1 + p, .ficha > h1 + p + p { color: var(--suave); font-size: 8.5pt; margin: 2pt 0; word-break: break-all; }
img { max-height: 95mm; }
"""


def pdf(nombre, texto_md, locales, color):
    texto = texto_md
    for url, ruta in locales.items():  # en el PDF las imágenes van incrustadas desde el disco
        texto = texto.replace(f"]({url})", f"]({ruta.as_uri()})")
    cuerpo = M.markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"])
    titulo = re.search(r"^# +(.+)$", texto_md, flags=re.M).group(1)
    doc = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>'
           f'<style>{M.CSS}{CSS_CORTO}</style></head><body>'
           f'<section class="ficha" style="--c:{M.COLOR[color]}">{cuerpo}</section></body></html>')
    original = M.IMPRIME
    M.IMPRIME = original.replace("Naix un sistema · Memoria técnica · izan · 1.º ASIX",
                                 f"{titulo.split(' · ')[0]} · izan · github.com/ethan3232/iso-naix-un-sistema-individual")
    salida = SALIDA / f"{nombre}.pdf"
    M.imprime(doc, salida)
    M.IMPRIME = original
    return len(PdfReader(str(salida)).pages)


def genera(nombre):
    ficha_nombre, color = TAREAS[nombre]
    texto, locales = md_autonomo(nombre, FICHAS / ficha_nombre)
    (SALIDA / f"{nombre}.md").write_text(texto, encoding="utf-8")
    paginas = pdf(nombre, texto, locales, color)
    print(f"{nombre}: {len(locales)} imágenes · PDF {paginas} páginas")


if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(TAREAS)
    SALIDA.mkdir(parents=True, exist_ok=True)
    for n in TAREAS:
        if any(n.startswith(p) for p in pedidas):
            genera(n)
