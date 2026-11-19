# 02 · Inventario y diagnóstico

**Tasca 2** · Estado: ✓ casa (con SMART y `dmidecode`) · ✓ clase (18/11/2026, en el aula)

Herramienta: [`scripts/inventari.sh`](../scripts/inventari.sh), que recoge hardware y hace diagnósticos de disco, memoria y red con el equipo **en reposo** (todas las VMs apagadas). Con `sudo` añade SMART (salud de los discos) y `dmidecode` (módulos de RAM).

## Equipo de clase (puesto 23)

Log completo: [`inventari-clase.txt`](../evidencies/logs/inventari-clase.txt) (18/11/2026, todas las VMs apagadas, 3 ejecuciones del test de disco).

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

## Equipo de casa

Log completo: [`inventari-casa.txt`](../evidencies/logs/inventari-casa.txt) (17/11/2026 19:28, ejecutado con `sudo`, todas las VMs apagadas).

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

## Comparativa clase vs. casa

| | Clase | Casa | Consecuencia |
|---|---|---|---|
| Tipo de equipo | Portátil ASUS ExpertBook | Torre Gigabyte B560M | El portátil se calienta más (61 ºC en reposo frente a 45 ºC): con carga larga puede bajar frecuencia |
| CPU | Core Ultra 5 125H · **18 hilos** (híbrida) | i5-11400F · **12 hilos** (todos iguales) | En clase caben más vCPU repartidas; en casa cada hilo es "completo" |
| RAM | **30 GiB** | **16 GB** | **La diferencia que más importa**: en clase ~24 GB para VMs (los 4 escenarios), en casa ~10 GB (un escenario cada vez, sin el clúster de 3 nodos + NAS) |
| Disco de las VMs | El SSD A400 en la caja **USB 5 Gb/s** | **El mismo SSD y la misma caja**, USB 5 Gb/s | **Igual en los dos sitios.** Antes pensaba que en clase iba por SATA: el inventario lo ha desmentido |
| Red | 1 Gb/s (Intel) | 1 Gb/s (Realtek) | Igual. La red de las VMs es interna (no sale del PC) |
| Diagnóstico de disco | 110–391 MB/s escr. · 308–397 MB/s lect. · **347–351 IOPS** 4K sync (3 ejecuciones) | 303–344 MB/s escr. · 351–363 MB/s lect. · **347–350 IOPS** (2 ejecuciones) | **Prácticamente idénticos** → el límite es el SSD + el puente USB, no el ordenador |
| Diagnóstico de RAM | 3,1 GB/s (copia en Python, sin errores) | 3,3 GB/s | Igual: la prueba en Python mide sobre todo al propio Python, no la RAM |
| Red local | 0 % pérdida · **0,5 ms** al router del aula | 0 % pérdida · 1,7 ms | Las dos bien |
| Internet | Ping a 1.1.1.1 y 8.8.8.8 **bloqueado** (100 % pérdida) · descarga **~14 Mb/s** (50 MB en 28,6 s) | 17 ms · ~210–260 Mb/s | En el aula el ICMP hacia fuera está filtrado y la salida es compartida por toda la clase. **Las ISOs grandes se descargan en casa** |

## Cuellos de botella y soluciones

| # | Cuello de botella | Evidencia | Solución propuesta | Coste |
|---|---|---|---|---|
| 1 | **Disco de las VMs por USB** | `lsblk` → `TRAN=usb`; el puente va a 5 Gb/s; **347 IOPS** en escritura 4K síncrona; en la Tasca 6 las escrituras caían a ~15 MB/s en **todos** los discos virtuales | El entorno **tiene que ir en el SSD de clase** (el NVMe de casa no se puede usar). Lo que sí se puede hacer: (a) conectar la caja a un puerto USB de **10 Gb/s** (el puente JMS583 lo admite); (b) reducir lo que escriben las VMs: VMs sin escritorio, un escenario cada vez y caché del host solo en las VMs sin datos importantes (c) a medio plazo, un SSD NVMe en caja USB de 10 Gb/s | 0 € |
| 2 | **SSD Kingston A400** (sin DRAM, caché SLC pequeña) | En la Tasca 6 la escritura sostenida bajaba de ~400 a ~15–25 MB/s | Para muchas VMs a la vez, un SSD con DRAM o NVMe | ~60 € (NVMe de 1 TB) |
| 3 | **RAM de 16 GB** | Escenarios limitados a ~10 GB de VMs | Ampliar a 32 GB (la B560M tiene 4 ranuras DDR4) | ~50 € |
| 4 | CPU con 12 hilos (casa) | Con Proxmox anidado, cada nodo consume vCPU | Suficiente para 1 escenario; no es el límite principal | — |
| 5 | **Clase:** el mismo disco por USB | Mismas IOPS que en casa (347–351) aunque el portátil es más potente | Igual que el nº 1: cable USB 3.2 Gen 2 (el puerto del portátil es de 20 Gb/s) | ~10 € |
| 6 | **Clase:** temperatura del portátil | 61 ºC en reposo | Usarlo enchufado y sobre una superficie dura; no encender más escenarios de los necesarios | 0 € |
| 7 | **Clase:** Internet del aula lento y con ICMP filtrado | ~14 Mb/s; `ping 1.1.1.1` sin respuesta | Descargar ISOs en casa y comprobar Internet de las VMs con `curl`/DNS, no solo con `ping` | 0 € |

