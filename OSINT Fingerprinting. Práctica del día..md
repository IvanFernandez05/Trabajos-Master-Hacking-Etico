#### 1. ¿Qué es  el User-Agent?

El User-Agent es una cadena enviada por el navegador o cliente HTTP en cada petición web.

Este es un ejemplo de user-agent:

```bash
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36
```

De esa cadena se puede extraer:
- Sistema operativo (Windows 10, Linux, Android, etc.)
- Arquitectura (x86, x64, ARM, etc.)
- Navegador y versión (Chrome 128, Firefox 121, etc.)
- Motor de renderizado (Blink, Gecko, WebKi, etc.)

#### 2. Herramientas OSINT que recopilan o utilizan el User-Agent

##### 2.1 Herramientas Pasivas

| Herramienta                    | Cómo obtiene User-Agent                                                                                                                             |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Shodan**                     | Cuando un dispositivo tiene un servicio HTTP visible, Shodan almacena las respuestas, encabezados y _a veces_ los User-Agent detectados en banners. |
| **Censys**                     | Similar a Shodan; indexa metadatos HTTP y puede mostrar el User-Agent usado en escaneos o el que responde el servidor.                              |
| **LeakCheck / HaveIBeenPwned** | Si una brecha de datos incluye logs de acceso o tokens con cabeceras HTTP, puede aparecer el User-Agent.                                            |
| **OSINT Framework / Recon-ng** | Algunos módulos extraen información de cabeceras HTTP sin tocar el objetivo directamente (usando fuentes públicas o cachés de motores).             |
| **VirusTotal**                 | Si un archivo o URL ha sido analizado, la plataforma puede mostrar las cabeceras HTTP asociadas (incluyendo User-Agent del cliente original).       |
##### 2.2 Herramientas Activas

| Herramienta                                | Cómo lo usa o recopila                                                                                                                 |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **theHarvester**                           | Cuando realiza consultas a motores o servicios, puede registrar las respuestas HTTP y sus cabeceras, incluido el User-Agent.           |
| **Burp Suite / OWASP ZAP**                 | Capturan tráfico HTTP/HTTPS y muestran o permiten modificar el User-Agent de cada petición.                                            |
| **Wappalyzer / WhatWeb**                   | Analizan sitios web y recopilan el User-Agent tanto del cliente (para pruebas) como el que devuelve el servidor.                       |
| **Nmap (scripts NSE)**                     | Algunos scripts HTTP (`http-headers`, `http-useragent-tester`, etc.) pueden revelar o probar distintas respuestas según el User-Agent. |
| **Metasploit**                             | En fases de reconocimiento o explotación web, algunos módulos guardan y manipulan User-Agents para evadir detección o fingerprinting.  |
| **Curl / HTTPie / recon-ng (modo activo)** | Permiten especificar y registrar manualmente User-Agents en peticiones de prueba.                                                      |

#### 3. Script en Python que haga la enumeración pasiva y activa

Realiza enumeración pasiva (whois, certificados en crt.sh, Wayback Machine, registros DNS) y opcionalmente una fase activa con nmap; reúne toda la información sobre un dominio en un JSON para que veas subdominios, snapshots archivados.

Hay que guardarlo como "enumeration.py"

