"""Estilo común de todos los esquemas del proyecto (SVG con coordenadas fijas).

Cada esquema es un script `diagrames/<nombre>.py` que usa `Lienzo` y llama a `guardar()`.
`bash diagrames/generar.sh` regenera todos los SVG y sus PNG.
"""
from pathlib import Path

FONT = "DejaVu Sans, Helvetica, Arial, sans-serif"
MONO = "DejaVu Sans Mono, monospace"

C = {  # paleta común
    "texto": "#1f2937", "suave": "#6b7280", "linea": "#64748b", "borde": "#94a3b8",
    "com": "#ea580c", "com_bg": "#fff7ed",      # comunicaciones
    "lan": "#059669", "lan_bg": "#ecfdf5",      # red LAN23
    "nas": "#0891b2", "nas_bg": "#ecfeff",      # almacenamiento
    "pve": "#d97706", "pve_bg": "#fffbeb",      # clúster Proxmox
    "cli": "#2563eb", "cli_bg": "#eff6ff",      # clientes / Windows
    "srv": "#db2777", "srv_bg": "#fdf2f8",      # servidores Linux (SRV2/SRV3)
    "sim": "#b45309", "drbd": "#be185d",
    "ext_bg": "#fefce8", "ext": "#ca8a04",      # red del aula
}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Lienzo:
    def __init__(self, ancho, alto, titulo, subtitulo=None):
        self.w, self.h, self.out = ancho, alto, []
        a = self.out.append
        a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">')
        a('<defs>')
        for nombre, color in (("flecha", C["linea"]), ("flecha-drbd", C["drbd"]), ("flecha-lan", C["lan"]), ("flecha-com", C["com"])):
            a(f'<marker id="{nombre}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
              f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
        a('</defs>')
        a(f'<rect width="{ancho}" height="{alto}" fill="#ffffff"/>')
        self.text(ancho / 2, 40, titulo, 22, weight="bold")
        if subtitulo:
            self.text(ancho / 2, 64, subtitulo, 13, C["suave"])

    # --- primitivas ---------------------------------------------------------
    def raw(self, s):
        self.out.append(s)

    def text(self, x, y, t, size=13, color=None, weight="normal", anchor="middle", font=FONT, italic=False):
        st = ' font-style="italic"' if italic else ""
        self.out.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
                        f'fill="{color or C["texto"]}" text-anchor="{anchor}"{st}>{esc(t)}</text>')

    def line(self, pts, color=None, width=2, dash=None, flecha=None):
        d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += f' marker-end="url(#{flecha})"' if flecha else ""
        self.out.append(f'<path d="{d}" fill="none" stroke="{color or C["linea"]}" stroke-width="{width}" stroke-linejoin="round"{extra}/>')

    def rect(self, x, y, w, h, fill="#ffffff", stroke=None, width=1.5, rx=10, dash=None, opacity=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += f' fill-opacity="{opacity}"' if opacity is not None else ""
        st = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}{extra}/>')

    def pastilla(self, cx, cy, t, color, bg="#ffffff", size=12, ancho=None):
        w = ancho or (len(t) * size * 0.62 + 24)
        self.rect(cx - w / 2, cy - 12, w, 24, bg, color, 1.3, rx=12)
        self.text(cx, cy + 4.5, t, size, color, "bold")

    # --- piezas -------------------------------------------------------------
    def grupo(self, x, y, w, h, titulo, color, bg, abajo=True, dash=None):
        self.rect(x, y, w, h, bg, color, 1.5, rx=14, dash=dash)
        if titulo:
            self.text(x + 16, y + h - 14 if abajo else y + 24, titulo, 14, color, "bold", "start")

    def tarjeta(self, x, y, w, h, nombre, funcion, ip, color, simulado=False, grueso=False, red=()):
        """Caja de un equipo: nombre, función (líneas con \\n), IP y datos de red (gateway, DNS…)."""
        dash = "7 5" if simulado else None
        self.rect(x, y, w, h, "#ffffff", color, 3 if grueso else 1.5, dash=dash)
        self.rect(x + 1.5, y + 1.5, 6, h - 3, color, rx=3)
        cx = x + w / 2 + 3
        fl = [l for l in funcion.split("\n") if l] if funcion else []
        total = 18 + 16 * len(fl) + (19 if ip else 0) + 15 * len(red)
        yy = y + (h - total) / 2 + 13
        self.text(cx, yy, nombre, 14, weight="bold")
        for l in fl:
            yy += 16
            self.text(cx, yy, l, 11.5, C["suave"])
        if ip:
            yy += 19
            self.text(cx, yy, ip, 12.5, color, "bold", font=MONO)
        for l in red:
            yy += 15
            self.text(cx, yy, l, 10.5, C["linea"], font=MONO)
        if simulado:
            bx, by = x + w - 82, y - 10
            self.rect(bx, by, 74, 20, "#fef3c7", C["sim"], 1, rx=10)
            self.text(bx + 37, by + 14, "SIMULADO", 10.5, C["sim"], "bold")

    def leyenda(self, x, y, items):
        """items: lista de (tipo, texto). tipo: 'linea', 'discontinua', 'simulado', o un color (cuadro)."""
        for tipo, t in items:
            if tipo == "linea":
                self.line([(x, y), (x + 40, y)], width=3)
                x += 48
            elif tipo == "discontinua":
                self.line([(x, y), (x + 40, y)], width=1.5, dash="6 5")
                x += 48
            elif tipo == "simulado":
                self.rect(x, y - 11, 40, 22, "#fff", C["sim"], 1.5, rx=5, dash="6 4")
                x += 48
            else:
                self.rect(x, y - 8, 16, 16, tipo, rx=4)
                x += 24
            self.text(x, y + 4, t, 12, anchor="start")
            x += len(t) * 7.1 + 34

    def guardar(self, script):
        self.out.append("</svg>")
        destino = Path(script).with_suffix(".svg")
        destino.write_text("\n".join(self.out), encoding="utf-8")
        print(f"{destino.name} generado ({self.w}x{self.h})")
