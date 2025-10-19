#!/usr/bin/env python3
"""
Visualizador universal de JSON
---------------------------------------------------------
Lee un archivo JSON con "entities" y "links" y genera:
  - Un grafo visual con Graphviz (SVG)
  - Un CSV con entidades y otro con enlaces
  - Un GraphML estándar y otro compatible con Maltego

Uso:
  python visualizador_json.py --json ejemplo_orquestador.json
"""

import json, argparse, csv
import os
import networkx as nx
from graphviz import Digraph
from xml.etree.ElementTree import Element, SubElement, ElementTree

# --- Carga y normalización ---
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_entities(data):
    ents = []
    for e in data.get("entities", []):
        ents.append({
            "id": e.get("id", ""),
            "type": e.get("type", "Unknown"),
            "value": e.get("value", ""),
            "properties": e.get("properties", {})
        })
    return ents

def normalize_links(data):
    links = []
    for l in data.get("links", []):
        links.append({
            "source": l.get("source"),
            "target": l.get("target"),
            "type": l.get("type", "related"),
            "properties": l.get("properties", {})
        })
    return links

# --- Grafo visual SVG ---
def generate_graph(entities, links, out_svg):
    dot = Digraph(comment="Visualización de relaciones", format="svg")
    for e in entities:
        dot.node(e["id"], f'{e["value"]}\n({e["type"]})', shape="ellipse")
    for l in links:
        if l["source"] and l["target"]:
            dot.edge(l["source"], l["target"], label=l["type"])
    dot.render(out_svg, cleanup=True)
    print(f"[+] Grafo generado: {out_svg}.svg")

# --- Exportación CSV ---
def export_csv(entities, links):
    """
    Exporta:
      - entities.csv con columnas: id,type,value,<todas las propiedades detectadas>
      - links.csv con columnas: source,target,type,<todas las propiedades detectadas en links>
    """
    # detectar keys dinámicas en entidades
    ent_prop_keys = set()
    for e in entities:
        props = e.get("properties") or {}
        for k in props.keys():
            ent_prop_keys.add(k)
    ent_prop_keys = sorted(ent_prop_keys)

    # escribir entities.csv
    ent_headers = ["id", "type", "value"] + ent_prop_keys
    with open("entities.csv", "w", newline='', encoding="utf-8") as fe:
        w = csv.writer(fe)
        w.writerow(ent_headers)
        for e in entities:
            props = e.get("properties") or {}
            row = [e.get("id",""), e.get("type",""), e.get("value","")]
            for k in ent_prop_keys:
                v = props.get(k, "")
                # convertir listas/dicts a JSON string
                if isinstance(v, (list, dict)):
                    v = json.dumps(v, ensure_ascii=False)
                row.append(v)
            w.writerow(row)

    # detectar keys dinámicas en links
    link_prop_keys = set()
    for l in links:
        props = l.get("properties") or {}
        for k in props.keys():
            link_prop_keys.add(k)
    link_prop_keys = sorted(link_prop_keys)

    link_headers = ["source", "target", "type"] + link_prop_keys
    with open("links.csv", "w", newline='', encoding="utf-8") as fl:
        w = csv.writer(fl)
        w.writerow(link_headers)
        for l in links:
            props = l.get("properties") or {}
            row = [l.get("source",""), l.get("target",""), l.get("type","")]
            for k in link_prop_keys:
                v = props.get(k, "")
                if isinstance(v, (list, dict)):
                    v = json.dumps(v, ensure_ascii=False)
                row.append(v)
            w.writerow(row)

    print("[+] Archivos CSV generados: entities.csv y links.csv (con propiedades dinámicas)")

# --- Exportación GraphML estándar ---
def export_graphml(entities, links, filename="graph.graphml"):
    G = nx.DiGraph()
    for e in entities:
        G.add_node(e["id"], label=e["value"], type=e["type"])
    for l in links:
        if l["source"] and l["target"]:
            G.add_edge(l["source"], l["target"], relation=l["type"])
    nx.write_graphml(G, filename)
    print(f"[+] Archivo GraphML estándar generado: {filename}")

# --- Exportación GraphML compatible con Maltego ---
def export_graphml_maltego(entities, links, filename="graph_maltego.graphml"):
    """
    Genera un archivo GraphML compatible con Maltego.
    Evita errores al importar o cierres inesperados.
    """
    graphml = Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    graph = SubElement(graphml, "graph", edgedefault="directed")

    # Nodos
    for e in entities:
        if not e.get("id"):  # Evitar IDs vacíos
            continue
        node = SubElement(graph, "node", id=str(e["id"]))
        data_label = SubElement(node, "data", key="Label")
        data_label.text = f'{e["value"]} ({e["type"]})'

    # Enlaces
    for i, l in enumerate(links):
        if not l.get("source") or not l.get("target"):
            continue
        edge = SubElement(graph, "edge", id=f"e{i}", source=str(l["source"]), target=str(l["target"]))
        data_rel = SubElement(edge, "data", key="Label")
        data_rel.text = l.get("type", "related")

    ElementTree(graphml).write(filename, encoding="utf-8", xml_declaration=True)
    print(f"[+] Archivo GraphML (Maltego compatible) generado: {filename}")

# --- Ejecución principal ---
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", required=True, help="Ruta al archivo JSON del orquestador")
    args = p.parse_args()

    data = load_json(args.json)
    entities = normalize_entities(data)
    links = normalize_links(data)

    if not entities or not links:
        print("[-] El JSON no contiene entidades o enlaces reconocibles.")
        return

    # Salidas automáticas con el nombre del JSON
    base = os.path.splitext(os.path.basename(args.json))[0]
    svg_out = f"{base}_graph"

    generate_graph(entities, links, svg_out)
    export_csv(entities, links)
    export_graphml(entities, links, f"{base}.graphml")
    export_graphml_maltego(entities, links, f"{base}_maltego.graphml")

    print("\n[✔] Listo. Archivos generados:")
    print(f"    - {svg_out}.svg  (visualización)")
    print(f"    - entities.csv, links.csv  (datos tabulares)")
    print(f"    - {base}.graphml  (GraphML estándar)")
    print(f"    - {base}_maltego.graphml  (GraphML para Maltego)\n")

if __name__ == "__main__":
    main()