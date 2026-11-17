# 09 · Plan de contingencia

Estado: 🟡 en curso (falta añadir el tiempo real del fallo de disco del RAID, Tasca 6)

## 1. Conceptos

| Término | Qué significa | Ejemplo en mi sistema |
|---|---|---|
| **RTO** (*Recovery Time Objective*) | Tiempo máximo que puede estar parado un servicio | Internet: 5 min |
| **RPO** (*Recovery Point Objective*) | Cuántos datos (medidos en tiempo) se pueden perder como máximo | Configuración de los routers: 24 h (copia diaria) |
| **Tiempo real** | Lo que **medimos** al provocar el fallo | MikroTik: 26 s sin Internet en el cliente |

> **Pregunta probable de defensa:** *"¿Qué diferencia hay entre RTO y RPO?"* → El RTO mira **hacia delante** (¿cuánto tardo en volver a funcionar?) y el RPO **hacia atrás** (¿desde cuándo pierdo cambios?). Una copia diaria da un RPO de hasta 24 h aunque la recuperación tarde solo segundos.

## 2. De dónde salen las copias

| Origen | Qué se copia | Cuándo | Destino | RPO resultante |
|---|---|---|---|---|
| MikroTik, DEB13-SRV1-NFT, OPNsense | Configuración (`.backup`/`.rsc`, `/etc`, `config.xml`) | Cron de TrueNAS **diario 02:00** (`scripts/copia-configs.sh`) | NAS `/mnt/copias/configs/` | 24 h |
| OPNsense (además) | Historial local de `config.xml` | **En cada cambio** | El propio OPNsense | ≈ 0 (último cambio) |
| Proxmox (CT 100, VM 101) | Imagen completa (`vzdump`) | Tarea **diaria 02:30**, se guardan 3 | `nas-copias` (NFS del NAS) | 24 h |
| WS2025-DC | Base de datos de AD + SYSVOL (`ntdsutil ifm`) | Manual (`scripts/windows/copia-ad.ps1`) | NAS `/mnt/copias/configs/ws2025-dc/` | Desde la última ejecución manual |
| TrueNAS | Las propias copias | Siempre (pool **espejo** `copias`) | 2 discos | 0 frente a fallo de **un** disco |

## 3. Escenarios

| Escenario | Función afectada | RTO objetivo | RPO objetivo | Tiempo real | Pérdida real | ¿Probado o 🧪 simulado? |
|---|---|---|---|---|---|---|
| **Comunicaciones** — MikroTik con la configuración borrada | Internet de toda la LAN | 5 min | 24 h | **26 s** sin servicio | 0 | ✅ Probado ([mikrotik §7](06-installacio/mikrotik.md)) |
| **Comunicaciones** — DEB13-SRV1-NFT con nftables roto + reinicio | Internet (router alternativo) | 5 min | 24 h | **21 s** | 0 | ✅ Probado ([debian-srv §7](06-installacio/debian-srv.md)) |
| **Comunicaciones** — OPNsense con una regla errónea | Internet (router alternativo) | 5 min | último cambio | **15 s** | 0 | ✅ Probado ([opnsense §8](06-installacio/opnsense.md)) |
| **Comunicaciones** — router activo totalmente caído | Internet | 5 min | — | Cambio de gateway con `scripts/canvi-gw.sh` a `.2` o `.3` | 0 | ✅ Probado (gateways intercambiables, [04-disseny](04-disseny.md)) |
| **Servidor virtual** — mantenimiento de un nodo Proxmox | Intranet (CT `srv-infra`) | 2 min | 0 | VM: **8 ms** de corte (migración en caliente) · CT: **~84 s** | 0 | ✅ Probado ([proxmox §8](06-installacio/proxmox.md)) |
| **Servidor virtual** — se cae un nodo del clúster | Gestión del clúster | Inmediato | 0 | El clúster sigue con quórum **2 de 3** | 0 | ✅ Probado (quórum) · 🧪 restaurar la VM desde `vzdump` en otro nodo |
| **Servidor virtual** — VM que no arranca (error en `fstab`) | Servidor Linux | 30 min | 0 | Diagnosticado y resuelto con el método síntoma → hipótesis → comprobación | 0 | ✅ Probado ([10-incidencies](10-incidencies.md)) |
| **Servidor** — DC de Windows perdido | Inicio de sesión del dominio, DNS | 1 h | Última copia IFM | — | Cambios en AD desde la copia | 🧪 Simulado (copia IFM hecha y verificada en el NAS) |
| **Cliente** — W11-CLI o DEB13-CLI estropeado | Puesto de un departamento | 1 h | 0 en datos del servidor | — | Solo lo guardado en local | 🧪 Simulado: reinstalar desde ISO y volver a unir al dominio; los datos viven en el servidor |
| **Host** — el PC anfitrión se rompe | **Todo** el sistema (punto único de fallo) | 1 día | 24 h | — | Hasta 24 h | 🧪 Simulado: otro PC con VirtualBox + copias del NAS. En la empresa real: varios hosts físicos y el NAS fuera del host |
| **Almacenamiento** — falla un disco del NAS | Copias de seguridad | 0 (sigue funcionando) | 0 | — | 0 | 🧪 Simulado: espejo `copias` (ZFS mirror) |
| **Almacenamiento** — falla un disco de un RAID 1/5 | Datos del servidor de ficheros | 0 (modo degradado) | 0 | **0 s** sin servicio (0 lecturas fallidas) · reconstrucción RAID 1: **54,3 s** · RAID 5: **14,6 s** · con disco de reserva: **21,2 s** automática | 0 (SHA256 iguales) | ✅ Probado ([07 §3](07-emmagatzematge-raid.md)) |

