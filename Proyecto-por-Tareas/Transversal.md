# Transversal · Predicciones y plan de contingencia

## Fet: subtareas del enunciado

> **Enunciado (part individual):** Partes comunes a todo el proyecto: la fase **PREDIU** (predicciones antes de investigar), el plan de contingencia (punto 4 de la Tasca 6, hecho también en el entorno individual) y el registro de incidencias.

| # | Subtarea | Nivel | Fet | Dónde / nota |
|---|---|---|:---:|---|
| 1 | Predicciones antes de cada fase y comparación con el resultado | — | ✓ | Predicciones |
| 2 | Plan de contingencia con RTO/RPO | — | ✓ | Plan de contingencia |
| 3 | Probar el plan y medir el tiempo sin servicio | — | ✓ | 9 de 13 escenarios probados |
| 4 | Valorar si el plan es adecuado o debe mejorar | — | ✓ | Puntos débiles y valoración personal |
| 5 | Registro de incidencias con su solución | — | ✓ | 26 incidencias (Tasca 0) |

**Resumen:** 5 de 5 subtareas completas.

**Leyenda:** ✓ Fet · ◐ Fet en parte (se explica en la nota) · ⏳ Pendiente de fecha


## 1. Predicciones (antes de investigar)

Antes de cada fase escribí lo que esperaba que pasara, para compararlo después con el resultado (método ThinkLoop: predicción → investigación → implementación → verificación → análisis).

### Preguntas del enunciado

| Pregunta | Mi predicción | Motivo | ¿Cambió tras las pruebas? ¿Por qué? |
|---|---|---|---|
| ¿Qué sistema pondría en un **cliente**? | Windows 11 en todos los puestos | Es lo que conoce la gente de oficina y lo que pide el software de gestión | **En parte.** Windows 11 en Administración (dominio, software de oficina), pero en Informática un **Debian 13**: gratis, ligero (≈ 890 MB de RAM real frente a los 4 GB que le había dado) y con las herramientas de red que usa el departamento ([clients](../docs/06-installacio/clients.md), [08](../docs/08-rendiment.md)) |
| ¿Qué sistema pondría en un **servidor de datos**? | Windows Server, porque ya hace el dominio | Un solo sistema para todo es más fácil de administrar | **Sí cambió.** Los datos van en un **NAS dedicado (TrueNAS)** con ZFS en espejo, y los ficheros del día a día en un Debian con RAID por software. Si el DC cae no quiero perder también los datos: separar funciones reduce el punto único de fallo ([truenas](../docs/06-installacio/truenas.md), [07](../docs/07-emmagatzematge-raid.md)) |
| ¿Qué sistema pondría en un **equipo de comunicaciones**? | Un router "de verdad" (MikroTik) y ya está | Es lo que se usa en las empresas pequeñas | **Se amplió.** Probé tres (MikroTik, OPNsense y Debian + nftables) y los tres hacen NAT y cortafuegos. MikroTik gasta muy poco (150 MB), OPNsense es el más fácil de revisar por web y Debian el más transparente. Tener **dos alternativos** permitió recuperar Internet en segundos cuando "rompí" el principal ([09](../docs/09-contingencia.md)) |
| ¿Qué comprobaría en el **hardware**? | La CPU y la RAM, que es lo que se nota | En las tiendas siempre se habla de procesador y memoria | **Sí cambió.** El cuello de botella real era el **disco**: en casa las VMs están en el SSD de clase dentro de una caja USB (347 IOPS, iowait alto) mientras la CPU estaba casi libre. Ahora lo primero que miro es `lsblk` (TRAN), `fio` y el iowait ([02](../docs/02-inventari.md)) |
| ¿Qué pasaría si se **pierde un disco**? | Se pierden los datos de ese disco | Pensaba que un RAID era "una copia" | **Depende del RAID.** RAID 0: se pierde **todo** el volumen. RAID 1 y 5: el volumen sigue en modo degradado y se reconstruye con un disco nuevo sin perder nada. Y he aprendido que **un espejo no es una copia de seguridad**: un borrado se replica al instante en los dos discos ([07](../docs/07-emmagatzematge-raid.md)) |

### Predicciones por fase (ThinkLoop)

