# Tasca 8 · Caso práctico individual (preparación)

**Examen:** miércoles 25/11/2026 · **Estado:** ✓ guía de intervención y banco de preguntas

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

> Atención: **En el aula el ICMP hacia Internet está filtrado.** Un `ping 1.1.1.1` fallido no demuestra que el router esté roto: hay que comprobarlo con `curl` y con DNS (`getent hosts debian.org`).

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

## Desarrollo

### Método de intervención (escribirlo mientras se hace)

| Paso | Qué hago | Ejemplo |
|---|---|---|
| **1. Estado inicial** | Qué funciona y qué no, **desde el punto de vista del usuario** | "DEB13-CLI no abre webs" |
| **2. Acotar** | Ir de abajo arriba: ¿VM encendida? → ¿enlace? → ¿IP? → ¿gateway? → ¿Internet? → ¿DNS? → ¿servicio? | `ip -br a` · `ping .1` · `ping 1.1.1.1` · `getent hosts debian.org` |
| **3. Hipótesis** | Una sola causa probable y **qué prueba la confirmaría** | "La NAT del router se ha borrado → `/ip firewall nat print` saldrá vacío" |
| **4. Punto de retorno** | **Antes de tocar nada**: instantánea o copia del estado actual | `VBoxManage snapshot <vm> take antes-arreglo` · `/export` · `cp fichero fichero.antes` |
| **5. Aplicar** | La recuperación del plan (copia local → NAS → alternativo) | `/system backup load`, `canvi-gw.sh 3`, `mdadm --add`… |
| **6. Prueba funcional** | Comprobar **la función**, no solo que la VM arranca | El cliente vuelve a navegar / abre su fichero / inicia sesión |
| **7. Registrar** | Hora, causa, solución, tiempo de corte y pérdida en [10](../docs/10-incidencies.md) | |

### Chuleta de diagnóstico por sistema

| Sistema | Ver estado | Ver registros | Arreglos habituales |
|---|---|---|---|
| **Linux (Debian)** | `ip -br a` · `ip route` · `ss -tlnp` · `systemctl --failed` · `df -h` · `free -h` | `journalctl -xb` · `journalctl -u <servicio>` · `dmesg -T` | `systemctl restart <s>` · `nft -c -f /etc/nftables.conf` · `findmnt --verify` |
| **nftables** | `sudo nft list ruleset` | `journalctl -k \| grep -E 'BLOQUEADO\|IN-DROP'` | Restaurar `nftables.conf` de la copia |
| **MikroTik** | `/interface print` · `/ip address print` · `/ip route print` · `/ip firewall nat print` | `/log print` | `/system backup load name=copia-nas.backup` |
| **OPNsense** | *Interfaces → Overview* | *Firewall → Log Files → Live View* | *System → Configuration → History* → revert |
| **RAID (mdadm)** | `cat /proc/mdstat` · `mdadm --detail /dev/md5` | `journalctl -k \| grep md` | `--fail` → `--remove` → `--add` |
| **Espejo DRBD** | `cat /proc/drbd` (`cs:` conexión, `ro:` roles, `ds:` datos) · `drbdadm role r0` | `dmesg \| grep drbd` | Caída del primario: en el otro `drbdadm primary r0` + `mount /dev/drbd0 /srv/espejo` · desconectado: `drbdadm up r0` / `connect r0` · split-brain: `drbdadm connect --discard-my-data r0` en el nodo que pierde |
| **Proxmox** | `pvecm status` · `pct list` · `qm list` | `journalctl -u pve-cluster -u corosync` | `pct start` · `pct restore` desde `nas-copias` |
| **TrueNAS** | `zpool status copias` | *System → Audit / Alerts* | Sustituir disco del espejo (*Storage → Replace*) |
| **Windows Server** | `Get-Service NTDS,DNS,ADWS` · `dcdiag /q` | Visor de eventos → *Directory Service*, *DNS Server* | `Restart-Service` · instantánea · medio IFM |
| **Windows 11** | `ipconfig /all` · `nltest /sc_query:asix23.lan` | Visor de eventos | `Test-ComputerSecureChannel -Repair` |
| **Rendimiento** | `vmstat 2` (`wa` = espera de disco, `si/so` = swap) · `top` · `bash scripts/mide-vm.sh <vm> 60` | — | Apagar VMs que no se usan, bajar RAM asignada |

## Evidencias

- Guía completa: [11-defensa](../docs/11-defensa.md) · Plan de contingencia: [09-contingencia](../docs/09-contingencia.md) · Incidencias: [10-incidencies](../docs/10-incidencies.md)
