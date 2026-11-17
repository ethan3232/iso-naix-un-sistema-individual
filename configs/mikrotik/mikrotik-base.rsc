# Configuración base del servidor de comunicaciones MikroTik (RouterOS 7.24.5)
# LAN23 192.168.23.0/24 · Gateway .1 · WAN por DHCP (NAT de VirtualBox)
# Sin contraseñas: los usuarios se crean aparte.
# Vuelta atrás: /system backup load name=00-estado-inicial   (o /system reset-configuration)

# --- Interfaces ---
/interface ethernet set [find default-name=ether1] comment="WAN - NAT VirtualBox"
/interface ethernet set [find default-name=ether2] comment="LAN23"
/interface list add name=WAN comment="Salida a Internet"
/interface list add name=LAN comment="Red interna LAN23"
/interface list member add list=WAN interface=ether1
/interface list member add list=LAN interface=ether2

# --- Direccionamiento ---
/ip address add address=192.168.23.1/24 interface=ether2 comment="LAN23 - gateway .1"
/ip dns set allow-remote-requests=yes servers=1.1.1.1,9.9.9.9
/system clock set time-zone-name=Europe/Madrid
/system ntp client set enabled=yes servers=es.pool.ntp.org

# --- NAT: la LAN sale a Internet con la IP de la WAN ---
/ip firewall nat add chain=srcnat out-interface-list=WAN action=masquerade comment="NAT LAN23 -> Internet"

# --- Cortafuegos: tráfico hacia el propio router (input) ---
/ip firewall filter add chain=input connection-state=established,related action=accept comment="IN: respuestas"
/ip firewall filter add chain=input connection-state=invalid action=drop comment="IN: invalidos"
/ip firewall filter add chain=input protocol=icmp action=accept comment="IN: ping"
/ip firewall filter add chain=input in-interface-list=LAN action=accept comment="IN: gestion desde LAN23"
/ip firewall filter add chain=input in-interface-list=WAN src-address=10.0.2.2 protocol=tcp dst-port=22,80,8291 action=accept comment="IN: gestion desde el host (NAT VirtualBox)"
/ip firewall filter add chain=input action=drop log=yes log-prefix="IN-DROP" comment="IN: resto bloqueado"

# --- Cortafuegos: tráfico que atraviesa el router (forward) ---
/ip firewall filter add chain=forward connection-state=established,related action=accept comment="FWD: respuestas"
/ip firewall filter add chain=forward connection-state=invalid action=drop comment="FWD: invalidos"
/ip firewall filter add chain=forward in-interface-list=LAN protocol=tcp dst-port=23 action=drop log=yes log-prefix="BLOQUEADO-TELNET" comment="PRUEBA BLOQUEADA: Telnet (contrasenas en claro)"
/ip firewall filter add chain=forward in-interface-list=LAN protocol=tcp dst-port=443 connection-state=new action=accept log=yes log-prefix="PERMITIDO-HTTPS" comment="PRUEBA PERMITIDA: HTTPS"
/ip firewall filter add chain=forward in-interface-list=LAN out-interface-list=WAN action=accept comment="FWD: LAN23 -> Internet"
/ip firewall filter add chain=forward action=drop log=yes log-prefix="FWD-DROP" comment="FWD: resto bloqueado"

# --- Servicios: solo los necesarios ---
/ip service set telnet disabled=yes
/ip service set ftp disabled=yes
/ip service set api disabled=yes
/ip service set api-ssl disabled=yes
