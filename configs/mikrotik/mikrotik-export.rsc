# 2026-11-17 09:38:40 by RouterOS 7.24.5
# software id = I7GD-SXLC
#
/interface ethernet set [ find default-name=ether2 ] comment=LAN23 disable-running-check=no name=ether1
/interface ethernet set [ find default-name=ether1 ] comment="WAN - NAT VirtualBox" disable-running-check=no name=ether2
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
/ip firewall filter add action=drop chain=forward comment="FWD: resto bloqueado" log=yes log-prefix=FWD-DROP
/ip firewall nat add action=masquerade chain=srcnat comment="NAT LAN23 -> Internet" out-interface-list=WAN
/ip service set ftp disabled=yes
/ip service set telnet disabled=yes
/ip service set api disabled=yes
/ip service set api-ssl disabled=yes
/system clock set time-zone-name=Europe/Madrid
/system ntp client set enabled=yes
/system ntp client servers add address=es.pool.ntp.org
