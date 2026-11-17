# 05 · Recursos

**Tasca 4** · Estado: ✅ · Datos sacados de VirtualBox con `VBoxManage showvminfo` (no estimados).

## Tabla de máquinas

Host de todas: **eth4n** (Linux Mint 22.3, Core Ultra 5 125H 14C/18T, 30 GiB RAM, SSD SATA Kingston A400 960 GB). Hipervisor: VirtualBox 7.0.20. Grupo de VMs: `ISO-INDV`.

| Nombre (VM) | Función | SO | vCPU | RAM | Disco | Red (VirtualBox) | Firmware |
|---|---|---|---|---|---|---|---|
| Mikrotik-IND | Comunicaciones · gateway .1 | RouterOS 7.24.5 x86 | 2 | 512 MB | 2 GB | NAT + LAN23 | BIOS |
| OPNsense | Comunicaciones · .2 | OPNsense 26.7 | 2 | 2 GB | 20 GB | NAT + LAN23 | BIOS |
| DEB13-SRV1-NFT | Comunicaciones · .3 (nftables) | Debian 13 | 1 | 2 GB | 20 GB | NAT + LAN23 | BIOS |
| TrueNas | NAS · .10 | TrueNAS SCALE 25.10.7 | 2 | 4 GB | 32 + 20 + 20 GB | LAN23 | BIOS |
| PMX1 | Virtualización · nodo 1 · .11 | Proxmox VE 9.2 | 2 | 4 GB | 20 GB | LAN23 (promiscuo) | BIOS |
| PMX2 | Virtualización · nodo 2 · .12 | Proxmox VE 9.2 | 2 | 4 GB | 32 GB | LAN23 (promiscuo) | BIOS |
| PMX3 | Virtualización · nodo 3 · .13 | Proxmox VE 9.2 | 2 | 4 GB | 20 GB | LAN23 (promiscuo) | BIOS |
| DEB13-SRV2 | Ficheros · RAID 0/1/5 (mdadm) · espejo DRBD · .21 | Debian 13 | 1 | 1 GB | 20 GB + 8 × 1 GB (RAID) + 1 GB (DRBD) | LAN23 (**virtio**) | BIOS |
| DEB13-SRV3 | Web (Apache) · espejo DRBD · .22 | Debian 13 | 1 | 1 GB | 20 GB + 1 GB (DRBD) | LAN23 (**virtio**) | BIOS |
| WS2025-DC | Dominio AD DS + DNS · .20 | Windows Server 2025 Std (escritorio) | 2 | 4 GB | 50 GB | LAN23 | **UEFI + TPM 2.0** |
| (LXC en PMX) | Servidor de infraestructura · .30 | Debian 13 (contenedor) | 1 | 512 MB | 8 GB | vmbr0 → LAN23 | — |
| W11-CLI | Cliente Administración · .51 | Windows 11 Pro 25H2 | 2 | 4 GB | 64 GB | LAN23 | **UEFI + TPM 2.0** |
| DEB13-CLI | Cliente Informática · .54 | Debian 13 (GNOME) | 1 | 4 GB | 20 GB | LAN23 | BIOS |

Discos: **VDI de reserva dinámica** (solo ocupan lo que se usa). Ocupación real: ver [inventario](02-inventari.md).

## Recursos simultáneos y reserva del hipervisor

| Concepto | Clase | Casa |
|---|---|---|
| **Suma de todas las VMs** (12 VMs de VirtualBox, 20 vCPU) | **34,5 GB** | **34,5 GB** |
| Recursos físicos del host | 18 hilos · 30 GiB | 12 hilos · 15,5 GiB |
| Reserva para el host (Linux Mint + escritorio + navegador + VirtualBox) | **~6 GB** | ~3,2 GB medidos sin navegador ([08 §1](08-rendiment.md)) + 1 GB de margen |
| **Disponible para VMs** | **~24 GB** | **~11 GB** (≈ 7 GB con el navegador abierto: **5 VMs** en la prueba real) |

**Conclusión**: no se pueden encender todas a la vez (34,5 GB > 24 GB en clase y > 11 GB en casa). La CPU no es el problema (las VMs pasan la mayor parte del tiempo esperando), pero la **RAM** sí: VirtualBox reserva la RAM de cada VM encendida y, si no cabe, el host empieza a usar swap y todo se bloquea. Por eso se trabaja por **escenarios**.

> La vCPU sí se puede "sobresuscribir" (dar más vCPU que hilos reales) porque se reparten por turnos. La RAM no: cada MB asignado a una VM se le quita al host.

## Escenarios de arranque

| Escenario | VMs encendidas | RAM | ¿Para qué? |
|---|---|---|---|
| **A · Comunicaciones** | router activo (.1, .2 o .3) + DEB13-CLI + TrueNas | 9–10,5 GB | Pruebas de gateway, NAT, cortafuegos, copias |
| **B · Dominio** | Mikrotik-IND + WS2025-DC + W11-CLI + TrueNas | 12,5 GB | AD DS, DNS, unión al dominio |
| **C · Clúster** | Mikrotik-IND + PMX1 + PMX2 + TrueNas | 12,5 GB | Clúster, migraciones, contenedor |
| **D · RAID / rendimiento** | Mikrotik-IND + DEB13-SRV2 + DEB13-SRV3 | 2,5 GB | RAID con mdadm, espejo DRBD, carga y optimizaciones (Tasca 7) |
| **E · Máximo** | Se van encendiendo mientras quede ≥ 1 GB libre | casa: 6,6 GB (5 VMs) | Tasca 7: límite real medido ([08 §4](08-rendiment.md)) |

> En **casa** (16 GB) caben A y D. B y C solo en clase (o en casa sin el NAS).

## Cuello de botella observado

Durante la instalación simultánea de WS2025-DC, W11-CLI y OPNsense ([log](../evidencies/logs/host-carga-3-instalaciones.txt)):

```
procs  ... -cpu-------
 r  b  ... us sy id wa
 0  3  ...  1  2 81 16
 3  1  ...  1  3 83 13
```

- `id` 80–83 % → la **CPU está casi libre**.
- `wa` 13–16 % y `b` = 3 → **procesos bloqueados esperando al disco**.

El cuello de botella es el **SSD SATA** (Kingston A400, sin caché DRAM), no la CPU ni la RAM. Mejora propuesta: mover las VMs al **NVMe** de 1 TB (otra partición del portátil, ~5–7 veces más rápido) o no instalar varios sistemas a la vez.
