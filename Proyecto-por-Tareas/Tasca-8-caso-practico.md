# Tasca 8 · Caso práctico individual (preparación)

**Examen:** miércoles 25/11/2026 · **Estado:** ✅ guía de intervención y banco de preguntas

## Qué pide el enunciado

El profesorado provocará un fallo en mi entorno y yo tendré que **acotar el impacto → formular una hipótesis → consultar el plan de contingencia → aplicarlo → comprobar que la función se recupera**. Se valora el razonamiento y no perder datos, no la rapidez. Como Apte+ hay un cuestionario teórico-práctico.

## Qué he preparado

1. **Guía de intervención** en 7 pasos: estado inicial → acotar de abajo arriba → hipótesis → punto de retorno → aplicar → prueba funcional → registrar.
2. **Chuleta de diagnóstico** por sistema (Linux, nftables, MikroTik, OPNsense, RAID, DRBD, Proxmox, TrueNAS, Windows).
3. **Tabla de fallos probables** con su primera comprobación y su recuperación.
4. **Banco de preguntas** con respuesta, al final de cada documento.
5. **Plan de contingencia** con 13 escenarios, 9 de ellos probados con tiempos reales ([Transversal](Transversal.md)).

## Fallos probables y dónde está la respuesta

| Fallo | Primera comprobación | Recuperación |
|---|---|---|
| NAT o configuración del MikroTik borrada | `curl -sI https://deb.debian.org` desde el cliente | Copia del router · cambio de gateway |
| Regla errónea en OPNsense | *Firewall → Live View* | Historial de configuración |
| `nftables.conf` roto | `nft -c -f /etc/nftables.conf` | Copia `etc.tgz` del NAS |
| Línea errónea en `/etc/fstab` | Consola: modo de emergencia | Comentar la línea y `findmnt --verify` |
| Disco del RAID roto | `cat /proc/mdstat` | `mdadm --add` |
| Se cae SRV2 (servidor de ficheros) | `cat /proc/drbd` en SRV3 | Promocionar SRV3 y montar |
| Nodo Proxmox apagado | `pvecm status` | El clúster sigue con 2 de 3 |
| Cable virtual desconectado | `ip -br a` → `NO-CARRIER` | `VBoxManage controlvm <vm> setlinkstate1 on` |

> ⚠️ **En el aula el ICMP hacia Internet está filtrado.** Un `ping 1.1.1.1` fallido no demuestra que el router esté roto: hay que comprobarlo con `curl` y con DNS (`getent hosts debian.org`).

## Las 10 cifras que hay que saber

| Cifra | Qué demuestra |
|---|---|
| **26 s** | Recuperación del MikroTik con la configuración borrada |
| **8 ms** | Corte de una migración en caliente en Proxmox |
| **2 de 3** | Quórum: el clúster sigue con un nodo caído |
| **54 s / 15 s / 21 s** | Reconstrucción RAID 1 / RAID 5 / disco de reserva |
| **~13 s · RPO 0** | Caída del servidor de ficheros con DRBD |
| **399 MB/s** | Techo del SSD por USB |
| **iowait 82 %** | Pico al arrancar DEB13-CLI: el límite es el disco, no la CPU |
| **5 VMs / ~11 GB** | Lo que aguanta el PC de casa |
| **4,7 → 12,3 Gbit/s** | Optimización virtio-net |
| **×80 en `fsync`** | Caché del host, revertida por seguridad |

## Evidencias

- Guía completa: [12-defensa](../docs/12-defensa.md) · Plan de contingencia: [09-contingencia](../docs/09-contingencia.md) · Incidencias: [10-incidencies](../docs/10-incidencies.md)
