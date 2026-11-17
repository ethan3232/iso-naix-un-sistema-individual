# 10 · Incidencias

| Fecha | Máquina | Síntoma | Hipótesis | Comprobación | Solución | Vuelta al estado normal |
|---|---|---|---|---|---|---|
| 2026-11-17 | TrueNas | Arrancaba el instalador en vez del sistema | La ISO seguía conectada y el DVD va antes que el disco en el orden de arranque | El disco ya ocupaba 3,5 GB → sistema instalado | Desconectar la ISO del lector | Arranca TrueNAS 25.10.7 desde el disco |
| 2026-11-17 | Host | `sudo` no funciona desde terminal | No hay terminal para pedir la contraseña | Error `a terminal is required` | Instalar `gh` sin sudo en `~/.local/bin` | `gh` 2.104.0 funcionando |
