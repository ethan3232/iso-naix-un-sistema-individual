# Tasca 7 · Rendimiento

**Módulos:** ISO-RA6, FDM-RA1 · **Estado:** ✓ Apte · ✓ Apte+

## Qué pide el enunciado

| Nivel | Criterio |
|---|---|
| Apte | Línea base y carga del anfitrión; qué VM satura qué recurso; cuántas VMs aguanta el equipo |
| Apte+ | Dos optimizaciones de las VMs con medidas antes y después |

## Qué he hecho

1. **Línea base** del anfitrión en reposo (CPU, RAM, disco, red) con mis scripts [`mide-vm.sh`](../scripts/mide-vm.sh) y [`mide-todas.sh`](../scripts/mide-todas.sh).
2. **Cada VM sola**: la he arrancado sin ninguna otra encendida y he medido su RAM real, el pico de CPU, la lectura de disco y lo que tarda en calmarse.
3. **Carga por recurso**: con SRV2 y SRV3 he metido carga de un solo tipo cada vez (CPU, RAM, disco, red) para ver qué satura qué.
4. **Capacidad**: he ido encendiendo VMs hasta el límite y lo he contrastado con el cálculo.
5. **Validación de las medidas**: tres de las primeras medidas eran falsas (disco a 0, RSS de VirtualBox, `dd` con ceros). Lo descubrí comparándolas con otra fuente y las corregí.

## Resultados


| Recurso | ¿Quién lo satura? | ¿Es el límite? |
|---|---|---|
| **RAM** | TrueNAS, WS2025-DC y PMX1 (~3 GB cada una) | ✓ **Sí: marca cuántas VMs caben** |
| **Disco** | Las Windows al arrancar; cualquier VM escribiendo | ✓ **Sí, con carga** (USB, 399 MB/s; iowait de hasta el 82 %) |
| **CPU** | Windows al arrancar (2 hilos) | ✗ No (máximo 32 %) |
| **Red interna** | Copias entre VMs, DRBD | ✗ No (12 Gbit/s con virtio) |

**¿Cuántas VMs aguanta?** En el PC de casa, unos **11 GB de VMs**: 5 VMs con el navegador abierto. El límite es la RAM y, con carga, el disco.

### Apte+: dos optimizaciones

| Optimización | Antes | Después | Decisión |
|---|---|---|---|
| **1. Tarjeta de red virtio-net** en lugar de Intel e1000 (SRV2 y SRV3) | 4,74 Gbit/s | **12,3 Gbit/s**, y la mitad de CPU por Gbit/s | ✓ Se mantiene |
| **2. Caché de E/S del anfitrión** en el disco de SRV2 | sin caché | ×60 en escritura, **×80 en `fsync`** | ✗ **Revertida**: escribe en la RAM del PC y un corte de luz perdería datos "ya escritos". En un servidor con RAID y DRBD no compensa |

Medida real de la optimización de red (`iperf3` entre SRV2 y SRV3, 3 rondas):

```
### antes-e1000 · NIC: 82540EM
ronda 1: 4.73 Gbit/s · CPU del host 28,4 % · 6,0 % de CPU por cada Gbit/s
ronda 3: 4.75 Gbit/s · CPU del host 27,5 % · 5,8 % de CPU por cada Gbit/s
### despues-virtio · NIC: virtio
ronda 1: 12.7 Gbit/s · CPU del host 33,7 % · 2,7 % de CPU por cada Gbit/s
ronda 3: 12.2 Gbit/s · CPU del host 37,1 % · 3,0 % de CPU por cada Gbit/s
```

## Evidencias

- Documento completo: [08-rendiment](../docs/08-rendiment.md)
- Logs: [`rend-por-vm.txt`](../evidencies/logs/rend-por-vm.txt) · [`rend-carga.txt`](../evidencies/logs/rend-carga.txt) · [`rend-capacidad.txt`](../evidencies/logs/rend-capacidad.txt) · [`optim-red-antes-e1000.txt`](../evidencies/logs/optim-red-antes-e1000.txt) · [`optim-red-despues-virtio.txt`](../evidencies/logs/optim-red-despues-virtio.txt) · [`optim-disco-antes-sin-cache.txt`](../evidencies/logs/optim-disco-antes-sin-cache.txt) · [`optim-disco-despues-con-cache.txt`](../evidencies/logs/optim-disco-despues-con-cache.txt)

