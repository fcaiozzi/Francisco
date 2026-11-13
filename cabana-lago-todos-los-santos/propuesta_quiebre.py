"""Propuesta 2: borde de terraza escalonado a 90° desde el quiebre (retorno de ~35 cm)."""
import os, math
BASE = os.path.dirname(os.path.abspath(__file__))
ns = {"__file__": os.path.join(BASE, "generar_planos.py")}
exec(open(os.path.join(BASE, "generar_planos.py")).read().split("\nwith PdfPages")[0], ns)
g = type("G", (), ns)
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
L, D, XB, DX, Y0, AL, H_T = g.L, g.D, g.XB, g.DIAG_X, g.Y0, g.ALERO, g.H_T
k = (D - Y0) / DX

# --- cálculo del retorno h ---
VUELO_MAX = 0.80          # voladizo máximo razonable tijeral 2x6 c/60 (con carga puntual de mantención)
H = 0.35                  # retorno elegido
YL = D - H                # línea del tramo largo
xc = (YL - Y0) / k        # donde la línea nueva cruza la diagonal
A_add = (YL - Y0) ** 2 / (2 * k)
A_cut = H ** 2 / (2 * k)
vuelo = (D + AL) - YL
w = 0.69; P = 1.0         # kN/m (norma, tijeral c/60) y carga puntual 100 kg en la punta
M = max(w * vuelo ** 2 / 2, P * vuelo)   # norma: carga repartida O puntual
sigma = M * 1e6 / (41 * 138 ** 2 / 6)
print(f"h={H} YL={YL:.2f} xc={xc:.2f} A_add={A_add:.2f} A_cut={A_cut:.2f} vuelo={vuelo:.2f} sigma={sigma:.1f}")

fig = plt.figure(figsize=(16.5, 11.7))
fig.text(0.04, 0.955, "PROPUESTA 2 · BORDE DE TERRAZA A 90° DESDE EL QUIEBRE", fontsize=16, weight="bold")
fig.text(0.04, 0.93, "Retorno corto de 0,35 m en el quiebre + tramo largo paralelo a la casa hasta el borde de la terraza · techo rectangular",
         fontsize=10, color="#444")

# ---------- PLANTA ----------
ax = fig.add_axes([0.03, 0.30, 0.62, 0.60]); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Rectangle((-0.3, -0.45), L + 0.6, 0.45, fc="#e6e6e6", ec="k", hatch="//"))
ax.text(L / 2, -0.22, "CASA EXISTENTE", ha="center", va="center", fontsize=9, bbox=dict(fc="white", ec="none"))
ax.add_patch(Polygon([(0, 0), (0, D + AL), (L, D + AL), (L, 0)], fc="#fff6d8", ec="#b8860b", lw=2, ls="-.", zorder=0))
nuevo = [(0, 0), (XB, 0), (XB, D), (DX, D), (DX, YL), (0, YL)]
ax.add_patch(Polygon(nuevo, fc="#f3e3c7", ec="k", lw=2, zorder=1))
ax.add_patch(Polygon([(0, Y0), (xc, YL), (0, YL)], fc="#c8e6c9", ec="none", zorder=2))
ax.add_patch(Polygon([(xc, YL), (DX, D), (DX, YL)], fc="#f8c9c4", ec="none", zorder=2))
ax.plot([0, DX, XB], [Y0, D, D], color="#999", lw=1, ls=":", zorder=3)
ax.add_patch(Rectangle((XB, 0), L - XB, D, fc="#d9e8f5", ec="#1f4e79", lw=2, zorder=2))
ax.text((XB + L) / 2, 1.2, "BODEGA", ha="center", fontsize=10, weight="bold", color="#1f4e79")
# vigas y pilares
ax.plot([0, DX], [YL, YL], color="#555", lw=4, ls="--", zorder=4)
ax.plot([DX, DX, XB], [YL, D, D], color="#555", lw=4, ls="--", zorder=4)
for px, py in [(0, YL), (DX / 2, YL), (DX, YL), (DX, D)]:
    ax.add_patch(Rectangle((px - 0.06, py - 0.06), 0.12, 0.12, fc="#c0392b", ec="k", zorder=5))
for x in [xx for xx in g.xs_ter + g.xs_bod]:
    ax.plot([x, x], [0.04, D + AL], color="#8b4513", lw=1.2, alpha=0.6, zorder=3)
for x, y in [(0, D + AL), (L, D + AL)]:
    ax.plot(x, y, "o", ms=10, mfc="none", mec="#2c7fb8", mew=2, zorder=6)
for x, y in [(DX, YL), (DX, D), (0, YL)]:
    ax.plot(x, y, "s", ms=11, mfc="none", mec="#2c7fb8", mew=2, zorder=6)
