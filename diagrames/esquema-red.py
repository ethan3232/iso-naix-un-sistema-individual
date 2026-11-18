#!/usr/bin/env python3
"""Esquema de red lógico de LAN23 (Tasca 4). Genera esquema-red.svg · PNG con generar.sh."""
from estilo import Lienzo, C

L = Lienzo(1600, 1080, "Esquema de red · entorno individual · puesto 23 · asix23.lan")

# --- exterior -------------------------------------------------------------
L.raw(f'<ellipse cx="800" cy="92" rx="70" ry="22" fill="#f1f5f9" stroke="{C["linea"]}" stroke-width="1.5"/>')
L.text(800, 97, "Internet", 14, weight="bold")
L.line([(800, 114), (800, 140)])
L.rect(660, 140, 280, 44, C["ext_bg"], C["ext"])
L.text(800, 160, "Red del aula · 172.16.222.0/24", 13, weight="bold")
L.text(800, 176, "compartida: no se toca", 11, C["suave"])
L.line([(800, 184), (800, 250)])
L.text(812, 222, "eno1 · 1 Gb/s", 11, C["suave"], anchor="start")

# --- anfitrión ------------------------------------------------------------
L.rect(30, 205, 1540, 850, "none", C["borde"], 1.5, rx=18, dash="8 6")
L.text(50, 230, "PC anfitrión eth4n · Linux Mint 22.3 · VirtualBox 7.0", 14, C["suave"], "bold", "start")
L.rect(680, 250, 240, 48, "#f8fafc", C["linea"])
L.text(800, 270, "NAT de VirtualBox", 13, weight="bold")
L.text(800, 288, "10.0.2.0/24 · gw 10.0.2.2", 11.5, C["suave"], font="DejaVu Sans Mono, monospace")

# --- comunicaciones -------------------------------------------------------
routers = [  # x, nombre, función, ip LAN, activo
    (480, "Mikrotik-IND", "RouterOS 7.24 · NAT + DNS", "192.168.23.1", True),
    (705, "OPNsense", "OPNsense 26.7 · Unbound", "192.168.23.2", False),
    (930, "DEB13-SRV1-NFT", "Debian 13 · nftables", "192.168.23.3", False),
]
RW = 200
L.grupo(455, 334, 700, 140, "", C["com"], C["com_bg"])
L.text(440, 392, "Comunicaciones", 14, C["com"], "bold", "end")
L.text(440, 410, "un solo gateway activo", 12, C["com"], anchor="end")
for x, n, f, ip, act in routers:
    cx = x + RW / 2
    L.line([(800, 298), (800, 314), (cx, 314), (cx, 350)], width=3 if act else 1.5, dash=None if act else "6 5")
    L.tarjeta(x, 350, RW, 108, n, f, ip, C["com"], grueso=act, red=("WAN 10.0.2.15 (DHCP)",))
    L.line([(cx, 458), (cx, 540)], width=3 if act else 1.5, dash=None if act else "6 5")
L.text(590, 500, "gateway activo", 11, C["com"], "bold", "start")
L.text(630, 308, "WAN por DHCP", 11, C["suave"])

# --- bus LAN23 ------------------------------------------------------------
L.rect(60, 533, 1480, 14, C["lan"], rx=7)
L.rect(64, 497, 330, 28, C["lan_bg"], C["lan"], rx=14)
L.text(229, 516, "LAN23 · 192.168.23.0/24 (red interna)", 13, C["lan"], "bold")
L.text(1536, 520, "gateway de todos: el router activo (por defecto .1)", 11.5, C["suave"], anchor="end", italic=True)

# --- almacenamiento -------------------------------------------------------
L.grupo(60, 590, 240, 380, "Almacenamiento", C["nas"], C["nas_bg"])
L.line([(180, 547), (180, 690)])
L.tarjeta(80, 690, 200, 130, "TrueNas", "NAS · pool espejo 'copias'\ncopias de VMs y configs", "192.168.23.10", C["nas"],
          red=("gw .1 · DNS .1",))

# --- clúster --------------------------------------------------------------
L.grupo(325, 590, 860, 380, "Clúster Proxmox 'asix23' · 3 nodos · quórum = 2", C["pve"], C["pve_bg"])
NW = 270
for x, n, ip in [(340, "PMX1", "192.168.23.11"), (620, "PMX2", "192.168.23.12"), (900, "PMX3", "192.168.23.13")]:
    cx = x + NW / 2
    L.line([(cx, 547), (cx, 620)])
    L.text(cx + 8, 578, "vmbr0", 11, C["suave"], anchor="start")
    L.rect(x, 620, NW, 285, "#ffffff", "#cbd5e1", 1.2, opacity=0.6)
    L.rect(x, 620, NW, 46, C["pve"], rx=10)
    L.rect(x, 650, NW, 16, C["pve"], rx=0)
    L.text(cx, 640, f"{n} · {ip}", 13.5, "#ffffff", "bold")
    L.text(cx, 658, "gw .1 · DNS .1", 10.5, "#fff7ed", font="DejaVu Sans Mono, monospace")

VW = 240
L.tarjeta(355, 700, VW, 128, "DEB13-SRV2", "ficheros · RAID 0/1/5\nDRBD primario", "192.168.23.21", C["srv"],
          simulado=True, red=("gw .1 · DNS .20 (.1)",))
L.tarjeta(635, 684, VW, 100, "srv-infra (LXC)", "intranet nginx", "192.168.23.30", C["pve"], red=("gw .1 · DNS .20",))
L.tarjeta(635, 798, VW, 100, "WS2025-DC", "AD DS + DNS", "192.168.23.20", C["cli"], simulado=True,
          red=("gw .1 · DNS 127.0.0.1 → .1",))
L.tarjeta(915, 700, VW, 128, "DEB13-SRV3", "web Apache\nDRBD secundario", "192.168.23.22", C["srv"],
          simulado=True, red=("gw .1 · DNS .20 (.1)",))

# espejo DRBD (por debajo de los nodos)
L.line([(475, 828), (475, 925), (1035, 925), (1035, 834)], C["drbd"], 2.5, flecha="flecha-drbd")
L.pastilla(755, 925, "espejo DRBD · TCP 7789", C["drbd"], ancho=230)

# --- clientes -------------------------------------------------------------
L.grupo(1210, 590, 330, 380, "Clientes", C["cli"], C["cli_bg"])
for x, n, f, ip, red in [
        (1222, "W11-CLI", "Windows 11\nAdministración", "192.168.23.51", ("gw .1", "DNS .20 (DC)")),
        (1378, "DEB13-CLI", "Debian 13\nInformática", "192.168.23.54", ("gw .1 / .2 / .3", "DNS = el gateway"))]:
    cx = x + 75
    L.line([(cx, 547), (cx, 690)])
    L.tarjeta(x, 690, 150, 140, n, f, ip, C["cli"], red=red)

# --- leyenda --------------------------------------------------------------
L.leyenda(60, 1010, [("linea", "gateway activo"), ("discontinua", "gateway alternativo (scripts/canvi-gw.sh)"),
                     ("simulado", "SIMULADO: va dentro del clúster en el diseño; por falta de RAM es una VM de VirtualBox en LAN23 (misma IP)")])
L.text(1540, 1040, "Todas las IP son fijas · máscara /24 · dominio asix23.lan", 11.5, C["suave"], anchor="end")

L.guardar(__file__)
