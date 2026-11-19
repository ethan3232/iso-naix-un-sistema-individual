<div align="center">

# Naix un sistema
### Entorno de pruebas individual · ASIX ThinkLab V2.0

**1º ASIX** · Módulos **ISO** y **FDM** · Puesto **23** · Red `192.168.23.0/24` · Alumno: **izan**

![VirtualBox](https://img.shields.io/badge/VirtualBox-7.0-183A61?style=for-the-badge&logo=virtualbox&logoColor=white)
![MikroTik](https://img.shields.io/badge/RouterOS-7.24-293239?style=for-the-badge&logo=mikrotik&logoColor=white)
![OPNsense](https://img.shields.io/badge/OPNsense-26.7-D94F00?style=for-the-badge&logo=opnsense&logoColor=white)
![Debian](https://img.shields.io/badge/Debian-13-A81D33?style=for-the-badge&logo=debian&logoColor=white)
<br>
![TrueNAS](https://img.shields.io/badge/TrueNAS_SCALE-25.10-0095D5?style=for-the-badge&logo=truenas&logoColor=white)
![Proxmox](https://img.shields.io/badge/Proxmox_VE-9.2-E57000?style=for-the-badge&logo=proxmox&logoColor=white)
![Windows Server](https://img.shields.io/badge/Windows_Server-2025-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![Windows 11](https://img.shields.io/badge/Windows-11_Pro-0078D4?style=for-the-badge&logo=windows11&logoColor=white)
<br>
![mdadm](https://img.shields.io/badge/RAID-0%20%C2%B7%201%20%C2%B7%205-5C2D91?style=for-the-badge&logo=linux&logoColor=white)
![DRBD](https://img.shields.io/badge/DRBD-espejo%20por%20red-BE185D?style=for-the-badge&logo=linux&logoColor=white)
![Estado](https://img.shields.io/badge/estado-Apte%20%2B%20Apte%2B-2EA44F?style=for-the-badge)
![Memoria](https://img.shields.io/badge/memoria-PDF-B91C1C?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)

*Simulación en VirtualBox del sistema informático de la empresa: tres servidores de comunicaciones, NAS con copias automáticas, clúster de virtualización, dominio de Active Directory y clientes, con RAID local y por red, medidas de rendimiento con optimizaciones y plan de contingencia probado.*

</div>

---

## 1. Resumen

| | |
|---|---|
| **Red** | LAN interna `LAN23` (192.168.23.0/24), dominio **`asix23.lan`**. 3 routers intercambiables (.1/.2/.3) con NAT y cortafuegos probados |
| **Datos** | TrueNAS con pool **espejo** `copias` → recibe cada noche las configuraciones de los equipos y las imágenes de las VMs |
| **Virtualización** | Clúster Proxmox **`asix23`** de 3 nodos: contenedor `srv-infra` (intranet) y VM de prueba. Migración en caliente con **8 ms** de corte |
| **Identidades** | Windows Server 2025 como **DC + DNS**, OUs por departamento, Windows 11 unido al dominio |
| **Almacenamiento** | RAID **0, 1 y 5** con `mdadm` (fallos y reconstrucción probados) + **espejo por red DRBD** entre dos servidores: el servicio vuelve en **~13 s** con RPO 0 |
| **Rendimiento** | 10 VMs medidas una a una, carga por recurso, **límite real: ~11 GB de VMs** en casa. 2 optimizaciones medidas: **virtio-net ×2,6** y caché del host (revertida, y por qué) |
| **Seguridad** | Credenciales fuera del repo + *hook* que bloquea cualquier commit con contraseñas |

**Memoria técnica completa en PDF:** [`entrega/memoria-naix-un-sistema.pdf`](entrega/memoria-naix-un-sistema.pdf) (se genera a partir de `docs/` con `scripts/genera-memoria.py`).

## 2. Esquema de red

<div align="center"><img src="diagrames/esquema-red.png" alt="Esquema de red" width="780"></div>


<sub>Línea gruesa: gateway activo · línea discontinua: gateways alternativos (se prueban de uno en uno con `scripts/canvi-gw.sh`) · borde discontinuo: SRV2, SRV3 y WS2025-DC van **dentro del clúster en el diseño**; por falta de RAM son VMs de VirtualBox en LAN23 con la misma IP ([04 §5.1](docs/04-disseny.md#51-servidores-dentro-del-clúster-simulados)).</sub>

## 3. Direccionamiento

| IP | VM | Función | Estado |
|---|---|---|:---:|
| `192.168.23.1` | Mikrotik-IND | RouterOS 7.24.5 · gateway por defecto · NAT + cortafuegos | Operativo |
| `192.168.23.2` | OPNsense | OPNsense 26.7 · comunicaciones alternativo | Operativo |
| `192.168.23.3` | DEB13-SRV1-NFT | Debian 13 + nftables · comunicaciones alternativo | Operativo |
| `192.168.23.10` | TrueNas | TrueNAS SCALE 25.10.7 · destino de las copias | Operativo |
| `192.168.23.11` | PMX1 | Proxmox VE 9.2 · nodo 1 del clúster `asix23` | Operativo |
| `192.168.23.12` | PMX2 | Proxmox VE 9.2 · nodo 2 del clúster `asix23` | Operativo |
| `192.168.23.13` | PMX3 | Proxmox VE 9.2 · nodo 3 del clúster `asix23` | Operativo |
| `192.168.23.20` | WS2025-DC | Windows Server 2025 · AD DS + DNS (`asix23.lan`) · en el diseño, VM en **PMX2** | Operativo |
| `192.168.23.21` | DEB13-SRV2 | Debian 13 · ficheros + **RAID 0/1/5** (mdadm) + DRBD primario · en el diseño, VM en **PMX1** | Operativo |
| `192.168.23.22` | DEB13-SRV3 | Debian 13 · web Apache + DRBD secundario · en el diseño, VM en **PMX3** | Operativo |
| `192.168.23.30` | srv-infra (LXC) | Servidor de infraestructura · intranet nginx | Operativo |
| `192.168.23.51` | W11-CLI | Windows 11 Pro · Administración · en el dominio | Operativo |
| `192.168.23.54` | DEB13-CLI | Debian 13 · Informática · cliente de pruebas | Operativo |
| `.50 .52 .53` | — | Dirección · Comercial · Producción | Solo diseño |

Máscara `255.255.255.0` · Asignación **fija** en todos (no hay DHCP en LAN23) · WAN de los routers: NAT de VirtualBox por DHCP.

## 4. Correspondencia entre tareas y evidencias

Todos los ítems **Apte** y **Apte+** de las tareas individuales están completados. Cada tarea tiene además una ficha de entrega (enunciado, trabajo hecho, resultados, evidencias y comprobación) en **[Proyecto-por-Tareas](Proyecto-por-Tareas/README.md)**.

| Tarea · nivel | Ítem | Evidencia |
|---|---|---|
| T0 · Apte / Apte+ | Entorno que simula el del grupo · repo documentado | Este repositorio · [04 · Diseño](docs/04-disseny.md) · [10 · Incidencias](docs/10-incidencies.md) |
| T2 · Apte | Inventario y comparativa clase/casa, cuellos de botella | [02 · Inventario](docs/02-inventari.md) · [`inventari-casa.txt`](evidencies/logs/inventari-casa.txt) |
| T2 · Apte+ | Tests de memoria, disco y red interpretados | [02 · Diagnósticos](docs/02-inventari.md#diagnósticos-apte) |
| T4 · Apte | Esquema de red y tabla de recursos | [04](docs/04-disseny.md) · [05](docs/05-recursos.md) · [diagrama](diagrames/esquema-red.png) |
| T4 · Apte+ | Conectividad verificada | [04](docs/04-disseny.md) · `evidencies/logs/prueba-gw-*.txt` |
| T5 · Apte | 3 routers, NAS, Proxmox, Windows Server, Linux, clientes; permitido/bloqueado; SHA256; incidencia | [06 · Instalación](docs/06-installacio/README.md) · [03 · Sistemas](docs/03-sistemes.md) · [10](docs/10-incidencies.md) |
| T5 · Apte+ | Copias automáticas de configuraciones | [truenas §6](docs/06-installacio/truenas.md#6-copias-automáticas-de-las-configuraciones-críticas-apte) |
| T6 · Apte | RAID 0, 1 y 5 verificados con fallo | [07 §1–6](docs/07-emmagatzematge-raid.md) |
| T6 · Apte+ | RAID en espejo entre 2 equipos + caso de uso | [07 §7 · DRBD](docs/07-emmagatzematge-raid.md#7-apte-raid-en-espejo-entre-dos-equipos) |
| T7 · Apte | Línea base, carga, qué VM satura qué, cuántas VMs | [08 §1–4](docs/08-rendiment.md) |
| T7 · Apte+ | 2 optimizaciones con antes/después | [08 §5](docs/08-rendiment.md#5-apte-dos-optimizaciones-antes-y-después) |
| Transversal | Predicciones · contingencia RTO/RPO · Tasca 8 | [00](docs/00-prediccions.md) · [09](docs/09-contingencia.md) · [12](docs/12-defensa.md) |

## 5. Documentación

| Documento | Contenido |
|---|---|
| [00 · Predicciones](docs/00-prediccions.md) | Lo que pensaba antes de investigar |
| [01 · Requisitos](docs/01-requisits.md) | Necesidades y requisitos mínimos |
| [02 · Inventario](docs/02-inventari.md) | Equipo de clase y de casa, diagnósticos |
| [03 · Sistemas](docs/03-sistemes.md) | Versiones, fuentes oficiales, licencias y **SHA256** |
| [04 · Diseño](docs/04-disseny.md) | Esquema lógico, interfaces, clúster |
| [05 · Recursos](docs/05-recursos.md) | Tabla de VMs, RAM simultánea, escenarios |
| [06 · Instalación](docs/06-installacio/README.md) | **Una guía por máquina** (ver abajo) |
| [07 · RAID](docs/07-emmagatzematge-raid.md) | RAID 0, 1 y 5, fallo y reconstrucción · **espejo por red DRBD** |
| [08 · Rendimiento](docs/08-rendiment.md) | Línea base, cada VM, carga por recurso, cuántas VMs, 2 optimizaciones |
| [09 · Contingencia](docs/09-contingencia.md) | RTO/RPO y recuperaciones probadas |
| [10 · Incidencias](docs/10-incidencies.md) | 26 problemas reales y cómo se resolvieron |
| [12 · Defensa](docs/12-defensa.md) | Guía de intervención para la Tasca 8 y banco de preguntas |

<details>
<summary><b>Guías de instalación por máquina</b></summary>

| Máquina | Lo más destacado |
|---|---|
| [MikroTik](docs/06-installacio/mikrotik.md) | NAT, cortafuegos input/forward, log de permitido/bloqueado |
| [OPNsense](docs/06-installacio/opnsense.md) | Interfaces corregidas, Unbound en reenvío, **orden de reglas** |
| [Debian SRV](docs/06-installacio/debian-srv.md) | `ip_forward` + nftables persistente, log del kernel |
| [TrueNAS](docs/06-installacio/truenas.md) | Pool espejo, NFS, **copias automáticas "pull"** |
| [Proxmox](docs/06-installacio/proxmox.md) | Clúster, contenedor vs VM, **migraciones medidas**, vzdump al NAS |
| [Windows Server](docs/06-installacio/windows-server.md) | Dominio `asix23.lan`, OUs, DNS, copia del AD |
| [Debian servidores](docs/06-installacio/debian-servidors.md) | SRV2 (Samba + RAID + DRBD) y SRV3 (intranet Apache), instalación desatendida |
| [Clientes](docs/06-installacio/clients.md) | Windows 11 en el dominio, Debian de pruebas |

</details>

<details>
<summary><b>Resultados destacados</b></summary>

| Prueba | Resultado |
|---|---|
| HTTPS desde la LAN por cada router (.1 / .2 / .3) | Permitido: `HTTP/2 200` |
| Telnet desde la LAN por cada router | Bloqueado y registrado en el log |
| Migración en caliente de una VM entre nodos | **12,7 s**, **8 ms** sin servicio |
| Migración de un contenedor | 85 s, ~84 s sin servicio (se copia el disco entero) |
| Copia completa del contenedor al NAS | 205 MB en 47 s |
| Copia del Directorio Activo (IFM) al NAS | 4,9 MB |
| Cuello de botella del host (3 instalaciones a la vez) | CPU 80 % libre, **13–16 % esperando al disco** → el SSD (A400 en caja USB) |
| RAID 1 / RAID 5 sin un disco | 0 lecturas fallidas · reconstrucción en **54 s / 15 s** · disco de reserva automático en **21 s** |
| **Caída de un servidor entero** (DRBD) | Datos montados en el otro en **~13 s**, SHA256 idéntico, al volver solo copia lo cambiado (206 MB en 25 s) |
| Red entre VMs: e1000 → **virtio** | **4,74 → 12,3 Gbit/s**, la mitad de CPU por Gbit/s |
| ¿Cuántas VMs aguanta el PC de casa? | **~11 GB** de VMs (5 VMs con el navegador abierto). Límite: RAM; con carga, el disco (399 MB/s por USB) |

</details>

<details>
<summary><b>6. Estructura del repositorio</b></summary>

```
docs/          documentación por tarea (nombres de archivo del enunciado)
Proyecto-por-Tareas/  una ficha por tarea para la entrega
entrega/       memoria técnica en PDF
diagrames/     esquemas (scripts .py → SVG y PNG con generar.sh)
evidencies/    captures/<máquina>/*.png  y  logs/*.txt (salidas reales de comandos)
configs/       configuraciones exportadas SIN credenciales (MikroTik, nftables, DRBD, Samba, Apache)
scripts/       automatización: copias, cambio de gateway, inventario, medidas de rendimiento, control de VMs, Windows…
```

</details>

<details>
<summary><b>Credenciales y seguridad</b></summary>

- Las contraseñas están solo en `CREDENCIALES-PRIVADAS.md`, que **está en `.gitignore`**.
- `scripts/comprova-secrets.sh` se ejecuta como *hook* `pre-commit` y **bloquea** el commit si encuentra alguna contraseña.
- En la documentación aparecen como `********`.
- Auditoría del historial completo: **0 contraseñas** publicadas.

</details>

---

<div align="center"><sub>Proyecto individual · ASIX ThinkLab "Naix un sistema" · CIP FP Batoi · Curso 2026-2027</sub></div>
