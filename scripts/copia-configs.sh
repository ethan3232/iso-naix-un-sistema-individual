#!/usr/bin/env bash
# =============================================================================
# copia-configs.sh — Copia automática de las configuraciones críticas de LAN23
# Se ejecuta EN EL NAS (TrueNAS, usuario izan) y RECOGE (pull) las copias:
# los equipos no guardan credenciales del NAS → si un router se compromete,
# no puede borrar las copias.
#
# Destino : /mnt/copias/configs/<equipo>/<AAAA-MM-DD_HHMM>/
# Registro: /mnt/copias/configs/copias.log
# Retención: se borran las copias de más de RETENCION_DIAS días.
# Programado: tarea cron de TrueNAS (System → Advanced → Cron Jobs), cada día a las 02:00.
# Uso manual: ./copia-configs.sh            (todos los equipos)
#             ./copia-configs.sh mikrotik   (solo uno)
# =============================================================================
set -uo pipefail

BASE=/mnt/copias/configs
RETENCION_DIAS=14
FECHA=$(date +%Y-%m-%d_%H%M)
LOG="$BASE/copias.log"
KEY="$HOME/.ssh/id_copias"
SSH="ssh -i $KEY -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new"
SCP="scp -q -i $KEY -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new"

log() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

# Comprueba si el equipo responde al puerto SSH antes de intentar la copia
vivo() { timeout 3 bash -c "</dev/tcp/$1/22" 2>/dev/null; }

copia_mikrotik() {   # MikroTik RouterOS — 192.168.23.1
  local ip=192.168.23.1 d="$BASE/mikrotik/$FECHA"
  vivo $ip || { log "AVISO mikrotik ($ip) no responde: copia omitida"; return 1; }
  mkdir -p "$d"
  $SSH izan@$ip "/export terse" > "$d/mikrotik-export.rsc" || return 1   # texto; por defecto RouterOS 7 oculta los datos sensibles
  $SSH izan@$ip "/system backup save name=copia-nas dont-encrypt=yes" >/dev/null || return 1
  sleep 2
  $SCP izan@$ip:copia-nas.backup "$d/mikrotik.backup" || return 1                         # binario, restaurable
  log "OK mikrotik -> $d ($(du -sh "$d" | cut -f1))"
}

copia_debian_srv() { # Debian SRV nftables — 192.168.23.3
  local ip=192.168.23.3 d="$BASE/debian-srv/$FECHA"
  vivo $ip || { log "AVISO debian-srv ($ip) no responde: copia omitida"; return 1; }
  mkdir -p "$d"
  # sudo sin contraseña SOLO para este comando exacto (ver /etc/sudoers.d/copias en deb-srv)
  $SSH izan@$ip "sudo /usr/bin/tar czf - -C / etc" > "$d/etc.tgz" || return 1
  $SSH izan@$ip "sudo /usr/sbin/nft list ruleset" > "$d/nft-ruleset.txt" || return 1
  log "OK debian-srv -> $d ($(du -sh "$d" | cut -f1))"
}

copia_opnsense() {   # OPNsense — 192.168.23.2 (por su API; la clave está en ~/.opnsense-apikey, permisos 600)
  local ip=192.168.23.2 d="$BASE/opnsense/$FECHA"
  timeout 3 bash -c "</dev/tcp/$ip/443" 2>/dev/null || { log "AVISO opnsense ($ip) no responde: copia omitida"; return 1; }
  mkdir -p "$d"
  curl -sk -m 30 -u "$(cat "$HOME/.opnsense-apikey")" -o "$d/config.xml" "https://$ip/api/core/backup/download/this" || return 1
  grep -q "<opnsense>" "$d/config.xml" || { log "ERROR opnsense: la descarga no es un config.xml"; return 1; }
  log "OK opnsense -> $d ($(du -sh "$d" | cut -f1))"
}

copia_proxmox() {    # Proxmox VE — 192.168.23.11 (configuración del nodo y del clúster)
  local ip=192.168.23.11 d="$BASE/proxmox/$FECHA"
  vivo $ip || { log "AVISO proxmox ($ip) no responde: copia omitida"; return 1; }
  mkdir -p "$d"
  $SSH root@$ip "tar czf - -C / etc/pve etc/network/interfaces etc/hosts etc/hostname etc/corosync 2>/dev/null" > "$d/pve-config.tgz" || return 1
  log "OK proxmox -> $d ($(du -sh "$d" | cut -f1))"
}

copia_truenas() {    # El propio NAS: exporta su base de datos de configuración
  local d="$BASE/truenas/$FECHA"
  mkdir -p "$d"
  cp /data/freenas-v1.db "$d/freenas-v1.db" 2>/dev/null || sudo -n cp /data/freenas-v1.db "$d/freenas-v1.db" || return 1
  log "OK truenas -> $d ($(du -sh "$d" | cut -f1))"
}

limpieza() {
  find "$BASE" -mindepth 2 -maxdepth 2 -type d -name '20*' -mtime +$RETENCION_DIAS -print -exec rm -rf {} + | while read -r x; do log "BORRADA copia antigua $x"; done
}

log "=== Inicio de copias ($FECHA) ==="
errores=0
for eq in ${1:-mikrotik debian_srv opnsense proxmox truenas}; do
  "copia_${eq//-/_}" || { errores=$((errores+1)); log "ERROR en $eq"; }
done
limpieza
log "=== Fin de copias: $errores equipo(s) con error ==="
exit 0
