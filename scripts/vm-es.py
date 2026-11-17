#!/usr/bin/env python3
"""Escribe texto en una VM cuyo teclado está en distribución ESPAÑOLA.
VBoxManage keyboardputstring asume teclado de EE. UU.; aquí se calculan los
scancodes para que el sistema invitado (layout es) reciba el carácter correcto.
Uso: vm-es.py <vm> "texto" [--no-enter]
"""
import subprocess, sys

BASE = {}
for i, c in enumerate("1234567890"): BASE[c] = 0x02 + i
for row, start in (("qwertyuiop", 0x10), ("asdfghjkl", 0x1e), ("zxcvbnm", 0x2c)):
    for i, c in enumerate(row): BASE[c] = start + i
BASE[" "] = 0x39
S, A = "S", "A"   # S = con Mayús, A = con AltGr
ES = {"-": 0x35, "_": (S, 0x35), ".": 0x34, ":": (S, 0x34), ",": 0x33, ";": (S, 0x33),
      "'": 0x0c, "?": (S, 0x0c), "+": 0x1b, "*": (S, 0x1b), "<": 0x56, ">": (S, 0x56),
      "!": (S, 0x02), '"': (S, 0x03), "$": (S, 0x05), "%": (S, 0x06), "&": (S, 0x07),
      "/": (S, 0x08), "(": (S, 0x09), ")": (S, 0x0a), "=": (S, 0x0b),
      "|": (A, 0x02), "@": (A, 0x03), "#": (A, 0x04), "~": (A, 0x05), "\\": (A, 0x29),
      "[": (A, 0x1a), "]": (A, 0x1b), "{": (A, 0x28), "}": (A, 0x2b)}

def codes(ch):
    if ch in BASE: return [f"{BASE[ch]:02x}", f"{BASE[ch]|0x80:02x}"]
    if ch.isalpha() and ch.lower() in BASE:
        k = BASE[ch.lower()]; return ["2a", f"{k:02x}", f"{k|0x80:02x}", "aa"]
    v = ES.get(ch)
    if v is None: raise SystemExit(f"Carácter no soportado: {ch!r}")
    if isinstance(v, int): return [f"{v:02x}", f"{v|0x80:02x}"]
    mod, k = v
    pre, post = (["2a"], ["aa"]) if mod == S else (["e0", "38"], ["e0", "b8"])
    return pre + [f"{k:02x}", f"{k|0x80:02x}"] + post

vm, text = sys.argv[1], sys.argv[2]
seq = [c for ch in text for c in codes(ch)]
if "--no-enter" not in sys.argv: seq += ["1c", "9c"]
for i in range(0, len(seq), 60):   # en trozos para no saturar el búfer de teclado
    subprocess.run(["VBoxManage", "controlvm", vm, "keyboardputscancode", *seq[i:i+60]], check=True)
