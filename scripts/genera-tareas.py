#!/usr/bin/env python3
"""Genera un PDF por tarea para subirlo a Aules (entrega tarea por tarea).

Uso:  ~/iso-lab/pdf-venv/bin/python scripts/genera-tareas.py [Tasca-5 ...]
Salida: entrega/tareas/<Tarea>.pdf

Cada PDF es autónomo: portada de la tarea, índice, la ficha de Proyecto-por-Tareas/
(enunciado, trabajo, resultados, comprobación) y después los capítulos completos de docs/
con todas sus capturas. Reutiliza el estilo y la impresión de genera-memoria.py.
"""
import html
import importlib.util
import re
import sys
from datetime import date
from pathlib import Path

from pypdf import PdfReader

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("memoria", RAIZ / "scripts" / "genera-memoria.py")
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

FICHAS = RAIZ / "Proyecto-por-Tareas"
SALIDA = RAIZ / "entrega" / "tareas"

# nombre del PDF: (ficha, color, [(capítulo de docs, color), ...], incluir preguntas de defensa)
TAREAS = {
    "Tasca-0-entorno-de-pruebas": ("Tasca-0-entorno-de-pruebas.md", "lan", [
        ("docs/01-requisits.md", "cli"),
        ("docs/04-disseny.md", "lan"),
        ("docs/05-recursos.md", "pve"),
        ("docs/10-incidencies.md", "com"),
    ], False),
    "Tasca-2-equipos-y-perifericos": ("Tasca-2-equipos-y-perifericos.md", "nas", [
        ("docs/02-inventari.md", "nas"),
    ], False),
    "Tasca-4-diseno-fisico-y-logico": ("Tasca-4-diseno-fisico-y-logico.md", "lan", [
        ("docs/04-disseny.md", "lan"),
        ("docs/05-recursos.md", "pve"),
    ], False),
    "Tasca-5-instalacion-y-comunicaciones": ("Tasca-5-instalacion-y-comunicaciones.md", "com", [
        ("docs/03-sistemes.md", "cli"),
        ("docs/06-installacio/README.md", "com"),
        ("docs/06-installacio/mikrotik.md", "com"),
        ("docs/06-installacio/opnsense.md", "com"),
        ("docs/06-installacio/debian-srv.md", "com"),
        ("docs/06-installacio/truenas.md", "nas"),
        ("docs/06-installacio/proxmox.md", "pve"),
        ("docs/06-installacio/windows-server.md", "cli"),
        ("docs/06-installacio/debian-servidors.md", "srv"),
        ("docs/06-installacio/clients.md", "cli"),
        ("docs/10-incidencies.md", "com"),
    ], False),
    "Tasca-6-almacenamiento": ("Tasca-6-almacenamiento.md", "srv", [
        ("docs/07-emmagatzematge-raid.md", "srv"),
    ], False),
    "Tasca-7-rendimiento": ("Tasca-7-rendimiento.md", "pve", [
        ("docs/08-rendiment.md", "pve"),
    ], False),
    "Tasca-8-caso-practico": ("Tasca-8-caso-practico.md", "drbd", [
        ("docs/09-contingencia.md", "drbd"),
        ("docs/11-defensa.md", "suave"),
        ("docs/10-incidencies.md", "com"),
    ], True),
    "Transversal-predicciones-y-contingencia": ("Transversal.md", "suave", [
        ("docs/00-prediccions.md", "suave"),
        ("docs/09-contingencia.md", "drbd"),
    ], False),
}


