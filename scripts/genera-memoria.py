#!/usr/bin/env python3
"""Genera la memoria técnica en PDF a partir de los Markdown de docs/.

Uso:  ~/iso-lab/pdf-venv/bin/python scripts/genera-memoria.py
Salida: entrega/memoria-naix-un-sistema.pdf

Necesita (fuera del repo, en ~/iso-lab):
  - pdf-venv:  python3 -m venv ~/iso-lab/pdf-venv && ~/iso-lab/pdf-venv/bin/pip install markdown pypdf
  - node:      cd ~/iso-lab/node && npm i puppeteer-core   (usa el Google Chrome instalado)

Pasos: Markdown -> HTML con estilo (paleta de diagrames/estilo.py) -> PDF con Chrome.
Se imprime dos veces: la primera para saber en qué página empieza cada capítulo y
la segunda con esos números en el índice.
Se omiten las secciones "Preguntas probables de la defensa" (son la preparación del examen)
y docs/11-defensa.md.
"""
import html
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import markdown
from pypdf import PdfReader

RAIZ = Path(__file__).resolve().parent.parent
BUILD = RAIZ / "build"
SALIDA = RAIZ / "entrega" / "memoria-naix-un-sistema.pdf"
NODE = Path.home() / "iso-lab" / "node" / "node_modules"

# Paleta común de los esquemas (diagrames/estilo.py)
COLOR = {
    "com": "#ea580c", "lan": "#059669", "nas": "#0891b2", "pve": "#d97706",
    "cli": "#2563eb", "srv": "#db2777", "drbd": "#be185d", "suave": "#64748b",
}

# (archivo, color) en el orden de la memoria
CAPITULOS = [
    ("docs/00-prediccions.md", "suave"),
    ("docs/01-requisits.md", "cli"),
    ("docs/02-inventari.md", "nas"),
    ("docs/03-sistemes.md", "cli"),
    ("docs/04-disseny.md", "lan"),
    ("docs/05-recursos.md", "pve"),
    ("docs/06-installacio/README.md", "com"),
    ("docs/06-installacio/mikrotik.md", "com"),
    ("docs/06-installacio/opnsense.md", "com"),
    ("docs/06-installacio/debian-srv.md", "com"),
    ("docs/06-installacio/truenas.md", "nas"),
    ("docs/06-installacio/proxmox.md", "pve"),
    ("docs/06-installacio/windows-server.md", "cli"),
    ("docs/06-installacio/debian-servidors.md", "srv"),
    ("docs/06-installacio/clients.md", "cli"),
    ("docs/07-emmagatzematge-raid.md", "srv"),
    ("docs/08-rendiment.md", "pve"),
    ("docs/09-contingencia.md", "drbd"),
    ("docs/10-incidencies.md", "com"),
]

# Símbolos que se sustituyen por texto o por un signo tipográfico (no emoji)
SUSTITUCIONES = {"✅": "✓", "✔️": "✓", "✔": "✓", "❌": "✗", "🚫": "✗", "⬜": "Pendiente", "🟡": "En curso",
                 "🧪": "(simulado)", "⚠️": "Atención:", "⚠": "Atención:", "➖": "—"}
EMOJI = re.compile("(?![✓✗])[\U0001F000-\U0001FAFF☀-⛿✀-➿⬀-⯿️‍]")


def limpia_emojis(texto: str) -> str:
    for k, v in SUSTITUCIONES.items():
        texto = texto.replace(k, v)
    texto = EMOJI.sub("", texto)
    return re.sub(r"^(#+) +", r"\1 ", texto, flags=re.M)


def quita_defensa(texto: str) -> str:
    """Elimina la sección de preguntas de la defensa (hasta el siguiente título del mismo nivel o el final)."""
    return re.sub(r"^## +Preguntas probables de la defensa.*?(?=^## |\Z)", "", texto, flags=re.M | re.S)


def ajusta_enlaces(texto: str, carpeta: Path) -> str:
    def img(m):
        alt, ruta = m.group(1), m.group(2)
        if ruta.startswith("http"):
            return m.group(0)
        return f"![{alt}]({(carpeta / ruta).resolve().as_uri()})"

    texto = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, texto)

    def enlace(m):
        txt, ruta = m.group(1), m.group(2)
        if ruta.startswith("http"):
            return m.group(0)
        return txt  # en papel, los enlaces internos se dejan como texto

    texto = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)", enlace, texto)
    # <img src="..."> en HTML incrustado
    texto = re.sub(r'<img src="([^"]+)"',
                   lambda m: f'<img src="{(carpeta / m.group(1)).resolve().as_uri()}"' if not m.group(1).startswith("http") else m.group(0),
                   texto)
    return texto


