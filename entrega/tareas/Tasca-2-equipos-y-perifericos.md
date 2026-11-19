# Tasca 2 · Equipos y periféricos

**Alumno:** izan · 1.º ASIX · Puesto 23 · Red `192.168.23.0/24` · Dominio `asix23.lan` · CIP FP Batoi · Curso 2026-2027

**Repositorio del proyecto:** [https://github.com/ethan3232/iso-naix-un-sistema-individual](https://github.com/ethan3232/iso-naix-un-sistema-individual) · **Esta tarea en GitHub:** [https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/Proyecto-por-Tareas/Tasca-2-equipos-y-perifericos.md](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/Proyecto-por-Tareas/Tasca-2-equipos-y-perifericos.md)

**Módulos:** FDM-RA1, FDM-RA4 · **Estado:**  Apte ·  Apte+

## Qué pide el enunciado

| Nivel | Criterio |
|---|---|
| Apte | Inventario del equipo de clase |
| Apte | Inventario del equipo de casa |
| Apte | Comparativa y cuellos de botella, con soluciones |
| Apte+ | Tests de memoria, disco y red en clase y en casa: herramienta, condiciones, resultado e interpretación |

## Qué he hecho

1. Script propio [`scripts/inventari.sh`](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/scripts/inventari.sh) que recoge el hardware (CPU, RAM, discos, red, periféricos, batería, temperaturas) y hace pruebas de disco, memoria y red con el equipo **en reposo** (todas las VMs apagadas).
2. Lo he ejecutado en los dos equipos:
   - **Clase:** portátil ASUS ExpertBook B3605CCA, el 18/11.
   - **Casa:** torre Gigabyte B560M, el 17/11, con `sudo` para incluir SMART y `dmidecode`.
3. He repetido las pruebas de disco varias veces para comprobar que los resultados se mantienen.

## Resultados

| | Clase | Casa |
|---|---|---|
| CPU | Core Ultra 5 125H · 18 hilos | i5-11400F · 12 hilos |
| RAM | 30 GiB | 16 GB (2 × 8 GB DDR4-2133) |
| Disco de las VMs | SSD Kingston A400 en caja **USB 5 Gb/s** | **El mismo SSD**, en la misma caja |
| Disco: escritura / lectura secuencial | 384–391 / 308–397 MB/s | 303–344 / 351–363 MB/s |
| Disco: 4K síncrono | **347–351 IOPS** | **347–350 IOPS** |
| RAM (copia de 512 MiB) | 3,1 GB/s, sin errores | 3,3 GB/s, sin errores |
| Internet | ~14 Mb/s · ICMP filtrado en el aula | 210–260 Mb/s |
| SMART | — (es el mismo SSD) | PASSED en los 3 discos |

Extracto real del inventario de clase (`scripts/inventari.sh`):

```
$ lsblk -o NAME,SIZE,TYPE,ROTA,TRAN,MODEL
NAME    SIZE   TYPE ROTA TRAN MODEL
sda     894.3G disk    1 usb  KINGSTON SA400S37960G
Escritura secuencial: 384 MB/s · Lectura secuencial: 308 MB/s
Escritura 4K síncrona: 347 IOPS
Ejecución 2: escritura 110 MB/s · lectura 397 MB/s · 4K sync 351 IOPS
Ejecución 3: escritura 391 MB/s · lectura 397 MB/s · 4K sync 348 IOPS
```

**Conclusión:** el disco da las **mismas ~350 IOPS en los dos ordenadores**, así que el límite es el SSD (sin DRAM) y el puente USB, no el PC. Lo que sí cambia entre los dos equipos es la **RAM**: en clase caben ~24 GB de VMs y en casa ~10 GB.

**Cuellos de botella y soluciones**

| Cuello de botella | Solución |
|---|---|
| SSD por USB 5 Gb/s (~350 IOPS) | Cable/puerto de 10 Gb/s (el puente lo admite); reducir escrituras (VMs sin escritorio, un escenario cada vez) |
| SSD A400 sin DRAM | A medio plazo, un NVMe en caja USB de 10 Gb/s |
| 16 GB de RAM en casa | Ampliar a 32 GB (quedan 2 ranuras libres) |
| RAM a 2133 MT/s en casa | Activar XMP en la BIOS si los módulos lo admiten |
| Internet del aula lento y con ICMP filtrado | Descargar las ISOs en casa; comprobar Internet con `curl` y DNS, no solo con `ping` |

## Desarrollo

### Equipo de clase (puesto 23)

Log completo: [`inventari-clase.txt`](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/evidencies/logs/inventari-clase.txt) (18/11/2026, todas las VMs apagadas, 3 ejecuciones del test de disco).

| Componente | Detalle | Comentario |
|---|---|---|
| Equipo | Portátil **ASUS ExpertBook B3605CCA** | Firmware UEFI |
| CPU | Intel **Core Ultra 5 125H** (Meteor Lake) · 14 núcleos (4 P + 8 E + 2 LP-E) / **18 hilos** · hasta 4,5 GHz · L3 18 MiB | **VT-x** activo (`vmx`, `/dev/kvm`). Núcleos híbridos: los E-cores son más lentos, por eso no conviene dar a una VM más vCPU de las necesarias |
| RAM | **30 GiB** utilizables (32 GB físicos; el resto lo reserva la gráfica integrada) | + 8 GB de swap en fichero + 7,6 GB de zram |
| Disco de Linux + VMs | **Kingston A400 960 GB** (SSD SATA) **dentro de la caja USB** (puente JMicron JMS583, driver `uas`) conectada a **5 Gb/s** | Atención: **También en clase va por USB**, no por SATA interno (`lsblk` → `TRAN=usb`, `lsusb -t` → `5000M`). Es el mismo SSD que me llevo a casa. `/` 58 GB + `/home` 381 GB (70 % usado) |
| Disco interno | Samsung **NVMe** 1 TB (PM9A1) | Es el disco del portátil (Windows y otras particiones del aula): **no se usa** para el proyecto |
| Puertos USB | El controlador del disco es de **20 Gb/s** (`lsusb -t` → `20000M/x2`), pero la caja negocia **5 Gb/s** | El puente JMS583 admite 10 Gb/s: con un cable USB-C 3.2 Gen 2 se podría doblar el techo |
| Gráfica | Intel **Arc** integrada (Meteor Lake-P) | No interviene en la virtualización |
| Red | Intel Ethernet (`eno1`) a **1000 Mb/s** + Wi-Fi Realtek RTL8852BE (apagada) | IP 172.16.222.207/24 (red del aula, DHCP) |
| Periféricos | Ratón Dell MS116, webcam FHD, lector de tarjetas Realtek, Bluetooth | |
| Batería | 100 %, **93 %** de la capacidad original, 19 ciclos | Portátil casi nuevo |
| Temperatura en reposo | CPU 61 ºC | Normal en un portátil fino (más alta que la torre de casa) |
| Virtualización | VirtualBox 7.0.20 · módulos `vboxdrv` y `kvm_intel` cargados | |

> SMART y `dmidecode` necesitan `sudo` (contraseña del aula). El SMART del SSD ya está hecho en casa (es el mismo disco: **PASSED**, 0 sectores reasignados).

### Equipo de casa

Log completo: [`inventari-casa.txt`](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/evidencies/logs/inventari-casa.txt) (17/11/2026 19:28, ejecutado con `sudo`, todas las VMs apagadas).

| Componente | Detalle | Comentario |
|---|---|---|
| Placa base | Gigabyte **B560M DS3H V2** | Chipset Intel B560 (socket LGA1200) |
| CPU | Intel **Core i5-11400F** · 6 núcleos / 12 hilos · hasta 4,4 GHz · L3 12 MiB | **VT-x** activo (`vmx`, `/dev/kvm`) → apta para virtualizar. La "F" = sin gráfica integrada |
| RAM | **16 GB** = 2 × 8 GB **DDR4 a 2133 MT/s** (canales A y B → *dual channel*) | La placa tiene **4 ranuras** (máx. 64 GB): quedan 2 libres para ampliar. + 8 GB de swap en fichero + 3,9 GB de zram |
| Disco 1 (Linux + VMs) | **Kingston A400 960 GB** (SSD SATA) **dentro de una caja USB** (puente JMicron JMS583, driver `uas`) a **5 Gb/s** | Es **el mismo SSD del PC de clase**: me lo llevo a casa y arranco desde él por USB. `/` 58 GB + `/home` 388 GB (68 % usado). **Aquí están todas las VMs** |
| Disco 2 | Kingston A400 480 GB (SSD SATA interno) | NTFS (datos de Windows) |
| Disco 3 | **WD_BLACK SN7100 1 TB (NVMe PCIe)** | NTFS · Windows de casa. **No se puede usar** para el proyecto: el entorno tiene que ir en el SSD de clase |
| Gráfica | NVIDIA GeForce **RTX 3060** | No interviene en la virtualización con VirtualBox |
| Red | Realtek RTL8111 Gigabit · `enp4s0` a **1000 Mb/s** | IP 192.168.1.101 (router de casa) |
| Periféricos | Teclado Apple (ANSI), ratón inalámbrico, auriculares Logitech G435, controlador RGB | Teclado **ANSI** (distribución de EE. UU.) |
| Firmware | UEFI (`/boot/efi`) | |
| Salud de los discos (SMART) | Los 3 discos: **PASSED** · SSD de clase: **2466 h** encendido, **0** sectores reasignados, 31 ºC (máx. histórico 43 ºC) · A400 480 GB: 8067 h, 0 reasignados · NVMe: 0 % de desgaste, 3,9 TB escritos | SMART pasa a través del puente USB (`-d sat`). Curiosidad: por USB el kernel marca el SSD como `rotacional=1` (el puente no informa del tipo); no es un disco mecánico |
| Temperatura en reposo | CPU 45 ºC | Normal |
| Virtualización | VirtualBox 7.0.20 · módulos `vboxdrv` y `kvm_intel` cargados | |

### Diagnósticos (Apte+)

| Prueba | Herramienta | Condiciones | Resultado (casa) | Resultado (clase) | Interpretación |
|---|---|---|---|---|---|
| Disco: escritura secuencial | `dd` 1 GiB, `oflag=direct` | VMs apagadas, en `/home` (SSD por USB) | **303 / 344 MB/s** (2 ejecuciones) | **384 / 110 / 391 MB/s** (3 ejecuciones) | Cerca del techo del USB 5 Gb/s (~400–450 MB/s reales). El 110 de clase es una caída puntual: el A400 no tiene DRAM y, si su caché SLC aún se está vaciando de la prueba anterior, la escritura se hunde. Por eso se repite la prueba |
| Disco: lectura secuencial | `dd` 1 GiB, `iflag=direct` | ídem | **351 / 363 MB/s** | **308 / 397 / 397 MB/s** | Un A400 por SATA interno da ~500 MB/s → el puente USB recorta ~20–30 % en los dos equipos |
| Disco: escritura aleatoria 4K síncrona | `dd` 2000 × 4 KiB, `dsync` | ídem | **347 / 350 IOPS** | **347 / 351 / 348 IOPS** | Muy bajo y **calcado en los dos PCs** → lo limita el SSD + el USB, no la CPU ni la placa. Es el patrón típico de las VMs (muchas escrituras pequeñas) |
| Disco: RAID virtual | `fio` (ver [07](https://github.com/ethan3232/iso-naix-un-sistema-individual/blob/main/docs/07-emmagatzematge-raid.md)) | 1 VM encendida | 14–436 MB/s según la ronda | — (mismo disco) | Inestable: se satura la caché del SSD |
| RAM | `python3`, copia de 512 MiB + patrón 0x55 | reposo | **3,3 GB/s**, sin errores | **3,1 GB/s**, sin errores | Correcto. Mide más a Python que a la RAM. Para un test completo: `memtest86+` desde GRUB |
| Red local | `ping` ×10 al router | reposo | 0 % de pérdida · **1,7 ms** | 0 % de pérdida · **0,5 ms** | Bien (por cable) |
| Internet | `ping` a 1.1.1.1 · `curl` 50 MB (Cloudflare) | reposo | 0 % de pérdida · 17 ms · **210–260 Mb/s** | ping **100 % de pérdida** (también a 8.8.8.8) · 50 MB en 28,6 s = **~14 Mb/s** (el primer intento agotó los 30 s) | Casa: es la velocidad contratada. Clase: el cortafuegos del centro **filtra el ICMP** hacia Internet (HTTPS sí funciona: `curl` a github.com → 200) y la conexión se comparte entre todo el aula. Lección: en clase, `ping 1.1.1.1` fallando **no** significa "sin Internet" |
| Salud de discos | `smartctl -H -A` (con `sudo`) | reposo | **PASSED** en los 3 · 0 sectores reasignados · SSD de clase a 31 ºC | El SSD de las VMs es el mismo (ya medido) | Discos sanos: el bajo rendimiento de 4K **no es una avería**, es el tipo de SSD (sin DRAM) + el USB. El puente JMS583 deja pasar SMART |
| Módulos de RAM | `dmidecode -t memory` | — | 2 × 8 GB DDR4-2133 en canales A y B | (necesita `sudo` del aula) | Casa: *dual channel* bien montado, a **2133 MT/s** (JEDEC). El i5-11400F admite DDR4-3200: activar XMP en la BIOS daría más ancho de banda (mejora gratuita) |
| Batería (solo clase) | `/sys/class/power_supply/BAT*` | — | — | 100 %, **93 %** de la capacidad de fábrica, 19 ciclos | Batería sana |

> **Conclusión de la comparativa:** la hipótesis inicial era "en clase el disco va por SATA y será más rápido". El inventario la ha **refutado**: en los dos sitios el SSD va en la misma caja USB y da las mismas ~350 IOPS. Por eso **no se repite la Tasca 7 en clase**: compararía el mismo disco consigo mismo. Lo que sí cambia entre los dos equipos es la **RAM** (cuántas VMs caben) y, un poco, la CPU.

## Cómo comprobarlo

```bash
bash scripts/inventari.sh clase        # o: sudo bash scripts/inventari.sh casa
lsblk -o NAME,TRAN,MODEL               # TRAN=usb → el SSD va por USB
lsusb -t                               # velocidad del enlace: 5000M
```

## Por qué lo he hecho así

- **¿Cuál es el cuello de botella de tu equipo y cómo lo has demostrado?** El disco: `lsblk` muestra `TRAN=usb` y la prueba de 4K da ~350 IOPS iguales en dos PCs muy distintos. Si el límite fuera el PC, saldrían cifras distintas.
- **¿Por qué en clase `ping 1.1.1.1` falla y aun así hay Internet?** El cortafuegos del centro filtra el ICMP hacia fuera, pero HTTPS funciona (`curl` a github.com devuelve 200).

---

**Documentación completa, capturas, salidas de los comandos, configuraciones y scripts:** [https://github.com/ethan3232/iso-naix-un-sistema-individual](https://github.com/ethan3232/iso-naix-un-sistema-individual)
