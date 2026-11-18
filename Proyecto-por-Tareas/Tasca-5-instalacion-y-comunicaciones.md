# Tasca 5 · Instalación y comunicaciones

**Módulos:** ISO-RA1, FDM-RA1 · **Estado:** ✅ Apte · ✅ Apte+

## Qué pide el enunciado

| Nivel | Criterio |
|---|---|
| Apte | MikroTik, OPNsense y Debian nftables: administración, WAN/LAN, Internet a la LAN, copia en el NAS, fallo y recuperación |
| Apte | En cada router: una conexión permitida y otra bloqueada, con la interpretación del registro |
| Apte | TrueNAS: administración, red y disco adicional para copias |
| Apte | Proxmox: administración, red, clúster, servidores, ventajas e inconvenientes, contenedor frente a VM, migración (tiempo y espacio), copias |
| Apte | Windows Server 2025: administración, red, qué es un dominio y qué aporta, copias |
| Apte | Servidores de infraestructura Linux: administración, red, servicio y copia |
| Apte | Clientes Windows 11 y Linux: administración, red, dominio (si se justifica) y copia |
| Apte | Requisitos, licencia y origen de cada imagen, y comprobación SHA256 |
| Apte | Una incidencia de instalación o arranque en una VM desechable |
| Apte+ | Copias automáticas de las configuraciones de los servidores críticos |

## Qué he hecho y resultados

### Comunicaciones (los tres routers)

| | MikroTik `.1` | OPNsense `.2` | Debian nftables `.3` |
|---|---|---|---|
| Configuración | Consola: NAT *masquerade*, cortafuegos input/forward, DNS | Interfaz web: interfaces, Unbound en reenvío, reglas | `ip_forward` + `nftables` persistente |
| Permitido | HTTPS → `HTTP/2 200` | HTTPS → `HTTP/2 200` | HTTPS → `HTTP/2 200` |
| Bloqueado y registrado | Telnet (TCP 23) en el log | Telnet en *Live View* | Telnet → `BLOQUEADO-TELNET` en `journalctl -k` |
| Fallo provocado | Configuración borrada | Regla errónea | `nftables.conf` roto + reinicio |
| Recuperación | **26 s**, 0 pérdida | **15 s**, 0 pérdida | **21 s**, 0 pérdida |

### Servidores

| Servidor | Lo principal |
|---|---|
| **TrueNAS `.10`** | Pool `copias` en **espejo ZFS** con 2 discos adicionales · NFS para Proxmox · destino de todas las copias |
| **Proxmox `.11–.13`** | Clúster `asix23` de 3 nodos (quórum 2 de 3, probado apagando uno) · contenedor `srv-infra` (intranet nginx) · migración en caliente de una VM: **12,7 s, 8 ms sin servicio** · migración de un contenedor: ~84 s (copia el disco entero) · copia `vzdump` al NAS: 205 MB en 47 s |
| **Windows Server 2025 `.20`** | Dominio `asix23.lan` (AD DS + DNS), OUs por departamento · copia del AD (IFM) en el NAS: 4,9 MB |
| **Debian SRV2 `.21` / SRV3 `.22`** | Ficheros + RAID (SRV2) y web Apache (SRV3), instalación desatendida, copias al NAS |
| **Clientes** | W11-CLI unido al dominio (canal seguro verificado) · DEB13-CLI como cliente de pruebas de los tres routers, sin dominio (justificado) |

### Imágenes y SHA256

Todas las ISOs se descargaron de la web oficial y se comprobó su SHA256 contra el publicado por el fabricante. Licencias y requisitos mínimos en [03-sistemes](../docs/03-sistemes.md).

### Incidencia provocada

Error en `/etc/fstab` en una VM desechable → no arranca y entra en modo de emergencia. Lo resolví siguiendo el método síntoma → hipótesis → comprobación → solución → vuelta atrás. La VM se borró al terminar.

### Apte+: copias automáticas

El NAS **recoge** (*pull*) cada noche las configuraciones de los routers y servidores por SSH/API. Los equipos no guardan credenciales del NAS, así que si se compromete un router no puede borrar las copias. Hay retención por días y un registro de cada ejecución.

## Evidencias

- Guías por máquina: [MikroTik](../docs/06-installacio/mikrotik.md) · [OPNsense](../docs/06-installacio/opnsense.md) · [Debian SRV](../docs/06-installacio/debian-srv.md) · [TrueNAS](../docs/06-installacio/truenas.md) · [Proxmox](../docs/06-installacio/proxmox.md) · [Windows Server](../docs/06-installacio/windows-server.md) · [Debian servidores](../docs/06-installacio/debian-servidors.md) · [Clientes](../docs/06-installacio/clients.md)
- Sistemas, licencias y SHA256: [03-sistemes](../docs/03-sistemes.md) · [`sha256-isos.txt`](../evidencies/logs/sha256-isos.txt)
- Fallos y recuperaciones: [`fallo-recuperacion-mikrotik.txt`](../evidencies/logs/fallo-recuperacion-mikrotik.txt) · [`fallo-recuperacion-opnsense.txt`](../evidencies/logs/fallo-recuperacion-opnsense.txt) · [`fallo-recuperacion-debian-srv.txt`](../evidencies/logs/fallo-recuperacion-debian-srv.txt)
- Clúster y migraciones: [`proxmox-cluster.txt`](../evidencies/logs/proxmox-cluster.txt) · [`proxmox-migraciones.txt`](../evidencies/logs/proxmox-migraciones.txt)
- Dominio: [`ws2025-dc-dominio.txt`](../evidencies/logs/ws2025-dc-dominio.txt) · [`w11-cli-dominio.txt`](../evidencies/logs/w11-cli-dominio.txt)
- Incidencia provocada: [10-incidencies](../docs/10-incidencies.md) · Capturas: [`evidencies/captures/`](../evidencies/captures)
- Script de copias: [`scripts/copia-configs.sh`](../scripts/copia-configs.sh)

## Cómo comprobarlo

```bash
ssh -F ~/iso-lab/ssh/config mk '/ip firewall nat print'   # NAT del MikroTik
curl -sI https://deb.debian.org | head -1                 # desde el cliente: Internet por el gateway
ssh -F ~/iso-lab/ssh/config pmx1 'pvecm status'           # clúster y quórum
ssh -F ~/iso-lab/ssh/config truenas 'zpool status copias' # espejo del NAS
```

## Preguntas probables de la defensa

- **¿Por qué *masquerade* y no `src-nat` con IP fija?** La WAN recibe la IP por DHCP (10.0.2.15) y *masquerade* usa siempre la IP actual de la interfaz.
- **¿Contenedor o VM?** El contenedor comparte el kernel del nodo: arranca en segundos y gasta poca RAM, pero solo puede ejecutar Linux. La VM tiene su propio kernel, aísla más y permite migración en caliente (8 ms frente a ~84 s).
- **¿Qué aporta un dominio a la empresa?** Usuarios y contraseñas centralizados, inicio de sesión en cualquier equipo, políticas (GPO) aplicadas a todos y DNS interno.
