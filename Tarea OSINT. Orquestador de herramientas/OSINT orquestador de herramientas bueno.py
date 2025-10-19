"""
OSINT Modular Tool (educational / lawful use)
- Uso: investigar dominios, emails (brechas con HaveIBeenPwned), WHOIS, DNS, metadatos de dominio, búsqueda de nombre de usuario en servicios públicos.
- Diseño modular: cada fuente es un "module" con la misma firma: run(target, config) -> dict
- Genera reporte JSON estructurado.
- Incluye una UI web básica (Flask) para ver el JSON y exportarlo a GraphML (formato compatible con Maltego via import XML/GraphML).

ADVERTENCIA LEGAL / ÉTICA:
No ejecutes esta herramienta contra personas privadas sin su consentimiento explícito ni para propósitos maliciosos. Usa únicamente con dominios/usuarios/emails que posees o cuando tengas autorización clara.

Requisitos:
pip install requests dnspython python-whois beautifulsoup4 Flask lxml

HaveIBeenPwned: necesitas una API key en HIBP_API_KEY (poner en config).
"""

import json
import requests
import socket
import whois
import dns.resolver
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string, send_file
from io import BytesIO
import xml.etree.ElementTree as ET
from datetime import datetime

# ------------------------- Utilities ---------------------------------

def safe_get(url, timeout=10, headers=None):
    try:
        r = requests.get(url, timeout=timeout, headers=headers or {})
        r.raise_for_status()
        return r
    except Exception as e:
        return None

# ------------------------- Modules -----------------------------------
# Each module implements run(target, config) -> dict

# 1) HaveIBeenPwned (email breaches)

def module_hibp(email, config):
    """Query HaveIBeenPwned for breaches and paste sites for an email.
    Requires config['hibp_api_key'] if HIBP requires key.
    """
    result = {'source': 'haveibeenpwned', 'email': email, 'breaches': [], 'pastes': []}
    api_key = config.get('hibp_api_key')
    headers = {'User-Agent': 'osint-tool/1.0'}
    if api_key:
        headers['hibp-api-key'] = api_key
    base = 'https://haveibeenpwned.com/api/v3'
    # breaches
    try:
        r = requests.get(f"{base}/breachedaccount/{email}", headers=headers, timeout=10)
        if r.status_code == 200:
            result['breaches'] = r.json()
        elif r.status_code == 404:
            result['breaches'] = []
        else:
            result['error'] = f"status {r.status_code}"
    except Exception as e:
        result['error'] = str(e)
    # pastes
    try:
        r = requests.get(f"{base}/pasteaccount/{email}", headers=headers, timeout=10)
        if r.status_code == 200:
            result['pastes'] = r.json()
        elif r.status_code == 404:
            result['pastes'] = []
    except Exception as e:
        result.setdefault('errors', []).append(str(e))
    return result

# 2) WHOIS

def module_whois(domain, config):
    result = {'source': 'whois', 'domain': domain}
    try:
        w = whois.whois(domain)
        # whois object may be dict-like
        result['whois_raw'] = dict(w)
    except Exception as e:
        result['error'] = str(e)
    return result

# 3) DNS (A, MX, TXT, NS)

def module_dns(domain, config):
    result = {'source': 'dns', 'domain': domain, 'records': {}}
    resolver = dns.resolver.Resolver()
    types = ['A', 'MX', 'TXT', 'NS', 'SOA', 'CNAME']
    for t in types:
        try:
            answers = resolver.resolve(domain, t, lifetime=5)
            vals = []
            for r in answers:
                vals.append(str(r).rstrip('\n'))
            result['records'][t] = vals
        except Exception as e:
            result['records'][t] = []
    return result

# 4) Domain metadata (title, meta tags, server header, favicon)

def module_meta(domain, config):
    url = domain
    if not url.startswith('http'):
        url = 'http://' + domain
    result = {'source': 'domain_meta', 'domain': domain, 'http': {}}
    r = safe_get(url, headers={'User-Agent':'osint-tool/1.0'})
    if not r:
        result['error'] = 'no http response'
        return result
    result['http']['status_code'] = r.status_code
    result['http']['headers'] = dict(r.headers)
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else ''
        metas = {m.get('name') or m.get('property') or f"meta_{i}": m.get('content') for i,m in enumerate(soup.find_all('meta'))}
        result['http']['title'] = title
        result['http']['meta'] = metas
    except Exception as e:
        result.setdefault('errors', []).append(str(e))
    # try favicon
    favicon = None
    try:
        ico = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if ico and ico.get('href'):
            href = ico.get('href')
            if href.startswith('http'):
                favicon = href
            else:
                favicon = url.rstrip('/') + '/' + href.lstrip('/')
    except Exception:
        pass
    result['http']['favicon'] = favicon
    return result

# 5) Username footprint (pluggable checks)

