# Windows Server 2025 — Controlador de dominio y DNS (192.168.23.20)

| Dato | Valor |
|---|---|
| VM en VirtualBox | `WS2025-DC` (grupo `ISO-INDV`) |
| Sistema | Windows Server 2025 **Standard Evaluation** (Experiencia de escritorio), build 26100.1742, es-ES |
| Función | Controlador de dominio **AD DS** + **DNS** del dominio `asix23.lan` (NetBIOS `ASIX23`) |
| Recursos | 2 vCPU · 4 GB RAM · 50 GB · **UEFI + TPM 2.0** |
| Red | `Ethernet` en `LAN23` · 192.168.23.20/24 · gw 192.168.23.1 · DNS 127.0.0.1 · **fija** |
| Estado | ✅ Instalado, promovido y verificado |

## 1. Requisitos, licencia e imagen

- Imagen `w2k25.iso` (Microsoft Evaluation Center). SHA256 calculado y guardado ([evidencia](../../evidencies/logs/sha256-isos.txt)); Microsoft no publica un fichero de sumas para estas ISO → **N/C**.
- **Licencia de evaluación de 180 días**: suficiente para el laboratorio. En producción se necesita licencia Standard (por núcleos) + CAL por usuario/dispositivo.
- Requisitos mínimos: 2 GB RAM con escritorio, 32 GB de disco, CPU de 64 bits; recomendados UEFI + TPM 2.0. Asignado: 4 GB / 50 GB.

## 2. Instalación (desatendida)

```bash
VBoxManage unattended install WS2025-DC --iso=w2k25.iso --image-index=2 \
  --user=izan --password=******** --hostname=WS2025-DC.asix23.lan \
  --locale=es_ES --country=ES --time-zone=Europe/Madrid --install-additions
```

- `--image-index=2` = *Standard Evaluation (experiencia de escritorio)*. La versión *Core* (sin escritorio) gasta menos, pero el enunciado pide gestionar por GUI.
- Firmware **UEFI** con disco GPT y **TPM 2.0** virtual.
- Incidencia: la VM se quedó en *"Press any key to boot from CD"* → [incidencia 6](../10-incidencies.md).

## 3. Usuarios de administración

| Cuenta | Uso |
|---|---|
| `Administrador` (local → pasa a ser `ASIX23\Administrador`) | Administrador del dominio |
| `izan` (local, grupo Administradores) | Creado por la instalación |

> **Contraseña compleja obligatoria**: Windows exige al menos 3 de 4 tipos de carácter (mayúscula, minúscula, número, símbolo). Por eso en Windows se usa una variante con mayúscula de la contraseña del proyecto (`********`).

## 4. Red

Script: [`scripts/windows/ws2025-dc.ps1`](../../scripts/windows/ws2025-dc.ps1) (fase `red`).

```powershell
New-NetIPAddress -InterfaceAlias Ethernet -IPAddress 192.168.23.20 -PrefixLength 24 -DefaultGateway 192.168.23.1
Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses 192.168.23.1   # antes de ser DC
Enable-NetFirewallRule -Name FPS-ICMP4-ERQ-In                                        # permitir ping
```

**¿Por qué IP fija?** Todos los equipos del dominio buscan al DC por su IP (es su servidor DNS). Si cambiara, nadie encontraría el dominio.

## 5. AD DS + DNS: dominio `asix23.lan`

```powershell
Install-WindowsFeature AD-Domain-Services, DNS -IncludeManagementTools
Install-ADDSForest -DomainName asix23.lan -DomainNetbiosName ASIX23 -InstallDns -SafeModeAdministratorPassword <********>
```

Después del reinicio:

| Ajuste | Valor | Por qué |
|---|---|---|
| DNS del propio DC | `127.0.0.1` | El DC se resuelve a sí mismo y a los registros SRV del dominio |
| Reenviador DNS | `192.168.23.1` (gateway) | Lo que no es `asix23.lan` (p. ej. `deb.debian.org`) se pregunta fuera |
| Unidades organizativas | Direccion, Administracion, Comercial, Produccion, Informatica | Una por departamento → se pueden aplicar GPO distintas a cada uno |

**¿Por qué `.lan` y no `.local`?** `.local` está reservado para mDNS (Bonjour/Avahi) y da conflictos con Linux y macOS. Microsoft recomienda usar un subdominio de un dominio propio; en el laboratorio usamos `.lan`, que no es un dominio público.

### Verificación ([log completo](../../evidencies/logs/ws2025-dc-dominio.txt))

