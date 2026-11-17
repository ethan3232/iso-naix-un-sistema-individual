# 10 · Incidencias

Registro de problemas reales que han aparecido al montar el entorno, con el método **síntoma → hipótesis → comprobación → solución → vuelta al estado normal**.

| # | Fecha | Máquina | Síntoma | Hipótesis | Comprobación | Solución | Estado final |
|---|---|---|---|---|---|---|---|
| 1 | 17/11 | TrueNas | Al arrancar aparece el **instalador** de TrueNAS en vez del sistema | La ISO sigue conectada y el orden de arranque pone el DVD antes que el disco | El disco virtual ya ocupaba 3,5 GB → el sistema estaba instalado | Desconectar la ISO del lector (`storageattach ... --medium emptydrive`) | Arranca TrueNAS 25.10.7 desde el disco |
| 2 | 17/11 | Mikrotik-IND | Mensaje *"ROUTER HAS NO SOFTWARE KEY — You have 21h…"* | RouterOS **x86** instalado desde ISO necesita licencia; sin ella es una demo de 24 h | Documentación de MikroTik + el propio mensaje: *"Turn off the device to stop the timer"* | Se mantiene la VM y **se apaga cuando no se usa**. Alternativa: CHR (licencia gratuita) | Router operativo; contador controlado |
| 3 | 17/11 | Todas | `ping` a Internet desde las VMs no responde, pero sí funciona HTTPS | La NAT de VirtualBox no puede enviar ICMP porque el anfitrión no permite *ping sockets* sin privilegios | `sysctl net.ipv4.ping_group_range` = `1 0` (desactivado) en el anfitrión; DNS y `curl` sí funcionan | Usar `traceroute -T` (TCP). Solución definitiva (requiere sudo en el anfitrión): `sysctl -w net.ipv4.ping_group_range="0 2147483647"` | Conectividad demostrada por TCP |
| 4 | 17/11 | DEB13-SRV | Tras pasar a LAN23, la WAN (`enp0s3`) no tiene IP y no hay Internet | El perfil de NetworkManager *Wired connection 1* se había quedado asociado a la otra tarjeta | `nmcli dev status`: `enp0s3` *desconectado*, `enp0s8` *obteniendo IP* | Perfil nuevo `WAN` (DHCP) en `enp0s3` y el antiguo renombrado a `LAN23` (IP fija) | Las dos interfaces con su IP |
| 5 | 17/11 | DEB13-SRV / CLI | Al escribir comandos desde el anfitrión, `-` sale como `/` y `=` como `)` | La consola de texto usa teclado de EE. UU. y la herramienta tenía otra distribución | Escribir `a-b/c=d` y ver qué aparece en pantalla | Usar la distribución de EE. UU. al enviar teclas por `VBoxManage` | Comandos correctos |
| 6 | 17/11 | WS2025-DC, W11-CLI | Pantalla negra *"Press any key to boot from CD or DVD…"* y después *"No bootable option"* | En UEFI, el instalador de Windows pide pulsar una tecla y nadie la pulsó | Captura de pantalla de la VM | Reiniciar la VM y enviar la tecla espacio repetidamente durante los primeros segundos | Instalación en marcha |
| 7 | 17/11 | W11-CLI | El instalador se para en **"Clave de producto"** aunque es una instalación desatendida | El nuevo instalador de Windows 11 25H2 no lee igual el `autounattend.xml` de VirtualBox 7.0 | Captura: *"' ' no es un carácter válido"* | Borrar el campo y elegir *"No tengo clave de producto"* | La instalación continúa |
| 8 | 17/11 | Anfitrión | `sudo` no funciona desde terminal | No hay terminal para pedir la contraseña | Error *"a terminal is required to read the password"* | Instalar `gh` sin sudo en `~/.local/bin`; lo que necesite root en el anfitrión lo ejecuta izan | `gh` 2.104.0 funcionando |

## Incidencia provocada (Tasca 5.5)

⬜ Pendiente: se provocará en una VM desechable (clon de `DEB13-CLI`) un fallo de arranque y se documentará con el mismo método.
