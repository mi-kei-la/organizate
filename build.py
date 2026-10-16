"""Arma el juego a partir del diagrama de Excalidraw.

Uso:  python3 -I build.py scene.excalidraw.json fonts template.html que-queres-organizar.html [--standalone]

Con --standalone sale un HTML completo (doctype, charset, viewport) para servirlo
tal cual, p. ej. en GitHub Pages. Sin el flag sale el formato de Artifact de claude.ai.

- scene.excalidraw.json: escena exportada/descifrada de Excalidraw (las flechas
  tienen startBinding/endBinding, de ahí sale el grafo).
- fonts/: Excalifont completa en chunks + ranges.json (unicode-range de cada uno).
"""
import base64
import json
import os
import sys

scene_path, fonts_dir, tpl_path, out_path = sys.argv[1:5]
standalone = "--standalone" in sys.argv[5:]
E = {x["id"]: x for x in json.load(open(scene_path))["elements"] if not x.get("isDeleted")}

FILL = {"transparent": "", "#fff5f5": "pink", "#e7f5ff": "blue", "#e6fcf5": "mint", "#ebfbee": "green"}
INK = {"#1e1e1e": "ink", "#2f9e44": "green", "#1971c2": "blue", "#e03131": "red"}

# Nodos donde habla "vos" (respuestas). El resto es la voz del diagrama.
ME = """7PGLRl CwRWmK PJcsgg oHD-AK xWyjy9 1JsSkN FCN0vx tcCqA5 MgS802 3HxY2D mnu6yJ btoVNv
dsmWUH LrfFu0 28WHzs R1l6z2 pranRm Zfi2vb dfJPu- 9Mgp1W XCE1IH myNeXC m_PLE1 p0M4vD LtRlLe
poE9WL 3PQ-B2 _CZqEM vO_Fs7 s0qOvJ tM-jAj I1xP6W Y_rIpl rd9JB_ bFduao TRryZ3 x02Dh5 VdB5Tg
Xyflwn QYYieg 4x572g 0uXxKO Eh8CGe""".split()
# Flechas sin respuesta escrita en el diagrama: texto del botón.
EDGE_LABEL = {("X5vapl", "Zo7j9U"): "se puede subdividir",
              ("Zo7j9U", "00hjLD"): "priorizá cada subtarea",
              ("MNBVBJ", "CwRWmK"): "planificá cada etapa (mediano plazo)"}
# Respuestas que abren un campo de texto: etiqueta, ejemplo y cómo queda el post-it.
INPUTS = {"4x572g": {"label": "quiero", "ph": "aprender a tocar la guitarra", "fmt": "quiero {x}"},
          "Eh8CGe": {"label": "para", "ph": "marzo de 2027", "fmt": "sí se: para {x}"}}
# Preguntas con caja de notas (opcional): lo que anotás arma el resumen "tus notas".
NOTES = {"Vuf_sx": "ej.: gimnasio lunes y jueves, pagar el alquiler el 10",
         "BRyJhF": "ej.: examen el 3/12, viaje del 20 al 27",
         "snF2Gf": "ej.: renovar el pasaporte, ordenar el placard",
         "rZfQtM": "ej.: llamar a alguien, conseguir un formulario, 2 horas sin interrupciones",
         "63HTB2": "ej.: el informe está enviado y aprobado",
         "X1FDYN": "ej.: 3 tardes de 2 horas",
         "MNBVBJ": "ej.: 1) aprender acordes 2) tocar una canción entera 3) tocar con otros",
         "Zo7j9U": "ej.: buscar datos, armar un borrador, revisar"}
START = "x0t3nz"

r1 = lambda v: round(v, 1)
rects = {i: x for i, x in E.items() if x["type"] == "rectangle"}
by_prefix = lambda p: next(i for i in rects if i.startswith(p))


def inside(t, r):
    cx, cy = t["x"] + t["width"] / 2, t["y"] + t["height"] / 2
    return r["x"] <= cx <= r["x"] + r["width"] and r["y"] <= cy <= r["y"] + r["height"]


def contains(o, r):
    return o is not r and o["x"] <= r["x"] and o["y"] <= r["y"] and \
        r["x"] + r["width"] <= o["x"] + o["width"] and r["y"] + r["height"] <= o["y"] + o["height"]


