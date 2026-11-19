# 11 · Preparación de la Tasca 8 (caso práctico individual · 25/11/2026)

En el examen, el profesorado provocará un fallo en mi entorno y yo tendré que **acotar el impacto → formular una hipótesis → consultar el [plan de contingencia](09-contingencia.md) → aplicarlo → comprobar que se recupera la función**. Se valora el razonamiento y **no perder datos**, no la rapidez.

## 1. Antes de empezar (2 min)

1. Abrir este documento, el [09](09-contingencia.md) y el [10](10-incidencies.md).
2. Arrancar **solo** el escenario necesario (ver [05-recursos](05-recursos.md)). En clase caben ~24 GB de VMs; en casa, ~10 GB.
3. Acceso a todo por SSH con la configuración del laboratorio:

| Equipo | Comando | Web desde el PC |
|---|---|---|
| MikroTik `.1` | `ssh -F ~/iso-lab/ssh/config mk` | `http://127.0.0.1:8001` |
| OPNsense `.2` | (web) | `https://127.0.0.1:8402` |
| DEB13-SRV1-NFT `.3` | `ssh -F ~/iso-lab/ssh/config deb-srv` | — |
| TrueNas `.10` | `ssh -F ~/iso-lab/ssh/config truenas` | `https://127.0.0.1:8410` |
| PMX1/2/3 `.11–.13` | `ssh -F ~/iso-lab/ssh/config pmx1` (pmx2, pmx3) | `https://127.0.0.1:8411` (8412, 8413) |
| WS2025-DC `.20` | RDP `127.0.0.1:8420` | — |
| DEB13-SRV2 `.21` | `ssh -F ~/iso-lab/ssh/config srv2` | — |
| DEB13-SRV3 `.22` | `ssh -F ~/iso-lab/ssh/config srv3` | `http://127.0.0.1:8422` |
| DEB13-CLI `.54` | `ssh -F ~/iso-lab/ssh/config cli-info` (a través de deb-srv) | — |

Si la red falla, la **consola de VirtualBox** (doble clic en la VM) siempre funciona.

> Atención: **En el aula el cortafuegos del centro filtra el ICMP hacia Internet** (comprobado el 18/11: `ping 1.1.1.1` y `ping 8.8.8.8` desde el propio PC → 100 % de pérdida, pero HTTPS funciona). Desde las VMs pasa lo mismo, porque salen por la NAT del PC. Para comprobar Internet en clase: `curl -sI https://deb.debian.org | head -1` y `getent hosts debian.org`. Un `ping 1.1.1.1` fallido **no** prueba que el router esté roto.

## 2. Método de intervención (escribirlo mientras se hace)

| Paso | Qué hago | Ejemplo |
|---|---|---|
| **1. Estado inicial** | Qué funciona y qué no, **desde el punto de vista del usuario** | "DEB13-CLI no abre webs" |
| **2. Acotar** | Ir de abajo arriba: ¿VM encendida? → ¿enlace? → ¿IP? → ¿gateway? → ¿Internet? → ¿DNS? → ¿servicio? | `ip -br a` · `ping .1` · `ping 1.1.1.1` · `getent hosts debian.org` |
| **3. Hipótesis** | Una sola causa probable y **qué prueba la confirmaría** | "La NAT del router se ha borrado → `/ip firewall nat print` saldrá vacío" |
| **4. Punto de retorno** | **Antes de tocar nada**: instantánea o copia del estado actual | `VBoxManage snapshot <vm> take antes-arreglo` · `/export` · `cp fichero fichero.antes` |
| **5. Aplicar** | La recuperación del plan (copia local → NAS → alternativo) | `/system backup load`, `canvi-gw.sh 3`, `mdadm --add`… |
| **6. Prueba funcional** | Comprobar **la función**, no solo que la VM arranca | El cliente vuelve a navegar / abre su fichero / inicia sesión |
| **7. Registrar** | Hora, causa, solución, tiempo de corte y pérdida en [10](10-incidencies.md) | |

## 3. Chuleta de diagnóstico por sistema

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

## 4. Fallos que me pueden poner y dónde está la respuesta

