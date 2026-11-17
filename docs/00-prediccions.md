# 00 · Predicciones (PREDIU)

> Lo que pensaba **antes de investigar** y lo que pasó después con las pruebas. La última columna enlaza con la evidencia que me hizo cambiar (o no) de opinión.

## Preguntas del enunciado

| Pregunta | Mi predicción | Motivo | ¿Cambió tras las pruebas? ¿Por qué? |
|---|---|---|---|
| ¿Qué sistema pondría en un **cliente**? | Windows 11 en todos los puestos | Es lo que conoce la gente de oficina y lo que pide el software de gestión | **En parte.** Windows 11 en Administración (dominio, software de oficina), pero en Informática un **Debian 13**: gratis, ligero (≈ 890 MB de RAM real frente a los 4 GB que le había dado) y con las herramientas de red que usa el departamento ([clients](06-installacio/clients.md), [08](08-rendiment.md)) |
| ¿Qué sistema pondría en un **servidor de datos**? | Windows Server, porque ya hace el dominio | Un solo sistema para todo es más fácil de administrar | **Sí cambió.** Los datos van en un **NAS dedicado (TrueNAS)** con ZFS en espejo, y los ficheros del día a día en un Debian con RAID por software. Si el DC cae no quiero perder también los datos: separar funciones reduce el punto único de fallo ([truenas](06-installacio/truenas.md), [07](07-emmagatzematge-raid.md)) |
| ¿Qué sistema pondría en un **equipo de comunicaciones**? | Un router "de verdad" (MikroTik) y ya está | Es lo que se usa en las empresas pequeñas | **Se amplió.** Probé tres (MikroTik, OPNsense y Debian + nftables) y los tres hacen NAT y cortafuegos. MikroTik gasta muy poco (150 MB), OPNsense es el más fácil de revisar por web y Debian el más transparente. Tener **dos alternativos** permitió recuperar Internet en segundos cuando "rompí" el principal ([09](09-contingencia.md)) |
| ¿Qué comprobaría en el **hardware**? | La CPU y la RAM, que es lo que se nota | En las tiendas siempre se habla de procesador y memoria | **Sí cambió.** El cuello de botella real era el **disco**: en casa las VMs están en el SSD de clase dentro de una caja USB (347 IOPS, iowait alto) mientras la CPU estaba casi libre. Ahora lo primero que miro es `lsblk` (TRAN), `fio` y el iowait ([02](02-inventari.md)) |
| ¿Qué pasaría si se **pierde un disco**? | Se pierden los datos de ese disco | Pensaba que un RAID era "una copia" | **Depende del RAID.** RAID 0: se pierde **todo** el volumen. RAID 1 y 5: el volumen sigue en modo degradado y se reconstruye con un disco nuevo sin perder nada. Y he aprendido que **un espejo no es una copia de seguridad**: un borrado se replica al instante en los dos discos ([07](07-emmagatzematge-raid.md)) |

## Predicciones por fase (ThinkLoop)

| Fase | Antes de empezar creo que… | Resultado real |
|---|---|---|
| Inventario | Mi PC de casa irá peor que el de clase sobre todo por la CPU (6 núcleos frente a 14) | La CPU sobra en los dos. Lo que limita en casa es la **RAM (16 GB)**, que deja un escenario cada vez, y el **disco por USB**. Ver [02](02-inventari.md) |
| Red / gateways | Cambiar de router obligará a reconfigurar todos los equipos | Basta con cambiar la puerta de enlace (`canvi-gw.sh`) porque los tres routers usan la misma LAN y hacen NAT. Lo difícil fue el **orden de reglas** de OPNsense: la de bloqueo estaba "creada" pero no actuaba ([opnsense](06-installacio/opnsense.md)) |
| RAID | El RAID 0 será mucho más rápido y el RAID 5 el más lento al escribir | En la teoría sí, pero en mis medidas **no se puede comparar**: todos los discos virtuales están en el mismo SSD por USB y las cifras varían de 14 a 436 MB/s. Lo que sí se ve claro es la tolerancia a fallos y la reconstrucción ([07](07-emmagatzematge-raid.md)) |
| Rendimiento (¿cuántas VMs aguanta mi PC?) | En casa unas 6–7 VMs, sumando la RAM que les he dado | Ver [08](08-rendiment.md): las VMs usan mucha menos RAM real de la asignada, pero no se puede contar con eso porque, cuando trabajan, crecen hasta lo asignado. El límite lo pone la **RAM asignada** más la reserva del host |
| Contingencia | Recuperar un router a partir de su copia en el NAS será lo más rápido | **Falló**: al NAS se llegaba a través del router roto. Solución: copia local en el propio equipo + Git + NAS. Después la recuperación tardó **26 s** ([09](09-contingencia.md)) |