## 3 bis. Fichas por escenario

Responsable en todos los casos: **izan** (único administrador del entorno individual). **Condición de parada general:** si un paso puede destruir la única copia de unos datos, **se para** y se hace antes una copia de lo que haya (instantánea de VirtualBox o copia del VDI). Se valora no perder datos, no la rapidez.

### C1 · Comunicaciones — el gateway activo (MikroTik) deja de dar Internet

| | |
|---|---|
| Síntomas | Los clientes no navegan; `ping 192.168.23.1` falla o responde pero `ping 1.1.1.1` no |
| Dependencias | Todo LAN23 sale por `.1`; el DNS de reserva también es `.1` |
| Recursos | `copia-nas.backup` en el propio router · `mikrotik-export.rsc` en Git · copia en el NAS · routers alternativos `.2` y `.3` |
| Pasos | 1) `ping` .1 → 1.1.1.1 → nombre (aislar la capa) · 2) consola del router: `/interface print`, `/ip address print`, `/ip route print`, `/ip firewall nat print` · 3) si la configuración está mal: `/system backup load name=copia-nas.backup` · 4) si el router no arranca: `scripts/canvi-gw.sh` a `.3` o `.2` |
| Parada | No cargar una copia sin ver antes qué ha cambiado (`/export` del estado actual) |
| Prueba final | Desde DEB13-CLI: `curl -I https://deb.debian.org` → `200` y `ping -c3 1.1.1.1` sin pérdida |
| Medido | **26 s** sin servicio · 0 pérdida |

### C2 · Comunicaciones — DEB13-SRV1-NFT con el cortafuegos roto

| | |
|---|---|
| Síntomas | Con `.3` como gateway, los clientes no salen; `nft list ruleset` vacío o con errores |
| Dependencias | nftables + `ip_forward` (`/etc/sysctl.d/99-router.conf`) |
| Recursos | `etc.tgz` en el NAS · `configs/debian-srv/nftables.conf` en Git |
| Pasos | 1) `sudo nft -c -f /etc/nftables.conf` (¿tiene errores de sintaxis?) · 2) restaurar el fichero de la copia · 3) `nft -c` otra vez → `systemctl restart nftables` · 4) `sysctl net.ipv4.ip_forward` = 1 |
| Parada | Si se pierde el SSH, se sigue por la **consola de VirtualBox** (no depende de la red) |
| Prueba final | Cliente: HTTPS permitido y Telnet bloqueado (aparece `BLOQUEADO-TELNET` en el log) |
| Medido | **21 s** · 0 pérdida |

### C3 · Servidor virtual — el contenedor de la intranet no responde