def ch(xa, xb, y, t):
    ax.annotate("", (xa, y), (xb, y), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((xa + xb) / 2, y + 0.13, t, ha="center", fontsize=9, bbox=dict(fc="white", ec="none", pad=0.3))
def cv(x, ya, yb, t):
    ax.annotate("", (x, ya), (x, yb), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(x - 0.08, (ya + yb) / 2, t, ha="right", va="center", fontsize=9, bbox=dict(fc="white", ec="none", pad=0.3))
ch(0, DX, YL - 0.30, f"tramo largo {DX:.2f}")
ch(DX, XB, D + 0.25, f"{XB - DX:.2f}")
ax.annotate("", (DX + 0.12, YL), (DX + 0.12, D), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(DX + 0.2, (YL + D) / 2, f"retorno {H:.2f}", va="center", fontsize=9, weight="bold", bbox=dict(fc="white", ec="none", pad=0.3))
cv(-0.15, 0, YL, f"{YL:.2f}")
ch(0, L, D + AL + 0.35, "techo rectangular 8,25 (canaleta y tapacán rectos)")
ax.text(0.30, 1.75, f"piso nuevo\n≈ {A_add:.1f} m²", fontsize=9, color="#2e7d32", weight="bold", zorder=6)
ax.annotate(f"se recorta ≈ {A_cut:.2f} m²", (DX - 0.2, YL + 0.12), (2.0, 1.75), fontsize=8, color="#c0392b", zorder=6,
            arrowprops=dict(arrowstyle="-", lw=0.6, color="#c0392b"), bbox=dict(fc="white", ec="none", pad=0.3))
ax.text(1.4, 0.6, "TERRAZA", fontsize=11, weight="bold", color="#6b4f1d", zorder=6)
ax.text(0.2, D + AL + 0.75, "■ pilar 4x4 (4)    - - viga 2x6 doble    □ esquinas del piso a 90°    ○ esquinas del techo",
        fontsize=8.5)
ax.set_xlim(-0.8, L + 0.4); ax.set_ylim(-0.6, D + AL + 0.95); ax.invert_yaxis()
ax.set_title("PLANTA · borde nuevo de la terraza (línea gruesa) y diagonal actual (punteada)", fontsize=10.5, weight="bold")

# ---------- CORTE por el tramo largo ----------
ax = fig.add_axes([0.66, 0.50, 0.33, 0.38]); ax.set_aspect("equal"); ax.axis("off")
zt = g.zt; ye = D + AL
ax.add_patch(Rectangle((-0.25, 0), 0.25, 2.9, fc="#e6e6e6", ec="k", hatch="//"))
ax.add_patch(Polygon([(0.041, zt(0.041)), (ye, zt(ye)), (ye, zt(ye) - H_T), (0.041, zt(0.041) - H_T)], fc=g.MADERA, ec="k"))
ax.add_patch(Rectangle((0, -0.2), YL, 0.2, fc="#a0784a", ec="k"))
ax.add_patch(Rectangle((YL - 0.09, 0), 0.09, zt(YL) - H_T - 0.138, fc="#6d5a45", ec="k"))
ax.add_patch(Rectangle((YL - 0.09, zt(YL) - H_T - 0.138), 0.09, 0.138, fc="#c9a46a", ec="k"))
ax.add_patch(Rectangle((ye, zt(ye) + 0.041 - 0.185), 0.019, 0.185, fc="#b8860b", ec="k"))
ax.annotate("", (YL, 2.95), (ye, 2.95), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text((YL + ye) / 2, 3.02, f"voladizo {vuelo:.2f}", ha="center", fontsize=9)
ax.annotate("", (0.041, 2.95), (YL, 2.95), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(YL / 2, 3.02, f"{YL - 0.041:.2f}", ha="center", fontsize=9)
ax.text(YL - 0.05, 1.0, "pilar 4x4", rotation=90, fontsize=8, ha="right")
ax.text(0.6, -0.45, "piso (tramo largo)", fontsize=8)
ax.set_xlim(-0.3, ye + 0.2); ax.set_ylim(-0.6, 3.2)
ax.set_title("CORTE por el tramo largo (T1 a T6)", fontsize=10, weight="bold")

# ---------- NOTAS ----------
ax = fig.add_axes([0.66, 0.05, 0.33, 0.42]); ax.axis("off")
ax.text(0, 1, "CÓMO SE CALCULÓ EL RETORNO", fontsize=11, weight="bold", va="top")
ax.text(0, 0.92, (
    f"• El techo queda RECTANGULAR (2 esquinas a 90°). En el tramo largo\n"
    f"  el tijeral vuela desde la viga: voladizo = 0,40 + retorno.\n"
    f"• Un 2x6 c/60 cm aguanta bien hasta ~{VUELO_MAX:.2f} m de voladizo (con\n"
    f"  carga de mantención en la punta) → retorno máximo ~0,40 m.\n"
    f"• Con retorno 0,35 m: voladizo {vuelo:.2f} m → esfuerzo ≈ {sigma:.1f} MPa (bien).\n"
    f"• Con 0,30 m el piso nuevo crece y se recorta menos; con 0,40 m\n"
    f"  el voladizo llega a 0,80 (al límite). 0,35 m es el punto medio.\n\n"
    f"RESULTADO (retorno 0,35 m)\n"
    f"• Tramo largo a {YL:.2f} m del muro, de {DX:.2f} m; retorno de {H:.2f} m.\n"
    f"• Piso nuevo ≈ {A_add:.1f} m² (verde); se recorta ≈ {A_cut:.2f} m² (rojo).\n"
    f"• 4 pilares 4x4 (antes 3). Viga 2x6 doble recta.\n"
    f"• Los 15 tijerales quedan IGUALES (2,87 m), sin cortes en bisel.\n"
    f"• Tapacán, canaleta y forro rectos: 1 tapacán y 1 unión menos.\n\n"
    f"FALTA SABER: cómo está hecho el piso actual (vigas, distancia\n"
    f"entre ellas, tablas y altura al terreno) para cuantificar el piso nuevo."),
    fontsize=9, va="top", linespacing=1.45)
fig.savefig(os.path.join(BASE, "propuesta_quiebre_90.png"), dpi=110)
