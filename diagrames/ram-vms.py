#!/usr/bin/env python3
"""Gráfica: RAM asignada frente a RAM real de cada VM al arrancar (Tasca 7).
RAM real = caída de MemAvailable del anfitrión (incluye la sobrecarga de VirtualBox)."""
from estilo import Lienzo, C, MONO

DATOS = [  # VM, asignada (MB), real (MB) — de docs/08-rendiment.md
    ("TrueNas", 4096, 3144), ("WS2025-DC", 4096, 2785), ("PMX1", 4096, 2738), ("W11-CLI", 4096, 2257),
    ("OPNsense", 2048, 2177), ("DEB13-CLI", 4096, 1334), ("DEB13-SRV2", 1024, 1162),
    ("DEB13-SRV1-NFT", 2048, 1134), ("DEB13-SRV3", 1024, 349), ("Mikrotik-IND", 512, 108),
]
SERIE, PISTA = "#2a78d6", "#d3e3f7"   # serie 1 (validada) y un paso más claro de la misma rampa

L = Lienzo(1200, 690, "RAM asignada frente a RAM real al arrancar",
           "MB por VM · cada una medida sola, con el resto apagadas")
X0, X1, Y0, FILA, ALTO = 190, 1000, 130, 44, 20
MAX = 4500
esc = lambda v: X0 + (X1 - X0) * v / MAX

# rejilla
for v in range(0, 4097, 1024):
    x = esc(v)
    L.line([(x, Y0 - 16), (x, Y0 + FILA * len(DATOS) - 14)], "#e5e7eb", 1)
    L.text(x, Y0 + FILA * len(DATOS) + 6, f"{v}", 11, C["suave"], font=MONO)
L.text((X0 + X1) / 2, Y0 + FILA * len(DATOS) + 28, "MB", 11.5, C["suave"])

for i, (vm, asig, real) in enumerate(DATOS):
    y = Y0 + i * FILA
    L.text(X0 - 14, y + 14, vm, 13, anchor="end")
    L.rect(X0, y, esc(asig) - X0, ALTO, PISTA, rx=4)                 # asignada (pista)
    L.rect(X0, y + 4, esc(real) - X0, ALTO - 8, SERIE, rx=4)         # real (barra fina dentro)
    pct = real / asig * 100
    L.text(max(esc(asig), esc(real)) + 12, y + 14, f"{real} / {asig}", 12, C["texto"], "bold", "start", font=MONO)
    L.text(1180, y + 14, f"{pct:.0f} %", 12.5, C["texto"] if pct <= 100 else C["sim"], "bold", "end", font=MONO)
L.text(1180, Y0 - 22, "real / asignada", 11, C["suave"], anchor="end")

# leyenda y notas
ly = Y0 + FILA * len(DATOS) + 52
L.rect(X0, ly - 8, 28, 16, PISTA, rx=4); L.text(X0 + 36, ly + 4, "RAM asignada a la VM", 12, anchor="start")
L.rect(X0 + 220, ly - 4, 28, 8, SERIE, rx=4); L.text(X0 + 256, ly + 4, "RAM real que pierde el PC", 12, anchor="start")
L.text(X0, ly + 28, "> 100 % (OPNsense, SRV2): la medida incluye la memoria propia de VirtualBox para esa VM.  "
       "TrueNas usa casi todo: ZFS aprovecha la RAM libre como caché (ARC).", 11.5, C["suave"], anchor="start")
L.guardar(__file__)
