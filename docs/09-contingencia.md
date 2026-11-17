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
| **Almacenamiento** — falla un disco de un RAID 1/5 | Datos del servidor de ficheros | 0 (modo degradado) | 0 | ⬜ Pendiente (Tasca 6, mdadm) | ⬜ | ⬜ Se probará |

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
