Creamos el siguiente script:

```bash
#!/usr/bin/env bash
set -euo pipefail

# nmap_shodan_report_full.sh
# Uso: ./nmap_shodan_report_full.sh <target> <output_basename>
# Genera:
#   - last_nmap.xml   (XML nmap para depuración, en el cwd)
#   - <output_basename>.csv
#   - <output_basename>.html
#
# Requisitos: nmap, curl, jq, xmlstarlet
# PONER AQUÍ TU SHODAN API KEY entre las comillas, esta recortada por seguridad:
SHODAN_API_KEY="e090ZQuyEf2CqpBYybz5L1U----------" 

if [[ -z "$SHODAN_API_KEY" ]]; then
  echo "ERROR: Añade tu SHODAN_API_KEY en la variable SHODAN_API_KEY dentro del script."
  exit 2
fi

if [[ $# -lt 2 ]]; then
  echo "Uso: $0 <target> <output_basename>"
  exit 1
fi

TARGET="$1"
OUTBASE="$2"
OUTCSV="${OUTBASE}.csv"
OUTHTML="${OUTBASE}.html"
NMAP_XML="./last_nmap.xml"
TMPDIR="$(mktemp -d)"

# check dependencies
for cmd in nmap curl jq xmlstarlet; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "ERROR: '$cmd' no encontrado. Instálalo e inténtalo de nuevo."; exit 1; }
done

echo "[*] Target: $TARGET"
echo "[*] CSV: $OUTCSV"
echo "[*] HTML: $OUTHTML"
echo "[*] Nmap XML (kept for debug): $NMAP_XML"
echo "[*] Temp dir: $TMPDIR"

# Run nmap and save XML (no --open so we capture all states)
# Use sudo for better coverage if available (necesario para algunas detecciones).
if command -v sudo >/dev/null 2>&1; then
  echo "[*] Ejecutando sudo nmap -sV -p- -T4 -oX $NMAP_XML $TARGET"
  sudo nmap -sV -p- -T4 -oX "$NMAP_XML" "$TARGET"
else
  echo "[*] Ejecutando nmap -sV -p- -T4 -oX $NMAP_XML $TARGET"
  nmap -sV -p- -T4 -oX "$NMAP_XML" "$TARGET"
fi

echo "[*] Parseando XML y construyendo CSV + HTML..."

# Helpers
esc_csv() { local s="$1"; s="${s//\"/\"\"}"; printf "\"%s\"" "$s"; }
html_escape() {
  local s="$1"
  s="${s//&/&amp;}"
  s="${s//</&lt;}"
  s="${s//>/&gt;}"
  s="${s//\"/&quot;}"
  s="${s//\'/&#39;}"
  printf "%s" "$s"
}

# Create CSV header
echo "IP,Port,Protocol,State,Service,Product,Version,SHODAN_CVEs" > "$OUTCSV"

# Prepare arrays for summary
declare -A UNIQUE_CVES
HOST_COUNT=0
TOTAL_PORTS=0

# Build parsed lines: host + each port (if any)
# Each line: IP,PORT,PROTO,STATE,SERVICE,PRODUCT,VERSION
xmlstarlet sel -t \
  -m "//host" \
    -v "address[1]/@addr" -o "||" \
    -m "ports/port" -v "@portid" -o "||" -v "@protocol" -o "||" -v "state/@state" -o "||" -v "service/@name" -o "||" -v "service/@product" -o "||" -v "service/@version" -n \
  "$NMAP_XML" > "$TMPDIR/parsed_ports.txt" || true

# The xmlstarlet above prints, for each host, repeated lines where the first line is IP||port||proto||...
# We will process grouped by IP. If a host had no ports, it won't generate lines—detect hosts separately.
hosts_list=$(xmlstarlet sel -t -m "//host" -v "address[1]/@addr" -n "$NMAP_XML" || true)

# Build a map of host -> whether we produced any line
declare -A HOST_HAS_PORTS

# Read parsed lines
while IFS= read -r line; do
  # skip empty lines
  [[ -z "$line" ]] && continue

  # Format: IP||PORT||PROTO||STATE||SERVICE||PRODUCT||VERSION
  IFS='||' read -r IP PORT PROTO STATE SVC PRODUCT VERSION <<< "$line"
  HOST_HAS_PORTS["$IP"]=1

  # Query Shodan for host info (best-effort)
  SHODAN_URL="https://api.shodan.io/shodan/host/${IP}?key=${SHODAN_API_KEY}"
  SHODAN_JSON="$(curl -sS --fail "$SHODAN_URL" || echo '{}')"

  # Extract vulns for given port, result is object of keys like "CVE-...."
  SHODAN_VULNS_OBJ=$(echo "$SHODAN_JSON" | jq -r --arg port "$PORT" '
    if (.data? | type == "array") then
      (.data[] | select(.port == ($port|tonumber)) | (.vulns // {}))
    else
      {}
    end
  ' 2>/dev/null || echo "{}")

  # Convert to list of CVE keys
  CVE_LIST=""
  if [[ -n "$SHODAN_VULNS_OBJ" ]] && [[ "$SHODAN_VULNS_OBJ" != "{}" ]]; then
    # keys may be returned; capture them safely
    CVE_LIST=$(echo "$SHODAN_VULNS_OBJ" | jq -r 'keys[]' 2>/dev/null || echo "")
  fi

  # Update summary counters
  (( TOTAL_PORTS++ ))
  if [[ -n "$CVE_LIST" ]]; then
    while IFS= read -r cve; do
      [[ -z "$cve" ]] && continue
      UNIQUE_CVES["$cve"]=1
    done <<< "$CVE_LIST"
  fi

  # CSV: semi-colon separated CVEs
  if [[ -z "$CVE_LIST" ]]; then
    CVE_FIELD=""
  else
    CVE_FIELD=$(echo "$CVE_LIST" | paste -sd ";" -)
  fi

  echo "$(esc_csv "$IP"),$(esc_csv "$PORT"),$(esc_csv "$PROTO"),$(esc_csv "$STATE"),$(esc_csv "$SVC"),$(esc_csv "$PRODUCT"),$(esc_csv "$VERSION"),$(esc_csv "$CVE_FIELD")" >> "$OUTCSV"

  # Save HTML row to a tmp file
  rowfile="$TMPDIR/rows.html"
  ip_e=$(html_escape "$IP")
  port_e=$(html_escape "$PORT")
  proto_e=$(html_escape "$PROTO")
  state_e=$(html_escape "$STATE")
  svc_e=$(html_escape "$SVC")
  prod_e=$(html_escape "$PRODUCT")
  ver_e=$(html_escape "$VERSION")

  # build CVE html
  if [[ -z "$CVE_LIST" ]]; then
    cve_cell='<span class="no-cve">(ninguna)</span>'
  else
    cve_cell='<div class="cvlist">'
    while IFS= read -r cve; do
      [[ -z "$cve" ]] && continue
      UNIQUE_CVES["$cve"]=1
      nvd_url="https://nvd.nist.gov/vuln/detail/${cve}"
      cve_cell+="<a class=\"cve\" href=\"${nvd_url}\" target=\"_blank\" rel=\"noopener noreferrer\">${cve}</a> "
    done <<< "$CVE_LIST"
    cve_cell+="</div>"
  fi

  cat >> "$rowfile" <<HTMLROW
<tr>
  <td class="mono">${ip_e}</td>
  <td>${port_e}</td>
  <td>${proto_e}</td>
  <td>${state_e}</td>
  <td>${svc_e}</td>
  <td>${prod_e}</td>
  <td>${ver_e}</td>
  <td>${cve_cell}</td>
</tr>
HTMLROW

  echo "[+] $IP:$PORT state=$STATE svc=$SVC product=$PRODUCT version=$VERSION -> CVEs: ${CVE_FIELD:-(none)}"

done < "$TMPDIR/parsed_ports.txt"

# For hosts with no ports listed, add a CSV row and an HTML row noting that
for ip in $hosts_list; do
  ((HOST_COUNT++))
  if [[ -z "${HOST_HAS_PORTS[$ip]:-}" ]]; then
    # no ports listed for this host
    echo "$(esc_csv "$ip"),$(esc_csv ""),$(esc_csv ""),$(esc_csv ""),$(esc_csv ""),$(esc_csv ""),$(esc_csv ""),$(esc_csv "(no ports listed)")" >> "$OUTCSV"
    rowfile="$TMPDIR/rows.html"
    ip_e=$(html_escape "$ip")
    cat >> "$rowfile" <<HTMLROW
<tr>
  <td class="mono">${ip_e}</td>
  <td colspan="6"><em>(no se listaron puertos en el XML para este host)</em></td>
  <td class="no-cve">(ninguna)</td>
</tr>
HTMLROW
    echo "[*] $ip: no se listaron puertos en el XML (se añadió fila de nota)."
  fi
done

# Build HTML with summary
UNIQUE_CVE_COUNT=${#UNIQUE_CVES[@]}

cat > "$OUTHTML" <<HTML_HEAD
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte Nmap + Shodan - ${OUTBASE}</title>
<style>
  body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial; margin: 24px; background:#f7f8fb; color:#111; }
  h1 { font-size: 1.6rem; margin-bottom: 0.2rem; }
  .meta { color:#555; margin-bottom: 1rem; }
  table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
  th, td { padding: 10px 12px; border-bottom: 1px solid #eee; text-align: left; font-size: 0.95rem; vertical-align: top; }
  th { background:#fafafa; position: sticky; top:0; z-index:1; }
  tr:hover td { background: #fbfdff; }
  .cve { font-weight: 600; color: #a33; margin-right:6px; text-decoration:none; }
  .no-cve { color:#888; font-style: italic; }
  .small { font-size:0.85rem; color:#666; }
  .badge { display:inline-block; padding:4px 8px; border-radius:999px; background:#eef6ff; color:#036; font-weight:600; font-size:0.8rem; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace; }
  .cvlist a { margin-right:6px; text-decoration:none; color:#a33; }
  .cvlist a:hover { text-decoration:underline; }
  tbody { max-height: 60vh; overflow: auto; display:block; }
  table thead, table tbody tr { display:table; width:100%; table-layout:fixed; }
  table thead { width: calc(100% - 1em); }
</style>
</head>
<body>
HTML_HEAD

cat >> "$OUTHTML" <<HTML_META
<h1>Reporte Nmap + Shodan</h1>
<div class="meta">
  <span class="badge">Target: $(html_escape "$TARGET")</span>
  &nbsp; &middot; &nbsp;
  Generado: <span class="small">$(date -u +"%Y-%m-%d %H:%M UTC")</span>
  &nbsp; &middot; &nbsp;
  Hosts detectados: <span class="small">${HOST_COUNT}</span>
  &nbsp; &middot; &nbsp;
  Puertos listados: <span class="small">${TOTAL_PORTS}</span>
  &nbsp; &middot; &nbsp;
  CVEs únicos (Shodan): <span class="small">${UNIQUE_CVE_COUNT}</span>
</div>

<table>
<thead>
<tr>
  <th>IP</th>
  <th>Puerto</th>
  <th>Proto</th>
  <th>Estado</th>
  <th>Servicio</th>
  <th>Producto</th>
  <th>Versión</th>
  <th>CVEs (Shodan)</th>
</tr>
</thead>
<tbody>
HTML_META

# Append rows temp file if exists
if [[ -f "$TMPDIR/rows.html" ]]; then
  cat "$TMPDIR/rows.html" >> "$OUTHTML"
else
  # No rows - show message
  cat >> "$OUTHTML" <<HTML_EMPTY
<tr>
  <td colspan="8"><em>No se encontraron puertos en el XML o no hubo hosts; revisa last_nmap.xml para más detalle.</em></td>
</tr>
HTML_EMPTY
fi

cat >> "$OUTHTML" <<HTML_FOOT
</tbody>
</table>

<p class="small">Nota: Los CVEs provienen de la información pública que Shodan indexa; pueden faltar CVEs o no corresponder exactamente si la versión no fue detectada por nmap.</p>

</body>
</html>
HTML_FOOT

# Cleanup tmpdir but keep XML
rm -rf "$TMPDIR"

echo "[*] Hecho."
echo "[*] CSV: $OUTCSV"
echo "[*] HTML: $OUTHTML"
echo "[*] Conservado: $NMAP_XML (útil para depuración manual)"

```

Damos permisos al script.

```bash
chmod +x nmap_shodan_report_full.sh
```

Ejecutamos el script

```bash
./nmap_shodan_report_full.sh 10.10.11.92 resultadofinalisimo
```

Vemos que se han creado dos archivos, el .html es una tabla en el que veremos la información mas estructurada

```bash
┌──(ivan㉿ivan)-[~]
└─$ ls                                                                                     
Descargas   Imágenes                    Plantillas                screenshots
Documentos  last_nmap.xml               Público                   Vídeos
Escritorio  Música                      resultadofinalisimo.csv   Wallpapers
hackerpwm   nmap_shodan_report_full.sh  resultadofinalisimo.html
```

