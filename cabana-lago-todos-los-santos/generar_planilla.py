"""Planilla Excel de materiales valorizada (Sodimac / Easy)."""
import math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import os
BASE = os.path.dirname(os.path.abspath(__file__)) + "/"
ns = {"__file__": BASE + "generar_planos.py"}
exec(open(BASE + "generar_planos.py").read().split("\ndef planta(ax):")[0], ns)
T = ns["TOT_TORN"]; TIPOS = ns["TIPOS"]; USOS = ns["USOS_TORN"]
PLANCHAS = ns["PLANCHAS"]
nT = sum(1 for p in PLANCHAS if p[2] == "T"); nO = len(PLANCHAS) - nT

SOD = "Sodimac"; EASY = "Easy"; EST = "Estimado"; IMP = "Imperial"
L = {
    "sopviga": "https://www.easy.cl/soporte-viga-2x4-simpson-1203253/p",
    "h25a": "https://www.easy.cl/soporte-sismoviento-h25a-simpson-strong-tie-149017/p",
    "1x8": "https://www.sodimac.cl/sodimac-cl/articulo/110314701/Pino-Certificado-Seco-Cepillado-1x8-3,2-m/110314729",
    "canal": "https://www.sodimac.cl/sodimac-cl/lista/CATG10941/Canaleta-de-Agua-y-Accesorios",
    "union": "https://www.easy.cl/union-canaleta-pvc-cafe-1211422/p",
    "tapa": "https://www.easy.cl/tapa-canaleta-pvc-cafe-1211429/p",
    "gancho": "https://www.easy.cl/ferreteria-y-gasfiteria/gasfiteria/canaletas",
    "tubo": "https://www.sodimac.cl/sodimac-cl/articulo/110318593/Tubo-para-bajada-de-PVC-3-m-80-mm/110318595",
    "codo": "https://www.easy.cl/materiales-de-construccion/techumbre/canaletas-y-bajadas-de-agua-lluvia-pvc",
    "abraz": "https://www.easy.cl/abrazadera-tubo-de-bajada-pvc-cafe-1211424/p",
    "lisa": "https://www.easy.cl/materiales-de-construccion/techumbre/planchas-zincalum",
    "2x6": "https://www.easy.cl/pino-impregnado-micronizado-2x6-32-m-1155432/p",
    "2x4": "https://www.sodimac.cl/sodimac-cl/b/pino-impregnado-2x4",
    "2x3": "https://www.sodimac.cl/sodimac-cl/b/pino-impregnado-2x3",
    "2x2": "https://www.easy.cl/pino-impregnado-micronizado-2x2-32-m-1155429/p",
    "5v": "https://www.easy.cl/plancha-zincalum-5v-035x895x3000-mm-118904/p",
    "greca": "https://www.sodimac.cl/sodimac-cl/product/5400228/plancha-policarbonato-greca-transparente-05mmx081mx25m",
    "angulo": "https://www.sodimac.cl/sodimac-cl/articulo/110299540/Angulo-de-refuerzo-2x4-/110299568",
    "puerta": "https://www.sodimac.cl/sodimac-cl/b/puerta-exterior-80x200",
    "smart": "https://www.sodimac.cl/sodimac-cl/product/238376/11,1mm-1,22x2,44-m-Smart-Side-panel-ranurado-cada-8cm/238376",
    "terciado": "https://www.sodimac.cl/sodimac-cl/lista/CATG34412/Terciado-ranurado",
    "membrana": "https://www.sodimac.cl/sodimac-cl/lista/CATG10954/Membrana-Hidrofuga-y-Tyvek",
    "t8x3": "https://www.sodimac.cl/sodimac-cl/articulo/128506956/Tornillo-Volcanita-Rosca-Madera-CRS-Zinc-8-x-3-x-250-Unidades/128506957",
    "t14x4": "https://www.sodimac.cl/sodimac-cl/articulo/110331896/Tirafondo-hexagonal-1-4X4-Pavonado-10-unidades",
    "t38": "https://www.sodimac.cl/sodimac-cl/product/13354X/Tirafondo-Hexagonal-3-8-x-4-1-2-pavonado-1-unidad",
    "techo": "https://www.easy.cl/autoperforante-hexagonal-con-golilla-12-x-112-mamut-402301/p",
}