| Fase | Antes de empezar creo que… | Resultado real |
|---|---|---|
| Inventario | Mi PC de casa irá peor que el de clase sobre todo por la CPU (6 núcleos frente a 14) | La CPU sobra en los dos. Lo que limita en casa es la **RAM (16 GB)**, que deja un escenario cada vez, y el **disco por USB**. Ver [02](../docs/02-inventari.md) |
| Red / gateways | Cambiar de router obligará a reconfigurar todos los equipos | Basta con cambiar la puerta de enlace (`canvi-gw.sh`) porque los tres routers usan la misma LAN y hacen NAT. Lo difícil fue el **orden de reglas** de OPNsense: la de bloqueo estaba "creada" pero no actuaba ([opnsense](../docs/06-installacio/opnsense.md)) |
| RAID entre 2 equipos | Copiar datos entre dos servidores por la red será lento y la recuperación complicada | Con DRBD el otro servidor tenía los datos idénticos y el servicio volvió en **~13 s**; al volver el caído solo se copiaron los 206 MB cambiados. Lo complicado no es la técnica sino **no montar el disco en los dos a la vez** ([07 §7](../docs/07-emmagatzematge-raid.md)) |
| RAID | El RAID 0 será mucho más rápido y el RAID 5 el más lento al escribir | En la teoría sí, pero en mis medidas **no se puede comparar**: todos los discos virtuales están en el mismo SSD por USB y las cifras varían de 14 a 436 MB/s. Lo que sí se ve claro es la tolerancia a fallos y la reconstrucción ([07](../docs/07-emmagatzematge-raid.md)) |
| Rendimiento (¿cuántas VMs aguanta mi PC?) | En casa unas 6–7 VMs, sumando la RAM que les he dado | **Menos: 5 VMs** (6,6 GB asignados) en la prueba real con el navegador abierto, ~11 GB sin él. Las VMs usan menos RAM de la asignada (MikroTik 108 MB de 512), pero no se puede contar con eso: cuando trabajan crecen hasta lo asignado. Con carga, el primero en saturarse es el **disco** (399 MB/s, el techo del USB), no la CPU (máx. 32 %). Ver [08](../docs/08-rendiment.md) |
| Contingencia | Recuperar un router a partir de su copia en el NAS será lo más rápido | **Falló**: al NAS se llegaba a través del router roto. Solución: copia local en el propio equipo + Git + NAS. Después la recuperación tardó **26 s** ([09](../docs/09-contingencia.md)) |

## 2. Plan de contingencia con RTO/RPO y tiempos reales

- **RTO** = cuánto tiempo puede estar parada una función. **RPO** = cuántos datos se pueden perder (desde la última copia).
- **13 escenarios**, **9 probados** provocando el fallo de verdad y midiendo el tiempo.

| Escenario | RTO objetivo | Tiempo real | Pérdida |
|---|---|---|---|
| MikroTik con la configuración borrada | 5 min | **26 s** | 0 |
| Debian nftables roto + reinicio | 5 min | **21 s** | 0 |
| OPNsense con una regla errónea | 5 min | **15 s** | 0 |
| Router activo caído | 5 min | Cambio de gateway a `.2`/`.3` | 0 |
| Mantenimiento de un nodo Proxmox | 2 min | VM: **8 ms** · contenedor: ~84 s | 0 |
| Nodo del clúster caído | Inmediato | Sigue con quórum 2 de 3 | 0 |
| VM que no arranca (`fstab`) | 30 min | Resuelto con el método de diagnóstico | 0 |
| Disco roto en RAID 1/5 | 0 | 0 s sin servicio · reconstrucción 54 s / 15 s | 0 |
| Servidor de ficheros caído (DRBD) | 5 min | **~13 s** | 0 |
| DC de Windows perdido · cliente estropeado · host roto · disco del NAS | — | Simulados: con copia hecha y verificada | Según la copia |

**Punto único de fallo:** el PC anfitrión. En una empresa real habría varios hosts físicos y el NAS fuera del host.


## 3. Incidencias

26 problemas reales encontrados durante el montaje, cada uno con síntoma, causa, solución y lección aprendida. La tabla completa está en la Tasca 0.

## Desarrollo

### De dónde salen las copias

| Origen | Qué se copia | Cuándo | Destino | RPO resultante |
|---|---|---|---|---|
| MikroTik, DEB13-SRV1-NFT, OPNsense | Configuración (`.backup`/`.rsc`, `/etc`, `config.xml`) | Cron de TrueNAS **diario 02:00** (`scripts/copia-configs.sh`) | NAS `/mnt/copias/configs/` | 24 h |
| OPNsense (además) | Historial local de `config.xml` | **En cada cambio** | El propio OPNsense | ≈ 0 (último cambio) |
| Proxmox (CT 100, VM 101) | Imagen completa (`vzdump`) | Tarea **diaria 02:30**, se guardan 3 | `nas-copias` (NFS del NAS) | 24 h |
| WS2025-DC | Base de datos de AD + SYSVOL (`ntdsutil ifm`) | Manual (`scripts/windows/copia-ad.ps1`) | NAS `/mnt/copias/configs/ws2025-dc/` | Desde la última ejecución manual |
| TrueNAS | Las propias copias | Siempre (pool **espejo** `copias`) | 2 discos | 0 frente a fallo de **un** disco |

