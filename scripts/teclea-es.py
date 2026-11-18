#!/usr/bin/env python3
"""Escribe texto en una VM con distribución de teclado ESPAÑOLA.

`VBoxManage keyboardputstring` usa la distribución de EE. UU., y en una VM con
teclado español salen mal símbolos como - / \\ : | @. Este script traduce cada
carácter a los códigos de tecla (scancodes) del teclado español.

Uso: scripts/teclea-es.py <vm> "texto" [--enter]
"""
import subprocess
import sys

SHIFT, ALTGR = "shift", "altgr"
# carácter -> (scancode, modificador)
TECLAS = {
    " ": (0x39, None), "\t": (0x0F, None), "\n": (0x1C, None),
    "º": (0x29, None), "ª": (0x29, SHIFT), "\\": (0x29, ALTGR),
    "'": (0x0C, None), "?": (0x0C, SHIFT), "¡": (0x0D, None), "¿": (0x0D, SHIFT),
    "`": (0x1A, None), "^": (0x1A, SHIFT), "[": (0x1A, ALTGR),
    "+": (0x1B, None), "*": (0x1B, SHIFT), "]": (0x1B, ALTGR),
    "´": (0x28, None), "{": (0x28, ALTGR), "}": (0x2B, ALTGR), "ç": (0x2B, None),
    ",": (0x33, None), ";": (0x33, SHIFT), ".": (0x34, None), ":": (0x34, SHIFT),
    "-": (0x35, None), "_": (0x35, SHIFT), "<": (0x56, None), ">": (0x56, SHIFT),
    "!": (0x02, SHIFT), '"': (0x03, SHIFT), "·": (0x04, SHIFT), "$": (0x05, SHIFT),
    "%": (0x06, SHIFT), "&": (0x07, SHIFT), "/": (0x08, SHIFT), "(": (0x09, SHIFT),
    ")": (0x0A, SHIFT), "=": (0x0B, SHIFT),
    "|": (0x02, ALTGR), "@": (0x03, ALTGR), "#": (0x04, ALTGR), "~": (0x05, ALTGR),
}
for i, c in enumerate("1234567890"):
    TECLAS[c] = (0x02 + i, None)
FILAS = ["qwertyuiop", "asdfghjklñ", "zxcvbnm"]
INICIO = [0x10, 0x1E, 0x2C]
for fila, ini in zip(FILAS, INICIO):
    for i, c in enumerate(fila):
        TECLAS[c] = (ini + i, None)
        TECLAS[c.upper()] = (ini + i, SHIFT)
TECLAS["ñ"] = (0x27, None)
TECLAS["Ñ"] = (0x27, SHIFT)


def codigos(texto):
    out = []
    for ch in texto:
        sc, mod = TECLAS[ch]
        pre, post = [], []
        if mod == SHIFT:
            pre, post = ["2a"], ["aa"]
        elif mod == ALTGR:
            pre, post = ["e0", "38"], ["e0", "b8"]
        out += pre + [f"{sc:02x}", f"{sc | 0x80:02x}"] + post
    return out


def main():
    vm, texto = sys.argv[1], sys.argv[2]
    if "--enter" in sys.argv[3:]:
        texto += "\n"
    cods = codigos(texto)
    for i in range(0, len(cods), 60):  # en bloques para no saturar el búfer del teclado
        subprocess.run(["VBoxManage", "controlvm", vm, "keyboardputscancode", *cods[i:i + 60]], check=True)


if __name__ == "__main__":
    main()
