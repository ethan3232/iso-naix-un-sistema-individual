#!/usr/bin/env python3
"""Cliente mínimo de la API de OPNsense usando una sesión de la web (como el navegador).
No guarda contraseñas: la lee de la variable de entorno OPN_PASS.

Uso:
  OPN_PASS=... scripts/opnsense-api.py GET  /api/core/firmware/status
  OPN_PASS=... scripts/opnsense-api.py POST /api/firewall/filter/apply '{}'
  OPN_PASS=... scripts/opnsense-api.py DOWNLOAD /api/core/backup/download/this salida.xml
Variables: OPN_URL (por defecto https://127.0.0.1:8402), OPN_USER (root), OPN_PASS.
"""
import http.cookiejar, json, os, re, ssl, sys, urllib.parse, urllib.request

URL = os.environ.get("OPN_URL", "https://127.0.0.1:8402")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE  # certificado autofirmado
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), urllib.request.HTTPCookieProcessor(jar))

def login():
    html = op.open(URL + "/").read().decode()
    m = re.search(r'name="([^"]+)" value="([^"]+)" autocomplete="new-password"', html) \
        or re.search(r'<input type="hidden" name="([^"]+)" value="([^"]+)"', html)
    data = {"usernamefld": os.environ.get("OPN_USER", "root"), "passwordfld": os.environ["OPN_PASS"], "login": "1"}
    if m: data[m.group(1)] = m.group(2)
    html = op.open(URL + "/", urllib.parse.urlencode(data).encode()).read().decode()
    tok = re.search(r'"X-CSRFToken",\s*"([^"]+)"', html) or re.search(r"X-CSRFToken['\"],\s*['\"]([^'\"]+)", html)
    if not tok: sys.exit("Login fallido en OPNsense")
    return tok.group(1)

def call(method, path, body=None, token=None):
    req = urllib.request.Request(URL + path, method="GET" if method in ("GET", "DOWNLOAD") else "POST")
    req.add_header("X-CSRFToken", token)
    if body is not None:
        req.add_header("Content-Type", "application/json"); req.data = body.encode()
    import http.client
    try:
        return op.open(req).read()
    except http.client.IncompleteRead as e:   # respuestas grandes troceadas: nos quedamos con lo recibido
        return e.partial

if __name__ == "__main__":
    method, path = sys.argv[1].upper(), sys.argv[2]
    tok = login()
    if method == "DOWNLOAD":
        open(sys.argv[3], "wb").write(call("GET", path, token=tok)); print("guardado", sys.argv[3])
    else:
        out = call(method, path, sys.argv[3] if len(sys.argv) > 3 else ("{}" if method == "POST" else None), tok)
        if os.environ.get("OPN_RAW"): sys.stdout.write(out.decode(errors="replace")); sys.exit(0)
        try: print(json.dumps(json.loads(out), indent=1, ensure_ascii=False)[:4000])
        except Exception: print(out[:2000].decode(errors="replace"))
