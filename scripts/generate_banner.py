"""
Genera el panel animado del perfil de GitHub de Joanna Carrión.

  pip install pillow
  python scripts/generate_banner.py

Crea assets/banner-dark.svg y assets/banner-light.svg:
  - Izquierda: una terminal que "escribe" tus datos línea por línea.
  - Derecha: tu foto convertida en un retrato de píxeles azules que se arma
    solo, con un fondo de píxeles que cambian de color, y tres mini datos.

Para cambiar textos edita LINES o TILES; para cambiar la foto reemplaza
assets/foto.png (mejor con fondo blanco). Luego vuelve a ejecutar el script
y cambia ?v=N en el README para que GitHub no muestre la versión vieja.
"""
import os
import random
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))

# ---------------------------------------------------------------- contenido
USER = "joanna@data"
COMMAND = "./profile.sh --live"

LINES = [  # (clave, valor)
    ("nombre", "Joanna Carrión"),
    ("formación", "Ingeniería Electrónica"),
    ("enfoque", "Data Analytics & Business Intelligence"),
    ("stack", "Python · SQL · Power BI · MATLAB"),
    ("ml / ia", "TensorFlow · PyTorch · Redes Neuronales"),
    ("intereses", "Visión por Computadora · Señales · Embebidos"),
    ("aprendiendo", "IA · Power BI · HTML / CSS"),
    ("estado", "abierta a colaborar"),  # la última lleva un punto verde que late
]

TILES = [  # (número, etiqueta)
    ("3", "proyectos"),
    ("10+", "tecnologías"),
    ("4", "intereses"),
]

PHOTO = os.path.join(ASSETS, "foto.png")
CROP = (55, 0, 345, 290)   # recorte cuadrado (izq, arriba, der, abajo) sobre la foto de 400x400
GRID = 48                  # retrato de 48 x 48 píxeles
PITCH, CELL = 6, 5         # separación y tamaño de cada píxel

# ---------------------------------------------------------------- temas
THEMES = {
    "dark": dict(
        bg="#0d1117", panel="#161b22", bar="#1c2230", border="#30363d",
        text="#e6edf3", muted="#8b949e", key="#79c0ff", accent="#3fa9f5",
        green="#3fb950", tile="#0d1117",
        back=["#161c26", "#132235", "#152c45", "#183757"],      # fondo que titila
        ramp=["#0f2a47", "#1d5f99", "#5fb2ec", "#e8f6ff"],      # oscuro -> claro
    ),
    "light": dict(
        bg="#ffffff", panel="#f6f8fa", bar="#eaeef2", border="#d0d7de",
        text="#24292f", muted="#57606a", key="#0550ae", accent="#007acc",
        green="#1a7f37", tile="#ffffff",
        back=["#eef2f6", "#e5edf5", "#dbe7f3", "#d0e1f1"],
        ramp=["#0a2540", "#1b5f9c", "#5ea6dd", "#cfe6f7"],
    ),
}

W, H = 1200, 420
FONT = "'JetBrains Mono','Fira Code',Consolas,Menlo,'DejaVu Sans Mono',monospace"
CHAR = 9.0  # ancho aproximado de un carácter a 15px
LEVELS = 10


def lerp_hex(stops, x):
    """Interpola un color entre varias paradas hex, x en [0, 1]."""
    x = min(max(x, 0.0), 1.0) * (len(stops) - 1)
    i = min(int(x), len(stops) - 2)
    f = x - i
    a = [int(stops[i][k:k + 2], 16) for k in (1, 3, 5)]
    b = [int(stops[i + 1][k:k + 2], 16) for k in (1, 3, 5)]
    return "#" + "".join(f"{round(a[j] + (b[j] - a[j]) * f):02x}" for j in range(3))