> **Pregunta probable de defensa:** *"¿Cuál es el cuello de botella de tu equipo y cómo lo has demostrado?"* → El **disco**, en clase y en casa: las VMs están en un SSD A400 (sin DRAM) dentro de una caja USB a 5 Gb/s. Lo demuestran `lsblk` (`TRAN=usb`), las **~350 IOPS iguales en los dos ordenadores** (si el límite fuera el PC, saldrían distintas) y el `fio` irregular de la Tasca 6. La RAM marca *cuántas* VMs caben (24 GB en clase, 10 en casa); el disco marca *lo rápido* que van. Solución: cable/puerto de 10 Gb/s y reducir escrituras.

## Diagnósticos (Apte+)

| Prueba | Herramienta | Condiciones | Resultado (casa) | Resultado (clase) | Interpretación |
|---|---|---|---|---|---|
| Disco: escritura secuencial | `dd` 1 GiB, `oflag=direct` | VMs apagadas, en `/home` (SSD por USB) | **303 / 344 MB/s** (2 ejecuciones) | **384 / 110 / 391 MB/s** (3 ejecuciones) | Cerca del techo del USB 5 Gb/s (~400–450 MB/s reales). El 110 de clase es una caída puntual: el A400 no tiene DRAM y, si su caché SLC aún se está vaciando de la prueba anterior, la escritura se hunde. Por eso se repite la prueba |
| Disco: lectura secuencial | `dd` 1 GiB, `iflag=direct` | ídem | **351 / 363 MB/s** | **308 / 397 / 397 MB/s** | Un A400 por SATA interno da ~500 MB/s → el puente USB recorta ~20–30 % en los dos equipos |
| Disco: escritura aleatoria 4K síncrona | `dd` 2000 × 4 KiB, `dsync` | ídem | **347 / 350 IOPS** | **347 / 351 / 348 IOPS** | Muy bajo y **calcado en los dos PCs** → lo limita el SSD + el USB, no la CPU ni la placa. Es el patrón típico de las VMs (muchas escrituras pequeñas) |
| Disco: RAID virtual | `fio` (ver [07](07-emmagatzematge-raid.md)) | 1 VM encendida | 14–436 MB/s según la ronda | — (mismo disco) | Inestable: se satura la caché del SSD |
| RAM | `python3`, copia de 512 MiB + patrón 0x55 | reposo | **3,3 GB/s**, sin errores | **3,1 GB/s**, sin errores | Correcto. Mide más a Python que a la RAM. Para un test completo: `memtest86+` desde GRUB |
| Red local | `ping` ×10 al router | reposo | 0 % de pérdida · **1,7 ms** | 0 % de pérdida · **0,5 ms** | Bien (por cable) |
| Internet | `ping` a 1.1.1.1 · `curl` 50 MB (Cloudflare) | reposo | 0 % de pérdida · 17 ms · **210–260 Mb/s** | ping **100 % de pérdida** (también a 8.8.8.8) · 50 MB en 28,6 s = **~14 Mb/s** (el primer intento agotó los 30 s) | Casa: es la velocidad contratada. Clase: el cortafuegos del centro **filtra el ICMP** hacia Internet (HTTPS sí funciona: `curl` a github.com → 200) y la conexión se comparte entre todo el aula. Lección: en clase, `ping 1.1.1.1` fallando **no** significa "sin Internet" |
| Salud de discos | `smartctl -H -A` (con `sudo`) | reposo | **PASSED** en los 3 · 0 sectores reasignados · SSD de clase a 31 ºC | El SSD de las VMs es el mismo (ya medido) | Discos sanos: el bajo rendimiento de 4K **no es una avería**, es el tipo de SSD (sin DRAM) + el USB. El puente JMS583 deja pasar SMART |
| Módulos de RAM | `dmidecode -t memory` | — | 2 × 8 GB DDR4-2133 en canales A y B | (necesita `sudo` del aula) | Casa: *dual channel* bien montado, a **2133 MT/s** (JEDEC). El i5-11400F admite DDR4-3200: activar XMP en la BIOS daría más ancho de banda (mejora gratuita) |
| Batería (solo clase) | `/sys/class/power_supply/BAT*` | — | — | 100 %, **93 %** de la capacidad de fábrica, 19 ciclos | Batería sana |

> **Conclusión de la comparativa:** la hipótesis inicial era "en clase el disco va por SATA y será más rápido". El inventario la ha **refutado**: en los dos sitios el SSD va en la misma caja USB y da las mismas ~350 IOPS. Por eso **no se repite la Tasca 7 en clase**: compararía el mismo disco consigo mismo. Lo que sí cambia entre los dos equipos es la **RAM** (cuántas VMs caben) y, un poco, la CPU.
