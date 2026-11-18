#!/usr/bin/env python3
"""Montaje "físico" en VirtualBox (Tasca 4): adaptadores, NAT, red interna y gestión por 127.0.0.1."""
from estilo import Lienzo, C, MONO

L = Lienzo(1600, 940, "Montaje en VirtualBox · cómo está cableado",
           "Todo corre en un solo equipo físico: los cables y el switch son adaptadores y redes de VirtualBox")

# --- exterior y anfitrión -------------------------------------------------
L.rect(920, 84, 280, 40, C["ext_bg"], C["ext"])
L.text(1060, 102, "Red del aula · 172.16.222.0/24", 13, weight="bold")
L.text(1060, 117, "no se toca: no hay VMs en puente", 10.5, C["suave"])
L.rect(30, 140, 1540, 780, "none", C["borde"], 1.5, rx=18, dash="8 6")
L.text(50, 165, "PC anfitrión eth4n · Linux Mint 22.3 · VirtualBox 7.0", 14, C["suave"], "bold", "start")
L.line([(1060, 124), (1060, 160)])
L.pastilla(1060, 172, "eno1 · 172.16.222.207 (DHCP del aula)", C["linea"], ancho=290, size=11.5)
L.line([(1060, 184), (1060, 196)])
L.line([(760, 196), (1360, 196)])

# --- routers: NAT (nic1) + LAN23 (nic2) -----------------------------------
routers = [(650, "Mikrotik-IND", "192.168.23.1", True), (950, "OPNsense", "192.168.23.2", False),
           (1250, "DEB13-SRV1-NFT", "192.168.23.3", False)]
for x, n, ip, act in routers:
    cx = x + 110
    L.line([(cx, 196), (cx, 212)])
    L.rect(x, 212, 220, 46, "#f8fafc", C["linea"])
    L.text(cx, 231, f"NAT de VirtualBox ({n.split('-')[0]})", 11.5, weight="bold")
    L.text(cx, 248, "10.0.2.0/24 · gw 10.0.2.2", 10.5, C["suave"], font=MONO)
    L.line([(cx, 258), (cx, 304)], width=2)
    L.text(cx + 8, 286, "nic1 · NAT", 11, C["suave"], anchor="start")
    L.tarjeta(x, 304, 220, 100, n, "router de LAN23", ip, C["com"], grueso=act,
              red=("nic1 10.0.2.15 · nic2 LAN23",))
    L.line([(cx, 404), (cx, 520)], width=3 if act else 1.5, dash=None if act else "6 5")
    L.text(cx + 8, 470, "nic2 · intnet", 11, C["suave"], anchor="start")

# --- gestión desde el PC --------------------------------------------------
L.grupo(60, 196, 520, 260, "", C["linea"], "#f8fafc")
L.text(80, 222, "Gestión desde el PC (solo en 127.0.0.1)", 14, C["texto"], "bold", "start")
fw = [("127.0.0.1:2201 / 8001", "Mikrotik · SSH / web"), ("127.0.0.1:8402", "OPNsense · web"),
      ("127.0.0.1:2210 / 8410", "TrueNas · SSH / web"), ("127.0.0.1:8411–8413", "Proxmox · web"),
      ("127.0.0.1:8420", "WS2025-DC · RDP"), ("127.0.0.1:2221 / 2222", "SRV2 / SRV3 · SSH"),
      ("127.0.0.1:8422", "SRV3 · web")]
for i, (p, d) in enumerate(fw):
    y = 252 + i * 24
    L.text(80, y, p, 12, C["com"], "bold", "start", font=MONO)
    L.text(300, y, "→ " + d, 12, C["texto"], anchor="start")
L.text(80, 432, "Redirección de puertos en la NAT del router + dst-nat hacia la LAN.", 11, C["suave"], anchor="start", italic=True)
L.text(80, 447, "Desde la red del aula no se ve ningún puerto.", 11, C["suave"], anchor="start", italic=True)
L.line([(580, 300), (620, 300), (620, 235), (648, 235)], C["com"], 1.8, dash="5 4", flecha="flecha-com")

# --- switch virtual LAN23 -------------------------------------------------
L.rect(60, 520, 1480, 14, C["lan"], rx=7)
L.rect(64, 484, 380, 28, C["lan_bg"], C["lan"], rx=14)
L.text(254, 503, "Red interna 'LAN23' = switch virtual aislado", 12.5, C["lan"], "bold")

# --- resto de VMs (una tarjeta cada una) ----------------------------------
vms = [("TrueNas", "1 tarjeta + 3 discos", ".10", C["nas"], False),
       ("PMX1", "modo promiscuo", ".11", C["pve"], False),
       ("PMX2", "modo promiscuo", ".12", C["pve"], False),
       ("PMX3", "modo promiscuo", ".13", C["pve"], False),
       ("WS2025-DC", "UEFI + TPM 2.0", ".20", C["cli"], True),
       ("DEB13-SRV2", "virtio · 10 discos", ".21", C["srv"], True),
       ("DEB13-SRV3", "virtio · 2 discos", ".22", C["srv"], True),
       ("W11-CLI", "UEFI + TPM 2.0", ".51", C["cli"], False),
       ("DEB13-CLI", "1 tarjeta", ".54", C["cli"], False)]
for i, (n, f, ip, col, sim) in enumerate(vms):
    x = 60 + i * 164
    L.line([(x + 76, 534), (x + 76, 580)])
    L.tarjeta(x, 580, 152, 100, n, f, "192.168.23" + ip, col, simulado=sim)

# --- explicación ----------------------------------------------------------
cajas = [(C["lan"], C["lan_bg"], "Red interna (intnet) LAN23",
          ["Un switch virtual que solo ven mis VMs.", "No sale a la red del aula: todo el tráfico", "hacia fuera pasa obligatoriamente por un router."]),
         (C["com"], C["com_bg"], "NAT de VirtualBox (una por router)",
          ["Cada router sale a Internet a través del PC", "con 10.0.2.15. Las demás VMs no tienen NAT:", "salen por el router activo (gateway .1)."]),
         (C["pve"], C["pve_bg"], "Modo promiscuo en los Proxmox",
          ["vmbr0 es un puente: los contenedores y VMs", "internas (srv-infra) usan su propia MAC.", "Sin promiscuo, VirtualBox descartaría sus tramas."])]
for i, (col, bg, t, lineas) in enumerate(cajas):
    x = 60 + i * 500
    L.grupo(x, 720, 480, 130, "", col, bg)
    L.text(x + 18, 748, t, 14, col, "bold", "start")
    for j, l in enumerate(lineas):
        L.text(x + 18, 774 + j * 20, l, 12.5, anchor="start")

L.leyenda(60, 888, [("linea", "gateway activo"), ("discontinua", "router alternativo"),
                    ("simulado", "SIMULADO: en el diseño va dentro del clúster Proxmox")])
L.guardar(__file__)