``` python
#!/usr/bin/env python3
"""
enumeration.py
Enumeración pasiva y activa básica para un dominio:
- Pasiva: whois, crt.sh (certificados -> subdominios), Wayback CDX, DNS (A, MX, NS, TXT)
- Activa: escaneos básicos con nmap (si está instalado) -- opcional
Salida: JSON + prints por consola.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

import requests

try:
    import whois
except Exception:
    whois = None

try:
    import dns.resolver
except Exception:
    dns = None

OUTPUT_DIR = "outputs_enumeration"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_output(domain, obj):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(OUTPUT_DIR, f"{domain.replace('*','_')}_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    print(f"[+] Resultado guardado en: {path}")


def do_whois(domain):
    print("[*] WHOIS...")
    if whois is None:
        print("    librería whois no instalada. Instálala con: pip install python-whois")
        return {"error": "whois not installed"}
    try:
        w = whois.whois(domain)
        return dict(w)
    except Exception as e:
        return {"error": str(e)}


def crtsh_subdomains(domain):
    """
    Consulta crt.sh para obtener certificados y extraer nombres.
    """
    print("[*] crt.sh (buscando certificados)...")
    url = "https://crt.sh/"
    params = {"q": f"%{domain}", "output": "json"}
    try:
        r = requests.get(url, params=params, timeout=20)
        # crt.sh sometimes devuelve 200 con no json; proteger
        data = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else r.json()
    except Exception as e:
        return {"error": f"crt.sh request failed: {e}"}
    names = set()
    for item in data:
        name = item.get("name_value") or item.get("common_name")
        if not name:
            continue
        # name_value may contain multiple names separated by \n
        for n in re.split(r"[\n,]+", name):
            n = n.strip()
            if n:
                names.add(n.lower())
    # filtrado por dominio que nos interesa
    subdomains = sorted([n for n in names if n.endswith(domain.lower())])
    return {"subdomains": subdomains, "count": len(subdomains)}


def wayback_snapshots(domain, limit=50):
    """
    Usa la CDX API de Wayback Machine para recuperar URLs archivadas.
    """
    print("[*] Wayback CDX (snapshots)...")
    cdx = "http://web.archive.org/cdx/search/cdx"
    params = {
        "url": f"*.{domain}/*",
        "output": "json",
        "fl": "timestamp,original,statuscode",
        "filter": "statuscode:200",
        "limit": limit,
    }
    try:
        r = requests.get(cdx, params=params, timeout=20)
        data = r.json()
    except Exception as e:
        return {"error": f"wayback request failed: {e}"}
    if not data:
        return {"snapshots": []}
    headers = data[0]
    rows = data[1:]
    snapshots = [{"timestamp": row[0], "url": row[1], "status": row[2] if len(row) > 2 else ""} for row in rows]
    return {"snapshots": snapshots, "count": len(snapshots)}


def dns_records(domain):
    print("[*] DNS (A, AAAA, MX, NS, TXT)...")
    if dns is None:
        print("    librería dnspython no instalada. Instálala con: pip install dnspython")
        return {"error": "dnspython not installed"}
    resolver = dns.resolver.Resolver()
    types = ["A", "AAAA", "MX", "NS", "TXT"]
    out = {}
    for t in types:
        try:
            answers = resolver.resolve(domain, t, lifetime=5)
            vals = []
            for r in answers:
                vals.append(r.to_text())
            out[t] = sorted(list(set(vals)))
        except Exception as e:
            out[t] = f"error or no records: {e}"
    return out


def nmap_scan(target, args="-Pn -sS -T4"):
    """
    Ejecuta nmap si está instalado en el sistema (subprocess).
    - target puede ser IP o dominio.
    """
    print("[*] Nmap scan (si nmap está instalado)...")
    if not shutil_which("nmap"):
        return {"error": "nmap not installed or not in PATH"}
    cmd = ["nmap"] + args.split() + [target]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {"returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
    except Exception as e:
        return {"error": str(e)}


def shutil_which(name):
    # pequeña compatibilidad, no importamos shutil al tope
    from shutil import which

    return which(name)


def main():
    parser = argparse.ArgumentParser(description="Enumeración pasiva y activa básica")
    parser.add_argument("domain", help="Dominio a enumerar (ej: example.com)")
    parser.add_argument("--no-active", action="store_true", help="No ejecutar fases activas (nmap)")
    parser.add_argument("--nmap-args", default="-Pn -sS -T4", help="Argumentos para nmap (si se usa)")
    args = parser.parse_args()
    domain = args.domain.strip().lower()

    result = {"domain": domain, "timestamp_utc": datetime.utcnow().isoformat()}

    result["whois"] = do_whois(domain)
    result["crtsh"] = crtsh_subdomains(domain)
    result["wayback"] = wayback_snapshots(domain, limit=100)
    result["dns"] = dns_records(domain)

    if not args.no_active:
        # nmap only if system has nmap
        if shutil_which("nmap"):
            print("[*] Ejecutando nmap (puede tardar)...")
            try:
                result["nmap"] = nmap_scan(domain, args.nmap_args)
            except Exception as e:
                result["nmap"] = {"error": str(e)}
        else:
            result["nmap"] = {"error": "nmap no encontrado en PATH. Instala nmap para escaneo activo."}

    save_output(domain, result)
    print("\nResumen rápido:")
    print(f" - subdominios crt.sh: {result['crtsh'].get('count') if isinstance(result.get('crtsh'), dict) else 'N/A'}")
    print(f" - wayback snapshots: {result['wayback'].get('count') if isinstance(result.get('wayback'), dict) else 'N/A'}")


if __name__ == "__main__":
    main()
```

