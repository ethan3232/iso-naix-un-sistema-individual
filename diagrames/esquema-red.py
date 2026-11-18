#!/usr/bin/env python3
"""Genera diagrames/esquema-red.svg (esquema de red de LAN23) con coordenadas fijas.

Uso:  python3 diagrames/esquema-red.py
PNG:  google-chrome --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1.5 \
        --window-size=1600,1000 --screenshot=diagrames/esquema-red.png diagrames/esquema-red.svg
"""
from pathlib import Path

W, H = 1600, 1020
FONT = "DejaVu Sans, Helvetica, Arial, sans-serif"
MONO = "DejaVu Sans Mono, monospace"

C = {  # paleta
    "texto": "#1f2937", "suave": "#6b7280", "linea": "#64748b",
    "com": "#ea580c", "com_bg": "#fff7ed",
    "lan": "#059669", "lan_bg": "#ecfdf5",
    "nas": "#0891b2", "nas_bg": "#ecfeff",
    "pve": "#d97706", "pve_bg": "#fffbeb",
    "cli": "#2563eb", "cli_bg": "#eff6ff",
    "sim": "#b45309", "drbd": "#be185d",
}

out = []
add = out.append


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=13, color=None, weight="normal", anchor="middle", font=FONT):
    add(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
        f'fill="{color or C["texto"]}" text-anchor="{anchor}">{esc(t)}</text>')


def line(pts, color=None, width=2, dash=None, arrow=False):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    extra += ' marker-end="url(#flecha)"' if arrow else ""
    add(f'<path d="{d}" fill="none" stroke="{color or C["linea"]}" stroke-width="{width}"'
        f' stroke-linejoin="round"{extra}/>')


def grupo(x, y, w, h, titulo, color, bg, dash=None, abajo=True):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{bg}" stroke="{color}" stroke-width="1.5"{extra}/>')
    if titulo:
        text(x + 16, y + h - 14 if abajo else y + 24, titulo, 14, color, "bold", "start")


def tarjeta(x, y, w, h, nombre, funcion, ip, color, simulado=False, grueso=False):
    borde = 3 if grueso else 1.5
    dash = ' stroke-dasharray="7 5"' if simulado else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#ffffff" stroke="{color}" stroke-width="{borde}"{dash}/>')
    add(f'<rect x="{x + 1.5}" y="{y + 1.5}" width="6" height="{h - 3}" rx="3" fill="{color}"/>')
    cx = x + w / 2 + 3
    lineas = funcion.split("\n")
    total = 18 + 16 * len(lineas) + 18
    y0 = y + (h - total) / 2 + 14
    text(cx, y0, nombre, 14, C["texto"], "bold")
    for i, l in enumerate(lineas):
        text(cx, y0 + 18 + 16 * i, l, 11.5, C["suave"])
    text(cx, y0 + 18 + 16 * len(lineas) + 3, ip, 12.5, color, "bold", font=MONO)
    if simulado:
        bx, by = x + w - 82, y - 10
        add(f'<rect x="{bx}" y="{by}" width="74" height="20" rx="10" fill="#fef3c7" stroke="{C["sim"]}" stroke-width="1"/>')
        text(bx + 37, by + 14, "SIMULADO", 10.5, C["sim"], "bold")


# --- lienzo ---------------------------------------------------------------
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs><marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{C["drbd"]}"/></marker></defs>')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(W / 2, 40, "Esquema de red · entorno individual · puesto 23 · asix23.lan", 22, C["texto"], "bold")

# --- exterior -------------------------------------------------------------
add(f'<ellipse cx="800" cy="92" rx="70" ry="22" fill="#f1f5f9" stroke="{C["linea"]}" stroke-width="1.5"/>')
text(800, 97, "Internet", 14, weight="bold")
line([(800, 114), (800, 140)])
add(f'<rect x="660" y="140" width="280" height="44" rx="10" fill="#fefce8" stroke="#ca8a04" stroke-width="1.5"/>')
text(800, 160, "Red del aula · 172.16.222.0/24", 13, weight="bold")
text(800, 176, "compartida: no se toca", 11, C["suave"])
line([(800, 184), (800, 250)])
text(812, 222, "eno1 · 1 Gb/s", 11, C["suave"], anchor="start")

# --- anfitrión ------------------------------------------------------------
add(f'<rect x="30" y="205" width="1540" height="790" rx="18" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="8 6"/>')
text(50, 230, "PC anfitrión eth4n · Linux Mint 22.3 · VirtualBox 7.0", 14, C["suave"], "bold", "start")

add(f'<rect x="680" y="250" width="240" height="48" rx="10" fill="#f8fafc" stroke="{C["linea"]}" stroke-width="1.5"/>')
text(800, 270, "NAT de VirtualBox", 13, weight="bold")
text(800, 288, "10.0.2.0/24 · gw 10.0.2.2", 11.5, C["suave"], font=MONO)