def cajas(n, por):
    return math.ceil(n / por)

# (grupo, ítem, medida, cant. necesaria, unidad venta, cant. a comprar, precio, tienda, nota, link)
G = []
def add(g, it, med, nec, uv, comp, pr, tienda, nota="", link=""):
    G.append((g, it, med, nec, uv, comp, pr, tienda, nota, link))

g = "1. ESTRUCTURA DE TECHO"
add(g, "Tijerales c/60 cm", "Pino IPV 2x6½\" x 3,20 m", 15, "pieza", 15, 14990, EST, "precio ref. 2x6 IPV Easy; confirmar 2x6½\"", L["2x6"])
add(g, "Tabla 1x10 apernada al muro (tijerales de tope)", "Pino 1x10 cepillado 4 caras x 3,20 m", 3, "pieza", 3, 7490, EST,
    "borde bajo a 2,63 m; tornillos del soporte deben anclar en el muro", "")
add(g, "Costaneras c/40 cm", "Pino IPV 2x2 x 3,20 m", ns["N_COST"], "pieza", ns["N_COST"], 2890, EASY, "", L["2x2"])
add(g, "Tapacán vertical", "Tabla pino seco cepillado 1x8 x 3,20 m", 3, "pieza", 3, 5950, SOD,
    "1x8 impregnado no apareció en web; pintar o aplicar preservante en todas las caras", L["1x8"])
add(g, "Bloqueos entre tijerales", "Pino IPV 2x6 x 3,20 m", 1, "pieza", 1, 14990, EASY, "", L["2x6"])
add(g, "Soporte viga madera cepillada 2x6 ZMAX (muro casa)", "Simpson · Imperial SKU 142184", 15, "unidad", 15, 2590, IMP,
    "1 por tijeral", "")
add(g, "Soporte sismo y viento H3 – tijerales sobre tabique bodega", "Simpson · Imperial SKU 142181", 14, "unidad", 14, 1090, IMP,
    "7 tijerales x 2 (uno izquierdo y uno derecho)", "")
add(g, "Soporte sismo y viento H3 – tijerales sobre viga terraza", "Simpson · Imperial SKU 142181", 16, "unidad", 16, 1090, IMP,
    "RECOMENDADO: 8 tijerales x 2. La terraza es abierta y el viento levanta más", L["h25a"])
g = "2. TERRAZA"
add(g, "Viga exterior doble (recta, 4,75 m)", "Pino IPV 2x6 x 3,20 m", 4, "pieza", 4, 14990, EASY, "", L["2x6"])
add(g, "Pilares", "Pino IPV 4x4 x 3,20 m", 2, "pieza", 2, 13990, EST, "no apareció impregnado 4x4 en web; consultar", "")
add(g, "Escuadras base de pilares", "Ángulo refuerzo galv. 2x4\" Simpson", 4, "unidad", 4, 4790, SOD, "", L["angulo"])
g = "2b. PISO TERRAZA (completar rectángulo)"
add(g, "Ampliación de piso ~2,4 m² (triángulo de la diagonal)", "Según piso existente", 1, "global", 1, 0, EST,
    "POR DEFINIR: falta saber cómo está hecho el piso actual", "")
g = "3. CUBIERTA"
add(g, "Plancha translúcida (policarbonato)", "Policarbonato greca 0,5 mm ~3,00 m", nT, "plancha", nT, 22190, EST,
    "precio prorrateado desde greca 0,81x2,50 m ($18.490). Ver nota perfil", L["greca"])
add(g, "Plancha opaca (zinc-alum)", "Zincalum 5V 0,35 x 895 x 3000 mm", nO, "plancha", nO, 9250, EASY,
    "PV4 no está en Sodimac/Easy; 5V es lo más parecido", L["5v"])
