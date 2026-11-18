#!/usr/bin/env python3
"""Espejo por red con DRBD entre DEB13-SRV2 y DEB13-SRV3 (Tasca 6 Apte+)."""
from estilo import Lienzo, C, MONO

L = Lienzo(1400, 780, "Espejo por red (RAID 1 entre dos equipos) con DRBD",
           "Recurso r0 · cada escritura se guarda en los dos servidores antes de darse por terminada")

# --- cliente --------------------------------------------------------------
L.tarjeta(560, 92, 280, 70, "Usuarios / servicio", "leen y escriben en /srv/espejo", None, C["linea"])
L.line([(700, 162), (700, 180), (300, 180), (300, 232)], C["linea"], 2, flecha="flecha")
L.text(310, 205, "solo el PRIMARIO tiene el disco montado", 11, C["suave"], anchor="start", italic=True)

# --- servidores -----------------------------------------------------------
def servidor(x, nombre, ip, nodo, rol, primario):
    L.grupo(x, 220, 440, 400, "", C["srv"], C["srv_bg"], dash="8 5")
    L.rect(x, 220, 440, 52, C["srv"], rx=14)
    L.rect(x, 250, 440, 22, C["srv"], rx=0)
    L.text(x + 220, 244, f"{nombre} · {ip}", 15, "#ffffff", "bold")
    L.text(x + 220, 263, f"{rol} · en el diseño, VM en {nodo} (SIMULADO)", 11, "#fdf2f8")
    cx = x + 220
    if primario:
        L.tarjeta(x + 40, 296, 360, 76, "/srv/espejo (ext4)", "montado y en uso", None, C["srv"])
    else:
        L.tarjeta(x + 40, 296, 360, 76, "/srv/espejo", "sin montar: solo recibe copias", None, C["borde"])
    L.line([(cx, 372), (cx, 400)], C["linea"], 2, flecha="flecha")
    L.tarjeta(x + 40, 400, 360, 76, "/dev/drbd0", "dispositivo DRBD · recurso r0", None, C["drbd"], grueso=True)
    L.line([(cx, 476), (cx, 504)], C["linea"], 2, flecha="flecha")
    L.tarjeta(x + 40, 504, 360, 76, "Disco virtual de 1 GB", "disco local de cada servidor", None, C["nas"])
    return cx


a = servidor(80, "DEB13-SRV2", ".21", "PMX1", "PRIMARIO", True)
b = servidor(880, "DEB13-SRV3", ".22", "PMX3", "SECUNDARIO", False)

# --- replicación ----------------------------------------------------------
L.line([(520, 425), (878, 425)], C["drbd"], 4, flecha="flecha-drbd")
L.line([(878, 452), (522, 452)], C["drbd"], 1.8, dash="6 4", flecha="flecha-drbd")
L.pastilla(700, 404, "LAN23 · TCP 7789", C["drbd"], ancho=180)
L.text(700, 474, "confirmación (ACK)", 11.5, C["drbd"])
pasos = ["1  SRV2 escribe en su disco", "2  envía el bloque a SRV3", "3  SRV3 lo escribe y confirma",
         "4  solo entonces se da por escrito"]
L.rect(540, 498, 320, 112, "#ffffff", C["drbd"], 1.2)
L.text(700, 520, "Protocolo C (síncrono)", 13, C["drbd"], "bold")
for i, p in enumerate(pasos):
    L.text(560, 542 + i * 19, p, 12, anchor="start")

# --- caída del primario ---------------------------------------------------
L.grupo(80, 650, 1240, 90, "", C["com"], C["com_bg"])
L.text(100, 676, "Si cae SRV2 (probado con un apagado brusco):", 14, C["com"], "bold", "start")
L.text(100, 700, "en SRV3 →  drbdadm primary r0  +  mount /dev/drbd0 /srv/espejo   →   servicio de nuevo en ~13 s,"
                 " sin perder datos (RPO = 0)", 12.5, anchor="start")
L.text(100, 722, "Al volver SRV2 se resincroniza solo. Sincronización inicial de 1 GB: 53 s.", 12.5, C["suave"], anchor="start")

L.leyenda(80, 762, [(C["drbd"], "replicación DRBD"), ("simulado", "SIMULADO: VM de VirtualBox en LAN23; en el diseño, dentro del clúster")])
L.guardar(__file__)