```
ADWS     Running Servicios web de Active Directory
DNS      Running Servidor DNS
Netlogon Running Net Logon
NTDS     Running Servicios de dominio de Active Directory

Maestro de esquema          WS2025-DC.asix23.lan      ← los 5 roles FSMO en este DC
PDC                         WS2025-DC.asix23.lan

"OU=Administracion,DC=asix23,DC=lan"  ... (5 OUs)
"CN=W11-CLI,OU=Administracion,DC=asix23,DC=lan"      ← el cliente ya es miembro
```

> **Incidencia**: tras el reinicio, los cmdlets `Get-ADOrganizationalUnit` fallaban con *"No se pudo encontrar ningún servidor que ejecutara Servicios web de Active Directory"* aunque el servicio ADWS estaba en marcha. Causa: la sesión remota de `guestcontrol` no tiene credenciales Kerberos para ADWS. Solución: usar `dsadd`/`dsquery`, que hablan LDAP directamente. ([incidencia 9](../10-incidencies.md))

## 6. ¿Qué es un dominio y qué aporta a la empresa?

Un **dominio** es un grupo de equipos y usuarios que comparten **una base de datos central de cuentas** (Active Directory) gestionada por uno o varios **controladores de dominio**.

| Sin dominio (grupo de trabajo) | Con dominio |
|---|---|
| Cada PC tiene sus propios usuarios: 5 PCs × 5 usuarios = 25 cuentas | **Una sola cuenta por persona**, válida en cualquier equipo |
| Cambiar una contraseña = ir PC por PC | Se cambia una vez en el DC |
| Configuraciones a mano en cada equipo | **GPO**: políticas (contraseñas, bloqueo de USB, fondos, software) aplicadas a toda una OU |
| Si alguien se va, hay que borrar su cuenta en todos los PCs | Se deshabilita una cuenta y pierde acceso a todo |
| Permisos de carpetas compartidas por equipo | Permisos por **grupos** de AD (p. ej. "Comercial" lee la carpeta de ventas) |

**Para nuestra empresa** (5 departamentos): un empleado puede sentarse en cualquier PC con su usuario, informática gestiona todo desde un único sitio y se aplican normas de seguridad iguales para todos.

## 7. Copias de seguridad

| ¿Qué copiar? | ¿Por qué? |
|---|---|
| **Estado del sistema / base de datos de AD** (`ntds.dit`, SYSVOL) | Es lo que no se puede rehacer rápido: usuarios, grupos, GPO |
| Zona DNS `asix23.lan` | Va dentro de AD (zona integrada) |
| Script de configuración | Ya está en Git |
| **No** hace falta: el sistema operativo completo | Se reinstala; lo valioso es AD |

✅ **Copia hecha** con [`scripts/windows/copia-ad.ps1`](../../scripts/windows/copia-ad.ps1):

```powershell
ntdsutil "activate instance ntds" "ifm" "create sysvol full C:\copias\ifm-<fecha>" quit quit
Compress-Archive ... C:\copias\ad-asix23-<fecha>.zip
```

- `ifm` (*Install From Media*) crea una **copia coherente** de la base de datos `ntds.dit`, el registro y SYSVOL mientras el DC sigue funcionando.
- Resultado: `ad-asix23-2026-11-17_1154.zip` (**4,9 MB**) → NAS `/mnt/copias/configs/ws2025-dc/`.
- La copia se borra del PC intermedio porque contiene los *hashes* de las contraseñas del dominio: solo debe estar en el NAS.
- Con esta copia se puede **reconstruir el DC** (o promover uno nuevo desde el medio IFM sin replicar por red).

## Preguntas probables de la defensa

- **¿Por qué el DC usa 127.0.0.1 como DNS?** Porque él mismo es el servidor DNS del dominio. Si apuntara al router, no encontraría sus propios registros SRV (`_ldap._tcp.asix23.lan`).
- **¿Para qué sirve el reenviador?** Para que los clientes, que solo preguntan al DC, puedan resolver también nombres de Internet.
- **¿Qué es FSMO?** Cinco "roles maestros" que solo puede tener un DC a la vez (esquema, nombres de dominio, PDC, RID, infraestructura). Con un solo DC, los tiene todos.
- **¿Qué pasa si se cae el DC?** Los usuarios ya conectados siguen trabajando (credenciales en caché), pero no se puede iniciar sesión con cuentas nuevas ni resolver nombres del dominio. Por eso en producción se ponen **dos DC**.
