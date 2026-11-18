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
DIAMETROS = [80, 100, 110, 125]        # mm, diámetros usuales de ducto de calefón
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
    x0, y0 = 12, 142
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
        "• Medir el diámetro real del ducto y usar esa hoja.\n"
        "• Confirmar con instalador SEC altura de salida y distancias."),
        fontsize=9.5, va="top", linespacing=1.5)
    fig.savefig(OUT + "12_ducto_calefon.png", dpi=110)
    return fig

if __name__ == "__main__":
    fig = lamina_explicativa()
    with PdfPages(OUT + "escantillon_ducto_calefon.pdf") as pdf:
        pdf.savefig(fig); plt.close(fig)
        for D in DIAMETROS:
            pagina_escantillon(pdf, D)
    print("ok", math.degrees(ALFA))