g = "3a. HOJALATERÍA DE REMATE"
add(g, "Plancha lisa zincalum para forros y remates", "0,35-0,4 x 1000 x 3000 mm", 3, "plancha", 3, 11620, EASY,
    "forro muro 8,25 m (3 tiras) + 2 remates laterales de 2,9 m", L["lisa"])
add(g, "Plegado de hojalatería (forro + remates)", "Servicio hojalatero", 1, "global", 1, 25000, EST, "cotizar en barraca/hojalatero local", "")
add(g, "Cierre de espuma para perfil trapezoidal", "Tira ~1 m", 9, "unidad", 9, 1500, EST, "bajo el forro, junto al muro", "")
add(g, "Sellante poliuretano", "Cartucho", 2, "unidad", 2, 6990, EST, "borde superior del forro y traslapos", "")
g = "3b. AGUAS LLUVIA (PVC café)"
add(g, "Canaleta aguas lluvia PVC café", "DVP Pro 110 mm x 4 m", 3, "pieza", 3, 12990, SOD, "borde recto de 8,25 m", L["canal"])
add(g, "Unión de canaleta", "PVC café", 2, "unidad", 2, 1490, EASY, "2 empalmes", L["union"])
add(g, "Tapa de canaleta", "PVC café", 2, "unidad", 2, 1390, EASY, "", L["tapa"])
add(g, "Salida de canaleta a bajada", "PVC café Ø80", 1, "unidad", 1, 3990, EST, "en el extremo derecho (esquina bodega)", "")
add(g, "Gancho / soporte de canaleta", "PVC café", 19, "unidad", 19, 1190, EASY, "c/50 cm, atornillado al tapacán 1x8", L["gancho"])
add(g, "Tubo de bajada", "PVC café Ø80 x 3 m", 2, "pieza", 2, 6590, SOD, "confirmar altura del piso al terreno", L["tubo"])
add(g, "Codo de bajada", "PVC café Ø80", 3, "unidad", 3, 18490, EASY, "2 para salvar el alero + 1 al final. Precio DVP; hay marcas más baratas", L["codo"])
add(g, "Abrazadera de bajada", "PVC café Ø80", 3, "unidad", 3, 1117, EASY, "", L["abraz"])
add(g, "Sellante para PVC / silicona", "Cartucho", 1, "unidad", 1, 4990, EST, "", "")
g = "4. BODEGA – ESTRUCTURA"
add(g, "Pies derechos c/40 cm", "Pino IPV 2x3 x 3,20 m", ns["N_PD_COMPRA"], "pieza", ns["N_PD_COMPRA"], 4790, SOD, "", L["2x3"])
add(g, "Soleras (inferior + superior doble)", "Pino IPV 2x3 x 3,20 m", ns["N_SOL"], "pieza", ns["N_SOL"], 4790, SOD, "", L["2x3"])
add(g, "Cadenetas (2 corridas)", "Pino IPV 2x3 x 3,20 m", ns["N_CAD"], "pieza", ns["N_CAD"], 4790, SOD, "", L["2x3"])
add(g, "Dintel puerta (de canto)", "Pino IPV 2x4 x 3,20 m", 1, "pieza", 1, 6295, SOD, "", L["2x4"])
add(g, "Puerta exterior", "Pino radiata maciza 80 x 200 cm", 1, "unidad", 1, 149990, SOD, "modelos desde ~$120.000 en oferta", L["puerta"])
add(g, "Marco puerta exterior", "Marco pino 80 x 200", 1, "unidad", 1, 35000, EST, "", "")
add(g, "Bisagras", "3½\" acero", 3, "unidad", 3, 3000, EST, "", "")
add(g, "Cerradura exterior", "Con llave", 1, "unidad", 1, 25000, EST, "", "")
g = "4b. VENTANAS (2)"
add(g, "Ventana V1 – muro lateral 2,5 m", "Aluminio fija/proyectante 150 x 30 cm", 1, "unidad", 1, 45000, EST,
    "a medida; vano 152 x 32, borde superior ~2,0 m", "")
