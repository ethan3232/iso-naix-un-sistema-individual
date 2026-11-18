. C:\cap\comun.ps1
$Host.UI.RawUI.WindowTitle = 'WS2025-DC - estado del dominio'
P 'Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias Ethernet | ft IPAddress,PrefixLength'
P '(Get-NetRoute 0.0.0.0/0).NextHop'
P '(Get-DnsClientServerAddress Ethernet -AddressFamily IPv4).ServerAddresses'
P 'Get-ADDomain | fl DNSRoot,NetBIOSName,DomainMode,PDCEmulator'
P 'Get-Service ADWS,DNS,Netlogon,Kdc | ft Status,Name,DisplayName -AutoSize'
