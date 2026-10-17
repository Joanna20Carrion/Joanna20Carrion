"""
Íconos de píxeles para el carrusel del panel (cuadrícula de 48 x 48).

Cada función devuelve un Canvas con:
  - px:     {(fila, col): intensidad 0..1}  -> un píxel por celda
  - blocks: [(col, fila, ancho, alto, intensidad)] -> bloques grandes (mapa de commits)

Intensidad 1 = lo más destacado (claro en tema oscuro, oscuro en tema claro).
Son dibujos propios y genéricos, no logos de marcas.
"""
import math
import random

N = 48


class Canvas:
    def __init__(self):
        self.px = {}
        self.blocks = []

    def set(self, x, y, i):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < N and 0 <= y < N:
            self.px[(y, x)] = max(self.px.get((y, x), 0), i)

    def dot(self, x, y, i, t=1):
        off = (t - 1) / 2
        for dy in range(t):
            for dx in range(t):
                self.set(x + dx - off, y + dy - off, i)

    def line(self, x0, y0, x1, y1, i, t=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for k in range(n + 1):
            f = k / n
            self.dot(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, i, t)

    def poly(self, pts, i, t=1):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            self.line(x0, y0, x1, y1, i, t)

    def rect(self, x0, y0, x1, y1, i):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, i)

    def box(self, x0, y0, x1, y1, i):
        self.line(x0, y0, x1, y0, i)
        self.line(x0, y1, x1, y1, i)
        self.line(x0, y0, x0, y1, i)
        self.line(x1, y0, x1, y1, i)

    def disc(self, cx, cy, r, i):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, i)

    def ellipse(self, cx, cy, rx, ry, i, a0=0, a1=2 * math.pi):
        steps = 240
        pts = [(cx + rx * math.cos(a0 + (a1 - a0) * k / steps),
                cy + ry * math.sin(a0 + (a1 - a0) * k / steps)) for k in range(steps + 1)]
        self.poly(pts, i)


def bi_chart():
    """Gráfico de barras con línea de tendencia: dashboards / Power BI."""
    c = Canvas()
    c.line(6, 41, 43, 41, 0.55)
    c.line(6, 5, 6, 41, 0.55)
    heights = [11, 19, 15, 25, 31]
    tops = []
    for k, h in enumerate(heights):
        x0 = 10 + k * 7
        top = 40 - h
        c.rect(x0, top, x0 + 4, 40, 0.45 + k * 0.08)
        c.line(x0, top, x0 + 4, top, 1.0)
        tops.append((x0 + 2, top - 5))
    c.poly(tops, 1.0)
    for x, y in tops:
        c.dot(x, y, 1.0, 2)
    return c


def database():
    """Cilindro de base de datos: SQL."""
    c = Canvas()
    cx, rx, ry, top, bot = 24, 15, 5, 9, 38
    c.ellipse(cx, top, rx, ry, 1.0)
    for y in range(top - ry + 1, top + ry):
        for x in range(cx - rx + 1, cx + rx):
            if ((x - cx) / rx) ** 2 + ((y - top) / ry) ** 2 < 0.75:
                c.set(x, y, 0.4)
    c.line(cx - rx, top, cx - rx, bot, 1.0)
    c.line(cx + rx, top, cx + rx, bot, 1.0)
    c.ellipse(cx, bot, rx, ry, 1.0, 0, math.pi)
    for yb in (top + 10, top + 20):
        c.ellipse(cx, yb, rx, ry, 0.75, 0, math.pi)
    for y in (top + 6, top + 16, top + 26):  # lucecitas de los discos
        c.dot(cx + rx - 4, y + 2, 1.0)
        c.dot(cx + rx - 7, y + 2, 0.6)
    return c


def neural_net():
    """Red neuronal de 3 capas: IA / Machine Learning."""
    c = Canvas()
    layers = [(8, [12, 24, 36]), (24, [7, 18, 30, 41]), (40, [17, 31])]
    for (x0, ys0), (x1, ys1) in zip(layers, layers[1:]):
        for y0 in ys0:
            for y1 in ys1:
                c.line(x0, y0, x1, y1, 0.35)
    for x, ys in layers:
        for y in ys:
            c.disc(x, y, 3.3, 0.8)
            c.disc(x, y, 1.6, 1.0)
    return c


def vision():
    """Ojo con visor de cámara: visión por computadora."""
    c = Canvas()
    up, lo = [], []
    for k in range(73):
        x = 5 + k * 0.53
        h = 12 * (1 - ((x - 24) / 19) ** 2)
        up.append((x, 24 - h))
        lo.append((x, 24 + h))
    c.poly(up, 1.0, 2)
    c.poly(lo, 1.0, 2)
    c.disc(24, 24, 8, 0.6)
    c.disc(24, 24, 3.8, 0.2)
    c.dot(21, 21, 1.0, 2)
    for sx, sy in ((1, 1), (46, 1), (1, 46), (46, 46)):  # esquinas del visor
        dx = 1 if sx < 24 else -1
        dy = 1 if sy < 24 else -1
        c.line(sx, sy, sx + dx * 6, sy, 0.75, 2)
        c.line(sx, sy, sx, sy + dy * 6, 0.75, 2)
    return c


def wavelet():
    """Onda wavelet (Morlet) con su envolvente: procesamiento de señales."""
    c = Canvas()
    c.line(3, 24, 44, 24, 0.3)
    pts = []
    for k in range(165):
        x = 3 + k * 0.25
        e = math.exp(-((x - 24) / 10) ** 2)
        pts.append((x, 24 - 15 * e * math.cos((x - 24) * 0.5)))
        if k % 8 == 0:
            c.set(x, 24 - 15 * e - 3, 0.45)
            c.set(x, 24 + 15 * e + 3, 0.45)
    c.poly(pts, 1.0, 2)
    return c


def chip():
    """Microcontrolador con pines: sistemas embebidos."""
    c = Canvas()
    c.rect(13, 13, 34, 34, 0.35)
    c.box(13, 13, 34, 34, 0.9)
    c.rect(19, 19, 28, 28, 0.7)
    c.box(19, 19, 28, 28, 1.0)
    c.dot(16, 16, 1.0, 2)
    for p in (16, 20, 24, 28, 31):
        c.line(p, 6, p, 12, 0.8, 2)
        c.line(p, 35, p, 41, 0.8, 2)
        c.line(6, p, 12, p, 0.8, 2)
        c.line(35, p, 41, p, 0.8, 2)
    return c


def code():
    """Símbolo </>: programación."""
    c = Canvas()
    c.poly([(16, 13), (6, 24), (16, 35)], 1.0, 3)
    c.line(28, 9, 20, 39, 0.75, 3)
    c.poly([(32, 13), (42, 24), (32, 35)], 1.0, 3)
    return c


def commits():
    """Mapa de actividad de 7 x 7 bloques, como las contribuciones de GitHub."""
    c = Canvas()
    rnd = random.Random(7)
    for row in range(7):
        for col in range(7):
            i = rnd.choices([0.12, 0.35, 0.55, 0.8, 1.0], weights=[22, 26, 22, 18, 12])[0]
            c.blocks.append((3 + col * 6, 3 + row * 6, 5, 5, i))
    return c


# (etiqueta que aparece bajo el panel, función)
ICONS = [
    ("dashboards.bi", bi_chart),
    ("sql.query", database),
    ("neural.net", neural_net),
    ("computer.vision", vision),
    ("wavelet.signal", wavelet),
    ("embedded.chip", chip),
    ("code.py", code),
    ("commits.map", commits),
]