add(g, "Ventana V2 – muro frente a la casa", "Aluminio fija/proyectante 200 x 30 cm", 1, "unidad", 1, 55000, EST,
    "a medida; vano 202 x 32, borde superior ~2,0 m", "")
add(g, "Dintel V2 (de canto, 2,10 m)", "Pino IPV 2x8 x 3,20 m", 1, "pieza", 1, 20990, EST, "recibe tijerales T10 a T13", "")
add(g, "Dintel V1 (de canto, 1,60 m)", "Pino IPV 2x6 x 3,20 m", 1, "pieza", 1, 14990, EASY, "", L["2x6"])
add(g, "Refuerzos: antepecho doble, muñecos, calce", "Pino IPV 2x3 x 3,20 m", ns["N_VEN_2X3"], "pieza", ns["N_VEN_2X3"], 4790, SOD,
    "jambas y pies derechos enteros ya incluidos en 'Pies derechos'", L["2x3"])
add(g, "Silicona neutra exterior", "Cartucho", 1, "unidad", 1, 4990, EST, "sello perimetral; botaguas salen de las planchas lisas", "")
g = "5. BODEGA – REVESTIMIENTOS"
add(g, "SmartPanel exterior", "LP SmartSide 11,1 mm 1,22 x 2,44", 11, "plancha", 11, 35290, SOD, "", L["smart"])
add(g, "Contrachapado ranurado interior", "Terciado ranurado 9 mm 1,22 x 2,44", 10, "plancha", 10, 18820, SOD, "", L["terciado"])
add(g, "Barrera de humedad", "Membrana hidrófuga 40 m² (Volcan)", 1, "rollo", 1, 20990, SOD, "Tyvek 46 m² cuesta ~$136.528", L["membrana"])
add(g, "Esquineros / tapajuntas", "Pino IPV 1x4 x 3,20 m", 6, "pieza", 6, 3290, EST, "incluye 2 esquinas del destaje", "")
add(g, "Cortagotera en Z", "Perfil galvanizado 3,00 m", 3, "unidad", 3, 4500, EST, "", "")
add(g, "Grapas para membrana", "Caja grapas corchetera", 1, "caja", 1, 3000, EST, "", "")
g = "6. TORNILLOS (sin clavos)"
add(g, TIPOS["A"], "Caja 250 un.", T["A"], "caja 250", cajas(T["A"], 250), 6490, SOD, "estructura, costaneras, tabiques", L["t8x3"])
add(g, TIPOS["B"], "Bolsa 10 un.", T["B"], "bolsa 10", cajas(T["B"], 10), 5390, SOD, "bloqueos, viga-pilar, tabiques a casa", L["t14x4"])
add(g, TIPOS["C"], "Caja 100 un.", T["C"], "caja 100", cajas(T["C"], 100), 9000, EST, "para soportes Simpson y escuadras (Simpson recomienda sus tornillos SD)", "")
add(g, TIPOS["D"], "Unidad", T["D"], "unidad", T["D"], 990, SOD, "2x4 al muro; incluye golilla aprox.", L["t38"])
add(g, TIPOS["F"], "Caja 100 un. (Mamut)", T["F"], "caja 100", cajas(T["F"], 100), 9590, EASY, "fijación de planchas y hojalatería", L["techo"])
add(g, TIPOS["G"], "Caja 100 un.", T["G"], "caja 100", cajas(T["G"], 100), 4000, EST, "traslapos laterales", "")
add(g, TIPOS["H"], "Caja 100 un.", T["H"], "caja 100", cajas(T["H"], 100), 4500, EST, "SmartPanel, esquineros, tapacán, ganchos canaleta, hojalatería", "")
add(g, TIPOS["I"], "Caja 100 un.", T["I"], "caja 100", cajas(T["I"], 100), 2500, EST, "contrachapado interior", "")
add(g, TIPOS["J"], "Caja 100 un.", T["J"], "caja 100", cajas(T["J"], 100), 2000, EST, "cortagotera", "")