# Salidas reales de los comandos que se adjuntan como anexo (evidencies/logs/)
ANEXOS = {
    "Tasca-0-entorno-de-pruebas": ["rend-capacidad.txt"],
    "Tasca-2-equipos-y-perifericos": ["inventari-clase.txt", "inventari-casa.txt"],
    "Tasca-4-diseno-fisico-y-logico": ["prueba-gw-mikrotik.txt", "prueba-gw-opnsense.txt", "prueba-gw-debian.txt"],
    "Tasca-5-instalacion-y-comunicaciones": [
        "sha256-isos.txt", "fallo-recuperacion-mikrotik.txt", "fallo-recuperacion-opnsense.txt",
        "fallo-recuperacion-debian-srv.txt", "truenas-estado.txt", "proxmox-cluster.txt", "proxmox-migraciones.txt",
        "proxmox-copias-nas.txt", "ws2025-dc-dominio.txt", "w11-cli-dominio.txt"],
    "Tasca-6-almacenamiento": ["raid-creacion.txt", "raid-fallos.txt", "raid-rendimiento-fio.txt", "drbd-espejo-red.txt"],
    "Tasca-7-rendimiento": ["rend-resumen.txt", "rend-por-vm.txt", "rend-carga.txt", "rend-capacidad.txt",
                            "optim-disco-antes-sin-cache.txt", "optim-disco-despues-con-cache.txt",
                            "optim-red-config-antes.txt", "optim-red-antes-e1000.txt", "optim-red-despues-virtio.txt"],
    "Tasca-8-caso-practico": ["fallo-recuperacion-mikrotik.txt", "fallo-recuperacion-opnsense.txt",
                              "fallo-recuperacion-debian-srv.txt"],
}

CSS_ANEXO = ".anexo pre { font-size: 6.6pt; line-height: 1.32; break-inside: auto; } .anexo h2 { font-size: 11pt; }"


def anexo(i, nombre, color):
    partes = []
    for log in ANEXOS.get(nombre, []):
        txt = (RAIZ / "evidencies" / "logs" / log).read_text(encoding="utf-8", errors="replace")
        partes.append(f'<h2><code>evidencies/logs/{log}</code></h2><pre>{html.escape(txt)}</pre>')
    if not partes:
        return None
    intro = ("<p>Salidas reales de los comandos, tal como se guardaron durante las pruebas "
             "(las contraseñas no aparecen: se escriben como <code>********</code>).</p>")
    return ("Anexo: salidas de los comandos", color,
            f'<section class="capitulo anexo" style="--c:{M.COLOR[color]}"><div class="marca">{i:02d}</div>'
            f'<h1>Anexo: salidas de los comandos</h1>{intro}{"".join(partes)}</section>')


def capitulo(i, ruta: Path, color, con_defensa):
    texto = M.limpia_emojis(ruta.read_text(encoding="utf-8"))
    if not con_defensa:
        texto = M.quita_defensa(texto)
    texto = M.ajusta_enlaces(texto, ruta.parent)
    m = re.search(r"^# +(.+)$", texto, flags=re.M)
    titulo = re.sub(r"^\d\d · ", "", m.group(1).strip()) if m else ruta.stem
    texto = re.sub(r"^# +.+$", "", texto, count=1, flags=re.M)
    cuerpo = M.markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"])
    titulo_html = M.markdown.markdown(titulo).removeprefix("<p>").removesuffix("</p>")
    return re.sub(r"[`*]", "", titulo), (
        f'<section class="capitulo" style="--c:{M.COLOR[color]}">'
        f'<div class="marca">{i:02d}</div><h1>{titulo_html}</h1>{cuerpo}</section>')


def portada(titulo, modulos, color):
    franja = "".join(f'<span style="background:{M.COLOR[c]}"></span>' for c in ("com", "lan", "nas", "pve", "cli", "srv"))
    esquema = (RAIZ / "diagrames" / "esquema-red.png").as_uri()
    nombre, _, sub = titulo.partition(" · ")
    return f"""
<section class="portada" style="--c:{M.COLOR[color]}">
  <div class="franja">{franja}</div>
  <div class="sup">ASIX ThinkLab · Naix un sistema · Parte individual</div>
  <h1>{html.escape(nombre)}</h1>
  <div class="sub">{html.escape(sub)}</div>
  <img src="{esquema}" alt="Esquema de red">
  <div class="datos">
    <div>Alumno<b>izan</b></div>
    <div>Curso<b>1.º ASIX · 2026-2027</b></div>
    <div>Módulos<b>{html.escape(modulos)}</b></div>
    <div>Red · Puesto<b>192.168.23.0/24 · 23</b></div>
    <div style="margin-top:8pt">Centro<b>CIP FP Batoi</b></div>
    <div style="margin-top:8pt">Dominio<b>asix23.lan</b></div>
    <div style="margin-top:8pt">Repositorio<b>iso-naix-un-sistema-individual</b></div>
    <div style="margin-top:8pt">Fecha<b>{date.today().strftime("%d/%m/%Y")}</b></div>
  </div>
</section>"""