## Desarrollo

### Línea base en reposo

Host sin ninguna VM ([`rend-base.csv`](../evidencies/logs/rend-base.csv), 60 s):

| CPU media | iowait | RAM disponible | Swap | Disco |
|---|---|---|---|---|
| **3,7 %** (máx. 5,2 %) | 0 % | **12 635 MB** de 15 859 | 0 | ~0 MB/s |

El host (Linux Mint + escritorio + navegador + terminal) ya se queda **~3,2 GB** para él: esa es la base de la **reserva del hipervisor**.

### Cada VM sola: qué consume al arrancar

Cada VM se arranca **sola**, se mide 120 s y se apaga por ACPI antes de la siguiente ([`rend-por-vm.txt`](../evidencies/logs/rend-por-vm.txt), [`rend-ram-real.txt`](../evidencies/logs/rend-ram-real.txt)).

Datos en bruto de cada medición (una muestra cada 2 s): `evidencies/logs/rend-<VM>-solo.csv` y `rend-DEB13-SRV2-carga-*.csv` · resumen: [`rend-resumen.txt`](../evidencies/logs/rend-resumen.txt).

| VM | RAM asignada | **RAM real** (caída de la disponible) | Pico CPU (hilos de 12) | Disco en el arranque | Arranque calmado* |
|---|---:|---:|---:|---:|---:|
| Mikrotik-IND | 512 MB | **108 MB** | 0,7 | 38 MB | 8 s |
| DEB13-SRV3 (web) | 1024 MB | 349 MB | 1,0 | 139 MB | 16 s |
| DEB13-SRV2 (ficheros + RAID) | 1024 MB | 1162 MB | 1,0 | 673 MB | 20 s |
| DEB13-SRV1-NFT | 2048 MB | 1134 MB | 1,1 | 495 MB | 22 s |
| OPNsense | 2048 MB | 2177 MB | 1,1 | 294 MB | 30 s |
| DEB13-CLI (escritorio) | 4096 MB | 1334 MB | 5,1 † | 583 MB | 30 s |
| PMX1 (Proxmox) | 4096 MB | 2738 MB | 1,5 | 486 MB | 32 s |
| WS2025-DC | 4096 MB | 2785 MB | 1,8 | 1358 MB | 22 s |
| W11-CLI | 4096 MB | 2257 MB | **2,0** | **2103 MB** | **68 s** |
| TrueNas | 4096 MB | **3144 MB** | 1,0 (media **51 %**) | 1113 MB | 20 s |

<sub>* Primer momento en que la VM se queda por debajo del 15 % de CPU durante 10 s. † El pico de DEB13-CLI no es su vCPU: son los hilos de E/S de VirtualBox leyendo disco (ese momento el host tuvo un **iowait del 82 %**).</sub>

![RAM asignada frente a real](../diagrames/ram-vms.png)
*Barra clara: RAM asignada · barra azul: RAM que pierde realmente el PC (caída de `MemAvailable`). Datos de la tabla de arriba. Fuente: [`diagrames/ram-vms.py`](../diagrames/ram-vms.py).*

**Lectura:**
- **RAM**: los que más gastan son **TrueNAS** (ZFS usa la RAM libre como caché ARC), **WS2025-DC** y **PMX1**. MikroTik apenas 108 MB.
- **CPU**: ninguna VM pasa de **2 hilos de 12**. Las Windows son las que más CPU piden al arrancar. TrueNAS se queda con un **51 % de un hilo** de media incluso en reposo (sus servicios de fondo).
- **Disco**: las **Windows** son las que más leen (W11: 2,1 GB y 68 s hasta calmarse). Es lo que más se nota con el SSD por USB.

