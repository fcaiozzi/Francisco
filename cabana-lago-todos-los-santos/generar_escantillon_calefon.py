"""Escantillón 1:1 para el paso del ducto del calefón por el techo nuevo (pendiente 11,7 %)."""
import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Polygon
from matplotlib.backends.backend_pdf import PdfPages

OUT = os.path.dirname(os.path.abspath(__file__)) + "/"
PEND = (2.63 - 2.34) / 2.48            # pendiente del techo nuevo
ALFA = math.atan(PEND)                 # 6,7°
DIAMETROS = [127]                      # mm, ducto de 5" (medido en obra)
H_COLLAR = 80                          # alto del collarín (mm)
MM = 1 / 25.4

def pagina_escantillon(pdf, D):
    W, H = 420, 297                    # A3 apaisado, en mm
    fig = plt.figure(figsize=(W * MM, H * MM))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    r = D / 2; per = math.pi * D; dz = r * math.tan(ALFA)
    ax.text(15, 282, f"ESCANTILLÓN 1:1 · DUCTO CALEFÓN Ø {D} mm · techo {PEND * 100:.1f} % ({math.degrees(ALFA):.1f}°)".replace(".", ","),
            fontsize=13, weight="bold")
    ax.text(15, 274, "Imprimir en A3 al 100 % (sin 'ajustar a página'). Verificar con la regla de control antes de cortar.",
            fontsize=9, color="#c0392b")
    # regla de control 100 mm
    ax.plot([15, 115], [265, 265], color="k", lw=1.5)
    for k in range(0, 101, 10):
        ax.plot([15 + k, 15 + k], [265, 268 if k % 50 else 270], color="k", lw=0.8)
    ax.text(120, 264, "← debe medir exactamente 100 mm", fontsize=8)

    # --- 1) Collarín (desarrollo del cilindro cortado al ángulo del techo) ---
    x0, y0 = 4, 142
    tr = 10                                # traslapo para remachar
    n = 200
    xs = [x0 + per * i / n for i in range(n + 1)]
    # s=0 en el lado de la CASA (alto del techo): ahí el collarín es más corto
    base = [y0 + dz * (1 + math.cos(2 * math.pi * i / n)) for i in range(n + 1)]
    top = y0 + 2 * dz + H_COLLAR
    pts = list(zip(xs, base)) + [(x0 + per + tr, base[-1]), (x0 + per + tr, top), (x0, top)]
    ax.add_patch(Polygon(pts, closed=True, fill=False, ec="k", lw=1.6))
    ax.plot([x0 + per, x0 + per], [base[-1], top], color="k", lw=0.8, ls="--")
    ax.text(x0 + per + tr / 2, (top + base[-1]) / 2, "traslapo\n10 mm", rotation=90, ha="center", va="center", fontsize=7)
    for frac, txt in [(0, "lado CASA\n(alto del techo)"), (0.25, "costado"), (0.5, "lado ALERO\n(bajo del techo)"),
                      (0.75, "costado"), (1.0, "lado CASA")]:
        xx = x0 + per * frac
        ax.plot([xx, xx], [top, top + 4], color="#2c7fb8", lw=1)
        ax.text(xx, top + 6, txt, ha="center", fontsize=7.5, color="#2c7fb8")
    ax.annotate("", (x0 - 6, y0), (x0 - 6, y0 + 2 * dz), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(x0 - 4, y0 + dz, f"{2 * dz:.1f}", fontsize=7, va="center")
    ax.text(x0 + per / 2, y0 + 2 * dz + H_COLLAR / 2,
            f"1 · COLLARÍN (cortar 1 pieza)\ndesarrollo {per:.0f} mm + 10 de traslapo · alto {H_COLLAR} mm\n"
            f"La curva de abajo es el corte al ángulo del techo: diferencia {2 * dz:.1f} mm\n"
            "Se enrolla alrededor del ducto y su borde curvo asienta sobre la base",
            ha="center", va="center", fontsize=8.5)

    # --- 2) Base (plancha plana con el agujero elíptico) ---
    cx, cy = 300, 70
    a_eje = D / math.cos(ALFA); b_eje = D
    lado_y, lado_x = 300 - 2 * 0, 0
    BX, BY = 200, 200
    ax.add_patch(Ellipse((cx, cy), b_eje + 2, a_eje + 2, fill=False, ec="k", lw=1.6))
    ax.plot([cx, cx], [cy - a_eje / 2 - 8, cy + a_eje / 2 + 8], color="#2c7fb8", lw=0.8, ls="-.")
    ax.plot([cx - b_eje / 2 - 8, cx + b_eje / 2 + 8], [cy, cy], color="#2c7fb8", lw=0.8, ls="-.")
    ax.text(cx + b_eje / 2 + 10, cy + 12, f"largo {a_eje + 2:.1f} mm\n(en el sentido de la pendiente)", fontsize=7.5, color="#2c7fb8")
    ax.text(cx + b_eje / 2 + 10, cy - 10, f"ancho {b_eje + 2:.0f} mm", fontsize=7.5, color="#2c7fb8")
    ax.text(cx + b_eje / 2 + 10, cy + 40, "↑ hacia la CASA\n(sube el techo)", fontsize=8)
    ax.text(15, 30, "2 · AGUJERO de la base / plancha (elipse 1:1, holgura 1 mm)\n"
            "La base del forro: mínimo 15 cm de plancha alrededor del agujero",
            fontsize=8)

    # --- notas ---
    ax.text(15, 128, (
        f"• Ángulo entre el ducto (vertical) y el techo: {90 - math.degrees(ALFA):.1f}° por el lado alto y "
        f"{90 + math.degrees(ALFA):.1f}° por el lado bajo.\n"
        "• Cortar el agujero en la plancha en una parte PLANA (valle) o usar un forro flexible tipo 'Dektite'\n"
        "  para plancha trapezoidal. Sellar con silicona alta temperatura y poner sombrerete en la punta.\n"
        "• El collarín va remachado a la base y sellado; el sombrerete o un 'cortagotera' tapa la unión con el ducto.\n"
        "• Ducto metálico: mantener ≥ 5 cm de cualquier madera (tijerales, costaneras); usar pasamuro/forro aislado.\n"
        "• La salida debe quedar FUERA y POR SOBRE el alero de la cabaña existente (no bajo el alero).\n"
        "  Altura y distancias finales: confirmar con instalador SEC (gas)."),
        fontsize=8.3, va="top", linespacing=1.45)
    pdf.savefig(fig); plt.close(fig)

def lamina_explicativa():
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.text(0.04, 0.95, "AMPLIACIÓN CABAÑA – LAGO TODOS LOS SANTOS", fontsize=16, weight="bold")
    fig.text(0.04, 0.92, "Lámina 12: PASO DEL DUCTO DEL CALEFÓN POR EL TECHO NUEVO", fontsize=10, color="#444")
    ax = fig.add_axes([0.03, 0.08, 0.55, 0.80]); ax.set_aspect("equal"); ax.axis("off")
    zb = lambda y: 2.63 - PEND * y
    H_T = 0.165
    # cabaña + alero existente
    ax.add_patch(Rectangle((-0.6, 0), 0.6, 3.03, fc="#e6e6e6", ec="k", hatch="//"))
    ax.plot([-1.0, 0.45], [3.03 + 0.12, 3.03 - 0.05], color="#555", lw=6)
    ax.text(-0.3, 1.5, "CABAÑA\nEXISTENTE", ha="center", fontsize=9, weight="bold", bbox=dict(fc="white", ec="none"))
    # techo nuevo
    ye = 2.88
    ax.add_patch(Polygon([(0.019, zb(0.019)), (ye, zb(ye)), (ye, zb(ye) + H_T), (0.019, zb(0.019) + H_T)],
                         fc="#e8c891", ec="k"))
    ax.plot([0, ye + 0.08], [zb(0) + H_T + 0.05, zb(ye + 0.08) + H_T + 0.05], color="#555", lw=3)
    ax.add_patch(Rectangle((2.48 - 0.065, 0), 0.065, zb(2.48), fc="#d9e8f5", ec="#1f4e79"))
    ax.text(1.5, 0.6, "BODEGA", ha="center", fontsize=11, weight="bold", color="#1f4e79")
    # calefón + ducto
    yd = 0.75                                   # posición de paso (referencial)
    ax.add_patch(Rectangle((0.05, 1.20), 0.35, 0.65, fc="white", ec="k", lw=1.5))
    ax.text(0.225, 1.52, "CALEFÓN", ha="center", fontsize=8, weight="bold")
    d = 0.11
    ax.add_patch(Polygon([(0.17, 1.85), (0.28, 1.85), (0.28, 2.0), (yd + d / 2, 2.25), (yd - d / 2, 2.25), (0.17, 2.0)],
                         fc="#bbb", ec="k"))
    ax.add_patch(Rectangle((yd - d / 2, 2.25), d, 1.25, fc="#bbb", ec="k"))
    ax.add_patch(Polygon([(yd - 0.10, 3.50), (yd + 0.10, 3.50), (yd, 3.60)], fc="#888", ec="k"))
    zr = zb(yd) + H_T + 0.05
    ax.add_patch(Polygon([(yd - 0.18, zr + 0.18 * PEND + 0.005), (yd + 0.18, zr - 0.18 * PEND + 0.005),
                          (yd + 0.18, zr - 0.18 * PEND + 0.02), (yd - 0.18, zr + 0.18 * PEND + 0.02)], fc="#5f6b73", ec="k"))
    ax.add_patch(Polygon([(yd - d / 2 - 0.01, zr + (d / 2) * PEND + 0.02), (yd + d / 2 + 0.01, zr - (d / 2) * PEND + 0.02),
                          (yd + d / 2 + 0.01, zr + 0.14), (yd - d / 2 - 0.01, zr + 0.14)], fc="#7d8a91", ec="k"))
    # ángulo
    ax.text(yd + 0.20, zr + 0.06, f"{90 + math.degrees(ALFA):.1f}°", fontsize=10, weight="bold", color="#c0392b")
    ax.text(yd - 0.40, zr + 0.13, f"{90 - math.degrees(ALFA):.1f}°", fontsize=10, weight="bold", color="#c0392b")
    notas = [((yd, 3.5), (1.5, 3.55), "sombrerete"),
             ((yd + d / 2, zr + 0.10), (1.5, 3.25), "1 · collarín (escantillón)"),
             ((yd + 0.15, zr), (1.6, 2.95), "2 · base del forro con agujero elíptico"),
             ((0.6, 2.1), (1.2, 1.75), "codo para separarse\ndel muro de la cabaña"),
             ((-0.2, 3.1), (-0.9, 3.55), "alero existente:\nla salida debe quedar\nFUERA y SOBRE él")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=8.5, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.6),
                    bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(-1.2, 3.1); ax.set_ylim(-0.1, 3.8)
    ax.set_title(f"CORTE · techo {PEND * 100:.1f} % ({math.degrees(ALFA):.1f}°)".replace(".", ","), fontsize=11, weight="bold")
    # tabla de medidas
    ax = fig.add_axes([0.60, 0.40, 0.38, 0.45]); ax.axis("off")
    filas = []
    for D in DIAMETROS:
        filas.append([f"Ø {D}", f"{math.pi * D:.0f}", f"{D * math.tan(ALFA):.1f}", f"{D / math.cos(ALFA) + 2:.1f} x {D + 2}"])
    t = ax.table(cellText=filas, colLabels=["Ducto (mm)", "Desarrollo collarín (mm)", "Diferencia de alto\ndel corte (mm)",
                                            "Agujero elíptico (mm)"], loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(9.5); t.scale(1, 1.8)
    ax.set_title("MEDIDAS DEL ESCANTILLÓN SEGÚN DIÁMETRO", fontsize=10.5, weight="bold")
    ax = fig.add_axes([0.60, 0.08, 0.38, 0.30]); ax.axis("off")
    ax.text(0, 1, "PARA EL HOJALATERO", fontsize=11, weight="bold", va="top")
    ax.text(0, 0.88, (
        f"• Ángulo del techo: {math.degrees(ALFA):.1f}° (pendiente {PEND * 100:.1f} %).\n"
        f"• Ducto vertical: forma {90 - math.degrees(ALFA):.1f}° con el techo por el lado alto\n"
        f"  (hacia la casa) y {90 + math.degrees(ALFA):.1f}° por el lado bajo (hacia el alero).\n"
        "• Escantillón 1:1 imprimible: archivo escantillon_ducto_calefon.pdf\n"
        "  (una hoja A3 por diámetro: 80, 100, 110 y 125 mm).\n"
        "• Ver lámina 12d: detalle del ángulo y falsa escuadra 1:1.\n"
        "• Confirmar con instalador SEC altura de salida y distancias."),
        fontsize=9.5, va="top", linespacing=1.5)
    fig.savefig(OUT + "12_ducto_calefon.png", dpi=110)
    return fig

# ---------------- BASE DEL FORRO desde el muro (va bajo el forro de atraque) ----------------
X_REF = 0.75        # distancia horizontal muro → eje del ducto (REFERENCIAL: medir en obra)
ANCHO_BASE = 600    # mm, de cresta a cresta de la plancha trapezoidal (ajustar a la onda real)
DOBLEZ = 50         # mm, pestaña que sube por el muro bajo el forro de atraque
BAJO_DUCTO = 200    # mm que la base sigue más abajo del ducto, montada SOBRE la plancha

def largo_base(X, D):
    """largo de la base medido sobre la pendiente, desde el muro hasta su borde bajo (mm)."""
    return (X * 1000 + D / 2) / math.cos(ALFA) + BAJO_DUCTO

def lamina_base():
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.text(0.04, 0.95, "AMPLIACIÓN CABAÑA – LAGO TODOS LOS SANTOS", fontsize=16, weight="bold")
    fig.text(0.04, 0.92, "Lámina 12b: BASE DEL DUCTO DEL CALEFÓN · nace en el muro y entra bajo el forro de atraque",
             fontsize=10, color="#444")
    D = 100
    # ---- CORTE ----
    ax = fig.add_axes([0.02, 0.40, 0.56, 0.50]); ax.set_aspect("equal"); ax.axis("off")
    zr = lambda y: 2.80 - PEND * y          # cara de la plancha (referencial)
    ax.add_patch(Rectangle((-0.30, 2.30), 0.30, 0.85, fc="#e6e6e6", ec="k", hatch="//"))
    ax.plot([-0.45, 0.25], [3.03 + 0.04, 3.03 - 0.03], color="#555", lw=6)
    ax.text(-0.15, 2.55, "MURO\nCABAÑA", ha="center", fontsize=8, weight="bold", bbox=dict(fc="white", ec="none"))
    yb = X_REF + D / 2000 + BAJO_DUCTO / 1000
    # plancha trapezoidal
    ax.plot([0, 1.35], [zr(0), zr(1.35)], color="#555", lw=3, zorder=2)
    # base del forro (azul)
    ax.plot([0.004, 0.004, yb], [zr(0) + DOBLEZ / 1000, zr(0) + 0.006, zr(yb) + 0.006], color="#2c7fb8", lw=4,
            solid_capstyle="round", zorder=4)
    # forro de atraque (gris) por encima de la base
    ax.plot([-0.008, 0.0, 0.0, 0.22, 0.24], [2.98, 2.98, zr(0) + 0.03, zr(0.22) + 0.03, zr(0.24) + 0.012], color="#5f6b73",
            lw=4, zorder=5)
    # ducto + collarín
    d = D / 1000
    ax.add_patch(Rectangle((X_REF - d / 2, zr(X_REF) - 0.30), d, 0.95, fc="#bbb", ec="k", zorder=3))
    ax.add_patch(Polygon([(X_REF - d / 2 - 0.006, zr(X_REF - d / 2) + 0.006), (X_REF + d / 2 + 0.006, zr(X_REF + d / 2) + 0.006),
                          (X_REF + d / 2 + 0.006, zr(X_REF) + 0.10), (X_REF - d / 2 - 0.006, zr(X_REF) + 0.10)],
                         fc="#7d8a91", ec="k", zorder=6))
    ax.add_patch(Polygon([(X_REF - 0.10, zr(X_REF) + 0.65), (X_REF + 0.10, zr(X_REF) + 0.65), (X_REF, zr(X_REF) + 0.73)],
                         fc="#888", ec="k"))
    def ch(a, b, z, t):
        ax.annotate("", (a, z), (b, z), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text((a + b) / 2, z - 0.05, t, ha="center", va="top", fontsize=8.5, bbox=dict(fc="white", ec="none", pad=0.3))
    ch(0, X_REF, 2.42, "X = muro → eje ducto\n(MEDIR EN OBRA)")
    ch(X_REF + d / 2, yb, 2.42, f"{BAJO_DUCTO / 10:.0f} cm")
    notas = [((0.004, zr(0) + 0.03), (-0.25, 2.18), f"pestaña {DOBLEZ / 10:.0f} cm sube por\nel muro BAJO el forro"),
             ((0.12, zr(0.12) + 0.03), (0.35, 3.08), "forro de atraque (existente en\nel proyecto, DET. 3) va ENCIMA"),
             ((0.45, zr(0.45) + 0.006), (0.55, 2.62), "BASE (este escantillón):\nnace en el muro, va bajo el forro\ny SOBRE la plancha hacia abajo"),
             ((X_REF + d / 2, zr(X_REF) + 0.06), (1.15, 3.00), "collarín remachado y\nsellado a la base"),
             ((yb, zr(yb) + 0.006), (1.20, 2.62), "borde bajo SOBRE la plancha:\nel agua escurre hacia afuera"),
             ((1.1, zr(1.1)), (1.25, 2.30), "plancha trapezoidal")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=8, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.6),
                    bbox=dict(fc="white", ec="none", pad=0.5), zorder=9)
    ax.set_xlim(-0.55, 1.45); ax.set_ylim(2.05, 3.25)
    ax.set_title("CORTE · orden de las piezas (de arriba hacia abajo: forro → base → plancha)", fontsize=10.5, weight="bold")

    # ---- PLANTA DE LA BASE (desarrollo, escala referencial) ----
    ax = fig.add_axes([0.60, 0.08, 0.38, 0.82]); ax.set_aspect("equal"); ax.axis("off")
    Lb = largo_base(X_REF, D); W = ANCHO_BASE
    ax.add_patch(Rectangle((0, -DOBLEZ), W, DOBLEZ, fc="#d6eaf8", ec="#2c7fb8", lw=1.2, ls="--"))
    ax.add_patch(Rectangle((0, 0), W, Lb, fc="#d6eaf8", ec="#2c7fb8", lw=2))
    yc = (X_REF * 1000) / math.cos(ALFA)
    ax.add_patch(Ellipse((W / 2, yc), D + 2, D / math.cos(ALFA) + 2, fc="white", ec="k", lw=1.5))
    ax.text(W / 2, -DOBLEZ / 2, f"pestaña {DOBLEZ} mm (doblar 90° hacia arriba, contra el muro)", ha="center", va="center", fontsize=8)
    ax.text(W / 2, Lb - 60, "borde bajo: queda SOBRE la plancha", ha="center", fontsize=8.5)
    ax.text(W / 2, yc - D / 2 - 40, "agujero elíptico\n(ver hoja 1:1 del diámetro)", ha="center", fontsize=8)
    def dv(x, a, b, t):
        ax.annotate("", (x, a), (x, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(x - 12, (a + b) / 2, t, rotation=90, ha="right", va="center", fontsize=8.5, bbox=dict(fc="white", ec="none", pad=0.3))
    dv(-30, 0, yc, "X / 0,993")
    dv(-80, 0, Lb, f"LARGO = X/0,993 + D/2/0,993 + {BAJO_DUCTO}")
    ax.annotate("", (0, Lb + 40), (W, Lb + 40), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(W / 2, Lb + 55, f"ANCHO ≈ {W} mm: de cresta a cresta de la plancha (ajustar a la onda)", ha="center", va="top",
            fontsize=8.5)
    ax.text(W + 20, 0, "MURO\n(arriba)", fontsize=8.5, weight="bold", va="center")
    ax.text(W + 20, Lb, "ALERO\n(abajo)", fontsize=8.5, weight="bold", va="center")
    ax.set_xlim(-200, W + 140); ax.set_ylim(Lb + 160, -DOBLEZ - 120)
    ax.set_title("BASE DESPLEGADA (vista desde arriba)", fontsize=10.5, weight="bold")

    # ---- tabla ----
    ax = fig.add_axes([0.04, 0.06, 0.52, 0.28]); ax.axis("off")
    filas = []
    for X in (0.50, 0.60, 0.75, 1.00):
        filas.append([f"{X:.2f}"] + [f"{largo_base(X, D) + DOBLEZ:.0f}" for D in DIAMETROS])
    t = ax.table(cellText=filas, colLabels=["X (m)"] + [f"Ø {D}" for D in DIAMETROS], loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(9.5); t.scale(1, 1.6)
    ax.set_title("LARGO TOTAL DE LA BASE en mm (incluye pestaña de 5 cm), según X y diámetro", fontsize=10, weight="bold")
    ax.text(0, 0.12, ("Material: zincalum liso 0,4 mm (de las planchas lisas de la hojalatería). Bordes laterales sobre crestas,\n"
                      "sellados con cinta butílica. Si me das X y el diámetro reales, genero la hoja 1:1 exacta."),
            fontsize=9, va="top", transform=ax.transAxes)
    fig.savefig(OUT + "12b_base_ducto_calefon.png", dpi=110)
    return fig

# ---------------- ESCANTILLÓN DEFINITIVO con medidas de obra ----------------
D_OBRA = 127          # mm = 5" (confirmado)
SEP_MURO = 340        # mm, del muro a la cara del ducto = justo topando el tapacán del alero existente (34 cm)
X_OBRA = (SEP_MURO + D_OBRA / 2) / 1000   # m, muro → eje
ALERO_EX = 0.34       # m, salida del alero existente (medido)
TAPACAN_EX = 0.10     # m, tapacán del alero existente (medido)
SUBIDA = 120          # mm, pestaña que sube por el muro bajo el forro de atraque
ANCHO_OBRA = 560      # mm, de cresta a cresta (ajustar a la onda real)
BAJO_OBRA = 200       # mm bajo el ducto, sobre la plancha
LARGO_OBRA = (SEP_MURO + D_OBRA) / math.cos(ALFA) + BAJO_OBRA   # mm sobre la pendiente (sin la pestaña)

def lamina_obra():
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.text(0.04, 0.95, "AMPLIACIÓN CABAÑA – LAGO TODOS LOS SANTOS", fontsize=16, weight="bold")
    fig.text(0.04, 0.92, f"Lámina 12c: DUCTO CALEFÓN · le hace el quite al alero: sube topando el tapacán (cara a {SEP_MURO / 10:.0f} cm del muro) · Ø 5\" ({D_OBRA} mm)",
             fontsize=10, color="#444")
    # ---- CORTE ----
    ax = fig.add_axes([0.02, 0.07, 0.50, 0.82]); ax.set_aspect("equal"); ax.axis("off")
    zp = lambda y: 2.63 + 0.165 / math.cos(ALFA) + 0.045 - PEND * y      # cara superior plancha nueva
    z_sof = 3.03                                                         # bajo alero existente en el muro
    ax.add_patch(Rectangle((-0.35, 2.2), 0.35, z_sof - 2.2, fc="#e6e6e6", ec="k", hatch="//"))
    ax.text(-0.17, 2.5, "MURO\nCABAÑA", ha="center", fontsize=8, weight="bold", bbox=dict(fc="white", ec="none"))
    # alero existente (como el croquis)
    ax.add_patch(Polygon([(-0.6, z_sof - 0.05), (ALERO_EX, z_sof + 0.06), (ALERO_EX, z_sof + 0.06 + TAPACAN_EX),
                          (-0.6, z_sof + 0.10)], fc="#cfcfcf", ec="k"))
    ax.text(-0.35, z_sof + 0.15, "alero / techo EXISTENTE", fontsize=8)
    # techo nuevo
    ax.add_patch(Polygon([(0.019, zp(0.019) - 0.045 - 0.165), (0.9, zp(0.9) - 0.045 - 0.165), (0.9, zp(0.9) - 0.045), (0.019, zp(0.019) - 0.045)],
                         fc="#e8c891", ec="k"))
    ax.plot([0, 0.9], [zp(0), zp(0.9)], color="#555", lw=3)
    # base (azul) con subida
    yb = (SEP_MURO + D_OBRA) / 1000 + BAJO_OBRA / 1000
    ax.plot([0.004, 0.004, yb], [zp(0) + SUBIDA / 1000, zp(0) + 0.005, zp(yb) + 0.005], color="#2c7fb8", lw=4, zorder=4)
    # forro de atraque encima
    ax.plot([-0.008, 0.0, 0.0, 0.22, 0.24], [zp(0) + SUBIDA / 1000 + 0.04, zp(0) + SUBIDA / 1000 + 0.04, zp(0) + 0.03,
            zp(0.22) + 0.03, zp(0.22) + 0.012], color="#5f6b73", lw=4, zorder=5)
    # ducto
    d = D_OBRA / 1000; xa = SEP_MURO / 1000
    ax.add_patch(Rectangle((0.03, 1.35), 0.30, 0.55, fc="white", ec="k", lw=1.5, zorder=3))
    ax.text(0.18, 1.62, "CALEFÓN", ha="center", fontsize=8, weight="bold", zorder=4)
    ax.add_patch(Polygon([(0.13, 1.90), (0.13 + d, 1.90), (0.13 + d, 2.00), (xa + d, 2.30), (xa, 2.30), (0.13, 2.00)],
                         fc="#bbb", ec="k", zorder=3))
    ax.add_patch(Rectangle((xa, 2.30), d, 1.25, fc="#bbb", ec="k", zorder=3))
    ax.add_patch(Polygon([(xa - 0.05, 3.55), (xa + d + 0.05, 3.55), (xa + d / 2, 3.63)], fc="#888", ec="k", zorder=3))
    ax.add_patch(Rectangle((xa - 0.006, zp(xa + d)), d + 0.012, 0.10, fc="#7d8a91", ec="k", zorder=6))
    def ch(a, b, z, t, dy=0.03):
        ax.annotate("", (a, z), (b, z), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text((a + b) / 2, z + dy, t, ha="center", fontsize=8.5, weight="bold", bbox=dict(fc="white", ec="none", pad=0.3))
    ch(0, ALERO_EX, 3.42, "34 cm (alero existente)")
    ch(0, xa, 2.20, f"{SEP_MURO / 10:.0f} cm a la cara del ducto", dy=-0.07)
    notas = [((ALERO_EX, z_sof + 0.11), (0.65, 3.35), "tapacán 10 cm"),
             ((xa, z_sof + 0.12), (0.75, 3.20), "sube TOPANDO el tapacán:\nle hace el quite al alero"),
             ((0.25, 2.12), (0.70, 2.05), "codos 45° para separarse\ndel muro hasta el tapacán"),
             ((0.004, zp(0) + 0.08), (-0.45, 2.85), f"base: sube {SUBIDA / 10:.0f} cm por el\nmuro BAJO el forro de atraque"),
             ((0.35, zp(0.35) + 0.006), (0.65, 2.55), "base sobre la plancha\nhacia abajo"),
             ((xa + d, zp(xa + d) + 0.05), (0.7, 2.80), "collarín 83,3° / 96,7°")]
    for p, t, tx in notas:
        ax.annotate(tx, p, t, fontsize=8, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.6),
                    bbox=dict(fc="white", ec="none", pad=0.5), zorder=9)
    ax.set_xlim(-0.65, 1.05); ax.set_ylim(1.25, 3.70)
    ax.set_title("CORTE CON MEDIDAS DE OBRA", fontsize=11, weight="bold")
    # ---- BASE desplegada con cotas ----
    ax = fig.add_axes([0.54, 0.30, 0.44, 0.60]); ax.set_aspect("equal"); ax.axis("off")
    W, Lb = ANCHO_OBRA, LARGO_OBRA
    ax.add_patch(Rectangle((0, -SUBIDA), W, SUBIDA, fc="#d6eaf8", ec="#2c7fb8", lw=1.2, ls="--"))
    ax.add_patch(Rectangle((0, 0), W, Lb, fc="#d6eaf8", ec="#2c7fb8", lw=2))
    yc = (SEP_MURO + D_OBRA / 2) / math.cos(ALFA)
    ax.add_patch(Ellipse((W / 2, yc), D_OBRA + 2, D_OBRA / math.cos(ALFA) + 2, fc="white", ec="k", lw=1.5))
    ax.plot([-20, W + 20], [0, 0], color="#c0392b", lw=1, ls="-.")
    ax.text(W + 25, 0, "línea de doblez\n(esquina muro)", fontsize=8, color="#c0392b", va="center")
    ax.text(W / 2, -SUBIDA / 2, f"PESTAÑA {SUBIDA} mm · doblar 90° hacia arriba\n(sube por el muro bajo el forro de atraque)",
            ha="center", va="center", fontsize=8)
    def dv(x, a, b, t):
        ax.annotate("", (x, a), (x, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(x - 8, (a + b) / 2, t, rotation=90, ha="right", va="center", fontsize=8.5, bbox=dict(fc="white", ec="none", pad=0.3))
    dv(W / 2 - D_OBRA / 2 - 20, 0, yc - D_OBRA / 2 / math.cos(ALFA) - 1, f"{(SEP_MURO / math.cos(ALFA)) - 1:.0f}")
    dv(-30, 0, yc, f"{yc:.0f} al centro")
    dv(-90, -SUBIDA, Lb, f"LARGO TOTAL {Lb + SUBIDA:.0f} mm")
    ax.annotate("", (0, Lb + 30), (W, Lb + 30), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(W / 2, Lb + 45, f"ANCHO {W} mm (de cresta a cresta; ajustar a la onda real) · agujero centrado", ha="center",
            va="top", fontsize=8.5)
    ax.text(W / 2, Lb - 40, "borde bajo SOBRE la plancha", ha="center", fontsize=8.5)
    ax.set_xlim(-180, W + 140); ax.set_ylim(Lb + 120, -SUBIDA - 60)
    ax.set_title("BASE DESPLEGADA · medidas en mm (vista desde arriba)", fontsize=10.5, weight="bold")
    # ---- notas ----
    ax = fig.add_axes([0.54, 0.04, 0.44, 0.24]); ax.axis("off")
    ax.text(0, 1, "IMPORTANTE", fontsize=11, weight="bold", va="top", color="#c0392b")
    ax.text(0, 0.86, (
        "• El ducto sube pegado al tapacán y PASA POR FUERA del alero. El sombrerete debe quedar\n"
        "  POR SOBRE el techo existente (no a la altura del alero). Confirmar altura con instalador SEC.\n"
        "• Separación a la madera: ducto doble pared o protección aislante donde toque el tapacán.\n"
        "• En el techo nuevo el ducto cae a 34–44 cm del muro: CHOCA con la costanera de 45 cm.\n"
        "  Cortarla y apoyar sus extremos en un trozo 2x2 a cada lado (dejar ≥ 5 cm al ducto).\n"
        "  Ubicar el ducto ENTRE dos tijerales (quedan 55 cm libres entre ellos).\n"
        "• Ducto Ø 5\" (127 mm)."),
        fontsize=9, va="top", linespacing=1.45)
    fig.savefig(OUT + "12c_ducto_calefon_obra.png", dpi=110)
    return fig

def pagina_obra_1a1(pdf):
    """Hoja A3 1:1: zona de la base con la línea de doblez y el agujero en su posición exacta + collarín."""
    W, H = 420, 297
    fig = plt.figure(figsize=(W * MM, H * MM))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    ax.text(15, 282, f"ESCANTILLÓN 1:1 DEFINITIVO · Ø {D_OBRA} mm · ducto a {SEP_MURO} mm del muro · techo {PEND * 100:.1f} %".replace(".", ","),
            fontsize=12, weight="bold")
    ax.text(15, 274, "Imprimir A3 al 100 %. Verificar la regla (100 mm). Esta hoja marca el agujero 1:1;"
            " el resto de la base es un rectángulo (ver lámina 12c).", fontsize=8.5, color="#c0392b")
    ax.plot([15, 115], [266, 266], color="k", lw=1.5)
    for k in range(0, 101, 10):
        ax.plot([15 + k, 15 + k], [266, 269 if k % 50 else 271], color="k", lw=0.8)
    ax.text(120, 265, "← 100 mm", fontsize=8)
    # zona de la base (eje del ducto en x = 110)
    cx = 110; yc = 140
    yd = yc + (SEP_MURO + D_OBRA / 2) / math.cos(ALFA)   # doblez (fuera de la hoja)
    borde = (SEP_MURO / math.cos(ALFA)) - 1
    ax.annotate("", (cx - 70, 255), (cx - 70, yc + (D_OBRA / math.cos(ALFA) + 2) / 2),
                arrowprops=dict(arrowstyle="->", lw=1, color="#c0392b"))
    ax.text(cx - 66, 238, f"hacia la línea de DOBLEZ (muro):\n{borde:.0f} mm desde el borde del agujero\n(medir con huincha)",
            fontsize=8.5, color="#c0392b", va="top")
    ax.add_patch(Ellipse((cx, yc), D_OBRA + 2, D_OBRA / math.cos(ALFA) + 2, fill=False, ec="k", lw=1.8))
    ax.plot([cx, cx], [20, 255], color="#2c7fb8", lw=0.7, ls="-.")
    ax.plot([cx - 80, cx + 80], [yc, yc], color="#2c7fb8", lw=0.7, ls="-.")
    ax.text(cx + 3, 24, "eje (centro de la base)", fontsize=7.5, color="#2c7fb8")
    ax.text(cx - 93, 25, "↓ hacia el alero (la base sigue\n   hasta completar el largo)", fontsize=7.5)
    ax.text(240, 200, (f"COLLARÍN: usar la hoja 1:1 'Ø {D_OBRA} mm' de este mismo PDF\n"
                       f"(desarrollo {math.pi * D_OBRA:.0f} mm + 10 de traslapo, curva de {D_OBRA * math.tan(ALFA):.1f} mm).\n\n"
                       "Collarín remachado y sellado a la base.\n\n"
                       f"Base completa: {ANCHO_OBRA} x {LARGO_OBRA + SUBIDA:.0f} mm\n"
                       f"(pestaña {SUBIDA} + {LARGO_OBRA:.0f} sobre el techo)."),
            fontsize=9, va="top", linespacing=1.5)
    pdf.savefig(fig); plt.close(fig)


# ---------------- DETALLE DEL ÁNGULO TECHO / DUCTO ----------------
def lamina_angulo():
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.text(0.04, 0.95, "AMPLIACIÓN CABAÑA – LAGO TODOS LOS SANTOS", fontsize=16, weight="bold")
    fig.text(0.04, 0.92, f"Lámina 12d: ÁNGULO ENTRE EL TECHO Y EL DUCTO DE 5\" ({D_OBRA} mm) · techo {PEND * 100:.1f} %".replace(".", ","),
             fontsize=10, color="#444")
    a = math.degrees(ALFA); D = D_OBRA; r = D / 2; dz = D * math.tan(ALFA)
    # ---- corte ampliado por el eje del ducto (mm) ----
    ax = fig.add_axes([0.03, 0.10, 0.55, 0.78]); ax.set_aspect("equal"); ax.axis("off")
    zr = lambda x: -PEND * x                          # techo: sube hacia la izquierda (casa)
    ax.plot([-260, 260], [zr(-260), zr(260)], color="#555", lw=5)
    ax.text(-250, zr(-250) + 18, "← CASA (sube)", fontsize=10, weight="bold")
    ax.text(150, zr(150) - 30, "ALERO (baja) →", fontsize=10, weight="bold")
    ax.add_patch(Rectangle((-r, -160), D, 420, fc="#d0d0d0", ec="k", lw=1.5, zorder=2))
    ax.plot([0, 0], [-170, 270], color="#2c7fb8", lw=0.8, ls="-.")
    # collarín
    hc = 80
    ax.add_patch(Polygon([(-r - 3, zr(-r)), (r + 3, zr(r)), (r + 3, zr(-r) + hc), (-r - 3, zr(-r) + hc)],
                         fc="#7d8a91", ec="k", lw=1.2, zorder=3, alpha=0.9))
    # arcos de ángulo
    from matplotlib.patches import Arc
    R = 70
    ax.add_patch(Arc((-r, zr(-r)), 2 * R, 2 * R, theta1=90, theta2=180 - a, color="#c0392b", lw=1.8, zorder=5))
    ax.text(-r - 75, zr(-r) + 55, f"{90 - a:.1f}°", fontsize=15, weight="bold", color="#c0392b", zorder=6)
    ax.add_patch(Arc((r, zr(r)), 2 * R, 2 * R, theta1=-a, theta2=90, color="#c0392b", lw=1.8, zorder=5))
    ax.text(r + 30, zr(r) + 55, f"{90 + a:.1f}°", fontsize=15, weight="bold", color="#c0392b", zorder=6)
    # ángulo del techo con la horizontal
    ax.plot([60, 230], [zr(60), zr(60)], color="#2c7fb8", lw=1, ls="--")
    ax.add_patch(Arc((60, zr(60)), 300, 300, theta1=-a, theta2=0, color="#2c7fb8", lw=1.5))
    ax.text(215, zr(60) + 4, f"{a:.1f}° (techo)", fontsize=10, color="#2c7fb8", weight="bold")
    # diferencia de altura del corte
    ax.annotate("", (r + 25, zr(-r)), (r + 25, zr(r)), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.plot([-r, r + 30], [zr(-r), zr(-r)], color="k", lw=0.6, ls=":")
    ax.text(r + 30, (zr(-r) + zr(r)) / 2 - 2, f"{dz:.1f} mm", fontsize=10, weight="bold")
    ax.annotate("", (-r, -185), (r, -185), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(0, -205, f"Ø {D} mm (5\")", ha="center", fontsize=10, weight="bold")
    ax.annotate(f"collarín {hc} mm de alto", (-r, zr(-r) + hc * 0.8), (-200, 170), fontsize=9, ha="center", arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.text(0, 200, "DUCTO\n(vertical)", ha="center", fontsize=10, weight="bold", zorder=4,
            bbox=dict(fc="white", ec="none"))
    ax.text(-250, -120, "plancha / base de zincalum", fontsize=9, color="#555")
    ax.set_xlim(-300, 320); ax.set_ylim(-230, 290)
    ax.set_title("CORTE POR EL EJE DEL DUCTO (ampliado, medidas en mm)", fontsize=11, weight="bold")
    # ---- tabla de medidas ----
    ax = fig.add_axes([0.60, 0.50, 0.38, 0.38]); ax.axis("off")
    filas = [["Ángulo del techo con la horizontal", f"{a:.1f}°  (pendiente {PEND * 100:.1f} %)"],
             ["Ducto / techo, lado CASA (arriba)", f"{90 - a:.1f}°"],
             ["Ducto / techo, lado ALERO (abajo)", f"{90 + a:.1f}°"],
             ["Diámetro ducto", f"5\" = {D} mm"],
             ["Desarrollo del collarín", f"{math.pi * D:.0f} mm + 10 de traslapo"],
             ["Diferencia de alto del corte", f"{dz:.1f} mm (más largo al lado alero)"],
             ["Agujero en la base (elipse)", f"{D / math.cos(ALFA) + 2:.1f} x {D + 2} mm"],
             ["Falsa escuadra (cateto 300 mm)", f"subir {300 * PEND:.1f} mm"]]
    t = ax.table(cellText=filas, colLabels=["Dato", "Valor"], loc="upper center", cellLoc="left", colWidths=[0.55, 0.45])
    t.auto_set_font_size(False); t.set_fontsize(10); t.scale(1, 1.7)
    ax.set_title("DATOS PARA LA CONFECCIÓN", fontsize=11, weight="bold")
    ax = fig.add_axes([0.60, 0.10, 0.38, 0.36]); ax.axis("off")
    ax.text(0, 1, "CÓMO SE USA", fontsize=11, weight="bold", va="top")
    ax.text(0, 0.88, (
        f"1. Con la falsa escuadra (hoja 1:1 del PDF) o con una regla: en 300 mm\n"
        f"   de largo el techo sube {300 * PEND:.0f} mm → ese es el ángulo de {a:.1f}°.\n"
        f"2. El collarín se corta con la hoja 1:1 del ducto de 5\": la curva\n"
        f"   de abajo sube y baja {dz / 2:.1f} mm a cada lado del promedio.\n"
        f"3. Al enrollarlo, el lado más corto va hacia la CASA ({90 - a:.1f}°)\n"
        f"   y el más largo hacia el ALERO ({90 + a:.1f}°).\n"
        "4. Comprobar en obra apoyando la falsa escuadra en la plancha\n"
        "   y el nivel/plomada en el ducto."),
        fontsize=10, va="top", linespacing=1.5)
    fig.savefig(OUT + "12d_angulo_ducto.png", dpi=110)
    return fig

def pagina_falsa_escuadra(pdf):
    W, H = 420, 297
    fig = plt.figure(figsize=(W * MM, H * MM))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    a = math.degrees(ALFA)
    ax.text(15, 282, f"FALSA ESCUADRA 1:1 · ángulo del techo {a:.1f}° · ducto / techo {90 - a:.1f}° y {90 + a:.1f}°".replace(".", ","),
            fontsize=12, weight="bold")
    ax.text(15, 274, "Imprimir A3 al 100 %. Verificar la regla (100 mm). Recortar por las líneas gruesas.", fontsize=8.5, color="#c0392b")
    ax.plot([15, 115], [266, 266], color="k", lw=1.5)
    for k in range(0, 101, 10):
        ax.plot([15 + k, 15 + k], [266, 269 if k % 50 else 271], color="k", lw=0.8)
    # plantilla A: ángulo del techo (triángulo 300 mm)
    x0, y0, Lt = 20, 175, 300
    ax.add_patch(Polygon([(x0, y0), (x0 + Lt, y0), (x0 + Lt, y0 + Lt * PEND)], fill=False, ec="k", lw=2))
    ax.text(x0 + Lt / 2, y0 - 8, f"{Lt} mm (horizontal)", ha="center", fontsize=9)
    ax.text(x0 + Lt + 4, y0 + Lt * PEND / 2, f"{Lt * PEND:.1f} mm", va="center", fontsize=9)
    ax.text(x0 + 45, y0 + 4, f"{a:.1f}°", fontsize=11, weight="bold", color="#c0392b")
    ax.text(x0, y0 + 50, "A · ÁNGULO DEL TECHO (apoyar la hipotenusa en la plancha)", fontsize=9, weight="bold")
    # plantilla B: ducto / techo
    bx, by = 170, 55
    ax.plot([bx, bx], [by, by + 70], color="k", lw=2.2)
    ax.plot([bx - 150, bx + 200], [by + 150 * PEND, by - 200 * PEND], color="k", lw=2.2)
    from matplotlib.patches import Arc
    ax.add_patch(Arc((bx, by), 70, 70, theta1=90, theta2=180 - a, color="#c0392b", lw=1.5))
    ax.add_patch(Arc((bx, by), 70, 70, theta1=-a, theta2=90, color="#c0392b", lw=1.5))
    ax.text(bx - 60, by + 32, f"{90 - a:.1f}°\nlado CASA", fontsize=11, weight="bold", color="#c0392b", ha="center")
    ax.text(bx + 55, by + 32, f"{90 + a:.1f}°\nlado ALERO", fontsize=11, weight="bold", color="#c0392b", ha="center")
    ax.text(bx + 4, by + 64, "ducto (vertical)", fontsize=9)
    ax.text(bx + 150, by - 150 * PEND + 6, "techo", fontsize=9)
    ax.text(15, 135, "B · ÁNGULOS DUCTO / TECHO (para el collarín y la base)", fontsize=9, weight="bold")
    pdf.savefig(fig); plt.close(fig)

if __name__ == "__main__":
    fig3 = lamina_obra()
    with PdfPages(OUT + "escantillon_ducto_calefon.pdf") as pdf:
        pdf.savefig(lamina_explicativa()); pdf.savefig(lamina_base()); pdf.savefig(fig3)
        pdf.savefig(lamina_angulo())
        pagina_obra_1a1(pdf)
        pagina_falsa_escuadra(pdf)
        plt.close("all")
        for D in DIAMETROS:
            pagina_escantillon(pdf, D)
    print("largo base", round(LARGO_OBRA + SUBIDA), "centro", round((SEP_MURO + D_OBRA / 2) / math.cos(ALFA)))