# ---------------- Excel ----------------
wb = Workbook()
ws = wb.active; ws.title = "Presupuesto"
thin = Side(style="thin", color="999999")
B = Border(left=thin, right=thin, top=thin, bottom=thin)
H_FILL = PatternFill("solid", fgColor="1F4E79")
G_FILL = PatternFill("solid", fgColor="DFE7EE")
EST_FILL = PatternFill("solid", fgColor="FFF2CC")
CLP = '"$"#,##0'

ws["A1"] = "AMPLIACIÓN CABAÑA – LAGO TODOS LOS SANTOS · Presupuesto de materiales"
ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = ("Precios de referencia Sodimac / Easy (con IVA), consultados en la web en noviembre 2026. "
            "Celdas amarillas = precio estimado (no se encontró el producto exacto). "
            "Puedes cambiar cualquier precio o cantidad y los totales se recalculan.")
ws["A2"].font = Font(italic=True, size=9, color="555555")
hdr = ["Ítem", "Material / medida", "Cant. necesaria", "Unidad de venta", "Cant. a comprar",
       "Precio unitario", "Total", "Tienda", "Nota", "Link"]
r = 4
for c, h in enumerate(hdr, 1):
    cell = ws.cell(r, c, h); cell.font = Font(bold=True, color="FFFFFF"); cell.fill = H_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); cell.border = B
r += 1
subtot_cells = []
grupo_actual = None; ini = None
def cerrar_grupo():
    global r
    ws.cell(r, 6, "Subtotal").font = Font(bold=True)
    c = ws.cell(r, 7, f"=SUM(G{ini}:G{r - 1})"); c.number_format = CLP; c.font = Font(bold=True)
    subtot_cells.append(f"G{r}")
    r += 2
for (gname, it, med, nec, uv, comp, pr, tienda, nota, link) in G:
    if gname != grupo_actual:
        if grupo_actual is not None:
            cerrar_grupo()
        grupo_actual = gname
        for c in range(1, 11):
            ws.cell(r, c).fill = G_FILL; ws.cell(r, c).border = B
        ws.cell(r, 1, gname).font = Font(bold=True)
        r += 1; ini = r
    vals = [it, med, nec, uv, comp, pr, f"=E{r}*F{r}", tienda, nota, link]
    for c, v in enumerate(vals, 1):
        cell = ws.cell(r, c, v); cell.border = B
        cell.alignment = Alignment(vertical="center", wrap_text=c in (1, 2, 9))
    ws.cell(r, 6).number_format = CLP; ws.cell(r, 7).number_format = CLP
    if tienda == EST or (tienda == IMP and "estimado" in nota):
        ws.cell(r, 6).fill = EST_FILL; ws.cell(r, 8).fill = EST_FILL
    if link:
        ws.cell(r, 10).hyperlink = link; ws.cell(r, 10).value = "ver producto"
        ws.cell(r, 10).font = Font(color="0563C1", underline="single")
    r += 1