def capitulo_html(i: int, archivo: str, color: str):
    ruta = RAIZ / archivo
    texto = ruta.read_text(encoding="utf-8")
    texto = quita_defensa(limpia_emojis(texto))
    texto = ajusta_enlaces(texto, ruta.parent)
    titulo = re.search(r"^# +(.+)$", texto, flags=re.M)
    titulo = titulo.group(1).strip() if titulo else ruta.stem
    titulo = re.sub(r"^\d\d · ", "", titulo)  # el número ya va en la marca del capítulo
    texto = re.sub(r"^# +.+$", "", texto, count=1, flags=re.M)
    cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"])
    titulo_html = markdown.markdown(titulo).removeprefix("<p>").removesuffix("</p>")
    return titulo, (f'<section class="capitulo" id="cap{i}" style="--c:{COLOR[color]}">'
                    f'<div class="marca">{i:02d}</div><h1>{titulo_html}</h1>{cuerpo}</section>')


CSS = """
@page { size: A4; margin: 20mm 17mm 20mm 17mm; }
:root { --texto:#1f2937; --suave:#64748b; --linea:#e2e8f0; --fondo:#f8fafc; }
* { box-sizing: border-box; }
html { font-family: Inter, 'DejaVu Sans', sans-serif; font-size: 9.6pt; color: var(--texto); line-height: 1.5; }
body { margin: 0; }
h1, h2, h3, h4 { font-family: 'Inter Display', Inter, sans-serif; line-height: 1.25; break-after: avoid; }
h2 { font-size: 13.5pt; margin: 18pt 0 6pt; padding-bottom: 3pt; border-bottom: 2px solid var(--c); color: #0f172a; }
h3 { font-size: 11pt; margin: 13pt 0 4pt; color: var(--c); }
h4 { font-size: 10pt; margin: 10pt 0 3pt; }
p { margin: 4pt 0 6pt; }
a { color: var(--c); text-decoration: none; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.3pt; background: #f1f5f9; border-radius: 3px; padding: 0 2px; }
pre { background: var(--fondo); border: 1px solid var(--linea); border-left: 3px solid var(--c); border-radius: 4px;
      padding: 6pt 8pt; white-space: pre-wrap; word-break: break-word; font-size: 8pt; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: inherit; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 8.4pt; break-inside: auto; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: var(--c); color: #fff; text-align: left; padding: 4pt 6pt; font-weight: 600; }
td { padding: 3.5pt 6pt; border-bottom: 1px solid var(--linea); vertical-align: top; }
tbody tr:nth-child(even) td { background: var(--fondo); }
blockquote { margin: 8pt 0; padding: 6pt 10pt; background: color-mix(in srgb, var(--c) 8%, white);
             border-left: 3px solid var(--c); border-radius: 0 4px 4px 0; break-inside: avoid; }
blockquote p { margin: 2pt 0; }
img { max-width: 100%; max-height: 120mm; border: 1px solid var(--linea); border-radius: 4px; }
p:has(> img) { text-align: center; break-inside: avoid; margin: 10pt 0; }
p:has(> img) em { display: block; text-align: center; font-size: 8.2pt; color: var(--suave); margin-top: 3pt; }
ul, ol { padding-left: 16pt; margin: 4pt 0 6pt; }
li { margin: 1.5pt 0; }
hr { border: none; border-top: 1px solid var(--linea); margin: 12pt 0; }
details { display: block; } summary { font-weight: 600; }

/* Capítulos */
.capitulo { break-before: page; position: relative; }
.capitulo > .marca { font-family: 'Inter Display', Inter; font-weight: 800; font-size: 34pt; color: var(--c); opacity: .9; line-height: 1; }
.capitulo > h1 { font-size: 21pt; margin: 2pt 0 12pt; padding-bottom: 8pt; border-bottom: 4px solid var(--c); color: #0f172a; }

/* Portada */
.portada { height: 257mm; display: flex; flex-direction: column; break-after: page; }
.portada .franja { height: 8pt; display: flex; border-radius: 4px; overflow: hidden; }
.portada .franja span { flex: 1; }
.portada .sup { margin-top: 26mm; color: var(--suave); font-size: 10.5pt; letter-spacing: .14em; text-transform: uppercase; font-weight: 600; }
.portada h1 { font-family: 'Inter Display', Inter; font-size: 40pt; margin: 6pt 0 2pt; color: #0f172a; letter-spacing: -.01em; }
.portada .sub { font-size: 14pt; color: #334155; margin-bottom: 14mm; }
.portada img { border: none; max-height: 105mm; }
.portada .datos { margin-top: auto; display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border-top: 1px solid var(--linea); padding-top: 10pt; }
.portada .datos div { font-size: 8.5pt; color: var(--suave); }
.portada .datos b { display: block; font-size: 10.5pt; color: var(--texto); font-weight: 600; }

/* Índice */
.indice { break-after: page; }
.indice h1 { font-family: 'Inter Display', Inter; font-size: 21pt; border-bottom: 4px solid #0f172a; padding-bottom: 8pt; }
.indice ol { list-style: none; padding: 0; margin: 10pt 0; }
.indice li { display: flex; align-items: baseline; gap: 8pt; padding: 5pt 0; border-bottom: 1px dotted #cbd5e1; font-size: 10.5pt; }
.indice li .n { font-weight: 700; color: var(--c); width: 22pt; }
.indice li .t { flex: 1; }
.indice li .p { font-variant-numeric: tabular-nums; color: var(--suave); }
.indice .nota { margin-top: 14pt; font-size: 8.5pt; color: var(--suave); }
"""


