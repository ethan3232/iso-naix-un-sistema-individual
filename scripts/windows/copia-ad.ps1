# Copia de seguridad del Directorio Activo (IFM = Install From Media) en WS2025-DC
# Genera una instantánea coherente de ntds.dit + registro + SYSVOL y la comprime.
$fecha = Get-Date -Format 'yyyy-MM-dd_HHmm'
$dir = "C:\copias\ifm-$fecha"
New-Item -ItemType Directory -Force -Path C:\copias | Out-Null
ntdsutil "activate instance ntds" "ifm" "create sysvol full $dir" quit quit
Compress-Archive -Path "$dir\*" -DestinationPath "C:\copias\ad-asix23-$fecha.zip" -Force
Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue  # las uniones de SYSVOL pueden dar avisos al borrar
Get-ChildItem C:\copias\*.zip | Sort-Object LastWriteTime | Select-Object -Last 1 | Format-Table Name, Length -AutoSize | Out-String