cerrar_grupo()
ws.cell(r, 6, "TOTAL MATERIALES").font = Font(bold=True, size=12)
c = ws.cell(r, 7, "=" + "+".join(subtot_cells)); c.number_format = CLP; c.font = Font(bold=True, size=12)
tot_row = r
r += 1
ws.cell(r, 6, "Imprevistos 5 %").font = Font(italic=True)
c = ws.cell(r, 7, f"=G{tot_row}*0.05"); c.number_format = CLP
r += 1
ws.cell(r, 6, "TOTAL CON IMPREVISTOS").font = Font(bold=True, size=12)
c = ws.cell(r, 7, f"=G{tot_row}+G{r - 1}"); c.number_format = CLP; c.font = Font(bold=True, size=12)
for col, w in zip("ABCDEFGHIJ", [40, 34, 10, 12, 10, 13, 14, 10, 40, 13]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A5"
ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToHeight = 0

# Hoja tornillos
wt = wb.create_sheet("Tornillos detalle")
wt["A1"] = "Detalle de tornillos por uso (sin clavos)"; wt["A1"].font = Font(bold=True, size=13)
for c, h in enumerate(["Uso", "Tornillo", "Puntos", "Tornillos por punto", "Total"], 1):
    cell = wt.cell(3, c, h); cell.font = Font(bold=True, color="FFFFFF"); cell.fill = H_FILL; cell.border = B
rr = 4
for uso, tp, p, cpp in USOS:
    for c, v in enumerate([uso, TIPOS[tp], p, cpp, f"=C{rr}*D{rr}"], 1):
        wt.cell(rr, c, v).border = B
    rr += 1
rr += 1
wt.cell(rr, 1, "Resumen por tipo (+10 % de reserva, redondeado)").font = Font(bold=True)
rr += 1
for k in sorted(T):
    wt.cell(rr, 2, TIPOS[k]).border = B
    wt.cell(rr, 5, T[k]).border = B
    rr += 1
rr += 1
wt.cell(rr, 1, "Todos los tornillos exteriores deben ser zincados o galvanizados por la humedad del lago.").font = Font(italic=True)
for col, w in zip("ABCDE", [52, 52, 9, 18, 9]):
    wt.column_dimensions[col].width = w

# Hoja notas
wn = wb.create_sheet("Notas")
notas = [
    "NOTAS IMPORTANTES",
    "",
    "1. Precios de referencia tomados de sodimac.cl y easy.cl (con IVA). Varían por tienda, zona y ofertas: confirmar antes de comprar.",
    "2. Celdas amarillas = precio estimado porque no apareció el producto exacto en la web (4x4 impregnado, marco, bisagras, cerradura, esquineros, cortagotera, algunos tornillos).",
    "3. CUBIERTA: Sodimac y Easy no venden plancha trapezoidal PV4. Lo más parecido es zincalum 5V (opaca) y policarbonato greca (translúcida),",
    "   pero tienen anchos y perfiles distintos, así que NO calzan para intercalarlas. Para intercalar translúcida/opaca conviene comprar ambas",
    "   del mismo perfil en un distribuidor de cubiertas (ej. perfil PV4 en zincalum + policarbonato PV4). El precio de cubierta aquí es referencial.",
    "4. Si el ancho útil de la plancha que compres no es ~1,0 m, cambia la cantidad de planchas (ver lámina 1 del plano).",
    "5. Tijerales, viga y bloqueos en 2x6 impregnado de 3,20 m: precio de Easy (en Sodimac el 2x6 IPV aparecía solo en 4,0 y 4,8 m).",
    "6. Soportes Simpson en Imperial: soporte viga 2x6 ZMAX (SKU 142184, $2.590) y H3 (SKU 142181, $1.090), precios entregados por el dueño.",
    "7. Medidas reales: tijeral 2x6½\" a 2,63 m en el muro, tabla 1x10 apernada, pendiente 12 %, muro exterior 2,33 m.",
    "   Punta del tijeral: corte a plomo (correr 2 cm) + rebaje de asiento de 5 mm (ver lámina 10).",
    "8. La bodega NO lleva tabique contra el muro de la casa: se usa el muro existente.",
    "   El H3 viene izquierdo o derecho: pedir la mitad de cada uno (uno por lado en cada tijeral).",
    "9. Canaleta y accesorios: comprar todo de la MISMA marca/sistema (DVP o Hoffens) para que calcen.",
    "10. No incluye: flete, mano de obra, pintura del SmartPanel, sellos/cintas.",
]
for i, t in enumerate(notas, 1):
    wn.cell(i, 1, t).font = Font(bold=(i == 1), size=12 if i == 1 else 10)
wn.column_dimensions["A"].width = 150

wb.save(BASE + "materiales_ampliacion_cabana.xlsx")

# total en Python para informar
tot = sum(comp * pr for (_, _, _, _, _, comp, pr, *_ ) in G)
print("TOTAL", tot, "con 5%", round(tot * 1.05))
grupos = {}
for (gname, it, med, nec, uv, comp, pr, *_ ) in G:
    grupos[gname] = grupos.get(gname, 0) + comp * pr
for k, v in grupos.items():
    print(k, v)
