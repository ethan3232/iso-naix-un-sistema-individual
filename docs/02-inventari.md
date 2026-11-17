# 02 · Inventario y diagnóstico

**Tasca 2** · Estado: 🟡 casa ✅ (falta SMART con `sudo`) · clase ⬜ (ejecutar `scripts/inventari.sh clase` en el aula)

Herramienta: [`scripts/inventari.sh`](../scripts/inventari.sh), que recoge hardware y hace diagnósticos de disco, memoria y red con el equipo **en reposo** (todas las VMs apagadas). Con `sudo` añade SMART (salud de los discos) y `dmidecode` (módulos de RAM).

## Equipo de clase (puesto 23)

> ⬜ Pendiente de ejecutar en el aula: `bash scripts/inventari.sh clase` y `sudo bash scripts/inventari.sh clase`.
> Datos conocidos: Intel Core Ultra 5 125H (14 núcleos / 18 hilos), 30 GiB de RAM, SSD SATA Kingston A400, red `eno1` a 1 Gb/s.

## Equipo de casa

Log completo: [`inventari-casa.txt`](../evidencies/logs/inventari-casa.txt) (17/11/2026, sin VMs encendidas).

| Componente | Detalle | Comentario |
|---|---|---|
| Placa base | Gigabyte **B560M DS3H V2** | Chipset Intel B560 (socket LGA1200) |
| CPU | Intel **Core i5-11400F** · 6 núcleos / 12 hilos · hasta 4,4 GHz · L3 12 MiB | **VT-x** activo (`vmx`, `/dev/kvm`) → apta para virtualizar. La "F" = sin gráfica integrada |
| RAM | **16 GB** (15,5 GiB útiles) | + 8 GB de swap en fichero + 3,9 GB de zram |
| Disco 1 (Linux + VMs) | **Kingston A400 960 GB** (SSD SATA) **dentro de una caja USB** (puente JMicron JMS583, driver `uas`) a **5 Gb/s** | `/` 58 GB + `/home` 388 GB (68 % usado). **Aquí están todas las VMs** |
| Disco 2 | Kingston A400 480 GB (SSD SATA interno) | NTFS (datos de Windows) |
| Disco 3 | **WD_BLACK SN7100 1 TB (NVMe PCIe)** | NTFS · Windows. **El disco más rápido del equipo y no lo usa Linux** |
| Gráfica | NVIDIA GeForce **RTX 3060** | No interviene en la virtualización con VirtualBox |
| Red | Realtek RTL8111 Gigabit · `enp4s0` a **1000 Mb/s** | IP 192.168.1.101 (router de casa) |
| Periféricos | Teclado Apple (ANSI), ratón inalámbrico, auriculares Logitech G435, controlador RGB | Teclado **ANSI** (distribución de EE. UU.) |
| Firmware | UEFI (`/boot/efi`) | |
| Temperatura en reposo | CPU 45 ºC | Normal |
| Virtualización | VirtualBox 7.0.20 · módulos `vboxdrv` y `kvm_intel` cargados | |

## Comparativa clase vs. casa

| | Clase | Casa | Consecuencia |
|---|---|---|---|
| CPU | Core Ultra 5 125H · **18 hilos** | i5-11400F · **12 hilos** | En casa caben menos vCPU repartidas sin que se pisen |
| RAM | **30 GiB** | **16 GB** | **El límite principal en casa**: unos 10 GB para VMs → un escenario cada vez y no el clúster de 3 nodos + NAS |
| Disco de las VMs | SSD SATA interno | **SSD SATA por USB 5 Gb/s** | Misma unidad (A400), pero en casa pasa además por el puente USB |
| Red | 1 Gb/s | 1 Gb/s | Igual. La red de las VMs es interna (no sale del PC) |
| Diagnóstico de disco | ⬜ | 303 MB/s escr. · 351 MB/s lect. · **347 IOPS** 4K sync | |
| Diagnóstico de RAM | ⬜ | 3,3 GB/s (copia en Python, sin errores) | |
| Internet | ⬜ | ~210–260 Mb/s · 17 ms a 1.1.1.1 | |

## Cuellos de botella y soluciones (casa)

| # | Cuello de botella | Evidencia | Solución propuesta | Coste |
|---|---|---|---|---|
| 1 | **Disco de las VMs por USB** | `lsblk` → `TRAN=usb`; el puente va a 5 Gb/s; **347 IOPS** en escritura 4K síncrona; en la Tasca 6 las escrituras caían a ~15 MB/s en **todos** los discos virtuales | Mover la carpeta `~/VirtualBox VMs` a un **disco interno**. Lo ideal es el **NVMe**, que es hasta ~10 veces más rápido. Como mínimo, conectar la caja a un puerto USB de **10 Gb/s** | 0 € (reorganizar discos) |
| 2 | **SSD Kingston A400** (sin DRAM, caché SLC pequeña) | En la Tasca 6 la escritura sostenida bajaba de ~400 a ~15–25 MB/s | Para muchas VMs a la vez, un SSD con DRAM o NVMe | ~60 € (NVMe de 1 TB) |
| 3 | **RAM de 16 GB** | Escenarios limitados a ~10 GB de VMs | Ampliar a 32 GB (la B560M tiene 4 ranuras DDR4) | ~50 € |
| 4 | CPU con 12 hilos | Con Proxmox anidado, cada nodo consume vCPU | Suficiente para 1 escenario; no es el límite principal | — |

> **Pregunta probable de defensa:** *"¿Cuál es el cuello de botella de tu equipo y cómo lo has demostrado?"* → En casa, el **disco**: las VMs están en un SSD SATA metido en una caja USB. Lo demuestran `lsblk` (`TRAN=usb`), las 347 IOPS y el comportamiento irregular de `fio` en la Tasca 6. La solución más barata es mover las VMs al NVMe interno.

## Diagnósticos (Apte+)

| Prueba | Herramienta | Condiciones | Resultado (casa) | Interpretación |
|---|---|---|---|---|
| Disco: escritura secuencial | `dd` 1 GiB, `oflag=direct` | VMs apagadas, en `/home` (SSD por USB) | **303 MB/s** | Cerca del techo del USB 5 Gb/s (~400–450 MB/s reales) |
| Disco: lectura secuencial | `dd` 1 GiB, `iflag=direct` | ídem | **351 MB/s** | Un A400 por SATA interno da ~500 MB/s → el USB recorta ~30 % |
| Disco: escritura aleatoria 4K síncrona | `dd` 2000 × 4 KiB, `dsync` | ídem | **347 IOPS** | Muy bajo: es el patrón típico de las VMs (muchas escrituras pequeñas) |
| Disco: RAID virtual | `fio` (ver [07](07-emmagatzematge-raid.md)) | 1 VM encendida | 14–436 MB/s según la ronda | Inestable: se satura la caché del SSD |
| RAM | `python3`, copia de 512 MiB + patrón 0x55 | reposo | **3,3 GB/s**, patrón sin errores | Correcto. Para un test completo: `memtest86+` desde GRUB |
| Red local | `ping` ×10 al router | reposo | 0 % de pérdida · **1,7 ms** | Bien (por cable) |
| Internet | `ping` a 1.1.1.1 · `curl` 50 MB (Cloudflare) | reposo | 0 % de pérdida · 17 ms · **210–260 Mb/s** | Bien. Es la velocidad contratada, no un límite del PC |
| Salud de discos | `smartctl -H -A` | ⬜ falta ejecutarlo con `sudo` | ⬜ | Por USB, SMART solo funciona si el puente lo deja pasar (`-d sat`) |