def portada():
    franja = "".join(f'<span style="background:{COLOR[c]}"></span>' for c in ("com", "lan", "nas", "pve", "cli", "srv"))
    esquema = (RAIZ / "diagrames" / "esquema-red.png").as_uri()
    hoy = date.today().strftime("%d/%m/%Y")
    return f"""
<section class="portada">
  <div class="franja">{franja}</div>
  <div class="sup">ASIX ThinkLab · Memoria técnica · Parte individual</div>
  <h1>Naix un sistema</h1>
  <div class="sub">Entorno de pruebas virtualizado: comunicaciones, almacenamiento, virtualización, dominio y rendimiento</div>
  <img src="{esquema}" alt="Esquema de red">
  <div class="datos">
    <div>Alumno<b>izan</b></div>
    <div>Curso<b>1.º ASIX · 2026-2027</b></div>
    <div>Módulos<b>ISO · FDM</b></div>
    <div>Red · Puesto<b>192.168.23.0/24 · 23</b></div>
    <div style="margin-top:8pt">Centro<b>CIP FP Batoi</b></div>
    <div style="margin-top:8pt">Dominio<b>asix23.lan</b></div>
    <div style="margin-top:8pt">Repositorio<b>iso-naix-un-sistema-individual</b></div>
    <div style="margin-top:8pt">Fecha<b>{hoy}</b></div>
  </div>
</section>"""


def indice(titulos, paginas):
    filas = []
    for i, (t, color) in enumerate(titulos):
        p = paginas.get(i, "")
        filas.append(f'<li style="--c:{COLOR[color]}"><span class="n">{i:02d}</span>'
                     f'<span class="t">{html.escape(t)}</span><span class="p">{p}</span></li>')
    return (f'<section class="indice"><h1>Índice</h1><ol>{"".join(filas)}</ol>'
            '<p class="nota">Las salidas completas de los comandos, las configuraciones exportadas y los scripts '
            'están en el repositorio (carpetas <code>evidencies/</code>, <code>configs/</code> y <code>scripts/</code>). '
            'Las capturas son de las propias máquinas virtuales.</p></section>')


def documento(titulos, capitulos, paginas):
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Naix un sistema · Memoria técnica</title>'
            f'<style>{CSS}</style></head><body>{portada()}{indice(titulos, paginas)}{"".join(capitulos)}</body></html>')


IMPRIME = r"""
const puppeteer = require('puppeteer-core');
(async () => {
  const [entrada, salida] = process.argv.slice(2);
  const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: true,
                                     args: ['--allow-file-access-from-files'] });
  const p = await b.newPage();
  await p.goto('file://' + entrada, { waitUntil: 'networkidle0', timeout: 120000 });
  await p.evaluateHandle('document.fonts.ready');
  const pie = `<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#64748b;
     padding:0 17mm;display:flex;justify-content:space-between">
     <span>Naix un sistema · Memoria técnica · izan · 1.º ASIX</span>
     <span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
  await p.pdf({ path: salida, format: 'A4', printBackground: true, preferCSSPageSize: true,
                displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: pie });
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
"""


def imprime(html_txt: str, pdf: Path):
    BUILD.mkdir(exist_ok=True)
    entrada = BUILD / "memoria.html"
    entrada.write_text(html_txt, encoding="utf-8")
    js = BUILD / "imprime.cjs"
    js.write_text(IMPRIME, encoding="utf-8")
    pdf.parent.mkdir(exist_ok=True)
    subprocess.run(["node", str(js), str(entrada), str(pdf)], check=True, env={"NODE_PATH": str(NODE), "PATH": "/usr/bin:/bin"})


def busca_paginas(pdf: Path, titulos):
    """Página de inicio de cada capítulo: la primera página (después del índice) que empieza por su número y título."""
    lector = PdfReader(str(pdf))
    textos = [(pg.extract_text() or "") for pg in lector.pages]
    paginas, desde = {}, 2
    for i, (t, _) in enumerate(titulos):
        clave = re.sub(r"\W+", "", t)[:25]
        for n in range(desde, len(textos)):
            if clave and clave in re.sub(r"\W+", "", textos[n])[:400]:
                paginas[i] = n + 1
                desde = n + 1
                break
    return paginas


def main():
    capitulos, titulos = [], []
    for i, (archivo, color) in enumerate(CAPITULOS):
        t, h = capitulo_html(i, archivo, color)
        titulos.append((re.sub(r"[`*]", "", t), color))
        capitulos.append(h)
    borrador = BUILD / "borrador.pdf"
    imprime(documento(titulos, capitulos, {}), borrador)
    paginas = busca_paginas(borrador, titulos)
    imprime(documento(titulos, capitulos, paginas), SALIDA)
    print(f"{SALIDA.relative_to(RAIZ)}  ({len(PdfReader(str(SALIDA)).pages)} páginas)")
    faltan = [titulos[i][0] for i in range(len(titulos)) if i not in paginas]
    if faltan:
        print("Aviso: no se encontró la página de:", *faltan, sep="\n  ", file=sys.stderr)


if __name__ == "__main__":
    main()
