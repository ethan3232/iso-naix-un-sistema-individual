. C:\cap\comun.ps1
$Host.UI.RawUI.WindowTitle = 'W11-CLI - red y dominio'
P 'Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet | ft IPAddress,PrefixLength'
P '(Get-NetRoute 0.0.0.0/0).NextHop'
P '(Get-DnsClientServerAddress Ethernet -AddressFamily IPv4).ServerAddresses'
P 'Test-Connection ws2025-dc.asix23.lan -Count 2 | ft Address,IPV4Address,ResponseTime'
P 'Get-CimInstance Win32_ComputerSystem | fl Name,Domain,PartOfDomain'
P 'Test-ComputerSecureChannel'