| | |
|---|---|
| Síntomas | `curl http://192.168.23.30` falla |
| Dependencias | Nodo Proxmox que lo aloja + clúster con quórum + red `vmbr0` |
| Recursos | Los otros nodos (migración) · `vzdump` diario en `nas-copias` (3 últimas) |
| Pasos | 1) `pvecm status` (¿quórum?) · 2) `pct status 100` → `pct start 100` · 3) si el nodo ha caído: restaurar el `vzdump` en otro nodo (`pct restore`) · 4) mantenimiento planificado: `pct migrate 100 pmx2 --restart` |
| Parada | No restaurar encima del contenedor original si aún puede arrancar: restaurar con **otro ID** |
| Prueba final | `curl http://192.168.23.30` devuelve la página de la intranet |
| Medido | Migración CT **~84 s** de corte · VM en caliente **8 ms** |

### C4 · Servidor — el DC (WS2025-DC) se pierde

| | |
|---|---|
| Síntomas | W11-CLI no inicia sesión con usuarios del dominio; `nslookup asix23.lan` falla |
| Dependencias | DNS del dominio (`.20`) · tiempo sincronizado (Kerberos) |
| Recursos | Copia IFM (`ntdsutil`) en el NAS · instantánea de VirtualBox |
| Pasos | 1) ¿la VM está encendida? ¿responde al ping? · 2) servicios `NTDS`, `DNS`, `ADWS` · 3) si el sistema está roto: volver a la instantánea o reinstalar y promover desde el medio IFM |
| Parada | Una instantánea antigua de un DC puede **romper el canal seguro** con los equipos: comprobar después con `Test-ComputerSecureChannel` |
| Prueba final | W11-CLI inicia sesión con un usuario del dominio |
| Estado | 🧪 Simulado |

### C5 · Almacenamiento — falla un disco del RAID de DEB13-SRV2

| | |
|---|---|
| Síntomas | `cat /proc/mdstat` muestra `[U_]` o `(F)` |
| Dependencias | Los demás discos del RAID (con RAID 5, si cae otro se pierde todo) |
| Recursos | Disco de reserva (`--add-spare`) · copia de los datos en el NAS |
| Pasos | 1) `mdadm --detail /dev/mdX` (qué disco) · 2) `--fail` + `--remove` · 3) `--add` disco nuevo · 4) `watch cat /proc/mdstat` hasta `[UU]` |
| Parada | **No** usar `--create` sobre un RAID existente (borra los metadatos); no quitar un disco que esté bien |
| Prueba final | `sha256sum -c datos.sha256` → «La suma coincide» |
| Medido | Servicio sin corte (**0 lecturas fallidas**) · reconstrucción RAID 1 **54 s**, RAID 5 **15 s**, disco de reserva automático **21 s** |

### C6 · Cliente — W11-CLI o DEB13-CLI inutilizable

| | |
|---|---|
| Síntomas | No arranca o no tiene red |
| Recursos | ISO + guía de instalación ([clients](06-installacio/clients.md)); los datos de usuario están en el servidor |
| Pasos | 1) ¿es el cliente o la red? (otro cliente funciona) · 2) si es el sistema: reinstalar, IP fija, unir al dominio |
| Prueba final | El usuario vuelve a abrir su fichero del servidor con el contenido y los permisos correctos |
| Estado | 🧪 Simulado |

### C7 · Host — el PC anfitrión falla

| | |
|---|---|
| Síntomas | Nada arranca |
| Recursos | El SSD con las VMs se puede conectar a otro PC (de hecho lo hago: clase ↔ casa por USB) · copias en el NAS (que está **dentro** del mismo SSD) |
| Limitación | **Punto único de fallo**: si se rompe el SSD, se pierden las VMs **y** el NAS a la vez. No hay continuidad automática |
| Mejora | Copia periódica de las configuraciones (ya están en Git = fuera del PC) y de los VDI críticos a otro disco |
| Estado | 🧪 Simulado (comprobado en parte: el entorno arranca en otro PC) |

## 4. Procedimiento general ante un fallo