### ¿Cuántas VMs aguanta mi equipo?

#### Prueba real

Con las 3 VMs encendidas voy arrancando más, **solo si después quedaría ≥ 1 GB libre** para el host ([`rend-capacidad.txt`](../evidencies/logs/rend-capacidad.txt)). Durante la prueba el host tenía abiertos Firefox y Chrome (~4 GB).

| Paso | RAM asignada total | RAM disponible (90 s después) | Swap |
|---|---:|---:|---:|
| MK + SRV2 + SRV3 | 2560 MB | 6626 MB | 0 |
| + DEB13-SRV1-NFT | 4608 MB | 5899 MB | 0 |
| + OPNsense | 6656 MB | 3858 MB | 4 MB |
| + TrueNas (4 GB) | — | **✗ no cabe** (3853 − 4096 < 1024) | — |
| + WS2025-DC (4 GB) | — | **✗ no cabe** | — |

→ **5 VMs** a la vez (6,6 GB asignados) con el navegador abierto.

#### Cálculo

```
RAM total del host ............................ 15 859 MB
− reserva del hipervisor (SO + escritorio) .... ~3 200 MB  (medido en la línea base)
− margen de seguridad .........................  1 024 MB
= RAM para VMs ................................ ~11 600 MB  (≈ 11 GB asignados)
  (con el navegador abierto: −4 GB → ~7 GB, como en la prueba)
```

**¿Por qué se cuenta la RAM asignada y no la real?** Porque la real **crece con el uso** hasta la asignada (TrueNAS llena su caché ZFS, Windows su caché de ficheros) y VirtualBox no la devuelve. Si sumo lo "real" y arranco más VMs, cuando trabajen todas el host irá a **swap** y todo se volverá lento.

| Escenario ([05](../docs/05-recursos.md)) | RAM asignada | Casa (~11 GB) | Clase (~23 GB) |
|---|---:|:---:|:---:|
| A · Comunicaciones (MK + CLI + NAS) | 8,7 GB | ✓ | ✓ |
| B · Dominio (MK + DC + W11 + NAS) | 12,8 GB | ✗ (se queda sin NAS: 8,7 GB) | ✓ |
| C · Clúster (MK + 2 PMX + NAS) | 12,8 GB | ✗ | ✓ |
| D · RAID / DRBD (MK + SRV2 + SRV3) | 2,5 GB | ✓ | ✓ |
| Todo el laboratorio (12 VMs) | 34,5 GB | ✗ | ✗ |

**Respuesta:** en casa, **unos 11 GB de VMs a la vez** (por ejemplo 2 VMs de 4 GB + 3 pequeñas, o 5–7 Debian/MikroTik). El límite es la **RAM**; con carga, el **disco** se nota antes que la CPU.

> **Pregunta probable de defensa:** *"Si tus VMs solo usan 1–3 GB reales, ¿por qué no arrancas más?"* → Porque es memoria que pueden reclamar en cualquier momento hasta lo asignado. Si me paso, el host entra en swap y se degradan **todas**. Mejor ajustar la RAM asignada a lo que necesita cada VM (DEB13-CLI usa 1,3 GB de 4).

## Cómo comprobarlo

```bash
vmstat 2                                   # wa = espera de disco · si/so = swap
bash scripts/mide-vm.sh DEB13-SRV2 60 solo # medir una VM
VBoxManage showvminfo DEB13-SRV2 | grep -i "nic 1"   # tipo de tarjeta: virtio
```

## Preguntas probables de la defensa

- **¿Cómo sabes que tus medidas son correctas?** Porque cada cifra se contrasta con otra fuente. Por ejemplo, la RAM de una VM no se mide con el RSS del proceso, sino con lo que baja la memoria disponible del PC: VirtualBox reserva la RAM desde su driver del kernel.
- **¿Por qué desactivaste una optimización que iba 80 veces más rápido?** Porque la velocidad venía de no escribir de verdad en el disco. En un servidor de ficheros, la seguridad de los datos va primero.
