# /etc/drbd.d/r0.res — RAID 1 por red (DRBD) entre DEB13-SRV2 y DEB13-SRV3
# Igual en los dos servidores. Los discos se nombran por su número de serie (/dev/disk/by-id),
# porque las letras sdX cambian al añadir discos (pasó al añadir este).
resource r0 {
  protocol C;                 # síncrono: la escritura termina cuando está en los DOS discos
  device    /dev/drbd0;       # el disco "espejo" que se formatea y se monta
  meta-disk internal;         # los metadatos de DRBD van al final del propio disco
  net {
    after-sb-0pri discard-zero-changes;   # recuperación automática si un lado no tenía cambios
  }
  on deb13-srv2 {             # debe coincidir con `uname -n`
    disk    /dev/disk/by-id/ata-VBOX_HARDDISK_VB5c4301f8-133fabf4;
    address 192.168.23.21:7789;
  }
  on deb13-srv3 {
    disk    /dev/disk/by-id/ata-VBOX_HARDDISK_VB8435b78f-30f53b1d;
    address 192.168.23.22:7789;
  }
}
