# Registros DNS (tipo A) de los equipos de LAN23 en la zona del dominio asix23.lan
# Ejecutar en WS2025-DC como administrador del dominio.
$registros = [ordered]@{
  'mikrotik'='192.168.23.1'; 'opnsense'='192.168.23.2'; 'deb-srv'='192.168.23.3'
  'truenas'='192.168.23.10'; 'pmx1'='192.168.23.11'; 'pmx2'='192.168.23.12'
  'srv-infra'='192.168.23.30'; 'intranet'='192.168.23.30'; 'deb13-cli'='192.168.23.54'
}
foreach ($n in $registros.Keys) {
  if (-not (Get-DnsServerResourceRecord -ZoneName 'asix23.lan' -Name $n -RRType A -ErrorAction SilentlyContinue)) {
    Add-DnsServerResourceRecordA -ZoneName 'asix23.lan' -Name $n -IPv4Address $registros[$n]
  }
}
Get-DnsServerResourceRecord -ZoneName 'asix23.lan' -RRType A |
  Format-Table HostName, @{n='IP';e={$_.RecordData.IPv4Address}} -AutoSize | Out-String
Resolve-DnsName intranet.asix23.lan | Format-Table Name, IPAddress -AutoSize | Out-String
