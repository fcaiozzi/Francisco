"""Plano de planta + isométrico: ampliación cabaña (bodega + terraza techada)."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Arc, Circle
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import os
OUT = os.path.dirname(os.path.abspath(__file__)) + "/"

# x: a lo largo del muro de la casa (0 = extremo izquierdo); y: hacia afuera de la casa
L, D = 8.25, 2.5
NW, NH = 0.40, 0.40               # destaje en la esquina exterior de la BODEGA = 1 módulo de tabique (40 cm)
XN = L - NW                       # inicio del destaje (7,90)
DIAG_X = 0.0                      # (compatibilidad) ya no hay diagonal
Y0 = D - NH                       # fondo del piso en el destaje (2,15 m)
ALERO = 0.40
BOD = 3.5
XB = L - BOD                      # inicio bodega (4.75): bodega a la DERECHA
piso = [(0, 0), (L, 0), (L, Y0), (XN, Y0), (XN, D), (0, D)]

def prof(x):
    return Y0 if x > XN + 1e-6 else D

def borde_techo(x):
    return D + ALERO                  # techo rectangular

H_T = 0.165                       # alto tijeral 2x6½"
Z_CASA = 2.63 + H_T               # parte de abajo del tijeral en el muro = 2,63 m (medido)
H_V = 0.23                        # tabla 1x10 cepillada 4 caras apernada al muro (alto)
TE_V = 0.019                      # espesor de esa tabla
Z_EX = 2.63 + 0.23 + 0.17         # parte de abajo del alero existente (medido) = 3,03 m
PEND = 0.12
def zt(y):
    return Z_CASA - PEND * y

xs_ter = [i * XB / 8 for i in range(9)]            # 0 .. 4.75 (c/0,59)
xs_bod = [XB + BOD / 6 * i for i in range(1, 7)]   # 5.33 .. 8.25 (c/0,58)
ESP_T, ESP_B = "0,59", "0,58"

# Planchas trapezoidales (ancho útil ~1,0 m): T = translúcida, O = opaca
PLANCHAS = [(i, min(i + 1.0, L), t) for i, t in zip(range(9), "TTTTTOTOT")]
def largo_plancha(x0, x1):
    return math.ceil((max(borde_techo(x0), borde_techo(x1)) + 0.08) * 1.005 * 20) / 20
tij = []
for i, x in enumerate(xs_ter + xs_bod, 1):
    ye = borde_techo(x)
    tij.append((f"T{i}", x, ye, (ye - TE_V) * math.sqrt(1 + PEND ** 2)))

PUERTA = (1.00, 1.88)

Y_MAX = borde_techo(L)
FILAS = [round(0.05 + 0.40 * k, 2) for k in range(20) if 0.05 + 0.40 * k < Y_MAX - 0.1] + [round(Y_MAX - 0.05, 2)]
def x_ini(yr):
    return 0.0
M_COST = sum(L - x_ini(y) for y in FILAS)
N_COST = math.ceil(M_COST / 3.2 * 1.10)
N_PERNOS = math.ceil(L / 0.60) + 1
print("filas costaneras", FILAS, "metros", round(M_COST, 1), "piezas", N_COST, "pernos", N_PERNOS)
SEP = 0.40   # 2x3 -> pies derechos cada 40 cm
# perímetro completo de la bodega (incluye el muro contra la casa)
MUROS = [((L, 0), (L, Y0)), ((L, Y0), (XN, Y0)), ((XN, Y0), (XN, D)), ((XN, D), (XB, D)), ((XB, D), (XB, 0))]

# ---------------- Ventanas ----------------
VEN_ALTO = (1.71, 2.03)        # vano bruto: antepecho -> dintel (ventana 30 cm, borde superior ~2,0 m)
VENTANAS = [
    dict(n="V1", muro="der", a=Y0 / 2 - 0.76, b=Y0 / 2 + 0.76, med="150 x 30", dintel="2x6", hd=0.138),
    dict(n="V2", muro="frente", a=(XB + XN) / 2 - 1.01, b=(XB + XN) / 2 + 1.01,
         med="200 x 30", dintel="2x8", hd=0.185),
]
def _pt(v, s):
    return (L, round(s, 3)) if v["muro"] == "der" else (round(s, 3), D)
def en_vano(p, marg=0.05):
    for v in VENTANAS:
        s = p[1] if v["muro"] == "der" else p[0]
        if (v["muro"] == "der" and abs(p[0] - L) < 1e-6) or (v["muro"] == "frente" and abs(p[1] - D) < 1e-6):
            if v["a"] - marg < s < v["b"] + marg:
                return v
    return None
def muñecos_inf(v):
    n = math.ceil((v["b"] - v["a"]) / SEP) - 1
    return [v["a"] + (v["b"] - v["a"]) * (i + 1) / (n + 1) for i in range(n)]
def tope_pd(muro, s):
    """altura de la cara superior de los pies derechos (bajo solera doble)."""
    y = s if muro == "der" else D
    return zt(y) - H_T - 0.082

def pies_derechos():
    pts = []
    for (x1, y1), (x2, y2) in MUROS:
        lg = math.hypot(x2 - x1, y2 - y1)
        n = max(1, math.ceil(lg / SEP - 1e-9))
        for i in range(n + 1):
            t = i / n
            p = (round(x1 + (x2 - x1) * t, 3), round(y1 + (y2 - y1) * t, 3))
            if x1 == x2 == XB and PUERTA[0] - 0.05 < p[1] < PUERTA[1] + 0.05:
                continue  # dentro del vano
            if en_vano(p):
                continue  # dentro de vano de ventana
            if p not in pts:
                pts.append(p)
    # vanos de ventana: pie derecho entero + jamba a cada lado
    for v in VENTANAS:
        for s in (v["a"] - 0.0205, v["a"] - 0.0615, v["b"] + 0.0205, v["b"] + 0.0615):
            pts.append(_pt(v, s))
    # vano puerta: 2 pies derechos enteros + 2 jambas (bajo dintel)
    pts += [(XB, PUERTA[0] - 0.045), (XB, PUERTA[0] - 0.09),
            (XB, PUERTA[1] + 0.045), (XB, PUERTA[1] + 0.09)]
    # refuerzo: doble pie derecho bajo cada tijeral que apoya en el muro exterior
    for x in xs_bod:
        if x < XN - 0.01 and not en_vano((round(x, 3), D)):
            pts.append((round(x, 3), D))
    # refuerzo de esquinas
    pts += [(L, Y0), (XN, Y0), (XN, D), (XB, D)]
    return pts
PD = pies_derechos()
N_PD = len(PD)
N_MUN_INF = sum(len(muñecos_inf(v)) for v in VENTANAS)
M_ANTEP = sum(2 * (v["b"] - v["a"] + 0.082) for v in VENTANAS)
N_VEN_2X3 = math.ceil(N_MUN_INF + M_ANTEP / 3.2 + 1)      # muñecos + antepecho doble + calce V2
print("ventanas: muñecos inf", N_MUN_INF, "antepecho m", round(M_ANTEP, 2), "piezas 2x3", N_VEN_2X3)
PERIM = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in MUROS)
N_PD_COMPRA = math.ceil(N_PD * 1.10)
N_SOL = math.ceil(((PERIM - 0.88) + 2 * PERIM) / 3.2 * 1.10)
N_CAD = math.ceil(2 * PERIM / 3.2 * 1.10)
print("pies derechos", N_PD, "-> compra", N_PD_COMPRA, "perim", round(PERIM, 2),
      "soleras", N_SOL, "cadenetas", N_CAD)
PILARES = [(0, D), (XB / 2, D)]
VIGA_T = [(0, D), (XB, D)]        # viga exterior terraza (recta)
SEGS = [list(m) for m in MUROS]

# ---------------- Tornillos (sin clavos) ----------------
TIPOS = {
    "A": "Tornillo madera 8 x 3\" zincado",
    "B": "Tirafondo 1/4\" x 4\" zincado",
    "C": "Tornillo Simpson SD #9 x 1½\" (para conectores)",
    "D": "Tirafondo 3/8\" x 4½\" + golilla",
    "F": "Autoperforante techo punta aguja 12 x 1½\" c/golilla EPDM",
    "G": "Autoperforante costura 1/4\" x 7/8\"",
    "H": "Tornillo exterior 8 x 2\" galvanizado",
    "I": "Tornillo madera 6 x 1¼\"",
    "J": "Tornillo 6 x 1\" (cortagotera)",
}
_cruces = sum(1 for yr in FILAS for n, x, ye, lg in tij if ye >= yr)
_filas_plancha = sum(sum(1 for yr in FILAS if yr <= max(borde_techo(a), borde_techo(b)))
                     for a, b, t in PLANCHAS)
USOS_TORN = [
    # (uso, tipo, puntos, tornillos por punto)
    ("Costaneras a tijerales (cada cruce)", "A", _cruces, 2),
    ("Viga doble terraza: unión de las 2 piezas c/40 cm", "A", 13, 2),
    ("Solera inferior bodega al piso c/40 cm", "A", 28, 1),
    ("Pies derechos a soleras (arriba y abajo)", "A", N_PD_COMPRA, 4),
    ("Solera superior doble: unión c/40 cm", "A", 30, 2),
    ("Cadenetas (2 corridas, 2 por extremo)", "A", 60, 4),
    ("Esquinas, vano y pies derechos dobles", "A", 12, 6),
    ("Dintel puerta", "A", 1, 6),
    ("Marco puerta", "A", 1, 12),
    ("Pie derecho extremo de tabiques al muro de la casa", "B", 2, 4),
    ("Tapacán 1x8 a punta de tijerales + uniones", "H", len(tij) + 3, 3),
    ("Bloqueos entre tijerales (muro bodega)", "B", 6, 4),
    ("Soporte viga 2x6 Simpson (colgador en muro casa)", "C", len(tij), 8),
    ("Soporte sismo y viento H3 (2 por tijeral)", "C", 2 * len(tij), 8),
    ("Escuadras base de pilares", "C", 4, 6),
    ("2x4 de apoyo apernado al muro c/60 cm", "D", N_PERNOS, 1),
    ("Viga terraza a pilares", "B", 2, 2),
    ("Planchas a costaneras (~4 por plancha y costanera)", "F", _filas_plancha, 4),
    ("Costura de traslapos laterales c/50 cm", "G", 8, 7),
    ("SmartPanel a pies derechos (c/15 bordes, c/30 centro)", "H", 11, 40),
    ("Esquineros / tapajuntas exteriores", "H", 5, 10),
    ("Contrachapado ranurado interior", "I", 10, 30),
    ("Cortagotera en Z", "J", 3, 6),
    ("Refuerzos de ventanas (jambas, antepecho, muñecos, dintel)", "A", 2, 45),
    ("Botaguas sobre ventanas", "H", 2, 6),
    ("Ganchos de canaleta al tapacán c/50 cm", "H", 19, 2),
    ("Forro muro: a la plancha c/30 cm", "F", 28, 1),
    ("Forro muro: al muro existente c/40 cm", "H", 21, 1),
    ("Remates laterales: a la plancha c/30 cm", "F", 15, 1),
    ("Remates laterales: al tijeral de borde c/40 cm", "H", 11, 1),
    ("Abrazaderas de bajada", "H", 3, 2),
]
def total_tornillos():
    tot = {}
    for uso, tp, p, c in USOS_TORN:
        tot[tp] = tot.get(tp, 0) + p * c
    # +10 % de reserva, redondeado a la decena
    return {tp: math.ceil(v * 1.10 / 10) * 10 for tp, v in tot.items()}
TOT_TORN = total_tornillos()


def planta(ax):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((-0.4, -0.9), L + 0.8, 0.9, facecolor="#e6e6e6",
                           edgecolor="k", hatch="//", lw=1.2))
    ax.text(L / 2, -0.45, "CASA EXISTENTE", ha="center", va="center",
            fontsize=11, weight="bold", bbox=dict(fc="white", ec="none"))
    techo = [(0, 0)] + [(x, borde_techo(x)) for x in (0, DIAG_X)] + \
            [(L, borde_techo(L)), (L, 0)]
    ax.add_patch(Polygon(techo, closed=True, fc="#fff6d8", ec="#b8860b",
                         lw=1.4, ls="-.", zorder=0))
    ax.add_patch(Polygon(piso, closed=True, fc="#f3e3c7", ec="k", lw=2, zorder=1))
    bod = [(XB, 0), (L, 0), (L, Y0), (XN, Y0), (XN, D), (XB, D)]
    ax.add_patch(Polygon(bod, closed=True, fc="#d9e8f5", ec="none", zorder=1))
    for name, x, ye, lg in tij:
        ax.plot([x, x], [0, ye], color="#8b4513", lw=2.2, zorder=3)
        ax.text(x, ye + 0.08, name, ha="center", va="top", fontsize=8,
                color="#8b4513", weight="bold")
    ax.plot([0, L], [-0.04, -0.04], color="#c0392b", lw=3.5, zorder=5)
    ax.text(L - 0.05, -0.12, "tabla 1x10 apernada al muro + soporte Simpson (tijerales de tope)", ha="right", fontsize=7.5, color="#c0392b", zorder=6, bbox=dict(fc="#e6e6e6", ec="none", pad=1))
    vx, vy = zip(*VIGA_T)
    ax.plot(vx, vy, color="#555", lw=3, ls="--", zorder=5)
    cx = [0, DIAG_X, L]; cy = [borde_techo(x) + 0.07 for x in cx]
    ax.plot(cx, cy, color="#7b4a1e", lw=3, zorder=5)
    ax.add_patch(Circle((L + 0.05, cy[-1]), 0.07, fc="#7b4a1e", ec="k", zorder=6))
    ax.text(L - 0.1, cy[-1] + 0.2, "canaleta PVC café → bajada Ø80", fontsize=7.5, color="#7b4a1e", ha="right")
    for px, py in PILARES:
        ax.add_patch(Rectangle((px - 0.045, py - 0.045), 0.09, 0.09, fc="k", zorder=5))
    V1, V2 = VENTANAS
    segs = [[(L, 0), (L, V1["a"])], [(L, V1["b"]), (L, Y0)], [(L, Y0), (XN, Y0)], [(XN, Y0), (XN, D)],
            [(XN, D), (V2["b"], D)], [(V2["a"], D), (XB, D)],
            [(XB, D), (XB, PUERTA[1])], [(XB, PUERTA[0]), (XB, 0)]]
    for (x1, y1), (x2, y2) in segs:
        ax.plot([x1, x2], [y1, y2], color="#1f4e79", lw=4, solid_capstyle="butt",
                zorder=4)
    for v in VENTANAS:
        (x1, y1), (x2, y2) = _pt(v, v["a"]), _pt(v, v["b"])
        for off in (-0.02, 0.02):
            dx, dy = (off, 0) if v["muro"] == "der" else (0, off)
            ax.plot([x1 + dx, x2 + dx], [y1 + dy, y2 + dy], color="#2c7fb8", lw=1.2, zorder=5)
        if v["muro"] == "der":
            ax.text(L + 0.12, v["a"] + 0.25, f'{v["n"]} {v["med"]}\nvano a 1,71–2,03 m', fontsize=7.5,
                    color="#2c7fb8", va="center", weight="bold")
        else:
            ax.text((v["a"] + v["b"]) / 2, D - 0.12, f'{v["n"]} {v["med"]} · vano a 1,71–2,03 m', fontsize=7.5,
                    color="#2c7fb8", ha="center", weight="bold")
    for x, y in PD:
        ax.plot(x, y, "s", ms=4, color="white", mec="k", zorder=6)
    ax.plot([XB, XB + 0.80], [PUERTA[0] + 0.04] * 2, color="k", lw=1.5, zorder=6)
    ax.add_patch(Arc((XB, PUERTA[0] + 0.04), 1.6, 1.6, theta1=0, theta2=90,
                     ls=":", lw=1, zorder=6))
    ax.text(XB - 0.12, (PUERTA[0] + PUERTA[1]) / 2, "PUERTA 80x200\n(vano 88)\nhacia terraza",
            fontsize=7.5, va="center", ha="right", zorder=7)
    ax.text((XB + L) / 2 + 0.25, 1.95, "BODEGA\n3,50 x 2,50 m\n(tabique 2x3 en 3 lados)", ha="center", va="center",
            fontsize=12, weight="bold", color="#1f4e79")
    ax.text(2.6, 0.55, "TERRAZA TECHADA\n4,75 m", ha="center", va="center",
            fontsize=12, weight="bold", color="#6b4f1d")
    ax.text(2.6, 2.32, "viga exterior 2x6 doble sobre pilares", fontsize=7.5, color="#333",
            ha="center")
    ax.text(1.6, 2.78, "borde del techo (alero 0,40 m)", fontsize=7.5,
            color="#b8860b", ha="center")

    def cota_h(x1, x2, y, txt):
        ax.annotate("", (x1, y), (x2, y), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text((x1 + x2) / 2, y - 0.05, txt, ha="center", va="bottom", fontsize=8.5)
    def cota_v(x, y1, y2, txt):
        ax.annotate("", (x, y1), (x, y2), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(x - 0.07, (y1 + y2) / 2, txt, ha="right", va="center",
                fontsize=8.5, rotation=90)
    cota_h(0, L, -1.15, "8,25 m")
    cota_h(0, XB, -1.55, "TERRAZA 4,75 m")
    cota_h(XB, L, -1.55, "BODEGA 3,50 m")
    cota_h(0, XN, 3.75, f"{XN:.2f}".replace(".", ","))
    cota_h(XN, L, 3.75, f"{NW:.2f}".replace(".", ","))
    cota_v(L + 0.45, Y0, D, f"{NH:.2f}".replace(".", ","))
    ax.text(L + 0.25, D + 0.2, f"destaje\n{NW:.2f} x {NH:.2f}".replace(".", ","), ha="center", fontsize=7.5,
            color="#6b4f1d", zorder=7)
    cota_v(-0.95, 0, D, "2,50 m")
    for x1, x2 in zip(xs_ter[:-1], xs_ter[1:]):
        ax.text((x1 + x2) / 2, 0.12, ESP_T, ha="center", fontsize=6.5, color="#8b4513")
    for x1, x2 in zip([XB] + xs_bod[:-1], xs_bod):
        ax.text((x1 + x2) / 2, 0.12, ESP_B, ha="center", fontsize=6.5, color="#8b4513")
    ax.plot([X_CT, X_CT], [-0.95, 3.45], color="#c0392b", lw=1, ls=(0, (8, 3, 2, 3)), zorder=8)
    ax.text(X_CT + 0.08, 3.55, "A", color="#c0392b", fontsize=11, weight="bold")
    ax.text(X_CT + 0.08, -0.98, "A", color="#c0392b", fontsize=11, weight="bold")
    ax.plot([-0.3, L + 0.3], [Y_CL, Y_CL], color="#c0392b", lw=1, ls=(0, (8, 3, 2, 3)), zorder=8)
    ax.text(-0.42, Y_CL, "B", color="#c0392b", fontsize=11, weight="bold", va="center")
    ax.text(L + 0.33, Y_CL, "B", color="#c0392b", fontsize=11, weight="bold", va="center")
    ax.set_xlim(-1.4, L + 1.0)
    ax.set_ylim(-1.9, 4.1)
    ax.invert_yaxis()


def leyenda_y_tabla(fig):
    ax = fig.add_axes([0.04, 0.05, 0.30, 0.22]); ax.axis("off")
    items = [
        ("#8b4513", "-", 2.2, "Tijeral 2x6½\" pino IPV"),
        ("#1f4e79", "-", 4, "Tabique bodega 2x3 pino IPV (pies derechos c/40 cm)"),
        ("#555", "--", 3, "Viga exterior 2x6 doble (terraza)"),
        ("#b8860b", "-.", 1.4, "Borde de techo / tapacán"),
        ("#c0392b", "-", 3.5, "tabla 1x10 apernada al muro de la casa"),
        ("#7b4a1e", "-", 3, "Canaleta aguas lluvia PVC café"),
    ]
    for i, (c, ls, lw, t) in enumerate(items):
        y = 0.97 - i * 0.145
        ax.plot([0.0, 0.12], [y, y], color=c, ls=ls, lw=lw)
        ax.text(0.15, y, t, va="center", fontsize=9)
    ax.plot(0.06, 0.1, "s", ms=6, color="white", mec="k")
    ax.text(0.15, 0.1, "Pie derecho", va="center", fontsize=9)
    ax.plot(0.50, 0.1, "s", ms=6, color="k")
    ax.text(0.55, 0.1, "Pilar terraza 4x4", va="center", fontsize=9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax = fig.add_axes([0.36, 0.03, 0.30, 0.25]); ax.axis("off")
    filas = [[n, f"{x:.2f}", f"{lg:.2f}", "entero"]
             for n, x, ye, lg in tij]
    t = ax.table(cellText=filas, colLabels=["Tijeral", "Posición (m)", "Largo (m)", "Nota"],
                 loc="center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(7); t.scale(1, 0.9)
    ax.set_title("Tijerales (largo inclinado, incluye alero)", fontsize=9)

    ax = fig.add_axes([0.69, 0.03, 0.29, 0.25]); ax.axis("off")
    filas = [[f"P{k + 1}", f"{x0:.1f} – {x1:.2f}", "Translúcida" if t == "T" else "OPACA",
              f"{largo_plancha(x0, x1):.2f}"] for k, (x0, x1, t) in enumerate(PLANCHAS)]
    t = ax.table(cellText=filas, colLabels=["Plancha", "Desde – hasta (m)", "Tipo", "Largo (m)"],
                 loc="center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.0)
    ax.set_title("Cubierta trapezoidal (ancho útil ~1,0 m) · lista completa en lámina 4", fontsize=9)


def iso(ax, azim, elev=30):
    ax.set_proj_type("ortho")
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.computed_zorder = False
    sup = [(x, y, 0) for x, y in piso]
    inf = [(x, y, -0.15) for x, y in piso]
    lados = [[sup[i], sup[(i + 1) % 6], inf[(i + 1) % 6], inf[i]] for i in range(6)]
    ax.add_collection3d(Poly3DCollection(lados, fc="#a0784a", ec="k", lw=0.5))
    ax.add_collection3d(Poly3DCollection([sup], fc="#d2b48c", ec="k", lw=1))
    HB = 1.2
    zb = lambda y: Z_EX + 0.1356 * y
    zback = zb(-HB)
    casa = [
        [(0, 0, 0), (L, 0, 0), (L, 0, Z_EX), (0, 0, Z_EX)],
        [(0, 0, 0), (0, -HB, 0), (0, -HB, zback), (0, 0, Z_EX)],
        [(L, 0, 0), (L, -HB, 0), (L, -HB, zback), (L, 0, Z_EX)],
    ]
    ax.add_collection3d(Poly3DCollection(casa, fc="#9db4c0", ec="#5a6f7a",
                                         alpha=0.30, lw=0.6))
    for (x1, y1), (x2, y2) in SEGS:
        ax.plot([x1, x2], [y1, y2], [0.04, 0.04], color="#1f4e79", lw=2.5)
        ax.plot([x1, x2], [y1, y2], [zt(y1) - H_T, zt(y2) - H_T],
                color="#1f4e79", lw=2.5)
        ax.plot([x1, x2], [y1, y2], [0.85, 0.85], color="#1f4e79", lw=1.2)
        ax.plot([x1, x2], [y1, y2], [1.7, 1.7], color="#1f4e79", lw=1.2)
    for x, y in PD:
        ax.plot([x, x], [y, y], [0, zt(y) - H_T], color="#2e75b6", lw=1.4)
    for v in VENTANAS:
        (x1, y1), (x2, y2) = _pt(v, v["a"]), _pt(v, v["b"])
        z0, z1 = VEN_ALTO
        ax.add_collection3d(Poly3DCollection([[(x1, y1, z0 + 0.01), (x2, y2, z0 + 0.01), (x2, y2, z1 - 0.01),
                                               (x1, y1, z1 - 0.01)]], fc="#9ecae1", ec="#2c7fb8", alpha=0.8))
        ax.plot([x1, x2], [y1, y2], [z1 + v["hd"] / 2] * 2, color="#1f4e79", lw=4)   # dintel
        ax.plot([x1, x2], [y1, y2], [z0 - 0.04] * 2, color="#1f4e79", lw=3)          # antepecho
        for s in muñecos_inf(v):
            px, py = _pt(v, s)
            ax.plot([px, px], [py, py], [0, z0 - 0.08], color="#2e75b6", lw=1.4)
    y0, y1 = PUERTA
    ax.plot([XB, XB], [y0, y1], [2.05, 2.05], color="#1f4e79", lw=4)
    puerta = [[(XB - 0.01, y0 + 0.04, 0), (XB - 0.01, y1 - 0.04, 0),
               (XB - 0.01, y1 - 0.04, 2.0), (XB - 0.01, y0 + 0.04, 2.0)]]
    ax.add_collection3d(Poly3DCollection(puerta, fc="#8b5a2b", ec="k", alpha=0.85))
    for px, py in PILARES:
        ax.plot([px, px], [py, py], [0, zt(py) - H_T], color="k", lw=3)
    vx, vy = zip(*VIGA_T)
    ax.plot(vx, vy, [zt(v) - H_T for v in vy], color="#444", lw=3.5)
    ax.plot([0, L], [0.02, 0.02], [zt(0) - H_V / 2] * 2, color="#c0392b", lw=3.5)
    for n, x, ye, lg in tij:
        ax.plot([x, x], [0, ye], [zt(0), zt(ye)], color="#8b4513", lw=3)
        ax.plot([x, x], [0, ye], [zt(0) - H_T, zt(ye) - H_T], color="#8b4513", lw=1)
    for yr in FILAS:
        ax.plot([x_ini(yr), L], [yr, yr], [zt(yr) + 0.04] * 2, color="#c8a165", lw=1.4)
    borde = [(0, 0), (0, borde_techo(0)), (DIAG_X, borde_techo(DIAG_X)),
             (L, borde_techo(L)), (L, 0)]
    for (x1, y1), (x2, y2) in zip(borde[:-1], borde[1:]):
        cara = [[(x1, y1, zt(y1) + 0.041 - 0.185), (x2, y2, zt(y2) + 0.041 - 0.185),
                 (x2, y2, zt(y2) + 0.02), (x1, y1, zt(y1) + 0.02)]]
        ax.add_collection3d(Poly3DCollection(cara, fc="#b8860b", ec="k", lw=0.5))
    ex = [0, DIAG_X, L]
    ax.plot(ex, [borde_techo(x) + 0.06 for x in ex], [zt(borde_techo(x)) - 0.08 for x in ex],
            color="#7b4a1e", lw=4)
    ax.plot([L, L], [borde_techo(L) + 0.06] * 2, [zt(borde_techo(L)) - 0.08, -0.15], color="#7b4a1e", lw=3)
    for x0, x1, tp in PLANCHAS:
        xs = [x0] + ([DIAG_X] if x0 < DIAG_X < x1 else []) + [x1]
        pts = [(x0, 0), (x1, 0)] + [(x, borde_techo(x)) for x in reversed(xs)]
        poly = [[(x, y, zt(y) + 0.07) for x, y in pts]]
        if tp == "T":
            ax.add_collection3d(Poly3DCollection(poly, fc="#bfe3f5", ec="#6a9fb5", alpha=0.22, lw=0.6))
        else:
            ax.add_collection3d(Poly3DCollection(poly, fc="#7d8a91", ec="#444", alpha=0.85, lw=0.6))
    techo_casa = [[(-0.3, 0.45, zb(0.45) + 0.05), (L + 0.3, 0.45, zb(0.45) + 0.05),
                   (L + 0.3, -HB - 0.2, zb(-HB - 0.2) + 0.05),
                   (-0.3, -HB - 0.2, zb(-HB - 0.2) + 0.05)]]
    ax.add_collection3d(Poly3DCollection(techo_casa, fc="#7f8c8d", ec="#444",
                                         alpha=0.30, lw=0.6))
    ax.text(6.0, 0.6, 2.9, "BODEGA", color="#1f4e79", fontsize=11, weight="bold")
    ax.text(1.6, 0.6, 0.05, "TERRAZA", color="#6b4f1d", fontsize=11, weight="bold")
    ax.text(3.0, -1.0, 3.3, "CASA EXISTENTE", color="#3d5361", fontsize=9)
    ax.set_xlim(-0.3, 8.55); ax.set_ylim(-1.6, 3.4); ax.set_zlim(-0.2, 3.2)
    ax.set_box_aspect((8.85, 5.0, 3.4), zoom=1.0)
    ax.invert_yaxis()   # mismo sentido que la planta (no espejado)


# ---------------- Lámina 3: CORTES ----------------
X_CT = 6.50      # corte transversal A-A (por la bodega)
Y_CL = 1.25      # corte longitudinal B-B
H_T = 0.165      # alto tijeral 2x6½"
MADERA = "#e8c891"

def _cota(ax, p1, p2, txt, off=(0, 0), rot=0, fs=8):
    ax.annotate("", p1, p2, arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text((p1[0] + p2[0]) / 2 + off[0], (p1[1] + p2[1]) / 2 + off[1], txt,
            ha="center", va="center", fontsize=fs, rotation=rot,
            bbox=dict(fc="white", ec="none", pad=0.5))

def corte_transversal(ax):
    ax.set_aspect("equal"); ax.axis("off")
    zb = lambda y: Z_EX + 0.1356 * y
    # casa existente
    ax.add_patch(Rectangle((-1.2, 0), 1.2, Z_EX, fc="#e6e6e6", ec="k", hatch="//", lw=1))
    ax.plot([-1.2, 0.45], [zb(-1.2) + 0.05, zb(0.45) + 0.05], color="#555", lw=4)
    ax.text(-0.6, 1.4, "CASA\nEXISTENTE", ha="center", fontsize=9, weight="bold",
            bbox=dict(fc="white", ec="none"))
    # piso
    ax.add_patch(Rectangle((0, -0.15), D, 0.15, fc="#a0784a", ec="k"))
    # 2x6 apernado al muro (de canto); el tijeral llega DE TOPE con soporte Simpson
    zl = zt(0) - H_T
    zv = zl
    ax.add_patch(Rectangle((0, zv), TE_V, H_V, fc="#c0392b", ec="k", zorder=5))
    ax.plot([-0.15, 0.06], [zv + 0.025] * 2, color="k", lw=1.5, zorder=6)
    # soporte viga (colgador): asiento bajo el tijeral + alas sobre el 2x4
    ax.plot([0.041, 0.041, 0.10, 0.10], [zl + 0.08, zl - 0.004, zl - 0.004 - 0.006, zl + 0.03],
            color="#333", lw=2, zorder=7)
    # soportes H3 en el muro exterior (uno por lado)
    ax.add_patch(Rectangle((D - 0.09, zt(D) - H_T - 0.07), 0.05, 0.15, fc="#333", ec="k", zorder=7))
    # tijeral (corte a plomo en la punta, de tope contra el 2x4)
    ye = borde_techo(X_CT)
    tij_poly = [(TE_V, zt(TE_V)), (ye, zt(ye)), (ye, zt(ye) - H_T), (TE_V, zt(TE_V) - H_T)]
    ax.add_patch(Polygon(tij_poly, fc=MADERA, ec="k", lw=1, zorder=4))
    # costaneras 2x2 c/40 + plancha
    for yr in FILAS:
        ax.add_patch(Rectangle((yr - 0.02, zt(yr)), 0.041, 0.041, fc="#c8a165", ec="k",
                               lw=0.6, zorder=5))
    ax.plot([0, ye + 0.05], [zt(0) + 0.05, zt(ye + 0.05) + 0.05], color="#555", lw=2.5, zorder=6)
    # tapacán vertical
    ax.add_patch(Rectangle((ye, zt(ye) + 0.041 - 0.185), 0.019, 0.185, fc="#b8860b",
                           ec="k", zorder=6))
    # canaleta PVC café colgada del tapacán
    zc0 = zt(ye) - 0.02
    ax.add_patch(Polygon([(ye + 0.019, zc0), (ye + 0.019, zc0 - 0.07), (ye + 0.07, zc0 - 0.09),
                          (ye + 0.13, zc0 - 0.06), (ye + 0.13, zc0)], fill=False, ec="#7b4a1e", lw=2, zorder=7))
    # tabique bodega contra la casa y muro exterior (2x3 = 65 mm)
    for y0w, ztop in [(D - 0.065, zt(D) - H_T)]:
        ax.add_patch(Rectangle((y0w, 0), 0.065, ztop, fc="#d9e8f5", ec="#1f4e79", lw=1.5))
    # puerta vista al fondo (muro bodega/terraza)
    ax.add_patch(Rectangle((PUERTA[0], 0), PUERTA[1] - PUERTA[0], 2.05, fill=False,
                           ec="#8b5a2b", ls="--", lw=1))
    ax.text((PUERTA[0] + PUERTA[1]) / 2, 1.0, "puerta 80x200\n(al fondo)", ha="center",
            fontsize=7.5, color="#8b5a2b")
    ax.text(1.5, 2.05, "BODEGA", ha="center", fontsize=10, weight="bold", color="#1f4e79")
    # cotas
    _cota(ax, (D + 1.05, 0), (D + 1.05, zt(D) - H_T), f"{zt(D) - H_T:.2f}", off=(0.12, 0), rot=90)
    _cota(ax, (0.35, 0), (0.35, zl), f"{zl:.2f}", off=(0.12, 0), rot=90)
    _cota(ax, (-1.45, 0), (-1.45, Z_EX), "3,03", off=(-0.12, 0), rot=90)
    _cota(ax, (0, -0.45), (D, -0.45), "2,50 (piso)")
    _cota(ax, (D, -0.45), (ye, -0.45), f"alero {ye - D:.2f}")
    ax.text(1.4, zt(1.4) + 0.32, "pendiente 12 %", ha="center", fontsize=8.5, rotation=-3)
    # rótulos
    notas = [((0.03, zl + 0.04), (0.55, 1.75), "ver DETALLE 1"),
             ((D - 0.07, zt(D) - H_T - 0.05), (D + 0.55, 1.95), "ver DETALLE 2"),
             ((1.6, zt(1.6) - 0.07), (1.9, 3.35), "tijeral 2x6½\""),
             ((FILAS[3], zt(FILAS[3]) + 0.03), (0.9, 3.5), "costanera 2x2 c/40 cm"),
             ((0.5, zt(0.5) + 0.06), (0.1, 3.2), "plancha trapezoidal"),
             ((ye + 0.02, zt(ye) - 0.05), (ye + 0.35, 2.75), "tapacán 1x8\n+ canaleta PVC café"),
             ((D - 0.03, 1.2), (D + 0.45, 1.6), "tabique\n2x3 c/40")]
    for p, t, txt in notas:
        ax.annotate(txt, p, t, fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=0.6),
                    ha="center", zorder=8)
    ax.set_xlim(-1.8, D + 1.4); ax.set_ylim(-0.75, 3.7)
    ax.set_title(f"CORTE TRANSVERSAL A-A (por la bodega)", fontsize=11, weight="bold")

def detalle(ax, cual):
    ax.set_aspect("equal"); ax.axis("off")
    zl = zt(0) - H_T
    if cual == 1:
        ax.add_patch(Rectangle((-0.25, zl - 0.35), 0.25, 0.75, fc="#e6e6e6", ec="k", hatch="//"))
        zv = zl
        ax.add_patch(Rectangle((0, zv), TE_V, H_V, fc="#c0392b", ec="k", zorder=5))
        ax.plot([-0.18, 0.06], [zv + 0.025] * 2, color="k", lw=2.5, zorder=6)
        ax.plot([-0.18, 0.06], [zv + H_V - 0.025] * 2, color="k", lw=2.5, ls=":", zorder=6)
        y1 = 0.45
        ax.add_patch(Polygon([(TE_V, zt(TE_V)), (y1, zt(y1)), (y1, zt(y1) - H_T),
                              (TE_V, zt(TE_V) - H_T)], fc=MADERA, ec="k", zorder=4))
        ax.add_patch(Rectangle((0.041, zl - 0.004), 0.06, 0.13, fill=False, ec="#333", lw=2, zorder=7))
        ax.plot([0.041, 0.101], [zl - 0.004] * 2, color="#333", lw=3, zorder=7)
        for yr in [0.05, 0.45]:
            ax.add_patch(Rectangle((yr - 0.02, zt(yr)), 0.041, 0.041, fc="#c8a165", ec="k", zorder=5))
        ax.plot([0.0, y1], [zt(0) + 0.05, zt(y1) + 0.05], color="#555", lw=2.5)
        txt = [((0.02, zl + 0.11), (0.13, zl + 0.40), "tabla 1x10\napernada"),
               ((-0.1, zv + 0.025), (-0.13, zl - 0.30), "pernos 3/8\" c/60,\nalternados arriba/abajo\nentre soportes"),
               ((0.10, zl + 0.02), (0.36, zl - 0.15), "soporte viga Simpson\n2x6 ZMAX (Imperial 142184)"),
               ((0.3, zt(0.3) - 0.07), (0.43, zl + 0.30), "tijeral 2x6½\" de tope\n(punta a plomo + asiento)"),
               ((0.041, zv), (0.42, zl - 0.33), "tabla 1x10 (23 cm), su\nborde bajo a 2,63 m")]
        ax.set_title("DETALLE 1 · apoyo en muro de la casa", fontsize=9, weight="bold")
        ax.set_xlim(-0.3, 0.55); ax.set_ylim(zl - 0.4, zl + 0.45)
    else:
        zw = zt(D) - H_T
        ax.add_patch(Rectangle((D - 0.065, zw - 0.45), 0.065, 0.45, fc="#d9e8f5", ec="#1f4e79", zorder=3))
        ax.add_patch(Rectangle((D - 0.065, zw - 0.082), 0.065, 0.082, fc="#9dbbd9", ec="#1f4e79", zorder=4))
        y0, y1 = D - 0.45, D + 0.35
        ax.add_patch(Polygon([(y0, zt(y0)), (y1, zt(y1)), (y1, zt(y1) - H_T), (y0, zt(y0) - H_T)],
                             fc=MADERA, ec="k", zorder=4))
        ax.add_patch(Polygon([(D - 0.095, zw - 0.10), (D - 0.045, zw - 0.10), (D - 0.045, zt(D - 0.045) - 0.03),
                              (D - 0.095, zt(D - 0.095) - 0.03)], fc="#333", ec="k", alpha=0.85, zorder=6))
        for yr in [2.45, 2.85]:
            ax.add_patch(Rectangle((yr - 0.02, zt(yr)), 0.041, 0.041, fc="#c8a165", ec="k", zorder=5))
        ax.plot([y0, y1], [zt(y0) + 0.05, zt(y1) + 0.05], color="#555", lw=2.5)
        txt = [((D - 0.07, zw - 0.06), (D - 0.38, zw - 0.3), "soporte sismo y viento\nH3, uno por lado\n(Imperial 142181)"),
               ((D - 0.03, zw - 0.04), (D + 0.22, zw - 0.25), "solera doble 2x3"),
               ((D - 0.03, zw - 0.3), (D + 0.22, zw - 0.42), "tabique 2x3"),
               ((D + 0.2, zt(D + 0.2) - 0.07), (D + 0.12, zw + 0.33), "tijeral 2x6½\" → alero")]
        ax.set_title("DETALLE 2 · apoyo en muro exterior", fontsize=9, weight="bold")
        ax.set_xlim(D - 0.55, D + 0.4); ax.set_ylim(zw - 0.5, zw + 0.42)
    for p, t, tx in txt:
        ax.annotate(tx, p, t, fontsize=7, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.6), zorder=9,
                    bbox=dict(fc="white", ec="none", pad=0.5))


def corte_longitudinal(ax):
    ax.set_aspect("equal"); ax.axis("off")
    zc = zt(Y_CL)
    # muro de la casa al fondo
    ax.add_patch(Rectangle((-0.3, 0), L + 0.6, Z_EX, fc="#f0f0f0", ec="#999", lw=0.8))
    ax.plot([-0.3, L + 0.3], [Z_EX + 0.06, Z_EX + 0.06], color="#555", lw=3)
    ax.add_patch(Rectangle((0, zt(0) - H_V), L, H_V, fc="#c0392b", ec="k", lw=0.5))
    # piso (cortado donde existe a esa distancia)
    x0 = 0.0
    ax.add_patch(Rectangle((x0, -0.15), L - x0, 0.15, fc="#a0784a", ec="k"))
    # pilar al fondo (esquina izquierda)
    ax.add_patch(Rectangle((0, -0.15), 0.09, zt(D) - H_T + 0.15, fc="#555", ec="k"))
    ax.text(0.05, -0.35, "pilar 4x4", ha="center", fontsize=7.5)
    # tabique bodega del lado casa (al fondo): pies derechos
    for x, y in PD:
        if y < 0.01:
            ax.plot([x, x], [0, zt(0) - H_T - 0.09], color="#9dbbd9", lw=1)
    # muros bodega cortados: lado terraza (con vano de puerta) y lado derecho
    zw = zc - H_T
    ax.add_patch(Rectangle((XB, PUERTA[0] * 0 + 2.05), 0.065, zw - 2.05, fc="#1f4e79", ec="k"))
    ax.add_patch(Rectangle((XB - 0.01, 0), 0.04, 2.0, fc="#8b5a2b", ec="k"))
    ax.add_patch(Rectangle((L - 0.065, 0), 0.065, zt(Y_CL) - H_T, fc="#1f4e79", ec="k"))
    ax.text(XB - 0.1, 1.0, "puerta\n80x200", ha="right", fontsize=7.5, color="#8b5a2b")
    # tijerales cortados + plancha
    for n, x, ye, lg in tij:
        if ye >= Y_CL:
            ax.add_patch(Rectangle((x - 0.02, zw), 0.041, H_T, fc=MADERA, ec="k", lw=0.8, zorder=5))
            ax.text(x, zc + 0.2, n, ha="center", fontsize=7, color="#8b4513")
    ax.plot([0, L], [zc + 0.05] * 2, color="#c8a165", lw=3, zorder=4)   # costanera
    ax.plot([0, L], [zc + 0.08] * 2, color="#555", lw=2, zorder=6)      # plancha
    ax.text((XB + L) / 2, 1.3, "BODEGA", ha="center", fontsize=10, weight="bold", color="#1f4e79")
    ax.text(XB / 2, 1.3, "TERRAZA TECHADA", ha="center", fontsize=10, weight="bold", color="#6b4f1d")
    _cota(ax, (0, -0.65), (XB, -0.65), "4,75 terraza (tijerales c/0,59)")
    _cota(ax, (XB, -0.65), (L, -0.65), "3,50 bodega (tijerales c/0,58)")
    _cota(ax, (L + 0.4, 0), (L + 0.4, zw), f"{zw:.2f}", off=(0.13, 0), rot=90)
    ax.set_xlim(-0.6, L + 0.8); ax.set_ylim(-0.95, 3.3)
    ax.set_title(f"CORTE LONGITUDINAL B-B (a {Y_CL:.2f} m del muro, mirando hacia la casa)",
                 fontsize=11, weight="bold")


# ---------------- Lámina 5: HOJALATERÍA ----------------
ZINC = "#5f6b73"

def detalle_forro(ax):
    ax.set_aspect("equal"); ax.axis("off")
    z0 = zt(0)
    # muro existente + alero existente
    ax.add_patch(Rectangle((-0.30, z0 - 0.45), 0.30, Z_EX - z0 + 0.45, fc="#e6e6e6", ec="k", hatch="//"))
    ax.plot([-0.30, 0.40], [Z_EX, Z_EX + 0.095], color="#555", lw=5)
    ax.text(0.05, Z_EX + 0.10, "alero / cubierta EXISTENTE", fontsize=7.5, color="#444")
    # viga 2x8 y tijeral
    zl = z0 - H_T; zv = zl
    ax.add_patch(Rectangle((0, zv), TE_V, H_V, fc="#c0392b", ec="k"))
    y1 = 0.55
    ax.add_patch(Polygon([(TE_V, zt(TE_V)), (y1, zt(y1)), (y1, zt(y1) - H_T), (TE_V, zt(TE_V) - H_T)],
                         fc=MADERA, ec="k"))
    for yr in [0.06, 0.46]:
        ax.add_patch(Rectangle((yr - 0.02, zt(yr)), 0.041, 0.041, fc="#c8a165", ec="k"))
    zp = lambda y: zt(y) + 0.041 + 0.004
    ax.plot([0.0, y1], [zp(0), zp(y1)], color="#555", lw=3)                       # plancha
    ax.add_patch(Rectangle((0.0, zp(0)), 0.035, 0.03, fc="#222", ec="k"))           # cierre espuma
    # forro (hojalatería): pliegue en muro, baja por el muro y sigue sobre la plancha
    zf = zp(0) + 0.035
    pts = [(-0.012, (Z_EX - 0.02)), (0.0, (Z_EX - 0.02)), (0.0, zf), (0.22, zp(0.22) + 0.035), (0.24, zp(0.24) + 0.012)]
    ax.plot(*zip(*pts), color=ZINC, lw=3.5, solid_capstyle="round")
    ax.add_patch(Rectangle((-0.02, (Z_EX - 0.03)), 0.025, 0.02, fc="#e67e22", ec="none"))   # sello
    ax.plot([0.14, 0.14], [zp(0.14) + 0.06, zp(0.14) - 0.06], color="k", lw=1.5)    # autoperforante
    ax.plot([-0.06, 0.01], [Z_EX - 0.05, Z_EX - 0.05], color="k", lw=1.5)                         # tornillo al muro
    notas = [((0.0, Z_EX - 0.05), (-0.17, Z_EX + 0.12), "forro zincalum 0,4 mm\ndesarrollo ~40 cm"),
             ((-0.01, (Z_EX - 0.02)), (-0.23, Z_EX - 0.22), "sello poliuretano\n(arriba del forro)"),
             ((-0.04, Z_EX - 0.05), (-0.21, Z_EX - 0.42), "tornillo 8x2\" c/40\nal muro existente"),
             ((0.017, zp(0) + 0.015), (0.20, Z_EX - 0.32), "cierre de espuma\n(tapa las ondas)"),
             ((0.14, zp(0.14) + 0.04), (0.36, Z_EX + 0.02), "autoperforante\n12x1½\" c/30 cm"),
             ((0.235, zp(0.235) + 0.015), (0.50, zp(0.24) + 0.10), "goterón"),
             ((0.35, zp(0.35)), (0.47, zp(0.35) - 0.12), "plancha trapezoidal"),
             ((0.3, zt(0.3) - 0.08), (0.40, zl - 0.12), "tijeral 2x6½\""),
             ((0.02, zv + 0.05), (0.15, zl - 0.22), "tabla 1x10 apernada")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=7.5, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6), bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(-0.32, 0.6); ax.set_ylim(z0 - 0.45, Z_EX + 0.20)
    ax.set_title("DETALLE 3 · forro contra el muro existente", fontsize=10, weight="bold")

def detalle_remate(ax):
    ax.set_aspect("equal"); ax.axis("off")
    yS = 1.5; zc = zt(yS)
    # tijeral de borde (T15) en corte
    ax.add_patch(Rectangle((L - 0.041, zc - H_T), 0.041, H_T, fc=MADERA, ec="k"))
    ax.add_patch(Rectangle((L - 0.62, zc - H_T), 0.041, H_T, fc=MADERA, ec="k", alpha=0.6))
    # costanera (vista larga, cortada al borde)
    ax.add_patch(Rectangle((L - 0.70, zc), 0.70, 0.041, fc="#c8a165", ec="k"))
    # plancha trapezoidal (perfil)
    zb = zc + 0.041; h = 0.035; per = 0.25
    xs, zs = [], []
    x = L - 0.70
    while x < L:
        xs += [x, x + 0.05, x + 0.09, x + 0.16, x + 0.20]
        zs += [zb, zb, zb + h, zb + h, zb]
        x += per
    xs = [min(v, L) for v in xs]
    ax.plot(xs, zs, color="#555", lw=2.5)
    # remate lateral
    pts = [(L - 0.17, zb + h + 0.004), (L + 0.015, zb + h + 0.004), (L + 0.015, zc - H_T - 0.03),
           (L + 0.035, zc - H_T - 0.045)]
    ax.plot(*zip(*pts), color=ZINC, lw=3.5, solid_capstyle="round")
    ax.plot([L - 0.12, L - 0.12], [zb + h + 0.05, zc + 0.01], color="k", lw=1.5)    # autoperforante
    ax.plot([L + 0.05, L - 0.03], [zc - 0.07] * 2, color="k", lw=1.5)               # tornillo lateral
    notas = [((L + 0.015, zc - 0.02), (L + 0.22, zc + 0.16), "remate lateral zincalum 0,4 mm\ndesarrollo ~35 cm"),
             ((L - 0.12, zb + h + 0.03), (L - 0.30, zc + 0.20), "autoperforante 12x1½\"\nc/30 cm (en la cresta)"),
             ((L + 0.03, zc - 0.07), (L + 0.24, zc - 0.07), "tornillo 8x2\" c/40\nal tijeral de borde"),
             ((L + 0.03, zc - H_T - 0.04), (L + 0.22, zc - H_T - 0.08), "goterón"),
             ((L - 0.02, zc - 0.10), (L - 0.30, zc - 0.22), "tijeral de borde\n(T15 / T1)"),
             ((L - 0.45, zc + 0.02), (L - 0.55, zc - 0.25), "costanera 2x2"),
             ((L - 0.40, zb + 0.01), (L - 0.62, zc + 0.15), "plancha trapezoidal\n(última onda en el borde)")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=7.5, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6), bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(L - 0.78, L + 0.45); ax.set_ylim(zc - 0.32, zc + 0.27)
    ax.set_title("DETALLE 4 · remate lateral (los dos bordes de 2,5 m)", fontsize=10, weight="bold")

def llave_hojalateria(ax):
    ax.set_aspect("equal"); ax.axis("off")
    techo = [(0, 0), (0, borde_techo(0)), (DIAG_X, borde_techo(DIAG_X)), (L, borde_techo(L)), (L, 0)]
    ax.add_patch(Polygon(techo, fc="#fff6d8", ec="#b8860b", lw=1, ls="-."))
    ax.add_patch(Rectangle((-0.3, -0.5), L + 0.6, 0.5, fc="#e6e6e6", ec="k", hatch="//"))
    ax.text(L / 2, -0.25, "CASA EXISTENTE", ha="center", va="center", fontsize=8, bbox=dict(fc="white", ec="none"))
    ax.plot([0, L], [0.03, 0.03], color=ZINC, lw=5)
    ax.plot([0, 0], [0, borde_techo(0)], color="#2c7fb8", lw=5)
    ax.plot([L, L], [0, borde_techo(L)], color="#2c7fb8", lw=5)
    cx = [0, DIAG_X, L]; ax.plot(cx, [borde_techo(x) + 0.07 for x in cx], color="#7b4a1e", lw=3)
    ax.text(L / 2, 0.35, "FORRO contra muro existente · 8,25 m · DETALLE 3", ha="center", fontsize=8.5, color=ZINC, weight="bold")
    ax.text(L + 0.12, 1.4, "REMATE LATERAL\n2,9 m · DETALLE 4", fontsize=8, color="#2c7fb8", weight="bold", va="center")
    ax.text(-0.12, 0.75, "REMATE LATERAL\n2,9 m · DETALLE 4", fontsize=8, color="#2c7fb8", weight="bold", va="center", ha="right")
    ax.text(5.6, borde_techo(L) + 0.35, "canaleta PVC café (borde bajo)", fontsize=8, color="#7b4a1e", ha="center")
    ax.set_xlim(-1.6, L + 1.6); ax.set_ylim(-0.7, 3.8); ax.invert_yaxis()
    ax.set_title("UBICACIÓN DE LA HOJALATERÍA (planta de techo)", fontsize=10, weight="bold")


# ---------------- Lámina 6: ELEVACIONES DE TABIQUERÍA CON VENTANAS ----------------
AZUL = "#9dbbd9"; AZUL_OSC = "#1f4e79"

def elevacion(ax, v):
    ax.set_aspect("equal"); ax.axis("off")
    if v["muro"] == "der":
        s0, s1 = 0.0, Y0
        tope = lambda s: tope_pd("der", s)
        titulo_e = "ELEVACIÓN MURO LATERAL (2,5 m) · ventana V1 150 x 30 — vista desde afuera"
        tijs = [(s0, s1)]
    else:
        s0, s1 = XB, XN
        tope = lambda s: tope_pd("frente", s)
        titulo_e = "ELEVACIÓN MURO FRENTE A LA CASA · ventana V2 200 x 30 — vista desde afuera"
        tijs = None
    z0, z1 = VEN_ALTO
    a, b, hd = v["a"], v["b"], v["hd"]
    pd = sorted({(p[1] if v["muro"] == "der" else p[0]) for p in PD
                 if (v["muro"] == "der" and abs(p[0] - L) < 1e-6)
                 or (v["muro"] == "frente" and abs(p[1] - D) < 1e-6 and XB - 1e-6 <= p[0] <= XN + 1e-6)})
    def poly_top(sa, sb, dz=0.0):
        return [(sa, tope(sa) + dz), (sb, tope(sb) + dz)]
    # solera inferior y superior doble
    ax.add_patch(Rectangle((s0, 0), s1 - s0, 0.041, fc=AZUL, ec=AZUL_OSC))
    for k in (0, 1):
        (xa, za), (xb, zb) = poly_top(s0, s1, 0.041 * k)
        ax.add_patch(Polygon([(xa, za), (xb, zb), (xb, zb + 0.041), (xa, za + 0.041)], fc=AZUL, ec=AZUL_OSC))
    # pies derechos (fuera del vano), jambas y enteros
    for s in pd:
        if a - 0.03 < s < a or b < s < b + 0.03:      # jambas
            ax.add_patch(Rectangle((s - 0.0205, 0.041), 0.041, z1 - 0.041, fc="#f4a261", ec="k", lw=0.6, zorder=3))
        else:
            ax.add_patch(Rectangle((s - 0.0205, 0.041), 0.041, tope(s) - 0.041, fc=AZUL, ec=AZUL_OSC, lw=0.6))
    # cadenetas (no cruzan el vano en la corrida alta)
    for zc in (0.85, 1.70):
        segs = [(s0, s1)] if zc < z0 - 0.1 else [(s0, a - 0.0615), (b + 0.0615, s1)]
        for sa, sb in segs:
            ax.add_patch(Rectangle((sa, zc - 0.0325), sb - sa, 0.065, fc="#cfe0ef", ec=AZUL_OSC, lw=0.4))
    # antepecho doble
    ax.add_patch(Rectangle((a, z0 - 0.082), b - a, 0.082, fc="#e76f51", ec="k", zorder=4))
    # muñecos inferiores
    for s in muñecos_inf(v):
        ax.add_patch(Rectangle((s - 0.0205, 0.041), 0.041, z0 - 0.082 - 0.041, fc="#f6bd60", ec="k", lw=0.6))
    # dintel
    ax.add_patch(Rectangle((a - 0.041, z1), b - a + 0.082, hd, fc="#c0392b", ec="k", zorder=4))
    # sobre el dintel: muñecos superiores (V1) o calce (V2)
    if v["muro"] == "der":
        for s in [a + (b - a) * k / 4 for k in (1, 2, 3)]:
            ax.add_patch(Rectangle((s - 0.0205, z1 + hd), 0.041, tope(s) - z1 - hd, fc="#f6bd60", ec="k", lw=0.6))
    else:
        ax.add_patch(Rectangle((a - 0.041, z1 + hd), b - a + 0.082, tope(a) - z1 - hd, fc="#f6bd60", ec="k", lw=0.6))
    # ventana
    ax.add_patch(Rectangle((a + 0.01, z0 + 0.01), b - a - 0.02, z1 - z0 - 0.02, fc="#bfe3f5", ec="#2c7fb8", lw=1.5, zorder=5))
    ax.text((a + b) / 2, (z0 + z1) / 2, f'{v["n"]} {v["med"]}', ha="center", va="center", fontsize=8,
            color="#1f4e79", weight="bold", zorder=6)
    # tijerales encima
    if v["muro"] == "der":
        ax.add_patch(Polygon([(s0, tope(s0) + 0.082), (s1, tope(s1) + 0.082), (s1, tope(s1) + 0.082 + H_T),
                              (s0, tope(s0) + 0.082 + H_T)], fc=MADERA, ec="k", alpha=0.7))
        ax.text(1.0, tope(1.0) + 0.082 + H_T / 2, "tijeral T15 (apoyado a lo largo del muro)", ha="center",
                va="center", fontsize=7)
    else:
        for n_, x, ye, lg in tij:
            if s0 - 0.01 <= x <= s1 + 0.01:
                ax.add_patch(Rectangle((x - 0.0205, tope(x) + 0.082), 0.041, H_T, fc=MADERA, ec="k"))
                ax.text(x, tope(x) + 0.082 + H_T + 0.05, n_, ha="center", fontsize=7, color="#8b4513")
    # cotas
    def cota_h(xa, xb, z, t):
        ax.annotate("", (xa, z), (xb, z), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text((xa + xb) / 2, z - 0.08, t, ha="center", fontsize=7.5)
    def cota_v(x, za, zb, t):
        ax.annotate("", (x, za), (x, zb), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(x + 0.05, (za + zb) / 2, t, va="center", fontsize=7.5, rotation=90)
    cota_h(a, b, -0.12, f"vano {b - a:.2f}")
    cota_h(s0, s1, -0.32, f"muro {s1 - s0:.2f}")
    cota_v(s1 + 0.12, 0, z0, f"{z0:.2f}")
    cota_v(s1 + 0.32, 0, z1, f"{z1:.2f}")
    # rótulos
    lab = [((a - 0.0615, 1.0), (s0 + 0.0 if v["muro"] == "der" else a - 0.45, 0.5), "pie derecho\nentero"),
           ((a - 0.0205, 1.4), (a - 0.40, 1.25) if v["muro"] == "der" else (a - 0.45, 1.25), "jamba\n(bajo dintel)"),

           ((a + 0.3, z0 - 0.04), (a + 0.55, z0 - 0.45), "antepecho doble 2x3"),
           ((muñecos_inf(v)[0], 0.9), ((a + b) / 2, 0.45), "muñecos 2x3 c/40"),
           ((b + 0.3 if b + 0.3 < s1 else s1 - 0.05, 0.85), (s1 - 0.2, 0.55) if v["muro"] == "frente" else (s1 - 0.05, 0.4), "cadeneta")]
    ax.text((a + b) / 2, z1 + hd / 2, f'DINTEL {v["dintel"]} de canto', ha="center", va="center",
            fontsize=7.5, color="white", weight="bold", zorder=6)
    lab.append(((a + 0.02, tope(a) - 0.03), (a - 0.40, 2.62) if v["muro"] == "der" else (a - 0.35, 2.75),
                "muñecos sup." if v["muro"] == "der" else "calce 2x3"))
    for p, t, tx in lab:
        ax.annotate(tx, p, t, fontsize=7, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6), bbox=dict(fc="white", ec="none", pad=0.5), zorder=8)
    ax.set_xlim(s0 - 0.6, s1 + 0.5); ax.set_ylim(-0.45, 3.05)
    if v["muro"] == "frente":
        ax.invert_xaxis()   # vista desde afuera: el extremo de la terraza queda a la derecha
    ax.set_title(titulo_e, fontsize=10, weight="bold")


VUELO_PL = 0.08     # la plancha sobresale 8 cm desde la punta del tijeral (llega a >½ de la canal)

def detalle_canal(ax):
    ax.set_aspect("equal"); ax.axis("off")
    ye = borde_techo(L)
    y0 = ye - 0.45
    # tijeral (punta cortada a plomo)
    ax.add_patch(Polygon([(y0, zt(y0)), (ye, zt(ye)), (ye, zt(ye) - H_T), (y0, zt(y0) - H_T)], fc=MADERA, ec="k"))
    # costaneras
    for yr in [f for f in FILAS if f > y0]:
        ax.add_patch(Rectangle((yr - 0.02, zt(yr)), 0.041, 0.041, fc="#c8a165", ec="k"))
    # tapacán 1x8
    zt_tap = zt(ye) + 0.041
    ax.add_patch(Rectangle((ye, zt_tap - 0.185), 0.019, 0.185, fc="#b8860b", ec="k"))
    # plancha (sobre costaneras) con vuelo y goterón
    zp = lambda y: zt(y) + 0.041 + 0.004
    yf = ye + VUELO_PL
    ax.plot([y0, yf], [zp(y0), zp(yf)], color="#555", lw=3)
    ax.plot([yf, yf + 0.006], [zp(yf), zp(yf) - 0.012], color="#555", lw=3)
    # canaleta 110 mm (perfil) colgada del tapacán con gancho
    yc0, yc1 = ye + 0.019, ye + 0.019 + 0.11
    zr = zp(yf) - 0.035
    perfil = [(yc0, zr + 0.01), (yc0, zr - 0.05), (yc0 + 0.02, zr - 0.075), (yc1 - 0.02, zr - 0.075),
              (yc1, zr - 0.04), (yc1, zr - 0.005), (yc1 - 0.012, zr - 0.005)]
    ax.add_patch(Polygon(perfil[:6], closed=False, fill=False, ec="#7b4a1e", lw=3))
    ax.plot(*zip(*perfil[5:]), color="#7b4a1e", lw=3)
    ax.plot([yc0 - 0.005, yc0, yc1 + 0.004, yc1 + 0.004], [zr - 0.06, zr + 0.012, zr + 0.012, zr - 0.005],
            color="#333", lw=1.5)                                                      # gancho
    ax.plot([ye - 0.03, ye + 0.03], [zr - 0.03] * 2, color="k", lw=1.5)               # tornillo
    # agua
    ax.annotate("", (yc0 + 0.05, zr - 0.06), (yf - 0.01, zp(yf) - 0.02),
                arrowprops=dict(arrowstyle="->", color="#2c7fb8", lw=1.5, ls="--"))
    # cotas
    ax.annotate("", (yc0, zr - 0.13), (yc1, zr - 0.13), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text((yc0 + yc1) / 2, zr - 0.155, "canal 11 cm", ha="center", fontsize=7.5)
    ax.plot([(yc0 + yc1) / 2] * 2, [zr - 0.12, zr + 0.06], color="#c0392b", lw=0.8, ls=":")
    ax.text((yc0 + yc1) / 2 + 0.005, zr + 0.075, "mitad", fontsize=7, color="#c0392b")
    ax.annotate("", (ye, zp(ye) + 0.09), (yf, zp(yf) + 0.09), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text((ye + yf) / 2, zp(ye) + 0.11, f"vuelo {VUELO_PL * 100:.0f} cm", ha="center", fontsize=7.5)
    notas = [((ye - 0.2, zt(ye - 0.2) - 0.07), (ye - 0.33, zt(ye) - 0.27), "tijeral 2x6½\"\n(punta a plomo)"),
             ((ye + 0.01, zt_tap - 0.15), (ye - 0.10, zt(ye) - 0.33), "tapacán 1x8"),
             ((ye - 0.30, zp(ye - 0.30)), (ye - 0.33, zt(ye) + 0.22), "plancha trapezoidal"),
             ((ye + 0.02, zr - 0.03), (ye + 0.30, zr - 0.20), "gancho PVC c/50 cm\n+ tornillo 8x2\" al tapacán"),
             ((yc1, zr - 0.04), (ye + 0.34, zr - 0.02), "canaleta PVC café\n110 mm, pend. 0,5 %\nhacia la bajada"),
             ((yf + 0.004, zp(yf) - 0.006), (ye + 0.30, zp(yf) + 0.12),
              "la plancha llega a MÁS\nde la mitad de la canal\n(con goterón)")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=7.5, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6), bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(ye - 0.50, ye + 0.48); ax.set_ylim(zt(ye) - 0.40, zt(ye) + 0.30)
    ax.set_title("DETALLE 5 · canaleta en el alero (borde bajo)", fontsize=10, weight="bold")


# ---------------- Lámina 7: FACHADA LATERAL BODEGA ----------------
def fachada_lateral(ax):
    ax.set_aspect("equal"); ax.axis("off")
    v = VENTANAS[0]
    ye = borde_techo(L)
    wtop = lambda y: zt(y) - H_T
    # casa existente (a la izquierda)
    ax.add_patch(Rectangle((-1.3, -0.15), 1.3, Z_EX + 0.15, fc="#e6e6e6", ec="k", hatch="//", lw=0.8))
    zb = lambda y: Z_EX + 0.1356 * y
    ax.add_patch(Polygon([(-1.3, zb(-1.3)), (0.45, zb(0.45)), (0.45, zb(0.45) + 0.05), (-1.3, zb(-1.3) + 0.05)],
                         fc="#7f8c8d", ec="k"))
    ax.text(-0.65, 1.3, "CASA\nEXISTENTE", ha="center", fontsize=9, weight="bold", bbox=dict(fc="white", ec="none"))
    # piso / viga de piso y pilotes
    ax.add_patch(Rectangle((0, -0.20), D, 0.20, fc="#a0784a", ec="k"))
    for yp in (0.15, D - 0.15):
        ax.add_patch(Rectangle((yp - 0.06, -0.75), 0.12, 0.55, fc="#8d6e4a", ec="k"))
    ax.plot([-1.4, ye + 0.6], [-0.75, -0.75], color="#6b8e23", lw=1.5, ls="--")
    ax.text(-1.35, -0.70, "terreno (referencial)", ha="left", fontsize=7, color="#6b8e23")
    # muro lateral: SmartPanel (0..2,0) y ochavo (2,0..2,5) en escorzo
    def panel(ya, yb, fc):
        pts = [(ya, -0.20), (yb, -0.20), (yb, wtop(yb)), (ya, wtop(ya))]
        ax.add_patch(Polygon(pts, fc=fc, ec="k", lw=1))
        y = ya + 0.08
        while y < yb - 0.01:
            ax.plot([y, y], [-0.20, wtop(y)], color="#c9b79c", lw=0.5, zorder=2)
            y += 0.08
    panel(0.0, Y0, "#e9dcc6")
    panel(Y0, D, "#d8c8ad")
    ax.text((Y0 + D) / 2, 0.9, "destaje\n(atrás)", ha="center", fontsize=7, color="#5a4a30")
    # esquineros
    for y in (0.0, Y0 - 0.035, D - 0.07):
        ax.add_patch(Rectangle((y, -0.20), 0.07, wtop(y) + 0.20, fc="#b8956a", ec="k", lw=0.6, zorder=3))
    # junta horizontal (franja superior con cortagotera)
    ax.plot([0.07, D - 0.07], [2.44 - 0.20, 2.44 - 0.20], color="#666", lw=1.2, ls=(0, (6, 2)), zorder=3)
    # ventana V1
    a, b = v["a"], v["b"]; z0, z1 = VEN_ALTO
    ax.add_patch(Rectangle((a, z0), b - a, z1 - z0, fc="#9aa5ab", ec="k", zorder=4))
    ax.add_patch(Rectangle((a + 0.03, z0 + 0.03), b - a - 0.06, z1 - z0 - 0.06, fc="#bfe3f5", ec="#2c7fb8", zorder=5))
    ax.plot([a + 0.25, a + 0.45], [z0 + 0.06, z1 - 0.06], color="white", lw=1.5, zorder=6)
    ax.plot([b - 0.40, b - 0.25], [z0 + 0.06, z1 - 0.06], color="white", lw=1.5, zorder=6)
    ax.add_patch(Rectangle((a - 0.04, z1), b - a + 0.08, 0.015, fc="#5f6b73", ec="k", zorder=6))   # botaguas
    ax.add_patch(Rectangle((a - 0.03, z0 - 0.02), b - a + 0.06, 0.02, fc="#5f6b73", ec="k", zorder=6))  # alféizar
    # tijeral T15 + remate lateral (hojalatería)
    ax.add_patch(Polygon([(TE_V, zt(TE_V)), (ye, zt(ye)), (ye, zt(ye) - H_T), (TE_V, zt(TE_V) - H_T)],
                         fc=MADERA, ec="k", zorder=3))
    ax.add_patch(Polygon([(0.0, zt(0) + 0.08), (ye + 0.02, zt(ye + 0.02) + 0.08),
                          (ye + 0.02, zt(ye + 0.02) - 0.13), (0.0, zt(0) - 0.13)], fc="#7d8a91", ec="k", zorder=4))
    # tapacán (canto) y canaleta (tapa lateral) + bajada
    ax.add_patch(Rectangle((ye, zt(ye) + 0.041 - 0.185), 0.019, 0.185, fc="#b8860b", ec="k", zorder=5))
    yc0, yc1 = ye + 0.019, ye + 0.129
    zr = zt(ye + VUELO_PL) + 0.045 - 0.035
    ax.add_patch(Polygon([(yc0, zr + 0.01), (yc1, zr), (yc1, zr - 0.04), (yc1 - 0.02, zr - 0.075),
                          (yc0 + 0.02, zr - 0.075), (yc0, zr - 0.05)], fc="#7b4a1e", ec="k", zorder=6))
    yb_ = (yc0 + yc1) / 2
    ax.add_patch(Rectangle((yb_ - 0.04, -0.70), 0.08, zr - 0.075 + 0.70, fc="#8a5a2b", ec="k", zorder=5))
    for zz in (2.0, 1.0, 0.1):
        ax.add_patch(Rectangle((yb_ - 0.05, zz), 0.10, 0.03, fc="#5c3a1a", ec="k", zorder=6))
    ax.add_patch(Polygon([(yb_ - 0.04, -0.70), (yb_ + 0.04, -0.70), (yb_ + 0.15, -0.74), (yb_ + 0.15, -0.66)],
                         fc="#8a5a2b", ec="k", zorder=6))
    # cotas
    def cv(x, za, zb_, t, side=1):
        ax.annotate("", (x, za), (x, zb_), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(x + 0.05 * side, (za + zb_) / 2, t, va="center", ha="left" if side > 0 else "right",
                fontsize=8, rotation=90)
    def ch(xa, xb, z, t):
        ax.annotate("", (xa, z), (xb, z), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text((xa + xb) / 2, z - 0.09, t, ha="center", fontsize=8)
    cv(ye + 0.45, 0, wtop(D), f"{wtop(D):.2f}")
    cv(0.25, 0, wtop(0), f"{wtop(0):.2f}")
    cv(a - 0.12, 0, z0, f"{z0:.2f}", side=-1)
    cv(b + 0.12, 0, z1, f"{z1:.2f}")
    ch(0, a, 0.75, f"{a:.2f}"); ch(a, b, 0.75, f"{b - a:.2f}"); ch(b, Y0, 0.75, f"{Y0 - b:.2f}")
    ch(0, D, -0.95, "2,50 (bodega)"); ch(D, ye, -0.95, f"alero {ye - D:.2f}")
    # rótulos
    notas = [(((a + b) / 2, z1 + 0.01), ((a + b) / 2, 2.85), "botaguas zincalum"),
             (((a + b) / 2, (z0 + z1) / 2), (1.0, 1.35), "V1 ventana aluminio 150 x 30"),
             ((1.6, zt(1.6) - 0.05), (1.75, 3.10), "remate lateral zincalum (DET. 4)"),
             ((0.6, 0.5), (0.9, 0.35), "SmartPanel (ranurado c/8 cm), pintado"),
             ((Y0, 1.2), (1.75, 0.45), "esquinero"),
             ((yb_, 1.4), (ye + 0.5, 1.6), "bajada PVC café Ø80\ncon abrazaderas"),
             ((yb_, zr - 0.04), (ye + 0.55, 2.75), "canaleta PVC café\n(tapa lateral)"),
             ((ye + 0.01, zt(ye) - 0.07), (ye + 0.40, 2.30), "tapacán 1x8"),
             ((0.03, 2.30), (-0.40, 2.62), "forro contra\nmuro (DET. 3)")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=7.5, ha="center", va="center", zorder=9,
                    arrowprops=dict(arrowstyle="-", lw=0.6), bbox=dict(fc="white", ec="none", pad=0.6))
    ax.set_xlim(-1.5, ye + 1.0); ax.set_ylim(-1.1, 3.25)
    ax.set_title("FACHADA LATERAL DE LA BODEGA (lado opuesto a la puerta) — vista desde afuera",
                 fontsize=11, weight="bold")


# ---------------- Lámina 8: FACHADA PRINCIPAL (muro largo, frente a la casa) ----------------
def fachada_frente(ax):
    ax.set_aspect("equal"); ax.axis("off")
    v = VENTANAS[1]
    wtop = lambda y: zt(y) - H_T
    xs = [i / 40 * L for i in range(41)]
    # casa existente al fondo
    ax.add_patch(Rectangle((-0.3, -0.20), L + 0.6, Z_EX + 0.20, fc="#eeeeee", ec="#999", lw=0.8, zorder=0))
    ax.plot([-0.4, L + 0.4], [Z_EX + 0.07, Z_EX + 0.07], color="#7f8c8d", lw=5, zorder=0)
    ax.text(2.4, 2.7, "muro casa existente (al fondo)", ha="center", fontsize=8, color="#777", zorder=1)
    # piso y pilotes
    ax.add_patch(Rectangle((0, -0.20), L, 0.20, fc="#a0784a", ec="k", zorder=2))
    for xp in (0.15, XB / 2, XB + 0.15, L - 0.5):
        ax.add_patch(Rectangle((xp - 0.06, -0.75), 0.12, 0.55, fc="#8d6e4a", ec="k", zorder=1))
    ax.plot([-0.5, L + 0.6], [-0.75, -0.75], color="#6b8e23", lw=1.5, ls="--")
    # terraza: pilares y viga sobre la diagonal
    for px, py in PILARES:
        ax.add_patch(Rectangle((px - 0.045, 0), 0.09, wtop(py) - 0.138, fc="#6d5a45", ec="k", zorder=3))
    vx = [0, XB]; vy = [D, D]
    top = [wtop(y) for y in vy]
    ax.add_patch(Polygon(list(zip(vx, top)) + list(zip(vx[::-1], [t - 0.138 for t in top[::-1]])),
                         fc="#c9a46a", ec="k", zorder=3))
    ax.text(1.9, 0.9, "TERRAZA TECHADA", ha="center", fontsize=11, weight="bold", color="#6b4f1d", zorder=4)
    # bodega: muro frente + ochavo (escorzo)
    def panel(xa, xb, ya, yb, fc):
        pts = [(xa, -0.20), (xb, -0.20), (xb, wtop(yb)), (xa, wtop(ya))]
        ax.add_patch(Polygon(pts, fc=fc, ec="k", lw=1, zorder=4))
        x = xa + 0.08
        while x < xb - 0.01:
            t = (x - xa) / (xb - xa)
            ax.plot([x, x], [-0.20, wtop(ya + (yb - ya) * t)], color="#c9b79c", lw=0.5, zorder=4)
            x += 0.08
    panel(XB, XN, D, D, "#e9dcc6")
    panel(XN, L, Y0, Y0, "#d8c8ad")
    for x in (XB, XN - 0.035, L - 0.07):
        ax.add_patch(Rectangle((x, -0.20), 0.07, 2.56, fc="#b8956a", ec="k", lw=0.6, zorder=5))
    ax.plot([XB + 0.07, L - 0.07], [2.24] * 2, color="#666", lw=1.2, ls=(0, (6, 2)), zorder=5)
    # ventana V2
    a, b = v["a"], v["b"]; z0, z1 = VEN_ALTO
    ax.add_patch(Rectangle((a, z0), b - a, z1 - z0, fc="#9aa5ab", ec="k", zorder=6))
    ax.add_patch(Rectangle((a + 0.03, z0 + 0.03), b - a - 0.06, z1 - z0 - 0.06, fc="#bfe3f5", ec="#2c7fb8", zorder=7))
    for xx in (a + 0.4, b - 0.6):
        ax.plot([xx, xx + 0.18], [z0 + 0.06, z1 - 0.06], color="white", lw=1.5, zorder=8)
    ax.add_patch(Rectangle((a - 0.04, z1), b - a + 0.08, 0.015, fc="#5f6b73", ec="k", zorder=8))
    ax.add_patch(Rectangle((a - 0.03, z0 - 0.02), b - a + 0.06, 0.02, fc="#5f6b73", ec="k", zorder=8))
    ax.text((XB + L) / 2, 0.9, "BODEGA", ha="center", fontsize=11, weight="bold", color="#1f4e79", zorder=6)
    # alero: tapacán 1x8 y canaleta a lo largo del borde
    ze = [zt(borde_techo(x)) for x in xs]
    ax.add_patch(Polygon([(x, z + 0.041) for x, z in zip(xs, ze)] + [(x, z + 0.041 - 0.185) for x, z in zip(xs[::-1], ze[::-1])],
                         fc="#b8860b", ec="k", zorder=6))
    zc = [zt(borde_techo(x) + VUELO_PL) + 0.045 - 0.035 for x in xs]
    ax.add_patch(Polygon([(x, z + 0.01) for x, z in zip(xs, zc)] + [(x, z - 0.075) for x, z in zip(xs[::-1], zc[::-1])],
                         fc="#7b4a1e", ec="k", zorder=7))
    ax.plot(xs, [z + 0.06 for z in ze], color="#555", lw=2.5, zorder=6)          # canto de la plancha
    # remates laterales (cantos)
    for x in (0, L):
        ax.add_patch(Rectangle((x - 0.02, ze[0 if x == 0 else -1] - 0.13), 0.04, 0.24, fc="#7d8a91", ec="k", zorder=8))
    # bajada en la esquina de la bodega
    zb0 = zc[-1] - 0.075
    ax.add_patch(Rectangle((L - 0.04, -0.70), 0.08, zb0 + 0.70, fc="#8a5a2b", ec="k", zorder=8))
    for zz in (2.0, 1.0, 0.1):
        ax.add_patch(Rectangle((L - 0.05, zz), 0.10, 0.03, fc="#5c3a1a", ec="k", zorder=9))
    # cotas (vista desde afuera: eje invertido)
    def ch(xa, xb, z, t):
        ax.annotate("", (xa, z), (xb, z), arrowprops=dict(arrowstyle="<->", lw=0.7), zorder=11)
        ax.text((xa + xb) / 2, z - 0.10, t, ha="center", fontsize=8, zorder=11,
                bbox=dict(fc="white", ec="none", pad=0.3))
    def cv(x, za, zb_, t):
        ax.annotate("", (x, za), (x, zb_), arrowprops=dict(arrowstyle="<->", lw=0.7), zorder=11)
        ax.text(x - 0.05, (za + zb_) / 2, t, va="center", fontsize=8, rotation=90, zorder=11,
                bbox=dict(fc="white", ec="none", pad=0.3))
    ch(0, L, -1.15, "8,25"); ch(0, XB, -0.95, "terraza 4,75"); ch(XB, L, -0.95, "bodega 3,50")
    ch(XB, a, 0.55, f"{a - XB:.2f}"); ch(a, b, 0.55, f"V2 {b - a:.2f}"); ch(b, XN, 0.55, f"{XN - b:.2f}")
    cv(XB - 0.15, 0, wtop(D), f"{wtop(D):.2f}")
    cv(a - 0.12, 0, z0, f"{z0:.2f}"); cv(b + 0.15, 0, z1, f"{z1:.2f}")
    notas = [(((a + b) / 2, (z0 + z1) / 2), ((a + b) / 2, 1.35), "V2 ventana aluminio 200 x 30"),
             (((a + b) / 2, z1 + 0.01), ((a + b) / 2 + 0.6, 3.10), "botaguas zincalum"),
             ((5.2, 0.3), (5.6, 0.2), "SmartPanel pintado"),
             ((L, 1.5), (L + 0.45, 1.0), "bajada PVC café Ø80"),
             ((6.0, zc[29] - 0.03), (6.0, 3.10), "canaleta PVC café"),
             ((2.6, ze[13] - 0.05), (2.6, 3.10), "tapacán 1x8"),
             ((PILARES[1][0], 1.2), (PILARES[1][0] - 0.6, 1.5), "pilar 4x4"),
             ((1.2, top[1] - 0.07), (1.6, 1.75), "viga 2x6 doble"),
             ((0, ze[0]), (-0.35, 3.10), "remate lateral")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=7.5, ha="center", va="center", zorder=10,
                    arrowprops=dict(arrowstyle="-", lw=0.6), bbox=dict(fc="white", ec="none", pad=0.6))
    ax.set_xlim(-0.7, L + 0.8); ax.set_ylim(-1.35, 3.25)
    ax.invert_xaxis()
    ax.set_title("FACHADA PRINCIPAL (muro largo, frente opuesto a la casa) — vista desde afuera",
                 fontsize=11, weight="bold")


# ---------------- Lámina 9: DETALLE DE TIJERALES ----------------
ANG_PEND = math.degrees(math.atan(PEND))                       # ~5,7°
ANG_BISEL = 0.0          # ~23,6° (borde diagonal en planta)
Y_INI = TE_V                                                    # cara de la tabla 1x10 apernada al muro
def largo_corte(x):
    return (borde_techo(x) - Y_INI) * math.sqrt(1 + PEND ** 2)
def apoyo_ext(x):
    return prof(x)                                              # muro bodega o viga de terraza

def tijeral_tipo_a(ax):
    ax.set_aspect("equal"); ax.axis("off")
    ye = borde_techo(L)
    # casa + viga 2x8 + soporte Simpson
    ax.add_patch(Rectangle((-0.30, 2.0), 0.30, Z_EX - 2.0, fc="#e6e6e6", ec="k", hatch="//"))
    zl = zt(0) - H_T; zv = zl
    ax.add_patch(Rectangle((0, zv), TE_V, H_V, fc="#c0392b", ec="k"))
    ax.add_patch(Rectangle((0.041, zl - 0.004), 0.06, 0.13, fill=False, ec="#333", lw=2, zorder=6))
    # muro bodega (2x3 + solera doble) bajo el apoyo exterior
    zw = zt(D) - H_T
    ax.add_patch(Rectangle((D - 0.065, 1.95), 0.065, zw - 0.082 - 1.95, fc="#d9e8f5", ec="#1f4e79"))
    ax.add_patch(Rectangle((D - 0.065, zw - 0.082), 0.065, 0.082, fc="#9dbbd9", ec="#1f4e79"))
    ax.add_patch(Rectangle((D - 0.09, zw - 0.07), 0.05, 0.15, fc="#333", ec="k", zorder=6))   # H3
    # tijeral
    ax.add_patch(Polygon([(Y_INI, zt(Y_INI)), (ye, zt(ye)), (ye, zt(ye) - H_T), (Y_INI, zt(Y_INI) - H_T)],
                         fc=MADERA, ec="k", lw=1.5, zorder=4))
    for yr in FILAS:
        ax.add_patch(Rectangle((yr - 0.02, zt(yr)), 0.041, 0.041, fc="#c8a165", ec="k", zorder=5))
    ax.plot([0, ye + VUELO_PL], [zt(0) + 0.05, zt(ye + VUELO_PL) + 0.05], color="#555", lw=2.5, zorder=5)
    ax.add_patch(Rectangle((ye, zt(ye) + 0.041 - 0.185), 0.019, 0.185, fc="#b8860b", ec="k", zorder=5))
    # cotas
    def ch(ya, yb, z, t):
        ax.annotate("", (ya, z), (yb, z), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text((ya + yb) / 2, z - 0.07, t, ha="center", fontsize=8.5, bbox=dict(fc="white", ec="none", pad=0.3))
    ch(Y_INI, D, 1.85, f"apoyo a apoyo {D - Y_INI:.2f} (horizontal)")
    ch(D, ye, 1.85, f"alero {ye - D:.2f}")
    ch(Y_INI, ye, 1.65, f"proyección horizontal {ye - Y_INI:.2f}")
    # largo de corte (a lo largo de la pieza)
    ax.annotate("", (Y_INI, zt(Y_INI) + 0.30), (ye, zt(ye) + 0.30), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#8b4513"))
    ax.text((Y_INI + ye) / 2, zt((Y_INI + ye) / 2) + 0.20, f"LARGO DE CORTE {largo_corte(L):.2f} m (pieza 2x6½\" x 3,20)",
            ha="center", fontsize=9.5, weight="bold", color="#8b4513", rotation=-ANG_PEND)
    # pendiente
    ax.plot([1.0, 2.0, 2.0, 1.0], [2.30, 2.30, 2.30 - PEND, 2.30], color="#2c7fb8", lw=1)
    ax.text(1.5, 2.32, "100", ha="center", fontsize=7.5, color="#2c7fb8")
    ax.text(2.03, 2.23, f"{PEND * 100:.0f}  (pendiente {ANG_PEND:.1f}°)", fontsize=7.5, color="#2c7fb8")
    notas = [((0.07, zl + 0.02), (0.45, 2.15), "soporte Simpson 2x6 ZMAX\n(muro casa)"),
             ((0.02, zv + 0.03), (-0.15, 1.90), "tabla 1x10\napernada"),
             ((Y_INI, zt(Y_INI) - 0.07), (-0.13, 3.07), "corte a plomo\n(ver detalle)"),
             ((D - 0.065, zw - 0.02), (D - 0.45, 2.10), "H3 uno por lado"),
             ((D - 0.03, 2.1), (D + 0.25, 2.0), "muro bodega 2x3\n(o viga terraza)"),
             ((ye - 0.01, zt(ye) - 0.07), (ye + 0.25, 2.55), "corte a plomo\n+ tapacán 1x8"),
             ((FILAS[6], zt(FILAS[6]) + 0.04), (2.75, 3.07), "costaneras 2x2 c/40")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=7.5, ha="center", va="center", zorder=9,
                    arrowprops=dict(arrowstyle="-", lw=0.6), bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(-0.35, ye + 0.5); ax.set_ylim(1.55, 3.15)
    ax.set_title("TIJERAL TIPO (los 15 iguales) · 2x6½\" pino IPV c/60 cm — elevación", fontsize=10, weight="bold")

def corte_plomo(ax):
    ax.set_aspect("equal"); ax.axis("off")
    h = H_T; off = h * PEND
    # pieza vista de costado, eje inclinado
    ang = math.radians(-ANG_PEND)
    def R(x, z):
        return (x * math.cos(ang) - z * math.sin(ang), x * math.sin(ang) + z * math.cos(ang))
    # pieza en coordenadas propias (x a lo largo, z perpendicular)
    largo = 0.40
    # la cara vertical (plomo) en coords globales: x = 0
    pts = [(0, 0), (0, h / math.cos(math.radians(ANG_PEND)))]
    top0 = pts[1][1]
    ax.add_patch(Polygon([(0, 0), (0, top0), (largo, top0 - largo * PEND), (largo, -largo * PEND)],
                         fc=MADERA, ec="k", lw=1.5))
    ax.plot([0, 0], [-0.04, top0 + 0.04], color="#c0392b", lw=1, ls="--")
    ax.text(-0.012, top0 + 0.055, "vertical (a plomo)", fontsize=7.5, color="#c0392b", ha="center")
    # escuadra de la pieza
    ax.plot([0, off], [top0, top0 - off * PEND + 0], color="k", lw=0.5)
    ax.plot([off, off], [-off * PEND, top0 - off * PEND], color="#2c7fb8", lw=1, ls=":")
    ax.annotate("", (0, -0.03), (off, -0.03), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(off / 2, -0.055, f"{off * 1000:.0f} mm", ha="center", fontsize=8)
    ax.text(0.20, 0.06, f"2x6½\" ({h * 1000:.0f} mm)", fontsize=8)
    ax.text(0.03, top0 + 0.12, f"Marcar la escuadra y correr {off * 1000:.0f} mm\n(= ángulo de {ANG_PEND:.1f}°) para que el\ncorte quede vertical una vez colocado.",
            fontsize=8, va="bottom")
    ax.set_xlim(-0.12, 0.45); ax.set_ylim(-0.10, 0.42)
    ax.set_title("DETALLE · corte a plomo (ambos extremos)", fontsize=10, weight="bold")

def tijerales_tipo_b(ax):
    """Planta de tijerales y apoyos (techo rectangular)."""
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((-0.3, -0.35), L + 0.6, 0.35, fc="#e6e6e6", ec="k", hatch="//"))
    ax.add_patch(Polygon([(0, 0), (0, D + ALERO), (L, D + ALERO), (L, 0)], fc="#fff6d8", ec="#b8860b", lw=1.5, ls="-."))
    ax.add_patch(Polygon(piso, fc="#f3e3c7", ec="k"))
    ax.add_patch(Polygon([(XB, 0), (L, 0), (L, Y0), (XN, Y0), (XN, D), (XB, D)], fc="#d9e8f5", ec="#1f4e79", lw=2))
    ax.plot([0, L], [0.02, 0.02], color="#c0392b", lw=4)
    vx, vy = zip(*VIGA_T); ax.plot(vx, vy, color="#555", lw=3, ls="--")
    for px, py in PILARES:
        ax.add_patch(Rectangle((px - 0.06, py - 0.06), 0.12, 0.12, fc="k"))
    for n_, x, ye, lg in tij:
        ax.plot([x, x], [Y_INI, ye], color="#8b4513", lw=2.5)
        ax.text(x, ye + 0.15, n_, ha="center", fontsize=7, color="#8b4513", weight="bold")
    ax.text(XN + NW / 2, D + 0.15, "destaje", ha="center", fontsize=7.5, color="#6b4f1d")
    ax.text(XB / 2 + 0.3, 1.0, "TERRAZA", ha="center", fontsize=10, weight="bold", color="#6b4f1d")
    ax.text((XB + L) / 2, 1.0, "BODEGA", ha="center", fontsize=10, weight="bold", color="#1f4e79")
    ax.text(0.1, D + ALERO + 0.55, "rojo: tabla 1x10 + soporte Simpson · gris: viga 2x6 doble / muro bodega · ■ pilar 4x4",
            fontsize=7.5)
    ax.set_xlim(-0.4, L + 0.3); ax.set_ylim(-0.45, D + ALERO + 0.75); ax.invert_yaxis()
    ax.set_title("PLANTA DE TIJERALES Y APOYOS · techo rectangular, 15 tijerales iguales", fontsize=10, weight="bold")

def tabla_corte(ax):
    ax.axis("off")
    filas = []
    for n_, x, ye, lg in tij:
        tipo = "A"
        lc = largo_corte(x)
        ap = apoyo_ext(x)
        donde = "muro" if x > XB - 1e-6 else "viga"
        punta = "plomo" + (f" (vuela {D + ALERO - Y0:.2f})" if prof(x) < D else "")
        filas.append([n_, tipo, f"{x:.2f}", f"{lc:.2f}", f"{ap:.2f} ({donde})", punta, f"{3.20 - lc:.2f}"])
    t = ax.table(cellText=filas, colLabels=["Tijeral", "Tipo", "Posición", "Largo corte",
                                            "Apoyo ext. a", "Punta", "Sobrante"],
                 loc="upper center", cellLoc="center", colWidths=[0.10, 0.08, 0.12, 0.14, 0.18, 0.22, 0.14])
    ax.text(0.0, 0.08, ("Medidas en metros. 'Apoyo ext. a' = distancia desde el muro de la casa al muro de bodega o viga de terraza.\n"
                        f"Los 15 tijerales son iguales ({tij[-1][3]:.2f} m). T15, en el destaje de la bodega, apoya a {Y0:.2f} m y vuela {D + ALERO - Y0:.2f} m.\n"
                        "Junto a la casa: punta a plomo, de tope en el soporte Simpson 2x6. En el apoyo exterior: sin rebaje, 2 H3."),
            fontsize=8, va="top", transform=ax.transAxes)
    t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.15)
    ax.set_title("TABLA DE CORTE · 15 tijerales 2x6½\" x 3,20 (junto a la casa siempre corte a plomo, de tope en soporte Simpson)",
                 fontsize=9.5, weight="bold")


# ---------------- Lámina 10: MEDIDAS REALES · pendiente y corte del tijeral ----------------
R_H0 = 2.63      # parte de abajo del tijeral en el muro de la cabaña (medido)
R_TAB = 0.23     # tabla 1x10 cepillada 4 caras (alto)
R_TE = 0.019     # espesor tabla 1x10
R_ALERO_EX = 0.17  # de la tabla al alero existente (medido)
R_A = 2.48       # muro cabaña -> cara exterior del apoyo (medido)
R_H = 0.165      # tijeral 2x6½"
R_P = 0.12       # pendiente elegida
R_ALERO = 0.40
r_zb = lambda y: R_H0 - R_P * y                   # parte de abajo del tijeral
r_zt = lambda y: R_H0 + R_H / math.cos(math.atan(R_P)) - R_P * y   # parte de arriba (medida a plomo)

def corte_real(ax):
    ax.set_aspect("equal"); ax.axis("off")
    ye = R_A + R_ALERO
    z_ex = R_H0 + R_TAB + R_ALERO_EX
    ax.add_patch(Rectangle((-0.35, 0), 0.35, z_ex, fc="#e6e6e6", ec="k", hatch="//"))
    ax.plot([-0.6, 0.55], [z_ex + 0.08, z_ex - 0.04], color="#555", lw=5)
    ax.text(-0.17, 1.4, "CABAÑA", rotation=90, ha="center", va="center", fontsize=9, weight="bold",
            bbox=dict(fc="white", ec="none"))
    ax.add_patch(Rectangle((0, -0.15), R_A, 0.15, fc="#a0784a", ec="k"))
    ax.add_patch(Rectangle((0, R_H0), R_TE, R_TAB, fc="#c0392b", ec="k", zorder=4))
    ax.add_patch(Polygon([(R_TE, r_zb(R_TE)), (ye, r_zb(ye)), (ye, r_zt(ye)), (R_TE, r_zt(R_TE))], fc=MADERA, ec="k", zorder=3))
    for yr in [0.06 + 0.4 * k for k in range(8)]:
        ax.add_patch(Rectangle((yr - 0.02, r_zt(yr)), 0.041, 0.041, fc="#c8a165", ec="k", zorder=4))
    ax.plot([0, ye + 0.08], [r_zt(0) + 0.05, r_zt(ye + 0.08) + 0.05], color="#555", lw=2.5, zorder=5)
    ax.add_patch(Rectangle((ye, r_zt(ye) + 0.041 - 0.185), 0.019, 0.185, fc="#b8860b", ec="k", zorder=5))
    ht = r_zb(R_A)
    ax.add_patch(Rectangle((R_A - 0.065, 0), 0.065, ht, fc="#d9e8f5", ec="#1f4e79", lw=1.5))
    ax.add_patch(Rectangle((R_A - 0.09, ht - 0.06), 0.05, 0.14, fc="#333", ec="k", zorder=6))
    def cv(x, za, zb, t, lado=-1):
        ax.annotate("", (x, za), (x, zb), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(x + 0.05 * lado, (za + zb) / 2, t, ha="right" if lado < 0 else "left", va="center", fontsize=9,
                weight="bold", bbox=dict(fc="white", ec="none", pad=0.3))
    def ch(ya, yb, z, t):
        ax.annotate("", (ya, z), (yb, z), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text((ya + yb) / 2, z - 0.12, t, ha="center", fontsize=9, bbox=dict(fc="white", ec="none", pad=0.3))
    cv(-0.45, 0, R_H0, "2,63", -1)
    cv(-0.45, R_H0, R_H0 + R_TAB, "0,23", -1)
    cv(-0.45, R_H0 + R_TAB, z_ex, "0,17", -1)
    cv(R_A + 0.12, 0, ht, f"{ht:.2f}".replace(".", ","), 1)
    ch(0, R_A, -0.35, "2,48"); ch(R_A, ye, -0.35, "alero 0,40")
    ax.plot([0.5, 1.5, 1.5, 0.5], [r_zt(0.5) + 0.35, r_zt(0.5) + 0.35, r_zt(0.5) + 0.23, r_zt(0.5) + 0.35], color="#2c7fb8", lw=1.2)
    ax.text(1.0, r_zt(0.5) + 0.38, "100", ha="center", fontsize=8, color="#2c7fb8")
    ax.text(1.55, r_zt(0.5) + 0.27, f"12  →  pendiente 12 % ({math.degrees(math.atan(R_P)):.1f}°)", fontsize=9,
            color="#2c7fb8", weight="bold")
    notas = [((R_TE / 2, R_H0 + 0.18), (0.55, 3.32), "tabla 1x10 cep. 4/c\napernada al muro"),
             ((1.2, r_zb(1.2) + 0.08), (1.4, 2.05), "tijeral 2x6½\"\nlargo 2,88 m"),
             ((R_A - 0.065, ht - 0.03), (R_A - 0.55, 1.7), "H3 uno por lado"),
             ((R_A - 0.03, 1.0), (R_A - 0.55, 1.0), f"TABIQUE OPUESTO\nalto {ht:.2f} m\n(bajo el tijeral)".replace(".", ","))]
    for p, tt, tx in notas:
        ax.annotate(tx, p, tt, fontsize=8.5, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.6),
                    bbox=dict(fc="white", ec="none", pad=0.5), zorder=8)
    ax.set_xlim(-0.95, ye + 0.6); ax.set_ylim(-0.55, 3.55)
    ax.set_title("CORTE CON MEDIDAS REALES · pendiente óptima 12 %", fontsize=11, weight="bold")

def detalle_corte_real(ax):
    ax.set_aspect("equal"); ax.axis("off")
    # muro, tabla, soporte y punta del tijeral (escala grande)
    ax.add_patch(Rectangle((-0.12, R_H0 - 0.12), 0.12, 0.45, fc="#e6e6e6", ec="k", hatch="//"))
    ax.add_patch(Rectangle((0, R_H0), R_TE, R_TAB, fc="#c0392b", ec="k"))
    y1 = 0.30
    seat = 0.045; dz = seat * R_P
    zs = r_zb(R_TE)                     # nivel del asiento del soporte
    pts = [(R_TE, r_zt(R_TE)), (y1, r_zt(y1)), (y1, r_zb(y1)), (R_TE + seat, r_zb(R_TE + seat)),
           (R_TE + seat, zs), (R_TE, zs)]
    ax.add_patch(Polygon(pts, fc=MADERA, ec="k", lw=1.5, zorder=3))
    # cuña que se rebaja para que el asiento quede horizontal
    ax.add_patch(Polygon([(R_TE, zs), (R_TE + seat, zs), (R_TE + seat, r_zb(R_TE + seat))],
                         fc="#f8c9c4", ec="#c0392b", lw=1.5, zorder=4))
    # soporte Simpson
    ax.plot([R_TE + 0.002, R_TE + 0.002, R_TE + seat + 0.004, R_TE + seat + 0.004],
            [zs + 0.13, zs - 0.003, zs - 0.003, zs + 0.05], color="#333", lw=3, zorder=6)
    for zz in (R_H0 + 0.03, R_H0 + 0.09, R_H0 + 0.18):
        ax.plot([-0.08, R_TE + 0.004], [zz, zz], color="k", lw=1.2, zorder=6)
    # corte a plomo: escuadra y desplazamiento
    off = R_H * R_P
    ax.plot([R_TE, R_TE + off], [r_zt(R_TE), r_zt(R_TE) - off * R_P - R_H], color="#2c7fb8", lw=1, ls=":")
    ax.annotate("", (R_TE, r_zt(R_TE) + 0.03), (R_TE + off, r_zt(R_TE) + 0.03), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(R_TE + off + 0.012, r_zt(R_TE) + 0.03, f"correr {off * 100:.1f} cm", ha="left", va="center", fontsize=8.5,
            color="#2c7fb8", weight="bold", bbox=dict(fc="white", ec="none", pad=0.3))
    notas = [((R_TE, r_zt(R_TE) - 0.06), (-0.10, R_H0 + 0.40), "1 · CORTE A PLOMO\n(vertical, de tope\ncontra la tabla)"),
             ((R_TE + seat / 2, R_H0 + 0.002), (0.20, R_H0 - 0.12), f"2 · ASIENTO: rebajar una cuña de\n{dz * 1000:.0f} mm en 4,5 cm (rojo) para que\nla punta apoye plana en el soporte"),
             ((R_TE + seat + 0.004, R_H0 + 0.03), (0.30, R_H0 + 0.05), "soporte Simpson\n2x6 ZMAX"),
             ((-0.05, R_H0 + 0.09), (-0.10, R_H0 - 0.08), "tornillos largos: atravesar\nla tabla y anclar\nen la estructura del muro"),
             ((R_TE / 2, R_H0 + 0.21), (0.12, R_H0 + 0.42), "tabla 1x10 (23 cm)")]
    for p, tt, tx in notas:
        ax.annotate(tx, p, tt, fontsize=8, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.6),
                    bbox=dict(fc="white", ec="none", pad=0.5), zorder=8)
    ax.set_xlim(-0.2, 0.42); ax.set_ylim(R_H0 - 0.2, R_H0 + 0.48)
    ax.set_title("DETALLE · corte del tijeral que atraca en el muro", fontsize=11, weight="bold")

def tabla_pendientes(ax):
    ax.axis("off")
    filas = []
    for p in (0.08, 0.10, 0.12, 0.13, 0.15):
        ht = R_H0 - p * R_A
        ok = ht - 0.082 >= 2.03 + 0.185
        filas.append([f"{p * 100:.0f} %", f"{math.degrees(math.atan(p)):.1f}°", f"{ht:.2f}", f"{ht - p * R_ALERO:.2f}",
                      "sí" if ok else "NO", "ELEGIDA" if abs(p - R_P) < 1e-9 else ("poca caída" if p < 0.10 else "")])
    t = ax.table(cellText=filas, colLabels=["Pendiente", "Ángulo", "Tabique opuesto (m)", "Borde alero (m)",
                                            "Cabe ventana V2 + dintel", "Comentario"], loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 1.3)
    for k in range(6):
        t[3, k].set_facecolor("#d4edda")
    ax.text(0, 0.18, ("Pendiente óptima 12 %: es más que el 10 % mínimo recomendado para plancha trapezoidal y policarbonato\n"
                      "en zona lluviosa, y todavía deja el tabique opuesto en 2,33 m, suficiente para la puerta (2,05) y\n"
                      "para la ventana V2 con su dintel 2x8 (2,03 + 0,185 = 2,22 m + solera doble). Con 15 % ya no cabe."),
            fontsize=8.5, va="top", transform=ax.transAxes)
    ax.set_title("COMPARACIÓN DE PENDIENTES (parte de abajo del tijeral en el muro = 2,63 m)", fontsize=10, weight="bold")


# ---------------- Lámina 11: CORTE A PLOMO PASO A PASO ----------------
def _pieza_banco(ax, paso):
    """Punta del tijeral acostada en el banco (sin inclinar)."""
    ax.set_aspect("equal"); ax.axis("off")
    h = H_T; off = h * PEND; Lp = 0.42
    # pieza: extremo de la casa a la izquierda
    if paso < 3:
        poly = [(0, 0), (Lp, 0), (Lp, h), (0, h)]
    else:
        poly = [(off, 0), (Lp, 0), (Lp, h), (0, h)]
    ax.add_patch(Polygon(poly, fc=MADERA, ec="k", lw=1.5))
    if paso >= 1:   # línea a escuadra
        ax.plot([off, off], [-0.02, h + 0.02], color="#2c7fb8", lw=1.5, ls="--")
        if paso < 3:
            ax.text(off + 0.008, -0.045, "1 · línea a escuadra", color="#2c7fb8", fontsize=9, weight="bold")
    if paso == 2:   # correr 2 cm en el canto de arriba
        ax.annotate("", (0, h + 0.03), (off, h + 0.03), arrowprops=dict(arrowstyle="<->", lw=1.2, color="#c0392b"))
        ax.text(off / 2, h + 0.05, f"{off * 100:.1f} cm", ha="center", color="#c0392b", fontsize=10, weight="bold")
        ax.plot([0, off], [h, 0], color="#c0392b", lw=2.5)
        ax.text(-0.01, h + 0.095, "2 · en el canto de ARRIBA corre 2 cm hacia la punta\n    y une con el pie de la escuadra: esa es la línea de corte",
                color="#c0392b", fontsize=8.5, va="bottom")
    if paso < 3:
        ax.text(Lp - 0.01, h / 2, "tijeral 2x6½\"\n(acostado en el banco)", ha="right", va="center", fontsize=8)
    else:
        ax.add_patch(Polygon([(0, 0), (off, 0), (0, h)], fc="#f8c9c4", ec="#c0392b", lw=1, ls="--"))
        ax.plot([0, off], [h, 0], color="#c0392b", lw=2.5)
        ax.annotate("este triangulito se bota", (0.006, 0.02), (0.10, -0.05), fontsize=8, color="#c0392b",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color="#c0392b"))
        ax.text(Lp - 0.01, h / 2, "3 · cortar con la sierra\n     por la línea roja", ha="right", va="center", fontsize=8.5,
                weight="bold")
    ax.annotate("", (Lp + 0.03, 0), (Lp + 0.03, h), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(Lp + 0.04, h / 2, f"{h * 100:.1f} cm", va="center", fontsize=8.5)
    ax.text(-0.04, h / 2, "lado de\nla CASA", ha="right", va="center", fontsize=8.5, weight="bold", color="#555")
    ax.set_xlim(-0.14, Lp + 0.12); ax.set_ylim(-0.08, h + 0.17)

def _pieza_colocada(ax):
    ax.set_aspect("equal"); ax.axis("off")
    th = math.atan(PEND); h = H_T
    z0 = 0.0
    # muro y tabla 1x10
    ax.add_patch(Rectangle((-0.10, -0.12), 0.10, 0.42, fc="#e6e6e6", ec="k", hatch="//"))
    ax.add_patch(Rectangle((0, -0.004), TE_V, H_V, fc="#c0392b", ec="k"))
    x0 = TE_V
    zt_ = lambda x: z0 + h / math.cos(th) - PEND * (x - x0)
    zb_ = lambda x: z0 - PEND * (x - x0)
    seat = 0.045
    pts = [(x0, zt_(x0)), (0.45, zt_(0.45)), (0.45, zb_(0.45)), (x0 + seat, zb_(x0 + seat)), (x0 + seat, z0), (x0, z0)]
    ax.add_patch(Polygon(pts, fc=MADERA, ec="k", lw=1.5))
    ax.add_patch(Polygon([(x0, z0), (x0 + seat, z0), (x0 + seat, zb_(x0 + seat))], fc="#f8c9c4", ec="#c0392b", lw=1.2))
    ax.plot([x0 + 0.002, x0 + 0.002, x0 + seat + 0.004, x0 + seat + 0.004], [0.13, -0.004, -0.004, 0.05], color="#333", lw=3)
    ax.plot([x0, x0], [-0.06, zt_(x0) + 0.06], color="#c0392b", lw=1, ls=":")
    ax.text(x0 + 0.006, zt_(x0) + 0.07, "corte VERTICAL (a plomo):\nqueda pegado a la tabla", fontsize=8.5, color="#c0392b", weight="bold")
    ax.plot([x0 + 0.15, 0.40, 0.40], [zt_(x0 + 0.15) + 0.03, zt_(x0 + 0.15) + 0.03, zt_(0.40) + 0.03], color="#2c7fb8", lw=1)
    ax.text(0.41, zt_(0.40) + 0.035, f"pendiente {PEND * 100:.0f} % ({math.degrees(th):.1f}°)", fontsize=8, color="#2c7fb8")
    notas = [((x0 + seat / 2, z0 - 0.002), (0.22, -0.08), f"4 · ASIENTO: rebajar esta cuña\n({PEND * seat * 1000:.0f} mm en {seat * 100:.1f} cm) para que apoye\nplano sobre el soporte Simpson"),
             ((x0 + seat + 0.004, 0.03), (0.30, 0.03), "soporte Simpson 2x6"),
             ((TE_V / 2, 0.18), (-0.06, 0.33), "tabla 1x10\napernada al muro")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=8, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.6),
                    bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(-0.14, 0.62); ax.set_ylim(-0.16, 0.40)

def _pieza_completa(ax):
    ax.set_aspect("auto"); ax.axis("off")
    Lc = tij[-1][3]; h = H_T; off = h * PEND
    poly = [(off, 0), (Lc + off, 0), (Lc, h), (0, h)]
    ax.add_patch(Polygon(poly, fc=MADERA, ec="k", lw=1.5))
    ax.annotate("", (0, h + 0.05), (Lc, h + 0.05), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(Lc / 2, h + 0.07, f"canto de ARRIBA {Lc:.2f} m", ha="center", fontsize=9, weight="bold")
    ax.annotate("", (off, -0.05), (Lc + off, -0.05), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(Lc / 2, -0.11, f"canto de ABAJO {Lc:.2f} m (corrido {off * 100:.0f} cm)", ha="center", fontsize=9)
    ax.text(-0.03, h / 2, "punta\ncasa", ha="right", va="center", fontsize=8.5, weight="bold")
    ax.text(Lc + off + 0.03, h / 2, "punta\nalero", ha="left", va="center", fontsize=8.5, weight="bold")
    ax.text(Lc / 2, h / 2, "las 2 puntas se cortan a plomo y quedan PARALELAS (la pieza es un paralelogramo)",
            ha="center", va="center", fontsize=8.5)
    ax.set_xlim(-0.35, Lc + 0.40); ax.set_ylim(-0.18, h + 0.13)

def lamina_corte_plomo(fig):
    titulo(fig, "Lámina 11: CORTE A PLOMO DEL TIJERAL · PASO A PASO")
    for k, (pos, tt) in enumerate([([0.02, 0.56, 0.31, 0.32], "PASO 1 · marcar la escuadra"),
                                    ([0.35, 0.56, 0.31, 0.32], "PASO 2 · correr 2 cm arriba"),
                                    ([0.68, 0.56, 0.31, 0.32], "PASO 3 · cortar")]):
        ax = fig.add_axes(pos); _pieza_banco(ax, k + 1); ax.set_title(tt, fontsize=11, weight="bold")
    ax = fig.add_axes([0.02, 0.20, 0.55, 0.34]); _pieza_colocada(ax)
    ax.set_title("ASÍ QUEDA COLOCADO (pieza inclinada 12 %)", fontsize=11, weight="bold")
    ax = fig.add_axes([0.60, 0.25, 0.38, 0.20]); ax.axis("off")
    ax.text(0, 1, "POR QUÉ 2 cm", fontsize=11, weight="bold", va="top")
    ax.text(0, 0.80, (f"El tijeral va inclinado {PEND * 100:.0f} %. Si lo cortas a escuadra (90°),\n"
                      f"al ponerlo inclinado la punta queda torcida y no asienta contra\n"
                      f"la tabla. Corriendo {H_T * PEND * 100:.1f} cm ({H_T * 100:.1f} cm de alto x {PEND:.2f}) la punta\n"
                      "queda vertical y apoya completa contra la tabla del muro."),
            fontsize=9.5, va="top", linespacing=1.5)
    ax = fig.add_axes([0.04, 0.03, 0.92, 0.15]); _pieza_completa(ax)
    ax.set_title("LA PIEZA COMPLETA", fontsize=10.5, weight="bold")


def titulo(fig, sub):
    fig.text(0.04, 0.95, "AMPLIACIÓN CABAÑA – LAGO TODOS LOS SANTOS", fontsize=16,
             weight="bold")
    fig.text(0.04, 0.92, sub + "   ·   Bodega 3,50 x 2,50 m + terraza techada 4,75 m   ·   "
             "Techo rectangular, esquinas a 90°   ·   Medidas en metros   ·   "
             "Borrador para revisión", fontsize=10, color="#444")


with PdfPages(OUT + "ampliacion_cabana.pdf") as pdf:
    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 1: PLANTA")
    ax = fig.add_axes([0.03, 0.30, 0.94, 0.60])
    planta(ax)
    leyenda_y_tabla(fig)
    pdf.savefig(fig); fig.savefig(OUT + "1_planta.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 2: ISOMÉTRICO (vista desde afuera, casa existente atrás en gris)")
    a1 = fig.add_axes([0.02, 0.06, 0.96, 0.84], projection="3d")
    iso(a1, azim=-120)
    fig.text(0.04, 0.04, "Tijerales 2x6½\" c/60 cm · alero 40 cm · cubierta trapezoidal translúcida en terraza e intercalada en bodega · pendiente 12 % · "
             "tabla 1x10 apernada al muro (rojo) · canaleta PVC café",
             fontsize=9, color="#444")
    pdf.savefig(fig); fig.savefig(OUT + "2_isometrico.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 3: CORTES")
    corte_transversal(fig.add_axes([0.02, 0.47, 0.46, 0.38]))
    corte_longitudinal(fig.add_axes([0.02, 0.03, 0.96, 0.36]))
    detalle(fig.add_axes([0.52, 0.43, 0.22, 0.19]), 1)
    detalle(fig.add_axes([0.76, 0.43, 0.22, 0.19]), 2)
    ax = fig.add_axes([0.52, 0.62, 0.45, 0.27]); ax.axis("off")
    ax.text(0, 1, "NOTAS", fontsize=11, weight="bold", va="top")
    ax.text(0, 0.88, (
        "1. Alturas en metros desde el piso de la ampliación.\n"
        "2. Junto a la casa: tijeral 2x6½\" DE TOPE contra tabla 1x10 apernada al muro\n"
        "    (borde bajo a 2,63 m), con soporte viga Simpson 2x6 ZMAX (ver lámina 10).\n"
        "    Por fuera: sobre muro de bodega o viga 2x6 doble, con 2 soportes\n"
        "    sismo y viento Simpson H3 por tijeral (uno por lado).\n"
        "3. MEDIDAS REALES: tijeral a 2,63 m en el muro, pendiente 12 % (CONFIRMADA),\n"
        "    muro exterior 2,33 m bajo el tijeral; alero existente a 3,03 m.\n"
        "4. Costaneras 2x2 c/40 cm; plancha en una sola pieza, vuela 8 cm sobre la canaleta (DET. 5).\n"
        "5. Tijerales 2x6½\" pino IPV cada 60 cm. Cubierta translúcida en terraza e\n"
        "    intercalada (translúcida / opaca) en bodega.\n"
        "6. Bodega: tabique 2x3 IPV c/40 cm en 3 lados (contra la casa no lleva tabique),\n"
        "    2 corridas de cadenetas y puerta 80x200 hacia la terraza."),
        fontsize=8.5, va="top", linespacing=1.4)
    pdf.savefig(fig); fig.savefig(OUT + "3_cortes.png", dpi=110); plt.close(fig)

    nT = sum(1 for p in PLANCHAS if p[2] == "T"); nO = len(PLANCHAS) - nT
    largos_T = ", ".join(f"{largo_plancha(a, b):.2f}" for a, b, t in PLANCHAS if t == "T")
    largos_O = ", ".join(f"{largo_plancha(a, b):.2f}" for a, b, t in PLANCHAS if t == "O")
    grupos = [
        ("ESTRUCTURA DE TECHO", [
            ["Tijerales c/60 cm", "Pino IPV 2x6½\" x 3,20", str(len(tij)), f"todos iguales, {tij[-1][3]:.2f} m"],
            ["Tabla 1x10 apernada al muro (tijerales de tope)", "Pino 1x10 cep. 4/c x 3,20", "3", "borde bajo a 2,63 m"],
            ["Pernos o tirafondos 3/8\"", "c/60 cm", str(N_PERNOS), "según material del muro existente"],
            ["Soporte viga madera cepillada 2x6 ZMAX", "Simpson · Imperial SKU 142184", str(len(tij)), "1 por tijeral, en muro casa"],
            ["Soporte sismo y viento H3", "Simpson · Imperial SKU 142181", str(2 * len(tij)), "2 por tijeral (uno por lado)"],
            ["Costaneras c/40 cm", "Pino IPV 2x2 x 3,20", str(N_COST), f"{len(FILAS)} corridas"],
            ["Tapacán vertical", "Tabla pino 1x8 x 3,20", "3", "8,25 m recto; pintar"],
            ["Bloqueos entre tijerales (muro bodega)", "Pino IPV 2x6 x 3,20", "1", ""],
        ]),
        ("TERRAZA", [
            ["Viga exterior doble (recta, 4,75 m)", "Pino IPV 2x6 x 3,20", "4", "unir sobre pilar"],
            ["Pilares", "Pino IPV 4x4 x 3,20", "2", ""],
        ]),
        ("PISO TERRAZA (completar rectángulo)", [
            ["Ampliación de piso (triángulo de la diagonal)", "según piso existente", "~2,4 m²", "POR DEFINIR: falta estructura del piso"],
        ]),
        ("CUBIERTA TRAPEZOIDAL", [
            ["Plancha translúcida (policarbonato)", f"largos: {largos_T}", str(nT), "mismo perfil que la opaca"],
            ["Plancha opaca (zinc-alum)", f"largos: {largos_O}", str(nO), "intercalada en bodega"],
        ]),
        ("HOJALATERÍA DE REMATE (zincalum 0,4 mm)", [
            ["Plancha lisa para plegar", "zincalum 1,00 x 3,00 m", "3", "el hojalatero pliega forros y remates"],
            ["Forro contra muro existente", "desarrollo ~40 cm x 3 m", "3", "8,25 m + traslapos (DETALLE 3)"],
            ["Remate lateral", "desarrollo ~35 cm", "2", "2 x 2,9 m (DETALLE 4)"],
            ["Cierre de espuma perfil trapezoidal", "tira ~1 m", "9", "bajo el forro, junto al muro"],
            ["Sellante poliuretano", "cartucho", "2", "borde superior del forro"],
        ]),
        ("AGUAS LLUVIA (PVC café)", [
            ["Canaleta PVC café 110 mm", "x 4,00 m", "3", "8,25 m de borde recto"],
            ["Uniones de canaleta", "PVC café", "2", ""],
            ["Tapas de canaleta", "PVC café", "2", ""],
            ["Salida a bajada", "PVC café Ø80", "1", "extremo derecho (esquina bodega)"],
            ["Ganchos de canaleta", "PVC café", "19", "c/50 cm, al tapacán 1x8"],
            ["Tubo de bajada", "PVC café Ø80 x 3 m", "2", "confirmar altura al terreno"],
            ["Codos de bajada", "PVC café Ø80", "3", "2 para el alero + 1 al final"],
            ["Abrazaderas de bajada", "PVC café Ø80", "3", ""],
            ["Sellante para PVC / silicona", "cartucho", "1", ""],
        ]),
        ("BODEGA – ESTRUCTURA", [
            ["Pies derechos c/40 cm", "Pino IPV 2x3 x 3,20", str(N_PD_COMPRA), "incluye vano y esquinas"],
            ["Soleras (inferior + superior doble)", "Pino IPV 2x3 x 3,20", str(N_SOL), ""],
            ["Cadenetas (2 corridas)", "Pino IPV 2x3 x 3,20", str(N_CAD), ""],
            ["Dintel puerta (de canto)", "Pino IPV 2x4 x 3,20", "1", ""],
            ["Puerta exterior + marco", "80 x 200 cm", "1", "bisagras 3 x 3½\" + cerradura"],
            ["Escuadras metálicas base pilares", "galvanizadas", "4", "2 por pilar"],
        ]),
        ("TORNILLOS (sin clavos · detalle en planilla Excel)", [
            [TIPOS[k], "", str(v), ""] for k, v in sorted(TOT_TORN.items())
        ]),
        ("VENTANAS (2)", [
            ["Ventana V1 (muro lateral 2,5 m)", "aluminio 150 x 30 cm", "1", "vano 152 x 32; borde sup. ~2,0 m"],
            ["Ventana V2 (muro frente a la casa)", "aluminio 200 x 30 cm", "1", "vano 202 x 32; borde sup. ~2,0 m"],
            ["Dintel V2 (de canto)", "Pino IPV 2x8 x 3,20", "1", "2,10 m, recibe 3 tijerales"],
            ["Dintel V1 (de canto)", "Pino IPV 2x6 x 3,20", "1", "1,60 m"],
            ["Refuerzos: antepecho doble, muñecos, calce", "Pino IPV 2x3 x 3,20", str(N_VEN_2X3), "jambas y p.d. enteros ya incluidos arriba"],
            ["Botaguas sobre ventanas", "zincalum (de las planchas lisas)", "2", "con sello"],
            ["Silicona neutra exterior", "cartucho", "1", "sello perimetral ventanas"],
        ]),
        ("BODEGA – REVESTIMIENTOS", [
            ["SmartPanel exterior", "1,22 x 2,44", "11", "~18 m², pintar"],
            ["Contrachapado ranurado interior", "1,22 x 2,44", "10", "~18 m² (sin muro de la casa)"],
            ["Barrera de humedad (Tyvek/fieltro)", "rollo", "1", "detrás del SmartPanel"],
            ["Esquineros / tapajuntas", "2,40 m", "6", "incluye las 2 esquinas del destaje"],
            ["Cortagotera en Z", "3,00 m", "3", "unión de franja superior"],
            ["Grapas para barrera de humedad", "caja", "1", "corchetera"],
]),
    ]
    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 4: LISTA DE MATERIALES")
    corte = [g for g, _ in grupos].index("BODEGA – ESTRUCTURA")
    for col, gs in enumerate([grupos[:corte], grupos[corte:]]):
        filas, colores = [], []
        for g, items in gs:
            filas.append([g, "", "", ""]); colores.append("#dfe7ee")
            for it in items:
                filas.append(it); colores.append("white")
        ax = fig.add_axes([0.02 + col * 0.49, 0.06, 0.475, 0.83]); ax.axis("off")
        t = ax.table(cellText=filas, colLabels=["Ítem", "Material / medida", "Cant.", "Nota"],
                     loc="upper center", cellLoc="left", colWidths=[0.33, 0.25, 0.07, 0.35])
        t.auto_set_font_size(False); t.set_fontsize(7); t.scale(1, 1.22)
        for r, c in enumerate(colores, 1):
            for k in range(4):
                t[r, k].set_facecolor(c)
                if c != "white":
                    t[r, k].get_text().set_weight("bold")
    fig.text(0.04, 0.03, "Cantidades de madera con ~10 % de pérdida (tijerales justos). "
             "Confirmar ancho útil y largos disponibles de las planchas en la tienda.",
             fontsize=9, color="#444")
    pdf.savefig(fig); fig.savefig(OUT + "4_materiales.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 5: HOJALATERÍA DE REMATE")
    llave_hojalateria(fig.add_axes([0.03, 0.50, 0.42, 0.38]))
    detalle_forro(fig.add_axes([0.48, 0.47, 0.50, 0.42]))
    detalle_remate(fig.add_axes([0.03, 0.04, 0.55, 0.40]))
    ax = fig.add_axes([0.62, 0.06, 0.35, 0.36]); ax.axis("off")
    ax.text(0, 1, "NOTAS HOJALATERÍA", fontsize=11, weight="bold", va="top")
    ax.text(0, 0.88, (
        "1. Hojalatería en zincalum liso 0,4 mm, plegada por hojalatero.\n"
        "2. FORRO (DETALLE 3): va contra el muro existente, bajo el alero de la\n"
        "    casa, en los 8,25 m. Baja por el muro y monta ~20 cm sobre la\n"
        "    plancha. Arriba lleva sello de poliuretano; abajo, goterón.\n"
        "3. Bajo el forro, una tira de cierre de espuma tapa las ondas de la\n"
        "    plancha trapezoidal para que no entre agua ni viento.\n"
        "4. REMATE LATERAL (DETALLE 4): en los dos bordes perpendiculares a\n"
        "    la casa (2,9 m cada uno). Cubre la última\n"
        "    onda y baja por la cara del tijeral de borde, con goterón.\n"
        "5. Traslapos entre piezas de hojalatería: mínimo 10 cm, con sello.\n"
        "6. Fijación: autoperforante 12x1½\" con golilla en la cresta (c/30 cm)\n"
        "    y tornillo exterior 8x2\" al muro / tijeral (c/40 cm). Sin clavos."),
        fontsize=9, va="top", linespacing=1.45)
    pdf.savefig(fig); fig.savefig(OUT + "5_hojalateria.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 6: VENTANAS, REFUERZOS Y CANALETA")
    elevacion(fig.add_axes([0.01, 0.40, 0.40, 0.50]), VENTANAS[0])
    elevacion(fig.add_axes([0.40, 0.40, 0.59, 0.50]), VENTANAS[1])
    detalle_canal(fig.add_axes([0.60, 0.01, 0.39, 0.345]))
    ax = fig.add_axes([0.04, 0.04, 0.55, 0.33]); ax.axis("off")
    ax.text(0, 1, "REFUERZOS EN CADA VANO DE VENTANA", fontsize=11, weight="bold", va="top")
    ax.text(0, 0.88, (
        "1. A cada lado del vano: un PIE DERECHO ENTERO (de solera a solera) + una JAMBA pegada a él, que sostiene el dintel.\n"
        "2. DINTEL de canto sobre las jambas: V2 (2,0 m) en 2x8 porque recibe los tijerales T10 a T13; V1 (1,5 m) en 2x6.\n"
        "    Sobre el dintel: en V2 un calce 2x3 hasta la solera; en V1 muñecos cortos (el muro sube con la pendiente).\n"
        "3. ANTEPECHO DOBLE 2x3 tendido bajo la ventana, a 1,71 m; bajo él, MUÑECOS 2x3 cada 40 cm (siguen la modulación).\n"
        "4. Los pies derechos que caían dentro del vano se reemplazan por los muñecos. La corrida alta de cadenetas (1,70 m)\n"
        "    se interrumpe en el vano: el antepecho hace ese trabajo.\n"
        "5. Ventanas centradas: V1 en el muro lateral (2,10 m hasta el destaje); V2 en el muro largo (3,10 m).\n"
        "6. Borde superior del vano a 2,03 m (ventana ~2,0 m, alineada con la puerta). No puede ir el antepecho a 2,0 m: no\n"
        "    queda altura para el dintel bajo los tijerales (el muro exterior mide 2,33 m).\n"
        "7. Ventanas de aluminio (fijas o proyectantes) a medida, con botaguas de zincalum arriba y sello de silicona."),
        fontsize=8.3, va="top", linespacing=1.5)
    pdf.savefig(fig); fig.savefig(OUT + "6_ventanas.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 7: FACHADA LATERAL BODEGA")
    fachada_lateral(fig.add_axes([0.03, 0.05, 0.94, 0.85]))
    pdf.savefig(fig); fig.savefig(OUT + "7_fachada_lateral.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 8: FACHADA PRINCIPAL")
    fachada_frente(fig.add_axes([0.02, 0.05, 0.96, 0.85]))
    pdf.savefig(fig); fig.savefig(OUT + "8_fachada_principal.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 9: DETALLE DE TIJERALES")
    tijeral_tipo_a(fig.add_axes([0.02, 0.50, 0.62, 0.40]))
    corte_plomo(fig.add_axes([0.66, 0.52, 0.32, 0.36]))
    tijerales_tipo_b(fig.add_axes([0.02, 0.03, 0.46, 0.44]))
    tabla_corte(fig.add_axes([0.50, 0.03, 0.48, 0.44]))
    pdf.savefig(fig); fig.savefig(OUT + "9_tijerales.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    titulo(fig, "Lámina 10: MEDIDAS REALES · PENDIENTE Y CORTE DEL TIJERAL")
    corte_real(fig.add_axes([0.02, 0.36, 0.55, 0.52]))
    detalle_corte_real(fig.add_axes([0.58, 0.36, 0.41, 0.52]))
    tabla_pendientes(fig.add_axes([0.05, 0.03, 0.90, 0.30]))
    pdf.savefig(fig); fig.savefig(OUT + "10_pendiente_corte.png", dpi=110); plt.close(fig)

    fig = plt.figure(figsize=(16.5, 11.7))
    lamina_corte_plomo(fig)
    pdf.savefig(fig); fig.savefig(OUT + "11_corte_plomo.png", dpi=110); plt.close(fig)