### Conceptos

| Término | Qué significa | Ejemplo en mi sistema |
|---|---|---|
| **RTO** (*Recovery Time Objective*) | Tiempo máximo que puede estar parado un servicio | Internet: 5 min |
| **RPO** (*Recovery Point Objective*) | Cuántos datos (medidos en tiempo) se pueden perder como máximo | Configuración de los routers: 24 h (copia diaria) |
| **Tiempo real** | Lo que **medimos** al provocar el fallo | MikroTik: 26 s sin Internet en el cliente |

> **Pregunta probable de defensa:** *"¿Qué diferencia hay entre RTO y RPO?"* → El RTO mira **hacia delante** (¿cuánto tardo en volver a funcionar?) y el RPO **hacia atrás** (¿desde cuándo pierdo cambios?). Una copia diaria da un RPO de hasta 24 h aunque la recuperación tarde solo segundos.

### Procedimiento general ante un fallo

1. **Detectar**: síntoma desde un cliente (`ping`, `curl`, no hay Internet, no inicia sesión…).
2. **Aislar**: ¿es la red, el servidor o el cliente? `ping` al gateway → al servidor → a Internet.
3. **Recuperar** con la vía más rápida que exista:
   - Copia **local** si la hay (historial de OPNsense, `copia-nas.backup` en el MikroTik).
   - Si no, copia del **NAS**.
   - Si el equipo no vuelve: **router alternativo** (`canvi-gw.sh`) o **migrar** el servicio a otro nodo.
4. **Verificar** desde el cliente (Internet, servicio, inicio de sesión).
5. **Documentar** en `10-incidencies.md`: hora, causa, solución y tiempo real.

### Lecciones aprendidas

- **Una copia que no se puede alcanzar no sirve**: en el primer intento del MikroTik, la copia estaba en el NAS, pero al NAS se llegaba *a través* del propio router roto. Solución: guardar también una copia **en el propio equipo** y tener un camino alternativo (WAN).
- **Un espejo no es una copia**: protege de un disco roto, no de un borrado o un ransomware.
- **El host es el punto único de fallo** de todo el entorno de pruebas. En la empresa se reparte en varios equipos físicos (el clúster de 3 nodos y el NAS separados).

### Puntos débiles detectados (con datos)

| Punto débil | Evidencia | Mejora posible |
|---|---|---|
| NAS y VMs en el **mismo SSD** | Inventario: todo está en el Kingston A400 | Copia de las configuraciones fuera del PC (Git ✓) y de los VDI críticos a otro disco |
| Copia del DC **manual** | `copia-ad.ps1` se lanza a mano | Tarea programada de Windows |
| RPO de 24 h en los routers | Cron diario a las 02:00 | Copia tras cada cambio (como el historial de OPNsense) |
| Migración del contenedor con **~84 s** de corte | Discos locales en cada nodo | Almacenamiento compartido (NFS del NAS) → solo se copia la RAM |

### Valoración personal

**¿Es adecuado el plan? Para un entorno de pruebas, sí; para la empresa real, tiene que mejorar en tres puntos.**

Lo que me convence es que **casi todos los escenarios están probados de verdad, no solo escritos**: he borrado la configuración del MikroTik, he roto nftables, he metido una regla errónea en OPNsense, he migrado servicios entre nodos y he arrancado los RAID sin un disco. Todos los tiempos reales quedan **muy por debajo del RTO** que me había puesto (26 s frente a 5 min en el peor router) y en ninguna prueba se han perdido datos. Además, las pruebas me sirvieron para **corregir el propio plan**: la primera versión de la recuperación del MikroTik confiaba en el NAS y no funcionaba, porque el camino al NAS pasaba por el router roto. Si no lo hubiera probado, lo habría descubierto en el peor momento.

Lo que tiene que mejorar:

1. **El host es un punto único de fallo.** Todo vive en un solo PC y en un solo SSD (incluido el NAS que guarda las copias). En la empresa pondría el NAS en otro equipo físico y una segunda copia fuera de la oficina (regla 3-2-1). Aquí lo compenso en parte con las configuraciones en Git.
2. **El RPO de 24 h de los routers es largo** para un equipo que cambia a menudo. Haría una copia tras cada cambio (como ya hace OPNsense con su historial).
3. **Quedan escenarios solo simulados**: la recuperación del DC desde la copia IFM y la restauración de una VM desde `vzdump` en otro nodo. Están preparados y las copias verificadas, pero no los he ejecutado de principio a fin, así que su tiempo real no lo conozco. Serían las siguientes pruebas que haría.

En resumen: el plan es **fiable para lo que se ha probado** y **honesto con lo que no**, que es lo que más me importa, porque un plan de contingencia que nunca se ha ensayado solo es una suposición.

