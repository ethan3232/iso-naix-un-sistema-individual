#!/usr/bin/env bash
# fio-disco.sh — 4 pruebas de disco dentro de una VM (se ejecuta DENTRO de la VM, como root). Datos aleatorios (no ceros).
# Cada prueba escribe/lee como máximo 1 GB o 20 s (sin repetir): así no se agota la caché SLC del SSD del host.
f=/var/tmp/fio.test
for t in "secuencial-escritura write 1M" "aleatoria-escritura-4k randwrite 4k" "aleatoria-lectura-4k randread 4k" "escritura-4k-con-fsync randwrite 4k 1"; do
  set -- $t
  r=$(fio --name=$1 --filename=$f --size=1G --rw=$2 --bs=$3 --direct=1 --ioengine=libaio --iodepth=1 --runtime=20 ${4:+--fsync=$4} --output-format=terse --terse-version=3)
  echo "$r" | awk -F';' -v n=$1 '{ if (n ~ /lectura/) printf "%-24s %8.1f MB/s %8d IOPS\n", n, $7/1024, $8; else printf "%-24s %8.1f MB/s %8d IOPS\n", n, $48/1024, $49 }'
done
rm -f $f