def portrait_levels():
    """Devuelve una matriz GRID x GRID con None (fondo) o un nivel 0..LEVELS-1."""
    im = Image.open(PHOTO).convert("RGB").crop(CROP)
    big = im.resize((GRID * 8, GRID * 8), Image.LANCZOS)
    # máscara de fondo: píxeles casi blancos y poco saturados
    px = big.load()
    mask = Image.new("L", big.size)
    mp = mask.load()
    for y in range(big.size[1]):
        for x in range(big.size[0]):
            r, g, b = px[x, y]
            mp[x, y] = 255 if min(r, g, b) > 222 and max(r, g, b) - min(r, g, b) < 28 else 0
    gray = ImageOps.grayscale(big).load()
    cs = big.size[0] // GRID
    cells = {}
    for gy_ in range(GRID):
        for gx_ in range(GRID):
            vals, bgc = [], 0
            for y in range(gy_ * cs, (gy_ + 1) * cs):
                for x in range(gx_ * cs, (gx_ + 1) * cs):
                    if mp[x, y]:
                        bgc += 1
                    else:
                        vals.append(gray[x, y])
            # fondo si más de un tercio de la celda es blanco
            if bgc > cs * cs * 0.33 or not vals:
                cells[(gx_, gy_)] = None
            else:
                cells[(gx_, gy_)] = sum(vals) / len(vals)

    # ecualización por rangos: reparte los tonos para que se lean ojos, boca y cabello
    fg = sorted(v for v in cells.values() if v is not None)
    n = len(fg)
    import bisect
    out = []
    for y in range(GRID):
        row = []
        for x in range(GRID):
            v = cells[(x, y)]
            if v is None:
                row.append(None)
            else:
                rank = bisect.bisect_left(fg, v) / max(1, n - 1)
                row.append(min(LEVELS - 1, int(rank * LEVELS)))
        out.append(row)
    return out


