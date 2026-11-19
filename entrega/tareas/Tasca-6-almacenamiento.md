# Tasca 6 · Almacenamiento

**Alumno:** izan · 1.º ASIX · Puesto 23 · Red `192.168.23.0/24` · Dominio `asix23.lan` · CIP FP Batoi · Curso 2026-2027

**Repositorio del proyecto:** [https://github.com/ethan3232/iso-naix-un-sistema-individual](https://github.com/ethan3232/iso-naix-un-sistema-individual) · **Esta tarea en GitHub:** [https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/Proyecto-por-Tareas/Tasca-6-almacenamiento.md](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/Proyecto-por-Tareas/Tasca-6-almacenamiento.md)

**Módulo:** ISO-RA3 · **Estado:** ✓ Apte · ✓ Apte+

## Fet: subtareas del enunciado

> **Enunciado (part individual):** Apte: *«Crea almenys 3 tipus de RAID en un dels equips, verifica el seu funcionament i explica que guanyem en cada un dels diferents tipus de RAID.»* · Apte+: *«Investiga com crear un RAID en espill entre 2 discos que es troben en 2 equips diferents. Indica alguna funcionalitat en la que puga ser interessant i dur-la a terme.»*

| # | Subtarea | Nivel | Fet | Dónde / nota |
|---|---|---|:---:|---|
| 1 | Crear al menos 3 tipos de RAID | Apte | ✓ | RAID 0, 1 y 5 con `mdadm` en DEB13-SRV2 |
| 2 | Verificar su funcionamiento con fallos provocados | Apte | ✓ | Verificación: fallos provocados |
| 3 | Explicar qué se gana con cada tipo | Apte | ✓ | Comparativa |
| 4 | Investigar cómo hacer un espejo entre 2 discos de 2 equipos | Apte+ | ✓ | DRBD |
| 5 | Indicar una funcionalidad útil | Apte+ | ✓ | Servidor de ficheros de la empresa |
| 6 | Llevarlo a cabo y probarlo | Apte+ | ✓ | Caída de SRV2: ~13 s y RPO 0 |

**Resumen:** 6 de 6 subtareas completas.

**Leyenda:** ✓ Fet · ◐ Fet en parte (se explica en la nota) · ⏳ Pendiente de fecha

## Qué he hecho

### Apte: RAID 0, 1 y 5 con `mdadm` en DEB13-SRV2

1. He añadido **8 discos virtuales de 1 GB** a DEB13-SRV2. Son pequeños para que la sincronización y la reconstrucción tarden segundos y se puedan repetir.
2. He creado RAID 0 (2 discos), RAID 1 (2 discos) y RAID 5 (3 discos + 1 de reserva), con sistema de archivos y montaje permanente en `/etc/fstab`.
3. Para verificarlos he **provocado fallos**: he marcado discos como rotos, los he quitado y vuelto a añadir, y he comprobado los datos con SHA256 antes y después.

| RAID | Espacio útil | ¿Aguanta un disco roto? | Resultado de la prueba |
|---|---|---|---|
| RAID 0 | 2,0 GB (100 %) | ✗ No | Más espacio y velocidad teórica, sin protección |
| RAID 1 | 1,0 GB (50 %) | ✓ Sí | 0 lecturas fallidas en modo degradado · reconstrucción en **54 s** |
| RAID 5 | 2,0 GB (67 %) | ✓ Sí (solo uno) | 0 lecturas fallidas · reconstrucción en **15 s** · **disco de reserva automático en 21 s** |

![Los tres RAID activos en SRV2](https://github.com/ethan3232/iso-naix-un-sistema-individual/raw/main/evidencies/captures/debian-servidors/01-srv2-tres-raid-activos.png)

*Demuestra: los tres RAID (`md0` nivel 0, `md1` nivel 1 y `md5` nivel 5) están activos con todos sus discos y montados en `/srv`.*

![RAID 5 degradado con los datos intactos](https://github.com/ethan3232/iso-naix-un-sistema-individual/raw/main/evidencies/captures/debian-servidors/02-srv2-raid5-degradado.png)

*Demuestra: con un disco menos el RAID 5 queda `clean, degraded` y el archivo de prueba sigue íntegro (`La suma coincide`).*

![RAID 5 reconstruido](https://github.com/ethan3232/iso-naix-un-sistema-individual/raw/main/evidencies/captures/debian-servidors/03-srv2-raid5-reconstruido.png)

*Demuestra: al volver a añadir el disco se reconstruye (`recovery`) y el RAID vuelve a `clean` con los 3 discos en `active sync`.*

**Qué se gana con cada uno:** RAID 0 da rendimiento sin seguridad (datos temporales). RAID 1 da seguridad sencilla (disco del sistema, pool del NAS). RAID 5 equilibra espacio y seguridad (carpetas de los departamentos).

**Límite del entorno:** los 8 "discos" son archivos en el mismo SSD físico, así que el RAID 0 no puede ir más rápido. El cuello de botella es el disco del anfitrión, no el RAID.

### Apte+: espejo entre dos equipos con DRBD

![Espejo DRBD](https://github.com/ethan3232/iso-naix-un-sistema-individual/raw/main/diagrames/espejo-drbd.png)

- **DRBD** replica un disco de 1 GB entre SRV2 (primario) y SRV3 (secundario) por la red, con **protocolo C** (síncrono): una escritura no termina hasta que está en los dos.
- **Caso de uso:** el servidor de ficheros de la empresa. Un RAID 1 normal protege de que se rompa un disco; DRBD protege de que se rompa **el servidor entero**.
- **Prueba:** apagado brusco de SRV2 (como un corte de luz). En SRV3, `drbdadm primary r0` + `mount` → datos disponibles en **~13 s**, con el SHA256 idéntico (**RPO 0**). Al volver SRV2 se resincronizó solo, copiando únicamente lo que había cambiado (206 MB en 25 s).

![DRBD primario en SRV2](https://github.com/ethan3232/iso-naix-un-sistema-individual/raw/main/evidencies/captures/debian-servidors/06-srv2-drbd-primario.png)

*Demuestra: SRV2 es primario, los dos discos están `UpToDate`, la replicación está establecida y el espejo conserva los archivos escritos en las pruebas de caída.*

## Desarrollo

### Predicción e investigación

> *Mis predicciones antes de empezar están en [00-prediccions.md](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/docs/00-prediccions.md).*

**¿Por qué RAID por software (`mdadm`) y no la controladora de VirtualBox?** VirtualBox no emula controladoras RAID. Además, `mdadm` es lo que se usa en servidores Linux reales sin tarjeta RAID, y deja ver y **provocar** los fallos con comandos.

**¿Por qué discos de 1 GB?** Para que la sincronización y la reconstrucción tarden segundos y se puedan repetir en clase. El comportamiento es el mismo que con discos grandes; solo cambia el tiempo.

#### Reparto de discos

| RAID | Dispositivo | Discos | Montado en | Sistema de ficheros |
|---|---|---|---|---|
| RAID 0 | `/dev/md0` | `sdb` + `sdc` | `/srv/raid0` | ext4 (etiqueta `raid-0`) |
| RAID 1 | `/dev/md1` | `sdd` + `sde` | `/srv/raid1` | ext4 (`raid-1`) |
| RAID 5 | `/dev/md5` | `sdf` + `sdg` + `sdh` | `/srv/raid5` | ext4 (`raid-5`) |
| Repuesto | — | `sdi` | — | Disco "nuevo" para sustituir al roto |

### Rendimiento medido y su límite en este entorno

Se midió con `fio` (escritura y lectura secuencial de 1 MiB, escritura aleatoria de 4 KiB, sin caché de la VM), en **3 rondas intercaladas**. Los datos completos están en el [log](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/evidencies/logs/raid-rendimiento-fio.txt).

| Destino | Escritura MB/s (mediana) | Lectura MB/s (mediana) | 4K IOPS (mediana) | Dispersión entre rondas |
|---|---|---|---|---|
| 1 disco | 25 | 370 | 5 909 | Escritura de **14 a 391** MB/s |
| RAID 0 | 17 | 110 | 2 204 | Escritura de **15 a 436** MB/s |
| RAID 1 | 15 | 117 | 1 236 | Lectura de **98 a 339** MB/s |
| RAID 5 | 15 | 248 | 1 433 | IOPS de **853 a 9 061** |

**Análisis:** las cifras **no permiten comparar los tipos de RAID**, y saber por qué es parte del resultado:

1. Los 8 "discos" son **ficheros `.vdi` en el mismo SSD físico** del anfitrión (Kingston A400 en caja USB). Un RAID 0 reparte los datos entre dos discos para escribir en paralelo, pero aquí los dos discos son el mismo hardware: no hay paralelismo real.
2. El A400 tiene una caché rápida pequeña. Cuando se llena, la escritura cae a ~15–25 MB/s, y eso se ve igual en **todos** los destinos, incluido el disco solo.
3. Los VDI son **dinámicos**: la primera escritura en una zona nueva obliga a VirtualBox a hacer crecer el fichero.

**El cuello de botella es el disco del anfitrión**, no el RAID. Esto conecta con la [Tasca 2](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/docs/02-inventari.md) (el SSD en caja USB da las mismas ~350 IOPS en clase y en casa) y la [Tasca 7](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/docs/08-rendiment.md).

### Verificación: caída de un servidor entero

| # | Prueba | Resultado | Tiempo |
|---|---|---|---|
| 1 | Sincronización inicial de 1 GB (SRV2 → SRV3) | `UpToDate/UpToDate` | **53 s** (19,8 MB/s: DRBD limita el ritmo para no ahogar la red; se ajusta con `resync-rate`) |
| 2 | Escribir 100 MB aleatorios en SRV2 + SHA256 | `e293a9a2…ca6f99` | — |
| 3 | Montar el disco en SRV3 mientras SRV2 es primario | ✗ *Can't open blockdev* — **correcto**: solo un nodo puede escribir a la vez (si no, se corrompe el ext4) | — |
| 4 | **Apagado brusco de SRV2** (`VBoxManage controlvm poweroff`, como un corte de luz) → en SRV3: `drbdadm primary r0` + `mount` | ✓ Datos montados en SRV3, **SHA256 idéntico** | **~13 s** (casi todo es DRBD detectando que el otro no responde: `ping-int` 10 s) |
| 5 | Escribir 50 MB nuevos en SRV3 con SRV2 apagado | ✓ DRBD apunta lo pendiente: `oos:51272` KB | — |
| 6 | SRV2 vuelve | Entra como **secundario**, sin *split-brain*. Solo copia **206 MB** (50 MB nuevos + 156 MB que marca por precaución por haber caído siendo primario) | **25 s** (no el disco entero) |
| 7 | Cambio controlado de vuelta: SRV3 `umount` + `secondary`, SRV2 `primary` + `mount` | ✓ Los 2 ficheros con su SHA256 correcto | **2,6 s** |
| 8 | Reinicio de SRV3 | Se reconecta solo: `Connected Primary/Secondary UpToDate/UpToDate` | — |

![DRBD secundario en SRV3](https://github.com/ethan3232/iso-naix-un-sistema-individual/raw/main/evidencies/captures/debian-servidors/07-srv3-drbd-secundario.png)

*Demuestra: SRV3 es secundario y tiene una copia al día (`UpToDate`), pero no monta el disco: solo el primario puede usarlo.*

### Caso de uso en la empresa

El **servidor de ficheros** de los departamentos. Hoy, si DEB13-SRV2 se rompe (no un disco: **el equipo**), los RAID 1 y 5 no sirven de nada porque sus discos están dentro. Con DRBD, los datos ya están en DEB13-SRV3 y el servicio vuelve en segundos:

| | RAID 1 local (`md1`) | Espejo por red (DRBD) |
|---|---|---|
| Se rompe un disco | ✓ sigue funcionando | ✓ sigue funcionando |
| Se rompe **el servidor** | ✗ datos inaccesibles hasta repararlo | ✓ el otro servidor los monta en ~13 s |
| Coste | 2 discos | 2 servidores + red |
| Escritura | velocidad del disco | velocidad del disco **+ ida y vuelta por la red** |
| ¿Es una copia de seguridad? | ✗ | ✗ — un borrado o un ransomware se replica al instante. Sigue haciendo falta la copia en el NAS |

**Limitaciones de mi montaje:** el cambio de primario es **manual** (en producción lo haría **Pacemaker/Corosync** con una IP flotante, para que los clientes no tengan que cambiar de servidor), y las dos VMs están en el **mismo PC** (en la empresa serían dos máquinas físicas, idealmente con una red dedicada para la réplica).

### Implementación

```bash
mdadm --create /dev/md0 --level=0 --raid-devices=2 /dev/sdb /dev/sdc
mdadm --create /dev/md1 --level=1 --raid-devices=2 /dev/sdd /dev/sde
mdadm --create /dev/md5 --level=5 --raid-devices=3 /dev/sdf /dev/sdg /dev/sdh
mkfs.ext4 -L raid-0 /dev/md0      # (igual con md1 y md5)
mdadm --detail --scan >> /etc/mdadm/mdadm.conf   # para que se monten solos al arrancar
update-initramfs -u
# /etc/fstab:
LABEL=raid-0 /srv/raid0 ext4 defaults,nofail 0 2
```

- **`mdadm.conf` + `update-initramfs`**: sin esto, al reiniciar los RAID pueden aparecer con otro nombre (`md127`) y el `fstab` no los encuentra.
- **`nofail` en el `fstab`**: es la lección de la [incidencia provocada](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/docs/10-incidencies.md). Si un RAID no arranca, el servidor arranca igualmente en lugar de quedarse en modo de emergencia.
- **Montar por `LABEL`** y no por `/dev/mdX`: si cambia el número del dispositivo, la etiqueta sigue siendo la misma.
- Copias de los ficheros originales en la VM: `/etc/fstab.antes-raid` y `/etc/mdadm/mdadm.conf.antes-raid` (vuelta atrás).

#### Capacidad resultante

| RAID | Espacio bruto | Espacio útil | Aprovechamiento | Fórmula |
|---|---|---|---|---|
| RAID 0 | 2 GB | **2,0 GB** | 100 % | N × disco |
| RAID 1 | 2 GB | **1,0 GB** | 50 % | 1 disco |
| RAID 5 | 3 GB | **2,0 GB** | 67 % | (N − 1) × disco |

### Verificación: fallos provocados

Método: se escriben **100 MB aleatorios** en cada RAID y se guarda su **SHA256**. Después se provoca el fallo y se comprueba si los datos siguen siendo **accesibles** y **exactamente iguales**. Durante el fallo, un bucle lee el fichero cada 0,5 s (vaciando la caché) para ver si el servicio se corta.

| Prueba | Qué se hace | Resultado | ¿Datos? |
|---|---|---|---|
| **RAID 0** sin un disco | Se para `md0` y se intenta arrancar solo con `sdb` | ✗ *"Not enough devices to start the array"*: **no arranca** | Inaccesibles (vuelven al poner los 2 discos) |
| **RAID 1** pierde `sde` | `mdadm --fail` → `--remove` → `--add sdi` | ✓ Sigue funcionando `[U_]` · **22 lecturas correctas, 0 fallidas** | SHA256 coincide en modo degradado y tras reconstruir |
| Reconstrucción RAID 1 | Copia completa de `sdd` → `sdi` | ✓ **54,3 s** (1 GB) · estado final `[UU]` | ✓ |
| **RAID 5** pierde `sdg` | `--fail` → `--remove` → `--add sde` (el disco "reparado") | ✓ Sigue funcionando `[U_U]` · **7 lecturas correctas, 0 fallidas** | SHA256 coincide |
| Reconstrucción RAID 5 | Recalcula el disco que falta con la **paridad** | ✓ **14,6 s** · estado final `[UUU]` | ✓ |
| **RAID 5 + disco de reserva** | `--add-spare sdg` y se rompe `sdf` **sin tocar nada más** | ✓ La reserva entra **automáticamente** y se reconstruye en **21,2 s** | ✓ |
| **Reinicio** | `systemctl reboot` | ✓ Los 3 RAID se montan solos | ✓ Los 3 SHA256 coinciden |

**Observaciones de la prueba:**
- En modo degradado el RAID 5 hizo **7 lecturas en 20 s** y el RAID 1 **22**. Con un disco menos, cada lectura del RAID 5 tiene que **recalcular los datos que faltan con la paridad** (XOR), así que va más lenta. En cambio, el RAID 1 sigue teniendo una copia completa.
- La reconstrucción del RAID 1 (54 s) fue más lenta que la del RAID 5 (15 s). No es por el tipo de RAID: el disco nuevo del RAID 1 (`sdi`) era un VDI **sin estrenar** y VirtualBox tenía que hacer crecer el fichero mientras escribía. Ver el apartado 4.

### Comparativa: qué ganamos con cada tipo

| | RAID 0 (*striping*) | RAID 1 (espejo) | RAID 5 (paridad distribuida) |
|---|---|---|---|
| Discos mínimos | 2 | 2 | 3 |
| Espacio útil | 100 % | 50 % | (N−1)/N → 67 % con 3 |
| ¿Aguanta un disco roto? | ✗ **No**, y con N discos el riesgo se multiplica por N | ✓ Sí | ✓ Sí (solo **uno**) |
| Lectura (teoría) | Muy alta: N discos en paralelo | Mejor: puede leer de los dos | Mejor: lee de N discos |
| Escritura (teoría) | Muy alta | = (escribe en los dos) | Peor: *penalización de escritura*: leer, recalcular la paridad y escribir |
| En modo degradado | — (perdido) | Igual de rápido | **Más lento** (recalcula con la paridad; lo hemos visto: 7 lecturas frente a 22) |
| Uso típico | Datos temporales, caché, edición de vídeo **con copia aparte** | Disco del sistema, servidores pequeños, el pool del NAS | Servidor de ficheros: buen equilibrio de espacio y seguridad |
| En mi sistema | No se usaría para datos de la empresa | **Pool `copias` del TrueNAS** (espejo) | Carpetas de departamentos en DEB13-SRV2 |

## Cómo comprobarlo

```bash
cat /proc/mdstat                       # estado de los RAID: [UU] sano, [U_] degradado
sudo mdadm --detail /dev/md5           # detalle del RAID 5 y el disco de reserva
cat /proc/drbd                         # Connected Primary/Secondary UpToDate/UpToDate
```

## Por qué lo he hecho así

- **¿Un RAID es una copia de seguridad?** No. Si borras un archivo, se borra en todos los discos a la vez. El RAID protege de que se rompa un disco; la copia protege de errores, borrados y ransomware.
- **¿Por qué no se nota que el RAID 0 vaya más rápido?** Porque todos los discos virtuales están en el mismo SSD físico. Con discos físicos separados sí se notaría.
- **¿Qué diferencia hay entre DRBD y una copia en el NAS?** DRBD es en tiempo real (no se pierde nada, RPO 0); la copia es periódica (se pierde lo escrito desde la última).

---

**Documentación completa, capturas, salidas de los comandos, configuraciones y scripts:** [https://github.com/ethan3232/iso-naix-un-sistema-individual](https://github.com/ethan3232/iso-naix-un-sistema-individual)
