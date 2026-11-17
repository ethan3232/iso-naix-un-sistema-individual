# =============================================================================
# ws2025-dc.ps1 — Windows Server 2025: red + AD DS + DNS (dominio asix23.lan)
# Ejecutar como Administrador. La contraseña DSRM se pasa como parámetro
# (nunca se guarda en el repositorio).
#   .\ws2025-dc.ps1 -Fase red
#   .\ws2025-dc.ps1 -Fase addc -DsrmPassword '********'
#   .\ws2025-dc.ps1 -Fase post
# =============================================================================
param(
    [ValidateSet('red','addc','post')] [string]$Fase = 'red',
    [string]$DsrmPassword
)
$ErrorActionPreference = 'Stop'
$If = 'Ethernet'

switch ($Fase) {
  'red' {
    # 1) IP fija: un servidor de dominio/DNS NUNCA debe tener IP dinámica,
    #    porque los clientes lo buscan por su IP para resolver nombres.
    Get-NetIPAddress -InterfaceAlias $If -AddressFamily IPv4 -ErrorAction SilentlyContinue | Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
    Get-NetRoute -InterfaceAlias $If -DestinationPrefix 0.0.0.0/0 -ErrorAction SilentlyContinue | Remove-NetRoute -Confirm:$false -ErrorAction SilentlyContinue
    Set-NetIPInterface -InterfaceAlias $If -Dhcp Disabled
    New-NetIPAddress -InterfaceAlias $If -IPAddress 192.168.23.20 -PrefixLength 24 -DefaultGateway 192.168.23.1 | Out-Null
    Set-DnsClientServerAddress -InterfaceAlias $If -ServerAddresses 192.168.23.1
    # Permitir ping (ICMPv4) para poder comprobar la conectividad desde la LAN
    Enable-NetFirewallRule -Name 'FPS-ICMP4-ERQ-In' -ErrorAction SilentlyContinue
    Set-TimeZone -Id 'Romance Standard Time'
    Get-NetIPConfiguration -InterfaceAlias $If
  }
  'addc' {
    # 2) Rol de Servicios de dominio de Active Directory + herramientas de gestión
    Install-WindowsFeature AD-Domain-Services, DNS -IncludeManagementTools | Format-Table -AutoSize
    # 3) Nuevo bosque asix23.lan con DNS integrado. Reinicia el servidor al acabar.
    $sec = ConvertTo-SecureString $DsrmPassword -AsPlainText -Force
    Install-ADDSForest -DomainName 'asix23.lan' -DomainNetbiosName 'ASIX23' `
        -ForestMode 'WinThreshold' -DomainMode 'WinThreshold' `
        -InstallDns -SafeModeAdministratorPassword $sec -NoRebootOnCompletion:$false -Force
  }
  'post' {
    # 4) Después del reinicio: el DC se usa a sí mismo como DNS y reenvía lo de
    #    Internet al gateway.
    Set-DnsClientServerAddress -InterfaceAlias $If -ServerAddresses 127.0.0.1
    Set-DnsServerForwarder -IPAddress 192.168.23.1
    # Unidades organizativas por departamento (estructura del enunciado)
    $base = 'DC=asix23,DC=lan'
    foreach ($ou in 'Direccion','Administracion','Comercial','Produccion','Informatica') {
        if (-not (Get-ADOrganizationalUnit -Filter "Name -eq '$ou'" -ErrorAction SilentlyContinue)) {
            New-ADOrganizationalUnit -Name $ou -Path $base -ProtectedFromAccidentalDeletion $true
        }
    }
    Get-ADDomain | Select-Object DNSRoot, NetBIOSName, DomainMode, PDCEmulator
    Get-ADOrganizationalUnit -Filter * | Select-Object Name, DistinguishedName
    Resolve-DnsName ws2025-dc.asix23.lan
    Resolve-DnsName deb.debian.org -Type A | Select-Object -First 1
  }
}
