# 01 · Requisitos

**Tasca 0 / Tasca 1 (parte individual)** · Estado: ✅

## 1. Necesidades del entorno individual

El enunciado pide simular **en mi propio equipo** el sistema de la empresa del grupo (no todo, ni exactamente igual). Las necesidades se agrupan así:

| Necesidad | Pregunta del enunciado | Cómo la cubro |
|---|---|---|
| **Comunicaciones** | ¿Cómo conectamos y filtramos redes? | 3 servidores de comunicaciones intercambiables (MikroTik, OPNsense, Debian+nftables) con NAT y cortafuegos |
| **Virtualización** | ¿Qué recursos y nodos necesita el laboratorio? | Clúster Proxmox de 3 nodos (virtualización anidada en VirtualBox) |
| **Gestión centralizada** | ¿Qué servicio gestiona identidades y equipos? | Windows Server 2025 con AD DS + DNS (`asix23.lan`) |
| **Clientes** | ¿Qué opción admite las tareas de cada departamento? | Windows 11 Pro (Administración) y Debian (Informática); el resto en diseño |
| **Datos** | ¿Cómo organizamos, compartimos y recuperamos ficheros? | TrueNAS con pool en espejo + copias automáticas |
| **Recuperación** | ¿Cómo volvemos a un estado bueno? | Copias en el NAS + copias locales + Git; fallos provocados y medidos |
| **Supervisión** | ¿Cómo sabemos que algo va mal? | Logs de cortafuegos, `journalctl`, `vmstat`/`iostat` (Tasca 7) |

**Supuestos** (el enunciado dice que usuarios y volumen de datos son N/C hasta definirlos):
- Empresa de **5 departamentos**, ~1–3 personas por departamento (supuesto).
- Volumen de datos de configuración: **< 10 MB** por equipo (medido: el mayor es la copia del AD, 4,9 MB).
- Volumen de imágenes de VMs: **~200 MB** comprimidas por contenedor (medido).

## 2. Requisitos del equipo anfitrión

| Recurso | Necesario | Mi equipo de clase | ¿Cumple? |
|---|---|---|---|
| CPU con virtualización | VT-x/AMD-V + virtualización anidada (Proxmox) | Core Ultra 5 125H, VT-x | ✅ |
| RAM | Suma de las VMs encendidas + ~6 GB para el host | 30 GiB | ⚠️ No caben todas a la vez → escenarios ([05-recursos](05-recursos.md)) |
| Disco | ~120 GB reales para VMs | 167 GB libres en el SSD (caja USB) | ✅ justo · ⚠️ es el cuello de botella de rendimiento |
| Red | Acceso a Internet para descargas y actualizaciones | 1 Gbps (red del aula) | ✅ |
| Firmware | UEFI y TPM 2.0 (Windows 11 / Server 2025) | Los aporta VirtualBox 7 (EFI + TPM virtual) | ✅ |

## 3. Requisitos mínimos oficiales vs. recursos propuestos

| Sistema | Mínimo oficial (fuente) | Propuesto en el laboratorio | Comentario |
|---|---|---|---|
| RouterOS x86 | 64 MB RAM ([MikroTik](https://help.mikrotik.com/docs/spaces/ROS/pages/328149/Getting+started)) | 512 MB · 2 GB | Holgado |
| OPNsense 26.7 | 2 GB RAM (mín. 1), 20 GB ([docs.opnsense.org](https://docs.opnsense.org/manual/hardware.html)) | 2 GB · 20 GB | El instalador pide 3 GB para copiar el *live*; funcionó con 2 |
| Debian 13 | 256 MB sin escritorio; 1–2 GB con GNOME ([debian.org](https://www.debian.org/releases/trixie/amd64/ch03s04.es.html)) | 2–4 GB · 20 GB | Con escritorio |
| TrueNAS SCALE 25.10 | **8 GB RAM**, 16 GB arranque ([truenas.com](https://www.truenas.com/docs/scale/gettingstarted/scalehardwareguide/)) | **4 GB** · 32 GB + 2×20 GB | ⚠️ Por debajo: válido solo para pruebas |
| Proxmox VE 9 | 2 GB + RAM de las VMs, CPU con VT-x ([proxmox.com](https://pve.proxmox.com/wiki/System_Requirements)) | 4 GB · 20–32 GB por nodo | Anidado |
| Windows Server 2025 | 2 GB (escritorio), 32 GB ([Microsoft](https://learn.microsoft.com/windows-server/get-started/hardware-requirements)) | 4 GB · 50 GB · UEFI+TPM | |
| Windows 11 | **4 GB, 64 GB, UEFI, Secure Boot, TPM 2.0** ([Microsoft](https://www.microsoft.com/windows/windows-11-specifications)) | 4 GB · 64 GB · UEFI+TPM | Justo en el mínimo |

Fecha de consulta de las fuentes: **17/11/2026**. Detalle de versiones, licencias y SHA256 en [03-sistemes](03-sistemes.md).

## 4. Requisitos de seguridad y documentación

- Credenciales **fuera del repositorio** (regla del enunciado) → `CREDENCIALES-PRIVADAS.md` en `.gitignore` + comprobación automática antes de cada commit.
- Antes de cambiar una regla o la red: **copia del estado anterior** y forma de volver atrás (documentado en cada máquina).
- No lanzar DHCP en la red compartida del aula → LAN interna aislada y sin DHCP.
- Documentación en Markdown, versionada en Git y publicada en GitHub.