Ejecutamos el script en Kali Linux

``` python
┌──(venv)─(kali㉿kali)-[~/Desktop]
└─$ python3 enumeration.py megacorpone.com 
```

Y se nos guardara un .json con la siguiente información.

``` bash
┌──(venv)─(kali㉿kali)-[~/Desktop]
└─$ cat outputs_enumeration/megacorpone.com_20251015T175348Z.json 
{
  "domain": "megacorpone.com",
  "timestamp_utc": "2025-10-15T17:53:24.172511",
  "whois": {
    "domain_name": "MEGACORPONE.COM",
    "registrar": "Gandi SAS",
    "registrar_url": "http://www.gandi.net",
    "reseller": null,
    "whois_server": "whois.gandi.net",
    "referral_url": null,
    "updated_date":                                                                
```

#### 4. Script que recoge información de las cabeceras de seguridad al hacer una petición a cualquier sitio

Hace una petición HTTP(S) a una URL y extrae las cabeceras relacionadas con seguridad, mostrando lo que falta o está presente y guardando un JSON con los resultados para revisar la postura de seguridad típica de ese sitio.

Lo guardaremos como "security_headers.py"

```python
#!/usr/bin/env python3
"""
security_headers.py
Realiza una petición GET a una URL y muestra/guarda las cabeceras de seguridad:
- Content-Security-Policy, Strict-Transport-Security, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, etc.
Salida: JSON en outputs_headers/
"""

import argparse
import json
import os
from datetime import datetime

import requests

OUTPUT_DIR = "outputs_headers"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SECURITY_HEADER_KEYS = [
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "expect-ct",
    "x-permitted-cross-domain-policies",
    "feature-policy",  # deprecated name sometimes present
    "public-key-pins",  # deprecated but might appear
]


def fetch_headers(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": "security-checker/1.0"})
    except Exception as e:
        return {"error": str(e)}
    headers = {k.lower(): v for k, v in r.headers.items()}
    security = {k: headers.get(k) for k in SECURITY_HEADER_KEYS if headers.get(k) is not None}
    return {
        "url": url,
        "status_code": r.status_code,
        "final_url": r.url,
        "security_headers": security,
        "all_headers": headers,
    }


def save_result(url, obj):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe = url.replace("://", "_").replace("/", "_")
    path = os.path.join(OUTPUT_DIR, f"{safe}_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    print(f"[+] Guardado en {path}")


def main():
    parser = argparse.ArgumentParser(description="Comprobar cabeceras de seguridad de una URL")
    parser.add_argument("url", help="URL a comprobar (ej: https://example.com)")
    parser.add_argument("--save", action="store_true", help="Guardar resultado en JSON")
    args = parser.parse_args()

    res = fetch_headers(args.url)
    if "error" in res:
        print("Error:", res["error"])
        return
    print(f"URL final: {res['final_url']} (HTTP {res['status_code']})\n")
    print("Cabeceras de seguridad encontradas:")
    if res["security_headers"]:
        for k, v in res["security_headers"].items():
            print(f" - {k}: {v}")
    else:
        print("  (No se encontraron cabeceras de seguridad estándar)")

    if args.save:
        save_result(args.url, res)


if __name__ == "__main__":
    main()
```

Lo lanzamos

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ python3 security_headers.py http://megacorpone.com --save
```

Y vemos el output

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ cat outputs_headers/http_megacorpone.com_20251015T180250Z.json 
{
  "url": "http://megacorpone.com",
  "status_code": 200,
  "final_url": "http://megacorpone.com/",
  "security_headers": {},
  "all_headers": {
    "date": "Wed, 15 Oct 2025 18:02:53 GMT",
    "server": "Apache/2.4.65 (Debian)",
    "last-modified": "Wed, 06 Nov 2019 15:04:14 GMT",
    "etag": "\"390b-596aedca79780-gzip\"",
    "accept-ranges": "bytes",
    "vary": "Accept-Encoding",
    "content-encoding": "gzip",
    "content-length": "3779",
    "keep-alive": "timeout=5, max=100",
    "connection": "Keep-Alive",
    "content-type": "text/html"
  }
} 
```

##### 4.1 Servidor HTTP que guarda "User-Agent" en archivo local