| Fallo probable | Primera comprobación | Recuperación | Documento |
|---|---|---|---|
| Se borra la NAT / la configuración del MikroTik | `ping 1.1.1.1` desde el cliente | Copia local del router · cambio de gateway | [mikrotik §7](06-installacio/mikrotik.md) |
| Regla errónea en OPNsense | Live View del cortafuegos | Historial de configuración | [opnsense §8](06-installacio/opnsense.md) |
| `nftables.conf` roto | `nft -c -f` | `etc.tgz` del NAS | [debian-srv §7](06-installacio/debian-srv.md) |
| Línea errónea en `/etc/fstab` → no arranca | Consola: modo de emergencia | Comentar la línea, `findmnt --verify` | [10 · incidencia provocada](10-incidencies.md) |
| Disco del RAID roto / desconectado | `/proc/mdstat` | `mdadm --add` | [07 §3](07-emmagatzematge-raid.md) |
| Se cae DEB13-SRV2 (servidor de ficheros) | `cat /proc/drbd` en SRV3 → `WFConnection`, `Unknown` | Promocionar SRV3 y montar; al volver SRV2 se resincroniza solo | [07 §7](07-emmagatzematge-raid.md) |
| Red lenta entre VMs | `iperf3` | Tarjeta virtio en lugar de e1000 | [08 §5.1](08-rendiment.md) |
| Nodo Proxmox apagado | `pvecm status` | El clúster sigue con 2/3; migrar o restaurar | [proxmox](06-installacio/proxmox.md) |
| Cable virtual desconectado (VirtualBox) | `ip -br a` → `NO-CARRIER` | *Configuración → Red → Cable conectado* / `VBoxManage controlvm <vm> setlinkstate1 on` | — |
| IP o gateway cambiados en un cliente | `ip a` / `ip route` | Volver a los datos de [04-disseny](04-disseny.md) | — |
| El host va muy lento | `vmstat 2` | Apagar VMs; ver [08](08-rendiment.md) | [08](08-rendiment.md) |

## 5. Banco de preguntas (cuestionario teórico-práctico, Apte+)

Las preguntas con su respuesta están al final de cada documento («Preguntas probables de la defensa»):

| Tema | Dónde |
|---|---|
| Virtualización, recursos, escenarios | [05](05-recursos.md) |
| Router, NAT, cortafuegos, logs | [mikrotik](06-installacio/mikrotik.md) · [opnsense](06-installacio/opnsense.md) · [debian-srv](06-installacio/debian-srv.md) |
| NAS, ZFS, espejo frente a copia | [truenas](06-installacio/truenas.md) |
| Clúster, quórum, contenedor frente a VM, migración | [proxmox](06-installacio/proxmox.md) |
| Dominio, DNS, Kerberos, canal seguro | [windows-server](06-installacio/windows-server.md) · [clients](06-installacio/clients.md) |
| RAID 0/1/5, reconstrucción, disco de reserva, espejo por red (DRBD) | [07](07-emmagatzematge-raid.md) |
| Rendimiento, cuellos de botella, cuántas VMs, virtio, caché del host | [02](02-inventari.md) · [08](08-rendiment.md) |
| RTO, RPO, contingencia | [09](09-contingencia.md) |

**Conceptos que tengo que saber explicar sin mirar:** hipervisor tipo 1 y tipo 2 · NAT frente a red interna frente a puente · máscara /24 y gateway · DNS directo e inverso · qué es un dominio · RAID frente a copia · RTO/RPO · quórum · *thin provisioning* (VDI dinámico) · `iowait` · swap · SHA256 · paravirtualización (virtio) · caché de escritura y `fsync` · DRBD y split-brain.

## 6. Las 10 cifras que conviene saber de memoria

| Cifra | Qué demuestra |
|---|---|
| **26 s** | Recuperar el MikroTik con la configuración borrada (RTO objetivo 5 min) |
| **8 ms** | Corte de una migración en caliente de VM en Proxmox (el contenedor: ~84 s) |
| **2 de 3** | Quórum: el clúster sigue con un nodo caído |
| **54 s / 15 s / 21 s** | Reconstrucción RAID 1 / RAID 5 / disco de reserva automático |
| **~13 s · RPO 0** | Caída del servidor de ficheros con DRBD hasta tener los datos en el otro |
| **399 MB/s** | Techo del SSD por USB: el cuello de botella con carga |
| **iowait 82 %** | Pico al arrancar DEB13-CLI: el disco, no la CPU |
| **5 VMs / ~11 GB** | Lo que aguanta mi PC de casa (límite: RAM) |
| **4,7 → 12,3 Gbit/s** | Optimización 1: virtio-net |
| **×80 en `fsync`** | Optimización 2: caché del host… revertida por seguridad de los datos |
