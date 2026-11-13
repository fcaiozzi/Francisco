"""Propuesta: terraza con esquinas a 90° (reemplaza el borde diagonal)."""
import os
ns = {"__file__": os.path.abspath("generar_planos.py")}
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "generar_planos.py")).read()
exec(src.split("\nwith PdfPages")[0], ns)
g = type("G", (), ns)
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
L, D, XB, DIAG_X, Y0 = g.L, g.D, g.XB, g.DIAG_X, g.Y0
AL = g.ALERO

def base(ax, titulo):
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((-0.3, -0.45), L + 0.6, 0.45, fc="#e6e6e6", ec="k", hatch="//"))
    ax.text(L / 2, -0.22, "CASA EXISTENTE", ha="center", va="center", fontsize=8, bbox=dict(fc="white", ec="none"))
    ax.add_patch(Rectangle((XB, 0), L - XB, D, fc="#d9e8f5", ec="#1f4e79", lw=2))
    ax.text((XB + L) / 2, 1.2, "BODEGA", ha="center", fontsize=9, weight="bold", color="#1f4e79")
    ax.set_title(titulo, fontsize=10.5, weight="bold")
    ax.set_xlim(-0.6, L + 0.4); ax.set_ylim(-0.6, 3.6); ax.invert_yaxis()

def techo(ax, pts):
    ax.add_patch(Polygon(pts, fc="#fff6d8", ec="#b8860b", lw=2, ls="-.", zorder=0))

def piso(ax, pts, fc="#f3e3c7"):
    ax.add_patch(Polygon(pts, fc=fc, ec="k", lw=1.5, zorder=1))

def pilar(ax, x, y, nuevo=False):
    ax.add_patch(Rectangle((x - 0.06, y - 0.06), 0.12, 0.12, fc="#c0392b" if nuevo else "k", ec="k", zorder=5))

def esquinas(ax, pts):
    for x, y in pts:
        ax.plot(x, y, "o", ms=9, mfc="none", mec="#2c7fb8", mew=2, zorder=6)

piso_act = [(0, 0), (XB, 0), (XB, D), (DIAG_X, D), (0, Y0)]
fig, axs = plt.subplots(2, 2, figsize=(16.5, 11.7))
fig.text(0.04, 0.955, "PROPUESTA · TERRAZA CON ESQUINAS A 90°", fontsize=16, weight="bold")
fig.text(0.04, 0.93, "Planta de techo · medidas en metros · círculos azules = esquinas del remate (tapacán, canaleta, hojalatería)",
         fontsize=10, color="#444")

# 0) Actual
ax = axs[0, 0]; base(ax, "HOY: borde diagonal (esquinas de 156° y cortes compuestos)")
techo(ax, [(0, 0), (0, Y0 + AL), (DIAG_X, D + AL), (L, D + AL), (L, 0)])
piso(ax, piso_act)
ax.plot([0, DIAG_X, XB], [Y0, D, D], color="#555", lw=3, ls="--")
for x, y in g.PILARES: pilar(ax, x, y)
esquinas(ax, [(0, Y0 + AL), (DIAG_X, D + AL), (L, D + AL)])
ax.text(1.4, 0.6, "TERRAZA", fontsize=9, weight="bold", color="#6b4f1d")

# A) Recomendada: techo rectangular + completar el piso
ax = axs[0, 1]; base(ax, "A · RECOMENDADA: techo rectangular + completar el piso")
techo(ax, [(0, 0), (0, D + AL), (L, D + AL), (L, 0)])
piso(ax, piso_act)
piso(ax, [(0, Y0), (DIAG_X, D), (0, D)], fc="#c8e6c9")
ax.plot([0, XB], [D, D], color="#555", lw=3, ls="--")
pilar(ax, 0, D, True); pilar(ax, XB / 2, D, True)
esquinas(ax, [(0, D + AL), (L, D + AL)])
ax.text(0.35, 2.05, "piso nuevo\n≈ 2,4 m²", fontsize=8, color="#2e7d32", weight="bold")
ax.text(1.4, 0.6, "TERRAZA 4,75 x 2,50", fontsize=9, weight="bold", color="#6b4f1d")
ax.text(0.2, 3.25, "viga 2x6 doble recta + 2 pilares 4x4 (rojo)", fontsize=8, color="#c0392b")

# B) Techo rectangular sin agrandar el piso
ax = axs[1, 0]; base(ax, "B · techo rectangular, piso igual (pilares al terreno)")
techo(ax, [(0, 0), (0, D + AL), (L, D + AL), (L, 0)])
piso(ax, piso_act)
ax.add_patch(Polygon([(0, Y0), (DIAG_X, D), (0, D)], fc="none", ec="#999", hatch="..", zorder=1))
ax.plot([0, XB], [D, D], color="#555", lw=3, ls="--")
pilar(ax, 0, D, True); pilar(ax, XB / 2, D, True)
esquinas(ax, [(0, D + AL), (L, D + AL)])
ax.text(0.15, 2.0, "terreno techado\n(sin piso)", fontsize=8, color="#666")
ax.text(0.2, 3.25, "2 pilares bajan al terreno sobre poyos de hormigón", fontsize=8, color="#c0392b")

# C) Escalonado
ax = axs[1, 1]; base(ax, "C · escalonado (siguiendo el piso): NO recomendado")
xm = DIAG_X / 2
techo(ax, [(0, 0), (0, g.prof(xm) + AL), (xm, g.prof(xm) + AL), (xm, D + AL), (L, D + AL), (L, 0)])
piso(ax, piso_act)
ax.plot([0, xm, xm, XB], [g.prof(xm), g.prof(xm), D, D], color="#555", lw=3, ls="--")
pilar(ax, 0, g.prof(xm), True); pilar(ax, xm, g.prof(xm)); pilar(ax, xm, D)
esquinas(ax, [(0, g.prof(xm) + AL), (xm, g.prof(xm) + AL), (xm, D + AL), (L, D + AL)])
ax.text(0.1, 3.25, "4 esquinas, 2 largos de tijeral, igual queda un pilar fuera del piso", fontsize=8, color="#c0392b")
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propuesta_esquinas_90.png"), dpi=110)