Este script monta un servidor con Flask, cuando alguien visita "/collect" (o cualquier ruta configurada), el script captura "User-Agent" y otras cabeceras útiles y las guarda en "capturas_user_agents.log"

``` python
#!/usr/bin/env python3
"""
user_agent_capture_server.py
Servidor Flask simple que captura cabeceras de las peticiones (incluido User-Agent)
y las guarda a disco. Diseñado para exponer con ngrok o ser usado como "request bin".

Rutas:
 - GET / -> simple página de info
 - any /collect (GET/POST) -> captura cabeceras, IP y user-agent y las guarda
"""

from datetime import datetime
import json
import os
from flask import Flask, request, jsonify, render_template_string

OUTPUT_LOG = "capturas_user_agents.log"
OUTPUT_DIR = "capturas_json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<title>User-Agent Collector</title>
<h2>User-Agent Collector</h2>
<p>Punto de captura: <code>/collect</code></p>
<p>Envía una petición GET o POST a /collect; los headers se guardarán en servidor.</p>
"""

def save_capture(data):
    # append a short log
    with open(OUTPUT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    # save full JSON file
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"capture_{ts}.json"
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/collect", methods=["GET", "POST"])
def collect():
    headers = {k: v for k, v in request.headers.items()}
    user_agent = headers.get("User-Agent", "")
    # intentar obtener IP real (X-Forwarded-For si viene por ngrok/reverse proxy)
    remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
    payload = None
    try:
        payload = request.get_json(silent=True)
    except Exception:
        payload = None
    data = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "remote_addr": remote_addr,
        "method": request.method,
        "path": request.path,
        "user_agent": user_agent,
        "headers": headers,
        "query_params": request.args.to_dict(),
        "payload": payload,
    }
    save_capture(data)
    # respuesta sencilla para la persona que visita
    return jsonify({"status": "captured", "user_agent": user_agent}), 200


if __name__ == "__main__":
    # requisitos: pip install flask
    app.run(host="0.0.0.0", port=5000, debug=False)
```

Lanzamos los siguientes comandos, el primero activa el "venv" y el segundo ejecuta el script.

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ source venv/bin/activate
```

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ python3 user_agent_capture_server.py
```

Vemos que algo así, esto significado que esta lanzado

```bash
┌──(venv)─(kali㉿kali)-[~/Desktop]
└─$ python3 user_agent_capture_server.py
 * Serving Flask app 'user_agent_capture_server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.181.128:5000
```

Probamos desde la maquina local a entrar en url donde hemos especificado que recolecte las cabeceras.

```bash
┌──(kali㉿kali)-[~]
└─$ curl -H "User-Agent: KaliTest/1.0" http://127.0.0.1:5000/collect
{"status":"captured","user_agent":"KaliTest/1.0"}
```

Y comprobamos que se ha guardado en el log

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ cat capturas_user_agents.log 
{"timestamp_utc": "2025-10-15T18:10:17.192415", "remote_addr": "127.0.0.1", "method": "GET", "path": "/collect", "user_agent": "KaliTest/1.0", "headers": {"Host": "127.0.0.1:5000", "Accept": "*/*", "User-Agent": "KaliTest/1.0"}, "query_params": {}, "payload": null}
{"timestamp_utc": "2025-10-15T18:10:42.132492", "remote_addr": "127.0.0.1", "method": "GET", "path": "/collect", "user_agent": "KaliTest/1.0", "headers": {"Host": "127.0.0.1:5000", "Accept": "*/*", "User-Agent": "KaliTest/1.0"}, "query_params": {}, "payload": null}
```

También comprobamos que se ha guardado la información de las cabeceras, lo importante.

```bash
┌──(kali㉿kali)-[~/Desktop/capturas_json]
└─$ ls
capture_20251015T181017Z.json  capture_20251015T181042Z.json                
┌──(kali㉿kali)-[~/Desktop/capturas_json]
└─$ cat capture_20251015T181017Z.json
{
  "timestamp_utc": "2025-10-15T18:10:17.192415",
  "remote_addr": "127.0.0.1",
  "method": "GET",
  "path": "/collect",
  "user_agent": "KaliTest/1.0",
  "headers": {
    "Host": "127.0.0.1:5000",
    "Accept": "*/*",
    "User-Agent": "KaliTest/1.0"
  },
  "query_params": {},
  "payload": null
}   
```