def module_username(username, config):
    """Check a list of public services for username presence.
    This module uses simple HTTP checks and public endpoints where allowed.
    """
    services = config.get('username_services', [
        ('GitHub', f'https://github.com/{username}'),
        ('Reddit', f'https://www.reddit.com/user/{username}'),
        ('Keybase', f'https://keybase.io/{username}'),
        ('Twitter', f'https://twitter.com/{username}'),
        ('Instagram', f'https://www.instagram.com/{username}/'),
    ])
    result = {'source': 'username', 'username': username, 'found_on': []}
    headers = {'User-Agent': 'osint-tool/1.0'}
    for name, url in services:
        try:
            r = requests.get(url, headers=headers, timeout=7)
            if r.status_code == 200:
                result['found_on'].append({'service': name, 'url': url, 'status': 200})
            elif r.status_code == 302 or r.status_code == 301:
                result['found_on'].append({'service': name, 'url': url, 'status': r.status_code})
        except Exception:
            pass
    return result

# ------------------------- Report builder ----------------------------

def build_report(targets, config):
    """targets: dict with optional keys: email, domain, username
    returns structured dict
    """
    report = {'generated_at': datetime.utcnow().isoformat() + 'Z', 'targets': targets, 'modules': []}
    if 'email' in targets:
        report['modules'].append(module_hibp(targets['email'], config))
    if 'domain' in targets:
        report['modules'].append(module_whois(targets['domain'], config))
        report['modules'].append(module_dns(targets['domain'], config))
        report['modules'].append(module_meta(targets['domain'], config))
    if 'username' in targets:
        report['modules'].append(module_username(targets['username'], config))
    return report

# ------------------------- Export to GraphML (simple) ----------------

def report_to_graphml(report):
    """Create a very simple GraphML containing nodes for email/domain/username and module findings.
    Maltego can import GraphML/GraphML-like formats; adjust as needed for your Maltego edition.
    """
    NS = 'http://graphml.graphdrawing.org/xmlns'
    graphml = ET.Element('graphml', xmlns=NS)
    graph = ET.SubElement(graphml, 'graph', edgedefault='undirected')
    nodes = []
    node_id = 0
    def make_node(label, ntype):
        nonlocal node_id
        nid = f'n{node_id}'
        node_id += 1
        n = ET.SubElement(graph, 'node', id=nid)
        data = ET.SubElement(n, 'data', key='label')
        data.text = f"{label} ({ntype})"
        return nid
    # target nodes
    tnodes = {}
    for k,v in report['targets'].items():
        tnodes[k] = make_node(v, k)
    # module nodes and edges
    for mod in report['modules']:
        label = mod.get('source')
        summary = ''
        if 'breaches' in mod:
            summary = f"breaches:{len(mod.get('breaches') or [])}"
        if 'found_on' in mod:
            summary = f"found_on:{len(mod.get('found_on') or [])}"
        if 'records' in mod:
            summary = 'dns_records'
        mnode = make_node(label + '\\n' + summary, 'module')
        # connect to relevant target
        if mod.get('email') and 'email' in tnodes:
            e = ET.SubElement(graph, 'edge', source=tnodes['email'], target=mnode)
        if mod.get('domain') and 'domain' in tnodes:
            e = ET.SubElement(graph, 'edge', source=tnodes['domain'], target=mnode)
        if mod.get('username') and 'username' in tnodes:
            e = ET.SubElement(graph, 'edge', source=tnodes['username'], target=mnode)
    # return XML bytes
    return ET.tostring(graphml, encoding='utf-8', xml_declaration=True)

# ------------------------- Flask UI ---------------------------------

app = Flask(__name__)

HTML_INDEX = '''
<!doctype html>
<title>OSINT Tool - UI</title>
<h1>OSINT Tool - Generador de reportes</h1>
<form method=post action="/run">
  Email: <input name="email"> <br>
  Domain: <input name="domain"> <br>
  Username: <input name="username"> <br>
  <button type=submit>Run</button>
</form>
<hr>
<p>También puedes POSTear JSON a /api/run con keys: email, domain, username y recibir JSON de vuelta.</p>
'''

@app.route('/')
def index():
    return render_template_string(HTML_INDEX)

@app.route('/run', methods=['POST'])
def run_form():
    email = request.form.get('email')
    domain = request.form.get('domain')
    username = request.form.get('username')
    targets = {}
    if email:
        targets['email'] = email
    if domain:
        targets['domain'] = domain
    if username:
        targets['username'] = username
    config = { 'hibp_api_key': None }
    report = build_report(targets, config)
    # store in session-free memory: return JSON and link to download
    graphml = report_to_graphml(report)
    buf = BytesIO(graphml)
    # return page with JSON and download link (in-memory)
    return jsonify(report)

@app.route('/api/run', methods=['POST'])
def api_run():
    data = request.get_json() or {}
    targets = {}
    for k in ('email','domain','username'):
        if k in data:
            targets[k] = data[k]
    config = data.get('config', {})
    report = build_report(targets, config)
    return jsonify(report)

@app.route('/export/graphml', methods=['POST'])
def export_graphml():
    report = request.get_json() or {}
    gm = report_to_graphml(report)
    return send_file(BytesIO(gm), mimetype='application/xml', as_attachment=True, download_name='report.graphml')

if __name__ == '__main__':
    app.run(port=5000)
