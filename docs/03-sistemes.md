# 03 · Sistemas elegidos

**Tasca 5.1** · Estado: ✓ imágenes verificadas · Fecha de consulta de las fuentes: **17/11/2026**

## Tabla de sistemas

| Función | Sistema y versión | Imagen | Fuente oficial | Licencia | SHA256 |
|---|---|---|---|---|---|
| Comunicaciones (principal) | MikroTik RouterOS 7.24.5 (x86) | `mikrotik-7.24.5.iso` | <https://mikrotik.com/download> | Propietaria; x86 necesita clave (demo 24 h) | ✓ coincide |
| Comunicaciones (alternativo) | OPNsense 26.7 | `OPNsense-26.7-dvd-amd64.iso` | <https://opnsense.org/download/> | BSD 2-Clause (libre y gratuito) | N/C ¹ |
| Comunicaciones (alternativo) | Debian 13.1 + nftables | `debian-13.1.0-amd64-netinst.iso` | <https://www.debian.org/distrib/netinst> | Libre (DFSG) | ✓ coincide |
| NAS / copias | TrueNAS SCALE 25.10.7 (Goldeye) | `TrueNAS-SCALE-25.10.7.iso` | <https://www.truenas.com/download-truenas-scale/> | Libre (GPL); soporte de pago opcional | ✓ coincide |
| Virtualización | Proxmox VE 9.2-1 | `proxmox-ve_9.2-1.iso` | <https://www.proxmox.com/en/downloads> | AGPLv3; suscripción opcional para el repo *enterprise* | ✓ coincide |
| Dominio | Windows Server 2025 Standard Evaluation (26100.1742) | `w2k25.iso` | <https://www.microsoft.com/evalcenter/download-windows-server-2025> | Propietaria; evaluación de 180 días | N/C ² |
| Cliente Windows | Windows 11 Pro 25H2 (26200.6584) | `win11.iso` | <https://www.microsoft.com/software-download/windows11> | Propietaria; sin activar en el laboratorio | N/C ² |
| Cliente Linux | Debian 13.1 (GNOME) | `debian-13.1.0-amd64-netinst.iso` | <https://www.debian.org/distrib/netinst> | Libre (DFSG) | ✓ coincide |

Resultado completo con todos los hashes y las URL de los valores oficiales: [`evidencies/logs/sha256-isos.txt`](../evidencies/logs/sha256-isos.txt).

¹ **OPNsense** publica el SHA256 del archivo **comprimido** (`.iso.bz2`), no de la ISO ya descomprimida. Como solo conservamos la ISO, no se puede comparar. *Propuesta de comprobación*: descargar de nuevo el `.bz2` (~500 MB), comprobar su hash y descomprimirlo.

² **Microsoft** no publica un fichero de sumas SHA256 junto a las ISOs de evaluación/consumo de forma estable. Se guarda el hash calculado para poder comprobar en el futuro que la imagen no ha cambiado. *Propuesta*: comparar con el hash que muestra la página de descarga de Microsoft en el momento de descargar.

## ¿Por qué verificar el SHA256?

El SHA256 es una "huella" de 64 caracteres del archivo. Si cambia **un solo bit** de la ISO (descarga corrupta o imagen manipulada por un atacante), la huella sale totalmente distinta. Comparar nuestra huella con la que publica el fabricante en su web demuestra que la imagen es **íntegra y auténtica**.

```bash
sha256sum mikrotik-7.24.5.iso
# 4bff16b8ee455eb00a0a5f183936fb0ecfd8f2bf3f5ba1ba64773d8375aaec02 → igual que mikrotik-7.24.5.iso.sha256 de MikroTik
```

## Requisitos mínimos oficiales vs. recursos del laboratorio

| Sistema | Mínimo oficial | Asignado en el laboratorio | Comentario |
|---|---|---|---|
| RouterOS x86 | 64–256 MB RAM | 2 vCPU · 512 MB · 2 GB | Sobra; consume ~200 MB |
| OPNsense | 2 GB RAM recomendado (mín. 1 GB), 20 GB disco | 2 vCPU · 2 GB · 20 GB | Recomendado |
| Debian 13 con GNOME | 1 GB RAM (2 GB recomendado con escritorio) | SRV: 1 vCPU · 2 GB · CLI: 1 vCPU · 4 GB | El SRV no necesita escritorio (optimización Tasca 7) |
| TrueNAS SCALE | **8 GB RAM**, 16 GB disco de arranque | 2 vCPU · 4 GB · 32 GB + 2×20 GB | Atención: Por debajo del mínimo: aceptado solo para pruebas (pocos datos) |
| Proxmox VE | 2 GB RAM (más la de las VMs), CPU con VT-x | 4 vCPU · 6 GB · 20 GB, *nested VT-x* | Virtualización anidada activada |
| Windows Server 2025 | 512 MB (Core) / **2 GB con escritorio**, 32 GB disco, UEFI + TPM 2.0 recomendados | 2 vCPU · 4 GB · 50 GB · EFI · TPM 2.0 | Con escritorio para gestionarlo por GUI |
| Windows 11 | **4 GB RAM, 64 GB disco, UEFI + Secure Boot, TPM 2.0** | 2 vCPU · 4 GB · 64 GB · EFI · TPM 2.0 | Justo en el mínimo |

## Firmware y arranque (Tasca 5.2)

| VM | Firmware | Motivo |
|---|---|---|
| Windows Server 2025 / Windows 11 | **UEFI + TPM 2.0** | Windows 11 lo exige; en Server 2025 es lo recomendado (arranque seguro, BitLocker) |
| MikroTik, OPNsense, Debian, TrueNAS, Proxmox | BIOS | Funcionan sin problema en BIOS y es lo más sencillo en VirtualBox |