def indice(titulos, paginas):
    filas = "".join(
        f'<li style="--c:{M.COLOR[c]}"><span class="n">{i:02d}</span><span class="t">{html.escape(t)}</span>'
        f'<span class="p">{paginas.get(i, "")}</span></li>' for i, (t, c) in enumerate(titulos, 1))
    return (f'<section class="indice"><h1>Índice</h1><ol>{filas}</ol>'
            '<p class="nota">El capítulo 01 resume la tarea (qué pide el enunciado, qué he hecho y los resultados). '
            'Los siguientes contienen el desarrollo completo con las capturas de las propias máquinas virtuales. '
            'Las salidas completas de los comandos, las configuraciones exportadas y los scripts están en el '
            'repositorio (<code>evidencies/</code>, <code>configs/</code> y <code>scripts/</code>).</p></section>')


def busca_paginas(pdf, titulos):
    textos = [(pg.extract_text() or "") for pg in PdfReader(str(pdf)).pages]
    paginas, desde = {}, 2
    for i, (t, _) in enumerate(titulos, 1):
        clave = re.sub(r"\W+", "", t)[:25]
        for n in range(desde, len(textos)):
            if clave and clave in re.sub(r"\W+", "", textos[n])[:400]:
                paginas[i], desde = n + 1, n + 1
                break
    return paginas


def genera(nombre):
    ficha, color, caps, con_defensa = TAREAS[nombre]
    ruta_ficha = FICHAS / ficha
    texto_ficha = ruta_ficha.read_text(encoding="utf-8")
    titulo = re.search(r"^# +(.+)$", texto_ficha, flags=re.M).group(1).strip()
    mod = re.search(r"\*\*Módulos:\*\* *([^·\n]+)", texto_ficha)
    modulos = mod.group(1).strip() if mod else "ISO · FDM"

    titulos, cuerpos = [], []
    for i, (ruta, c) in enumerate([(ruta_ficha, color)] + [(RAIZ / a, c) for a, c in caps], 1):
        t, h = capitulo(i, ruta, c, con_defensa)
        if i == 1:
            t = "Resumen de la tarea"
            h = re.sub(r"<h1>.*?</h1>", "<h1>Resumen de la tarea</h1>", h, count=1)
        titulos.append((t, c))
        cuerpos.append(h)
    a = anexo(len(titulos) + 1, nombre, color)
    if a:
        titulos.append(a[:2])
        cuerpos.append(a[2])

    def doc(paginas):
        return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{html.escape(titulo)}</title>'
                f'<style>{M.CSS}{CSS_ANEXO}</style></head><body>{portada(titulo, modulos, color)}'
                f'{indice(titulos, paginas)}{"".join(cuerpos)}</body></html>')

    pie_original = M.IMPRIME
    M.IMPRIME = pie_original.replace("Naix un sistema · Memoria técnica", f"Naix un sistema · {html.escape(titulo.split(' · ')[0])}")
    borrador = M.BUILD / f"borrador-{nombre}.pdf"
    M.imprime(doc({}), borrador)
    paginas = busca_paginas(borrador, titulos)
    salida = SALIDA / f"{nombre}.pdf"
    SALIDA.mkdir(parents=True, exist_ok=True)
    M.imprime(doc(paginas), salida)
    M.IMPRIME = pie_original
    faltan = [titulos[i - 1][0] for i in range(1, len(titulos) + 1) if i not in paginas]
    print(f"{salida.relative_to(RAIZ)}  ({len(PdfReader(str(salida)).pages)} páginas)"
          + (f"  aviso, sin página: {faltan}" if faltan else ""))


if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(TAREAS)
    for n in TAREAS:
        if any(n.startswith(p) for p in pedidas):
            genera(n)
