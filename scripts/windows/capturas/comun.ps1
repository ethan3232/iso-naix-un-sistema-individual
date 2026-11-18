# Funciones comunes para las capturas: muestra el comando como si se escribiera y después su salida real.
$Host.UI.RawUI.BackgroundColor = 'Black'; $Host.UI.RawUI.ForegroundColor = 'Gray'
try { $Host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size(140, 3000) } catch {}
Clear-Host
function P([string]$c) {
    Write-Host "PS C:\> " -NoNewline -ForegroundColor Yellow
    Write-Host $c -ForegroundColor White
    Invoke-Expression $c | Out-String -Width 130 | ForEach-Object { $_.TrimEnd() } | Write-Host
    Write-Host ""
}
