#!/usr/bin/env python3
"""
Interfaz web básica para el visualizador JSON (OSINT)
-----------------------------------------------------
Permite subir un archivo JSON y visualizar su grafo con todas las propiedades.
"""

from flask import Flask, render_template_string, request
import json
from graphviz import Digraph
import networkx as nx

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Visualizador OSINT</title>
  <style>
    body { font-family: Arial; margin: 2em; }
    h1 { color: #333; }
    .graph { margin-top: 2em; }
    svg { width: 100%; height: auto; border: 1px solid #ccc; }
  </style>
</head>
<body>
  <h1> Visualizador de relaciones OSINT</h1>
  <form method="post" enctype="multipart/form-data">
    <label>Selecciona un archivo JSON:</label>
    <input type="file" name="jsonfile" accept=".json">
    <button type="submit">Visualizar</button>
  </form>

  {% if svg %}
    <div class="graph">
      <h2>Resultado:</h2>
      {{ svg|safe }}
    </div>
  {% endif %}
</body>
</html>
"""

def generate_graph_from_json(data):
    dot = Digraph(format='svg')
    G = nx.DiGraph()

    for e in data.get("entities", []):
        props = e.get("properties") or {}
        # Construir label con <BR/> para todas las propiedades
        props_text = "<BR/>".join(f"{k}: {v}" for k, v in props.items())
        label_html = f'<B>{e.get("value","")}</B><BR/><I>{e.get("type","")}</I>'
        if props_text:
            label_html += f"<BR/>{props_text}"

        # Crear nodo como HTML
        dot.node(e["id"], label=f'<{label_html}>', shape="box", style="rounded", fontsize="12")
        G.add_node(e["id"], label=e.get("value",""), type=e.get("type",""))

    for l in data.get("links", []):
        if l.get("source") and l.get("target"):
            dot.edge(l["source"], l["target"], label=l.get("type","related"))
            G.add_edge(l["source"], l["target"], relation=l.get("type","related"))

    svg = dot.pipe().decode("utf-8")
    nx.write_graphml(G, "web_graph.graphml")
    return svg


@app.route("/", methods=["GET", "POST"])
def index():
    svg = None
    if request.method == "POST" and "jsonfile" in request.files:
        file = request.files["jsonfile"]
        try:
            data = json.load(file)
            svg = generate_graph_from_json(data)
        except Exception as e:
            svg = f"<p style='color:red;'>Error al procesar el JSON: {e}</p>"
    return render_template_string(TEMPLATE, svg=svg)

if __name__ == "__main__":
    app.run(debug=True)