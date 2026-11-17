# 2026-11-17 13:52:51 by RouterOS 7.24.5
# software id = I7GD-SXLC
#
/interface ethernet set [ find default-name=ether1 ] comment=LAN23 disable-running-check=no
/interface ethernet set [ find default-name=ether2 ] comment="WAN - NAT VirtualBox" disable-running-check=no
/interface list add comment="Salida a Internet" name=WAN
/interface list add comment="Red interna LAN23" name=LAN
/ip settings set ipv4-high-fragment-thresh=32.0MiB
/ipv6 settings set max-neighbor-entries=16384 min-neighbor-entries=4096 soft-max-neighbor-entries=8192
/interface list member add interface=ether1 list=WAN
/interface list member add interface=ether2 list=LAN
/ip address add address=192.168.23.1/24 comment="LAN23 - gateway .1" interface=ether2 network=192.168.23.0
/ip dhcp-client add comment=WAN interface=ether1 name=client1
/ip dns set allow-remote-requests=yes servers=1.1.1.1,9.9.9.9
/ip firewall filter add action=accept chain=input comment="IN: respuestas" connection-state=established,related
/ip firewall filter add action=drop chain=input comment="IN: invalidos" connection-state=invalid
/ip firewall filter add action=accept chain=input comment="IN: ping" protocol=icmp
/ip firewall filter add action=accept chain=input comment="IN: gestion desde LAN23" in-interface-list=LAN
/ip firewall filter add action=accept chain=input comment="IN: gestion desde el host (NAT VirtualBox)" dst-port=22,80,8291 in-interface-list=WAN protocol=tcp src-address=10.0.2.2
/ip firewall filter add action=drop chain=input comment="IN: resto bloqueado" log=yes log-prefix=IN-DROP
/ip firewall filter add action=accept chain=forward comment="FWD: respuestas" connection-state=established,related
/ip firewall filter add action=drop chain=forward comment="FWD: invalidos" connection-state=invalid
/ip firewall filter add action=drop chain=forward comment="PRUEBA BLOQUEADA: Telnet (contrasenas en claro)" dst-port=23 in-interface-list=LAN log=yes log-prefix=BLOQUEADO-TELNET protocol=tcp
/ip firewall filter add action=accept chain=forward comment="PRUEBA PERMITIDA: HTTPS" connection-state=new dst-port=443 in-interface-list=LAN log=yes log-prefix=PERMITIDO-HTTPS protocol=tcp
/ip firewall filter add action=accept chain=forward comment="FWD: LAN23 -> Internet" in-interface-list=LAN out-interface-list=WAN
/ip firewall filter add action=accept chain=forward comment="FWD: gestion desde el host (dst-nat)" connection-nat-state=dstnat in-interface-list=WAN src-address=10.0.2.2
/ip firewall filter add action=drop chain=forward comment="FWD: resto bloqueado" log=yes log-prefix=FWD-DROP
/ip firewall nat add action=masquerade chain=srcnat comment="NAT LAN23 -> Internet" out-interface-list=WAN
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> TrueNAS web" dst-port=8410 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.10 to-ports=443
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> Proxmox web" dst-port=8411 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.11 to-ports=8006
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> OPNsense web" dst-port=8402 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.2 to-ports=443
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> RDP Windows Server" dst-port=8420 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.20 to-ports=3389
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> TrueNAS SSH" dst-port=2210 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.10 to-ports=22
/ip firewall nat add action=masquerade chain=srcnat comment="GESTION: el trafico del host sale a la LAN con IP .1 (evita rutas asimetricas)" out-interface-list=LAN src-address=10.0.2.2
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> PMX1 SSH" dst-port=2211 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.11 to-ports=22
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> PMX2 SSH" dst-port=2212 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.12 to-ports=22
/ip firewall nat add action=dst-nat chain=dstnat comment="GESTION: host -> PMX2 web" dst-port=8412 in-interface-list=WAN protocol=tcp src-address=10.0.2.2 to-addresses=192.168.23.12 to-ports=8006
/ip service set ftp disabled=yes
/ip service set telnet disabled=yes
/ip service set api disabled=yes
/ip service set api-ssl disabled=yes
/system clock set time-zone-name=Europe/Madrid
/system ntp client set enabled=yes
/system ntp client servers add address=es.pool.ntp.org