# --- comunicaciones -------------------------------------------------------
routers = [  # x, nombre, función, ip, activo
    (480, "Mikrotik-IND", "RouterOS 7.24 · NAT", "192.168.23.1", True),
    (705, "OPNsense", "OPNsense 26.7", "192.168.23.2", False),
    (930, "DEB13-SRV1-NFT", "Debian 13 · nftables", "192.168.23.3", False),
]
RW = 200
grupo(455, 334, 700, 128, "", C["com"], C["com_bg"])
text(440, 392, "Comunicaciones", 14, C["com"], "bold", "end")
text(440, 410, "un solo gateway activo", 12, C["com"], anchor="end")
for x, n, f, ip, act in routers:
    cx = x + RW / 2
    line([(800, 298), (800, 314), (cx, 314), (cx, 352)], width=3 if act else 1.5, dash=None if act else "6 5")
    tarjeta(x, 352, RW, 92, n, f, ip, C["com"], grueso=act)
    line([(cx, 444), (cx, 540)], width=3 if act else 1.5, dash=None if act else "6 5")
text(590, 500, "gateway activo", 11, C["com"], "bold", "start")
text(630, 308, "WAN por DHCP", 11, C["suave"])

# --- bus LAN23 ------------------------------------------------------------
add(f'<rect x="60" y="533" width="1480" height="14" rx="7" fill="{C["lan"]}"/>')
add(f'<rect x="64" y="497" width="330" height="28" rx="14" fill="{C["lan_bg"]}" stroke="{C["lan"]}" stroke-width="1.5"/>')
text(229, 516, "LAN23 · 192.168.23.0/24 (red interna)", 13, C["lan"], "bold")

# --- almacenamiento -------------------------------------------------------
grupo(60, 590, 240, 330, "Almacenamiento", C["nas"], C["nas_bg"])
line([(180, 547), (180, 680)])
tarjeta(80, 680, 200, 110, "TrueNas", "NAS · pool espejo 'copias'\ncopias de VMs y configs", "192.168.23.10", C["nas"])

# --- clúster --------------------------------------------------------------
grupo(325, 590, 860, 330, "Clúster Proxmox 'asix23' · 3 nodos · quórum = 2", C["pve"], C["pve_bg"])
nodos = [(340, "PMX1", "192.168.23.11"), (620, "PMX2", "192.168.23.12"), (900, "PMX3", "192.168.23.13")]
NW = 270
for x, n, ip in nodos:
    cx = x + NW / 2
    line([(cx, 547), (cx, 620)])
    text(cx + 8, 578, "vmbr0", 11, C["suave"], anchor="start")
    add(f'<rect x="{x}" y="620" width="{NW}" height="240" rx="10" fill="#ffffff" fill-opacity="0.6" stroke="#cbd5e1" stroke-width="1.2"/>')
    add(f'<rect x="{x}" y="620" width="{NW}" height="34" rx="10" fill="{C["pve"]}"/>')
    add(f'<rect x="{x}" y="640" width="{NW}" height="14" fill="{C["pve"]}"/>')
    text(cx, 642, f"{n} · {ip}", 13.5, "#ffffff", "bold", font=FONT)

VW = 240
tarjeta(355, 680, VW, 110, "DEB13-SRV2", "ficheros · RAID 0/1/5\nDRBD primario", "192.168.23.21", "#db2777", simulado=True)
tarjeta(635, 670, VW, 82, "srv-infra (LXC)", "intranet nginx", "192.168.23.30", C["pve"])
tarjeta(635, 768, VW, 82, "WS2025-DC", "AD DS + DNS", "192.168.23.20", C["cli"], simulado=True)
tarjeta(915, 680, VW, 110, "DEB13-SRV3", "web Apache\nDRBD secundario", "192.168.23.22", "#db2777", simulado=True)

# espejo DRBD (por debajo de los nodos)
line([(475, 790), (475, 875), (1035, 875), (1035, 796)], C["drbd"], 2.5, arrow=True)
add(f'<rect x="640" y="864" width="230" height="22" rx="11" fill="#ffffff" stroke="{C["drbd"]}" stroke-width="1.2"/>')
text(755, 880, "espejo DRBD · TCP 7789", 12, C["drbd"], "bold")

# --- clientes -------------------------------------------------------------
grupo(1210, 590, 330, 330, "Clientes", C["cli"], C["cli_bg"])
for x, n, f, ip in [(1225, "W11-CLI", "Windows 11\nAdministración", "192.168.23.51"),
                    (1385, "DEB13-CLI", "Debian 13\nInformática", "192.168.23.54")]:
    cx = x + 70
    line([(cx, 547), (cx, 680)])
    tarjeta(x, 680, 140, 110, n, f, ip, C["cli"])

# --- leyenda --------------------------------------------------------------
ly = 958
line([(60, ly), (100, ly)], width=3); text(108, ly + 4, "gateway activo", 12, anchor="start")
line([(240, ly), (280, ly)], width=1.5, dash="6 5"); text(288, ly + 4, "gateway alternativo (scripts/canvi-gw.sh)", 12, anchor="start")
add(f'<rect x="600" y="{ly - 11}" width="40" height="22" rx="5" fill="#fff" stroke="{C["sim"]}" stroke-width="1.5" stroke-dasharray="6 4"/>')
text(648, ly + 4, "SIMULADO: en el diseño va dentro del clúster; por falta de RAM es una VM de VirtualBox en LAN23 con la misma IP y función",
     12, anchor="start")

add("</svg>")
Path(__file__).with_name("esquema-red.svg").write_text("\n".join(out), encoding="utf-8")
print("esquema-red.svg generado")
