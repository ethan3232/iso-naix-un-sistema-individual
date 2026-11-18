# Transversal · Predicciones, plan de contingencia

## 1. Predicciones (antes de investigar)

Antes de cada fase escribí lo que esperaba que pasara, para compararlo después con el resultado (método ThinkLoop: predicción → investigación → implementación → verificación → análisis).

→ [00-prediccions](../docs/00-prediccions.md)

## 2. Plan de contingencia con RTO/RPO y tiempos reales

- **RTO** = cuánto tiempo puede estar parada una función. **RPO** = cuántos datos se pueden perder (desde la última copia).
- **13 escenarios**, **9 probados** provocando el fallo de verdad y midiendo el tiempo.

| Escenario | RTO objetivo | Tiempo real | Pérdida |
|---|---|---|---|
| MikroTik con la configuración borrada | 5 min | **26 s** | 0 |
| Debian nftables roto + reinicio | 5 min | **21 s** | 0 |
| OPNsense con una regla errónea | 5 min | **15 s** | 0 |
| Router activo caído | 5 min | Cambio de gateway a `.2`/`.3` | 0 |
| Mantenimiento de un nodo Proxmox | 2 min | VM: **8 ms** · contenedor: ~84 s | 0 |
| Nodo del clúster caído | Inmediato | Sigue con quórum 2 de 3 | 0 |
| VM que no arranca (`fstab`) | 30 min | Resuelto con el método de diagnóstico | 0 |
| Disco roto en RAID 1/5 | 0 | 0 s sin servicio · reconstrucción 54 s / 15 s | 0 |
| Servidor de ficheros caído (DRBD) | 5 min | **~13 s** | 0 |
| DC de Windows perdido · cliente estropeado · host roto · disco del NAS | — | 🧪 Simulados: con copia hecha y verificada | Según la copia |

**Punto único de fallo:** el PC anfitrión. En una empresa real habría varios hosts físicos y el NAS fuera del host.

→ [09-contingencia](../docs/09-contingencia.md) (fichas por escenario: síntomas, dependencias, pasos, prueba final)

## 3. Incidencias

26 problemas reales encontrados durante el montaje, cada uno con síntoma, causa, solución y lección aprendida.

→ [10-incidencies](../docs/10-incidencies.md)