1. **Detectar**: síntoma desde un cliente (`ping`, `curl`, no hay Internet, no inicia sesión…).
2. **Aislar**: ¿es la red, el servidor o el cliente? `ping` al gateway → al servidor → a Internet.
3. **Recuperar** con la vía más rápida que exista:
   - Copia **local** si la hay (historial de OPNsense, `copia-nas.backup` en el MikroTik).
   - Si no, copia del **NAS**.
   - Si el equipo no vuelve: **router alternativo** (`canvi-gw.sh`) o **migrar** el servicio a otro nodo.
4. **Verificar** desde el cliente (Internet, servicio, inicio de sesión).
5. **Documentar** en `10-incidencies.md`: hora, causa, solución y tiempo real.

## 5. Lecciones aprendidas

- **Una copia que no se puede alcanzar no sirve**: en el primer intento del MikroTik, la copia estaba en el NAS, pero al NAS se llegaba *a través* del propio router roto. Solución: guardar también una copia **en el propio equipo** y tener un camino alternativo (WAN).
- **Un espejo no es una copia**: protege de un disco roto, no de un borrado o un ransomware.
- **El host es el punto único de fallo** de todo el entorno de pruebas. En la empresa se reparte en varios equipos físicos (el clúster de 3 nodos y el NAS separados).

## Preguntas probables de la defensa

- *¿Por qué tu RPO es de 24 h si la recuperación tarda segundos?* → Porque la copia es diaria: si cambio algo a las 10:00 y el router muere a las 18:00, la última copia es la de las 02:00.
- *¿Cómo bajarías el RPO?* → Copias más frecuentes o en cada cambio (como hace OPNsense con su historial).
- *¿Qué escenario no has podido probar y por qué?* → La pérdida del host: rompería todo el entorno. Se explica cómo se haría.

## Puntos débiles detectados (con datos)

| Punto débil | Evidencia | Mejora posible |
|---|---|---|
| NAS y VMs en el **mismo SSD** | Inventario: todo está en el Kingston A400 | Copia de las configuraciones fuera del PC (Git ✅) y de los VDI críticos a otro disco |
| Copia del DC **manual** | `copia-ad.ps1` se lanza a mano | Tarea programada de Windows |
| RPO de 24 h en los routers | Cron diario a las 02:00 | Copia tras cada cambio (como el historial de OPNsense) |
| Migración del contenedor con **~84 s** de corte | Discos locales en cada nodo | Almacenamiento compartido (NFS del NAS) → solo se copia la RAM |

## Valoración personal

**¿Es adecuado el plan? Para un entorno de pruebas, sí; para la empresa real, tiene que mejorar en tres puntos.**

Lo que me convence es que **casi todos los escenarios están probados de verdad, no solo escritos**: he borrado la configuración del MikroTik, he roto nftables, he metido una regla errónea en OPNsense, he migrado servicios entre nodos y he arrancado los RAID sin un disco. Todos los tiempos reales quedan **muy por debajo del RTO** que me había puesto (26 s frente a 5 min en el peor router) y en ninguna prueba se han perdido datos. Además, las pruebas me sirvieron para **corregir el propio plan**: la primera versión de la recuperación del MikroTik confiaba en el NAS y no funcionaba, porque el camino al NAS pasaba por el router roto. Si no lo hubiera probado, lo habría descubierto en el peor momento.

Lo que tiene que mejorar:

1. **El host es un punto único de fallo.** Todo vive en un solo PC y en un solo SSD (incluido el NAS que guarda las copias). En la empresa pondría el NAS en otro equipo físico y una segunda copia fuera de la oficina (regla 3-2-1). Aquí lo compenso en parte con las configuraciones en Git.
2. **El RPO de 24 h de los routers es largo** para un equipo que cambia a menudo. Haría una copia tras cada cambio (como ya hace OPNsense con su historial).
3. **Quedan escenarios solo simulados**: la recuperación del DC desde la copia IFM y la restauración de una VM desde `vzdump` en otro nodo. Están preparados y las copias verificadas, pero no los he ejecutado de principio a fin, así que su tiempo real no lo conozco. Serían las siguientes pruebas que haría.

En resumen: el plan es **fiable para lo que se ha probado** y **honesto con lo que no**, que es lo que más me importa, porque un plan de contingencia que nunca se ha ensayado solo es una suposición.
