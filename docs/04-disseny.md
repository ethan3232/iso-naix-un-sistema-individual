# 04 · Diseño físico y lógico

**Tasca 4** · Estado: ✓ · Red de mi puesto: **192.168.23.0/24** (puesto 23 del aula)

## 1. Esquema lógico

![Esquema de red](../diagrames/esquema-red.png)
*Esquema de red generado con [`diagrames/esquema-red.py`](../diagrames/esquema-red.py) (SVG dibujado con coordenadas fijas; también en [SVG](../diagrames/esquema-red.svg)). Línea gruesa: gateway activo; discontinua: gateways alternativos. Etiqueta **SIMULADO** y borde discontinuo: **dentro del clúster en el diseño, simuladas fuera** (ver [§5.1](#51-servidores-dentro-del-clúster-simulados)).*


## 2. Esquema "físico" (montaje en VirtualBox)

Todo corre en **un solo equipo físico**: el portátil de clase (eth4n). Los "cables" son adaptadores virtuales:

| Elemento real | Equivalente en VirtualBox |
|---|---|
| Conmutador de la LAN | **Red interna `LAN23`** (`--nic intnet --intnet LAN23`): un switch virtual aislado, solo para mis VMs |
| Router del ISP / red del rack | **NAT de VirtualBox** (adaptador 1 de cada router): cada router recibe 10.0.2.15 por DHCP y sale por el PC |
| Cable de cada equipo al switch | Adaptador conectado a `LAN23` (`cableconnected on`) |
| Acceso del técnico a la gestión | Redirecciones de puertos **solo en 127.0.0.1** (no se ven desde la red del aula) |

![Montaje en VirtualBox](../diagrames/esquema-fisico.png)
*Cómo está cableado: cada router tiene un adaptador NAT (nic1) y otro en la red interna LAN23 (nic2); el resto de VMs solo están en LAN23. La gestión se hace desde el propio PC por 127.0.0.1. Fuente: [`diagrames/esquema-fisico.py`](../diagrames/esquema-fisico.py).*

**¿Por qué red interna y no puente (bridge)?** Con puente, mis VMs aparecerían en la red compartida del aula (172.16.222.0/24) y un DHCP o una IP repetida molestaría a los compañeros. El enunciado prohíbe lanzar un DHCP de pruebas en la red compartida. La red interna aísla mi LAN y **obliga a que todo el tráfico pase por el router**, que es lo que queremos demostrar.

## 3. Parámetros de red de cada interfaz

| Máquina | Interfaz | Red VBox | IP / máscara | Gateway | DNS | Dominio | Asignación |
|---|---|---|---|---|---|---|---|
| Mikrotik-IND | ether1 (WAN) | NAT | 10.0.2.15/24 | 10.0.2.2 | 10.0.2.3 → 1.1.1.1, 9.9.9.9 | — | DHCP |
| Mikrotik-IND | ether2 (LAN) | LAN23 | **192.168.23.1/24** | — | (servidor DNS para la LAN) | — | Fija |
| OPNsense | em0 (WAN) | NAT | 10.0.2.15/24 | 10.0.2.2 | 10.0.2.3 | — | DHCP |
| OPNsense | em1 (LAN) | LAN23 | **192.168.23.2/24** | — | Unbound (reenvío) | — | Fija |
| DEB13-SRV1-NFT | enp0s3 (WAN) | NAT | 10.0.2.15/24 | 10.0.2.2 | 10.0.2.3 | — | DHCP |
| DEB13-SRV1-NFT | enp0s8 (LAN) | LAN23 | **192.168.23.3/24** | — (`never-default`) | — | — | Fija |
| TrueNas | enp0s3 | LAN23 | 192.168.23.10/24 | 192.168.23.1 | 192.168.23.1 | asix23.lan | Fija |
| PMX1 | vmbr0 (nic0) | LAN23 | 192.168.23.11/24 | 192.168.23.1 | 192.168.23.1 | asix23.lan | Fija |
| PMX2 | vmbr0 (nic0) | LAN23 | 192.168.23.12/24 | 192.168.23.1 | 192.168.23.1 | asix23.lan | Fija |
| PMX3 | vmbr0 (nic0) | LAN23 | 192.168.23.13/24 | 192.168.23.1 | 192.168.23.1 | asix23.lan | Fija |
| WS2025-DC | Ethernet | LAN23 | 192.168.23.20/24 | 192.168.23.1 | **127.0.0.1** (él mismo) · reenviador .1 | asix23.lan | Fija |
| srv-infra (LXC) | eth0 → vmbr0 | LAN23 | 192.168.23.30/24 | 192.168.23.1 | 192.168.23.20 | asix23.lan | Fija |
| W11-CLI | Ethernet | LAN23 | 192.168.23.51/24 | 192.168.23.1 | **192.168.23.20** (DC) | asix23.lan | Fija |
| DEB13-CLI | enp0s3 | LAN23 | 192.168.23.54/24 | .1 / .2 / .3 (`canvi-gw.sh`) | el del gateway activo | asix23.lan | Fija |

**¿Por qué todo con IP fija y sin DHCP?** Son servidores (siempre se les busca por la misma IP) y además hay tres routers en la misma LAN: con tres servidores DHCP, cada cliente cogería el gateway del que respondiera primero. Los clientes .50–.54 también van fijos para que las pruebas sean repetibles. **Rango reservado** para un futuro DHCP: `.100–.199`.

### Plan de direccionamiento

| Rango | Uso |
|---|---|
| .1 – .3 | Servidores de comunicaciones (fijados por el enunciado) |
| .10 – .19 | Almacenamiento y virtualización (NAS .10, nodos Proxmox .11–.13) |
| .20 – .29 | Servidores de identidad e infraestructura (DC .20) |
| .30 – .49 | VMs y contenedores dentro de Proxmox (srv-infra .30) |
| .50 – .54 | Clientes por departamento: Dirección .50, Administración .51, Comercial .52, Producción .53, Informática .54 |
| .100 – .199 | Reservado para DHCP (solo dentro de LAN23) |

## 4. Cambio de gateway activo

Solo un router hace de gateway a la vez. Los tres están siempre en la LAN con su IP, pero los clientes apuntan a uno:

```bash
scripts/canvi-gw.sh 1   # MikroTik   (DNS .1)
scripts/canvi-gw.sh 2   # OPNsense   (DNS .2)
scripts/canvi-gw.sh 3   # Debian     (DNS 1.1.1.1, porque Debian no tiene servidor DNS)
```

Comprobación en cada caso: `ip route` (gateway) + `traceroute -T` (el primer salto es el router elegido). Resultados: [MikroTik](../evidencies/logs/prueba-gw-mikrotik.txt) · [OPNsense](../evidencies/logs/prueba-gw-opnsense.txt) · [Debian](../evidencies/logs/prueba-gw-debian.txt).

## 5. Clúster: nodos, quórum, red y almacenamiento

| | Diseño |
|---|---|
| Nodos | **3** (PMX1, PMX2, PMX3) → quórum = 2 votos: **si cae un nodo, el clúster sigue funcionando** |
| Red | Corosync sobre LAN23 (en producción: red separada y redundante) |
| Almacenamiento | `local-lvm` en cada nodo (local) + `nas-copias` (NFS de TrueNAS, compartido, para copias) |
| Gestión conjunta | ✓ |
| Migración | ✓ medida ([Proxmox](06-installacio/proxmox.md#8-migraciones-medidas-log-completo)) |
| Alta disponibilidad | Diseño: necesitaría almacenamiento compartido para los **discos** de las VMs (NFS/iSCSI/Ceph) |

### 5.1 Servidores dentro del clúster (simulados)

En el diseño, los servidores de la empresa **no son máquinas sueltas**: corren **dentro del clúster Proxmox**, que es lo que aporta la virtualización (gestión conjunta, copias con `vzdump` al NAS, migración entre nodos). El problema es la RAM: meter VMs dentro de los nodos Proxmox (virtualización anidada) exige dar a cada nodo la RAM de sus VMs **más** la del propio Proxmox, y no cabe.

| Servidor | Ubicación en el diseño | Ubicación real (implementada) | IP (la misma en los dos casos) |
|---|---|---|---|
| DEB13-SRV2 (ficheros + RAID + DRBD primario) | VM en **PMX1**, puente `vmbr0` → LAN23 | VM de VirtualBox en LAN23 | .21 |
| WS2025-DC (AD DS + DNS) | VM en **PMX2**, puente `vmbr0` → LAN23 | VM de VirtualBox en LAN23 | .20 |
| DEB13-SRV3 (web + DRBD secundario) | VM en **PMX3**, puente `vmbr0` → LAN23 | VM de VirtualBox en LAN23 | .22 |
| srv-infra (intranet, LXC) | Contenedor en PMX2 | ✓ **Real**, dentro del clúster | .30 |

**Cálculo de por qué no cabe (clase, ~24 GB para VMs):** 3 nodos Proxmox + NAS ≈ 10 GB ya en marcha. Llevar dentro SRV2 (1 GB) + SRV3 (1 GB) + WS2025-DC (4 GB) obliga a subir la RAM de los nodos esos 6 GB más ~1 GB de sobrecarga por nodo, y además Windows dentro de una VM anidada va muy lento (sin aceleración de hardware real). En casa (~10 GB) es imposible.

**¿Por qué la simulación es válida?** Para el resto de la red es **indistinguible**: un puente `vmbr0` de Proxmox conecta la VM a LAN23 igual que el adaptador de VirtualBox, así que la VM tiene la misma IP, la misma puerta de enlace, el mismo DNS y da el mismo servicio. Lo que **no** se puede demostrar con ellas es lo propio del clúster (migrarlas de nodo o copiarlas con `vzdump`); eso se ha demostrado con `srv-infra` y la VM de prueba (101) en [Proxmox](06-installacio/proxmox.md).

**Reparto por nodos:** SRV2 y SRV3 van en **nodos distintos** (PMX1 y PMX3) a propósito: el espejo DRBD solo protege si los dos lados están en **equipos físicos diferentes**. Si los dos estuvieran en el mismo nodo, la caída de ese nodo se llevaría las dos copias. El DC va en PMX2 junto a `srv-infra`, que lo usa como DNS.

> **Pregunta probable de defensa:** *"¿Dónde está tu servidor de ficheros, en el clúster o fuera?"* → En el diseño, dentro del clúster (PMX1). En mi montaje es una VM de VirtualBox en la misma LAN23 y con la misma IP, porque la virtualización anidada no cabe en la RAM. Para la red es lo mismo; lo único que no puedo hacer con ella es migrarla, y eso lo he demostrado con el contenedor `srv-infra`.

## 6. Decisiones y alternativas

| Decisión | Alternativas | Por qué esta |
|---|---|---|
| Red interna `LAN23` | Puente al aula, red host-only | Aislada y sin riesgo para la red compartida |
| WAN por NAT de VirtualBox | Puente con IP del rack | El enunciado lo permite en la parte individual |
| Dominio `asix23.lan` | `.local`, subdominio público | `.local` choca con mDNS; no tenemos dominio público |
| DNS del dominio en el DC | DNS en el router | AD necesita registros SRV que solo gestiona su DNS |
| Copias "pull" desde el NAS | Cada equipo envía | Los equipos no guardan credenciales del NAS |