# Cajitas dibujadas adentro de otra caja (p. ej. "semana" en "un color por") son decoración.
nested = {i for i, r in rects.items() if any(contains(o, r) for o in rects.values())}
boxes = {i: r for i, r in rects.items() if i not in nested}
alias, texts_of = {}, {}
for t in E.values():
    if t["type"] != "text":
        continue
    c = [r for r in boxes.values() if inside(t, r)]
    if not c:
        sys.exit(f"texto sin caja: {t['text']!r}")
    r = min(c, key=lambda r: r["width"] * r["height"])
    alias[t["id"]] = r["id"]
    texts_of.setdefault(r["id"], []).append(t)

me = {by_prefix(p) for p in ME}
edge_label = {(by_prefix(a), by_prefix(b)): l for (a, b), l in EDGE_LABEL.items()}
start = by_prefix(START)
inputs = {by_prefix(p): v for p, v in INPUTS.items()}

nodes = {}
for i, r in boxes.items():
    ts = sorted(texts_of.get(i, []), key=lambda t: (round(t["y"]), t["x"]))
    label = " ".join(" ".join(t["text"].split()) for t in ts).strip()
    nodes[i] = {"t": label, "sp": "me" if i in me else "bot", "f": FILL[r["backgroundColor"]],
                "b": [r1(r["x"]), r1(r["y"]), r1(r["width"]), r1(r["height"])], "o": []}
nodes[start]["t"] = "qué querés organizar?"
for i, v in inputs.items():
    nodes[i]["in"] = v
for p, ph in NOTES.items():
    nodes[by_prefix(p)]["nt"] = ph

arrows = []
for a in E.values():
    if a["type"] != "arrow":
        continue
    s, t = (alias.get(b["elementId"], b["elementId"]) for b in (a["startBinding"], a["endBinding"]))
    dashed = a["strokeStyle"] != "solid"
    edge = {"to": t}
    if dashed:
        edge["d"] = 1
    if (s, t) in edge_label:
        edge["l"] = edge_label[(s, t)]
    nodes[s]["o"].append(edge)
    pts = [v for p in a["points"] for v in (r1(a["x"] + p[0]), r1(a["y"] + p[1]))]
    arrows.append([s, t, int(dashed), pts])

# Orden estable de opciones: izquierda a derecha según el diagrama.
for n in nodes.values():
    n["o"].sort(key=lambda e: nodes[e["to"]]["b"][0])

for i, n in nodes.items():
    if n["sp"] == "me" and not n["o"]:
        sys.exit(f"respuesta sin salida: {n['t']!r}")

scene_rects = [[i if i in nodes else "", r1(r["x"]), r1(r["y"]), r1(r["width"]), r1(r["height"]), FILL[r["backgroundColor"]],
                INK.get(r["strokeColor"], "ink"), int(r["strokeStyle"] != "solid"), r["strokeWidth"]]
               for i, r in rects.items()]
scene_texts = [[r1(t["x"]), r1(t["y"]), r1(t["width"]), t["text"], r1(t["fontSize"]), t["textAlign"],
                INK.get(t["strokeColor"], "ink"), t.get("lineHeight", 1.25)]
               for t in E.values() if t["type"] == "text"]
scene_lines = [[v for p in l["points"] for v in (r1(l["x"] + p[0]), r1(l["y"] + p[1]))]
               for l in E.values() if l["type"] == "line"]
xs = [r[1] for r in scene_rects] + [r[1] + r[3] for r in scene_rects]
ys = [r[2] for r in scene_rects] + [r[2] + r[4] for r in scene_rects]
pad = 40
view = [r1(min(xs) - pad), r1(min(ys) - pad), r1(max(xs) - min(xs) + 2 * pad), r1(max(ys) - min(ys) + 2 * pad)]

data = {"start": start, "nodes": nodes, "view": view,
        "scene": {"r": scene_rects, "t": scene_texts, "a": arrows, "l": scene_lines}}

ranges = json.load(open(os.path.join(fonts_dir, "ranges.json")))
faces = "\n".join(
    "@font-face { font-family: Excalifont; font-display: block; unicode-range: %s; src: url(data:font/woff2;base64,%s) format(\"woff2\"); }"
    % (rng, base64.b64encode(open(os.path.join(fonts_dir, f), "rb").read()).decode()) for f, rng in ranges.items())
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = open(tpl_path).read().replace("/*FONTFACES*/", faces).replace("/*DATA*/", payload)
if standalone:
    html = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
            'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
            + html + "\n</html>\n")
open(out_path, "w").write(html)

leaves = [n["t"][:40] for n in nodes.values() if not n["o"]]
print(f"{len(nodes)} nodos, {len(arrows)} flechas, {len(leaves)} finales, {len(html)//1024} KB")
for l in leaves:
    print("  final:", l)
