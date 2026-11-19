# Tasca 2 · Equipos y periféricos

**Alumno:** izan · 1.º ASIX · Puesto 23 · Red `192.168.23.0/24` · Dominio `asix23.lan` · CIP FP Batoi · Curso 2026-2027

**Módulos:** FDM-RA1, FDM-RA4 · **Estado:**  Apte ·  Apte+

## Qué pide el enunciado

| Nivel | Criterio |
|---|---|
| Apte | Inventario del equipo de clase |
| Apte | Inventario del equipo de casa |
| Apte | Comparativa y cuellos de botella, con soluciones |
| Apte+ | Tests de memoria, disco y red en clase y en casa: herramienta, condiciones, resultado e interpretación |

## Qué he hecho

1. Script propio `scripts/inventari.sh` que recoge el hardware (CPU, RAM, discos, red, periféricos, batería, temperaturas) y hace pruebas de disco, memoria y red con el equipo **en reposo** (todas las VMs apagadas).
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

## Cómo comprobarlo

```bash
bash scripts/inventari.sh clase        # o: sudo bash scripts/inventari.sh casa
lsblk -o NAME,TRAN,MODEL               # TRAN=usb → el SSD va por USB
lsusb -t                               # velocidad del enlace: 5000M
```

## Por qué lo he hecho así

- **¿Cuál es el cuello de botella de tu equipo y cómo lo has demostrado?** El disco: `lsblk` muestra `TRAN=usb` y la prueba de 4K da ~350 IOPS iguales en dos PCs muy distintos. Si el límite fuera el PC, saldrían cifras distintas.
- **¿Por qué en clase `ping 1.1.1.1` falla y aun así hay Internet?** El cortafuegos del centro filtra el ICMP hacia fuera, pero HTTPS funciona (`curl` a github.com devuelve 200).