def build(theme_name: str, levels) -> str:
    t = THEMES[theme_name]
    rnd = random.Random(20)  # semilla fija: mismo patrón en cada ejecución
    out = []
    a = out.append
    bk = t["back"]

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="Joanna Carrión - profile.sh --live">')
    a("<title>Joanna Carrión · Data Analytics, BI e Inteligencia Artificial</title>")
    a("<style>")
    a(f"text{{font-family:{FONT};}}")
    a(f"@keyframes b0{{0%,85%,100%{{fill:{bk[0]}}}92%{{fill:{bk[2]}}}}}")
    a(f"@keyframes b1{{0%,100%{{fill:{bk[0]}}}50%{{fill:{bk[1]}}}}}")
    a(f"@keyframes b2{{0%,100%{{fill:{bk[1]}}}50%{{fill:{bk[2]}}}}}")
    a(f"@keyframes b3{{0%,100%{{fill:{bk[0]}}}45%{{fill:{bk[3]}}}60%{{fill:{bk[2]}}}}}")
    a("@keyframes rv{0%{opacity:0;transform:scale(.2)}100%{opacity:1;transform:scale(1)}}")
    a("@keyframes tw{0%,100%{fill-opacity:1}50%{fill-opacity:.55}}")
    a("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
    a("@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}")
    a(".cur{animation:blink 1s steps(1) infinite}")
    a(".pulse{animation:pulse 1.6s ease-in-out infinite}")
    a(".p{transform-box:fill-box;transform-origin:center}")
    a("</style>")

    a('<defs>')
    a(f'<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{t["accent"]}" stop-opacity=".28"/>'
      f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient>')

    # ------------------------------------------------ terminal: recortes para el efecto de tipeo
    tx, ty, tw, th = 20, 20, 712, 380
    x0, y0, lh = 48, 92, 29
    key_w = 150
    rows = [("cmd", None)] + [("kv", kv) for kv in LINES] + [("prompt", None)]
    begin = 0.5
    timing = []
    for kind, kv in rows:
        if kind == "cmd":
            n, dur = len(USER) + 4 + len(COMMAND), 0.8
        elif kind == "kv":
            n, dur = 2 + key_w / CHAR + len(kv[1]) + 2, max(0.25, len(kv[1]) * 0.016)
        else:
            n, dur = len(USER) + 6, 0.3
        timing.append((begin, dur, n * CHAR + 30))
        begin += dur + (0.35 if kind == "cmd" else 0.08)

    for i, (b, d, width) in enumerate(timing):
        y = y0 + i * lh
        a(f'<clipPath id="l{i}"><rect x="{x0 - 4}" y="{y - 18}" height="{lh}" width="0">'
          f'<animate attributeName="width" from="0" to="{width:.0f}" begin="{b:.2f}s" '
          f'dur="{d:.2f}s" fill="freeze"/></rect></clipPath>')

    px, py, pw, ph = 752, 20, 428, 380
    gx, gy = px + 14, py + 46
    gsz = GRID * PITCH - (PITCH - CELL)
    a(f'<clipPath id="gridclip"><rect x="{gx}" y="{gy}" width="{gsz}" height="{gsz}" rx="6"/></clipPath>')
    a('</defs>')

    # ------------------------------------------------ fondo
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["bg"]}" stroke="{t["border"]}"/>')

    # ------------------------------------------------ ventana de terminal
    a(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    a(f'<path d="M{tx} {ty + 12} a12 12 0 0 1 12 -12 h{tw - 24} a12 12 0 0 1 12 12 v24 h-{tw} z" fill="{t["bar"]}"/>')
    a(f'<line x1="{tx}" y1="{ty + 36}" x2="{tx + tw}" y2="{ty + 36}" stroke="{t["border"]}"/>')
    for k, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        a(f'<circle cx="{tx + 22 + k * 20}" cy="{ty + 18}" r="6" fill="{col}"/>')
    a(f'<text x="{tx + tw / 2}" y="{ty + 23}" font-size="13" fill="{t["muted"]}" text-anchor="middle">'
      f'{USER}: ~ — profile.sh --live</text>')

    for i, (kind, kv) in enumerate(rows):
        y = y0 + i * lh
        g = f'<g clip-path="url(#l{i})">'
        if kind == "cmd":
            g += (f'<text x="{x0}" y="{y}" font-size="15"><tspan fill="{t["accent"]}" font-weight="700">{USER}</tspan>'
                  f'<tspan fill="{t["muted"]}">:~$ </tspan><tspan fill="{t["text"]}">{escape(COMMAND)}</tspan></text>')
        elif kind == "kv":
            k, v = kv
            vx = x0 + 18 + key_w
            g += f'<text x="{x0}" y="{y}" font-size="15" fill="{t["accent"]}">›</text>'
            g += f'<text x="{x0 + 18}" y="{y}" font-size="15" fill="{t["key"]}">{escape(k)}</text>'
            if i == len(rows) - 2:  # estado: punto verde que late
                g += f'<circle class="pulse" cx="{vx + 5}" cy="{y - 5}" r="5" fill="{t["green"]}"/>'
                g += f'<text x="{vx + 18}" y="{y}" font-size="15" fill="{t["green"]}" font-weight="700">{escape(v)}</text>'
            else:
                g += f'<text x="{vx}" y="{y}" font-size="15" fill="{t["text"]}">{escape(v)}</text>'
        else:
            g += (f'<text x="{x0}" y="{y}" font-size="15"><tspan fill="{t["accent"]}" font-weight="700">{USER}</tspan>'
                  f'<tspan fill="{t["muted"]}">:~$</tspan></text>')
            cx = x0 + (len(USER) + 4) * CHAR
            g += f'<rect class="cur" x="{cx:.0f}" y="{y - 14}" width="9" height="18" fill="{t["accent"]}"/>'
        g += "</g>"
        a(g)

    # ------------------------------------------------ panel del retrato
    a(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    a(f'<circle class="pulse" cx="{px + 22}" cy="{py + 23}" r="5" fill="{t["green"]}"/>')
    a(f'<text x="{px + 36}" y="{py + 28}" font-size="13" fill="{t["muted"]}">live · joanna.px</text>')
    a(f'<text x="{px + pw - 18}" y="{py + 28}" font-size="13" fill="{t["accent"]}" text-anchor="end" '
      f'font-weight="700">{GRID}×{GRID}</text>')

    ramp = [lerp_hex(t["ramp"], i / (LEVELS - 1)) for i in range(LEVELS)]
    a('<g>')
    for r in range(GRID):
        for c in range(GRID):
            x, y = gx + c * PITCH, gy + r * PITCH
            lv = levels[r][c]
            if lv is None:
                k = rnd.choices(["b0", "b1", "b2", "b3"], weights=[40, 30, 18, 12])[0]
                dur = rnd.choice([2.6, 3.4, 4.2, 5.0, 6.2])
                a(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="1.2" fill="{bk[0]}" '
                  f'style="animation:{k} {dur}s ease-in-out -{rnd.uniform(0, 5):.2f}s infinite"/>')
            else:
                # se arma en diagonal, de arriba-izquierda a abajo-derecha, con un poco de azar
                d = 0.4 + (r + c) * 0.03 + rnd.uniform(0, 0.25)
                anim = f"rv .45s ease-out {d:.2f}s both"
                if rnd.random() < 0.18:
                    anim += f",tw {rnd.choice([2.2, 3.0, 3.8])}s ease-in-out {d + 1 + rnd.uniform(0, 3):.2f}s infinite"
                a(f'<rect class="p" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="1.2" '
                  f'fill="{ramp[lv]}" style="animation:{anim}"/>')
    a('</g>')

    # barrido de luz vertical sobre el retrato
    a(f'<rect clip-path="url(#gridclip)" x="{gx}" y="{gy - 50}" width="{gsz}" height="50" fill="url(#scan)">'
      f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {gsz + 50}" '
      f'dur="5s" begin="3s" repeatCount="indefinite"/></rect>')

    # leyenda tipo "menos ▢▢▢ más", como el mapa de contribuciones
    ly = gy + gsz + 22
    a(f'<text x="{gx}" y="{ly}" font-size="11" fill="{t["muted"]}">menos</text>')
    for i in range(5):
        a(f'<rect x="{gx + 44 + i * 13}" y="{ly - 9}" width="10" height="10" rx="2" '
          f'fill="{ramp[round(i * (LEVELS - 1) / 4)]}"/>')
    a(f'<text x="{gx + 44 + 5 * 13 + 4}" y="{ly}" font-size="11" fill="{t["muted"]}">más</text>')
    a(f'<text x="{gx + gsz}" y="{ly}" font-size="11" fill="{t["muted"]}" text-anchor="end">foto → datos</text>')

    # mini datos apilados a la derecha
    tx2 = gx + gsz + 12
    tw2 = px + pw - 14 - tx2
    tile_h = (gsz - 2 * 10) / 3
    for i, (num, label) in enumerate(TILES):
        y = gy + i * (tile_h + 10)
        a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{0.8 + i * 0.3:.1f}s" '
          f'dur="0.6s" fill="freeze"/>')
        a(f'<rect x="{tx2}" y="{y:.0f}" width="{tw2}" height="{tile_h:.0f}" rx="8" fill="{t["tile"]}" stroke="{t["border"]}"/>')
        a(f'<text x="{tx2 + 12}" y="{y + tile_h / 2 + 2:.0f}" font-size="26" font-weight="700" fill="{t["accent"]}">{escape(num)}</text>')
        a(f'<text x="{tx2 + 12}" y="{y + tile_h / 2 + 22:.0f}" font-size="11" fill="{t["muted"]}">{escape(label)}</text>')
        a('</g>')

    a("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    lv = portrait_levels()
    os.makedirs(ASSETS, exist_ok=True)
    for name in THEMES:
        path = os.path.join(ASSETS, f"banner-{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(name, lv))
        print(f"ok  {path}  ({os.path.getsize(path) / 1024:.0f} KB)")
