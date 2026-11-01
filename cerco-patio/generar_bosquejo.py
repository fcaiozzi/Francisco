W_P = 4.1   # ancho real pieza 1x2 cepillado (cm)
H = 80.0
S = 2.0     # px por cm en elevaciones
out = []
def r(x,y,w,h,fill="#e9c891",stroke="#7a5426",sw=1,extra=""):
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def t(x,y,s,size=14,anchor="start",weight="normal",fill="#222"):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" font-family="Arial, sans-serif">{s}</text>')
def l(x1,y1,x2,y2,stroke="#333",sw=1,extra=""):
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def cota_h(x1,x2,y,label):
    l(x1,y,x2,y,extra='marker-start="url(#a)" marker-end="url(#a)"'); l(x1,y-6,x1,y+6); l(x2,y-6,x2,y+6)
    t((x1+x2)/2,y-6,label,13,"middle","bold")
def cota_v(x,y1,y2,label,side=1):
    l(x,y1,x,y2,extra='marker-start="url(#a)" marker-end="url(#a)"'); l(x-5,y1,x+5,y1); l(x-5,y2,x+5,y2)
    t(x+8*side,(y1+y2)/2+4,label,12,"start" if side>0 else "end")

rails = [(10,10+W_P),(40-W_P/2,40+W_P/2),(H-10-W_P,H-10)]  # desde arriba (cm)

def elevacion(x0,y0,largo,n,desde_esquina,postes,titulo):
    t(x0,y0-38,titulo,17,weight="bold")
    # postes (recomendados) detrás
    for p in postes:
        px = min(max(p-W_P/2,0),largo-W_P)
        r(x0+px*S,y0,W_P*S,H*S,fill="#cfcfcf",stroke="#888",extra='stroke-dasharray="4 3"')
    # travesaños
    for a,b in rails:
        r(x0,y0+a*S,largo*S,(b-a)*S,fill="#c99a5b")
    # verticales
    if desde_esquina:
        g=(largo-n*W_P)/n; xs=[g+i*(W_P+g) for i in range(n)]
    else:
        g=(largo-n*W_P)/(n-1); xs=[i*(W_P+g) for i in range(n)]
    for x in xs:
        r(x0+x*S,y0,W_P*S,H*S)
    # tornillos
    for x in xs:
        for a,b in rails:
            out.append(f'<circle cx="{x0+(x+W_P/2)*S:.1f}" cy="{y0+(a+b)/2*S:.1f}" r="2" fill="#333"/>')
    # suelo
    l(x0-20,y0+H*S,x0+largo*S+20,y0+H*S,stroke="#555",sw=2)
    cota_h(x0,x0+largo*S,y0+H*S+28,f"{largo/100:.2f} m  —  {n} piezas verticales (separación real ≈ {g:.1f} cm ≈ {g/2.54:.2f}\")".replace('.',','))
    return g

out_w,out_h=1400,1180
# ---------- PLANTA ----------
t(40,40,"CERCO DE MADERA — PATIO 1er PISO (bosquejo, medidas en cm)",22,weight="bold")
t(40,64,"Pino seco cepillado 1x2\" (medida real ≈ 1,9 x 4,1 cm) · altura 80 cm · separación entre piezas 3\" (7,6 cm)",14,fill="#555")
px0,py0,ps=80,160,0.9
t(40,100,"1) VISTA EN PLANTA (desde arriba)",17,weight="bold")
l(px0,py0,px0+550*ps,py0,stroke="#7a5426",sw=6)
l(px0+550*ps,py0,px0+550*ps,py0+200*ps,stroke="#7a5426",sw=6)
postesA=[0,137.5,275,412.5,550]; postesB=[100,200]
for p in postesA: r(px0+p*ps-5,py0-5,10,10,fill="#999",stroke="#333")
for p in postesB: r(px0+550*ps-5,py0+p*ps-5,10,10,fill="#999",stroke="#333")
cota_h(px0,px0+550*ps,py0-22,"Tramo A = 5,50 m")
cota_v(px0+550*ps+30,py0,py0+200*ps,"Tramo B = 2,00 m")
t(px0+550*ps-14,py0+20,"quiebre 90°",12,"end",fill="#a33")
t(px0+150,py0+45,"Tu patio (mascota)",14,fill="#2a6")
t(px0+400,py0+150,"Patio vecino",14,"end",fill="#888")
t(px0+700,py0+40,"■ = poste recomendado 2x2\" (7 en total)",13,fill="#555")
t(px0+700,py0+60,"Largo total: 5,50 + 2,00 = 7,50 m",13,fill="#555")

# ---------- ELEVACIONES ----------
gA=elevacion(80,420,550,47,False,postesA,"2) ELEVACIÓN TRAMO A (5,50 m)")
cota_v(60,420,420+H*S,"80",-1)
gB=elevacion(80,760,200,17,True,[100,200],"3) ELEVACIÓN TRAMO B (2,00 m, parte en el quiebre)")
cota_v(60,760,760+H*S,"80",-1)

# ---------- DETALLE ----------
dx,dy,ds=620,760,3.0
t(dx,dy-38,"4) DETALLE: posición de travesaños",17,weight="bold")
for i in range(3):
    r(dx+i*(W_P+7.62)*ds,dy-0,W_P*ds,H*ds*0.0+0,fill="none",stroke="none")
# dibujo a escala reducida de alto (ds en vertical 3px/cm -> 240px)
for i in range(3):
    xx=dx+20+i*(W_P+7.62)*ds
    for a,b in rails:
        pass
for a,b in rails:
    r(dx,dy+a*ds*0.95,140,(b-a)*ds*0.95,fill="#c99a5b")
for i in range(3):
    r(dx+15+i*(W_P+7.62)*ds,dy,W_P*ds,H*ds*0.95)
k=ds*0.95
cota_v(dx+160,dy,dy+10*k,"10 cm")
cota_v(dx+160,dy+(40-W_P/2)*k,dy+(40+W_P/2)*k,"centro a 40 cm")
cota_v(dx+160,dy+(H-10)*k,dy+H*k,"10 cm")
cota_v(dx-15,dy,dy+H*k,"80",-1)
xg=dx+15+W_P*ds
cota_h(xg,xg+7.62*ds,dy+H*k+22,"3\"")

# corte lateral
cx=dx+300
t(cx,dy+10,"Corte lateral:",13,weight="bold")
r(cx,dy+20,1.9*ds*3,H*k*0.6,fill="#e9c891")
for a,b in rails:
    r(cx+1.9*ds*3,dy+20+a*k*0.6,1.9*ds*3,(b-a)*k*0.6,fill="#c99a5b")
r(cx+2*1.9*ds*3,dy+20,4.1*ds*3*0.5,H*k*0.6,fill="#cfcfcf",stroke="#888",extra='stroke-dasharray="4 3"')
t(cx+70,dy+40,"vertical  →",12); t(cx+70,dy+56,"travesaño →",12); t(cx+70,dy+72,"poste (atrás)",12)
t(cx+70,dy+100,"Tornillo: 1¼\" (32 mm)",12,weight="bold",fill="#a33")
t(cx+70,dy+116,"cruza 1,9 + entra 1,3 cm",12,fill="#a33")
t(cx+70,dy+132,"(3/4\" = 1,9 cm no agarra)",12,fill="#a33")

# ---------- MATERIALES ----------
mx,my=80,1000
t(mx,my,"5) LISTA DE MATERIALES",17,weight="bold")
filas=[
 ("Verticales 1x2\" de 80 cm","47 + 17 = 64 piezas","64 ÷ 4 = 16 tablas de 3,20 m"),
 ("Travesaños 1x2\" (3 líneas)","3 × 7,50 m = 22,5 m","9 tablas de 3,20 m"),
 ("TOTAL 1x2\" cepillado","","25 tablas (+2 de reserva = 27)"),
 ("Postes 2x2\" de 80 cm (recomendado)","7 postes","2 tablas de 3,20 m"),
 ("Tornillos 1¼\" (verticales)","64 × 3 = 192","+ postes ≈ 1 caja de 250"),
]
y=my+28
for a,b,c in filas:
    t(mx,y,a,14,weight="bold" if "TOTAL" in a else "normal"); t(mx+380,y,b,14); t(mx+640,y,c,14,weight="bold")
    y+=24
t(mx,y+10,"Gris punteado = postes recomendados (no estaban en la idea original, pero sin ellos el cerco no queda firme).",12,fill="#777")

svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{out_w}" height="{out_h}" viewBox="0 0 {out_w} {out_h}"><defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs><rect width="100%" height="100%" fill="#fff"/>'+"\n".join(out)+"</svg>"
open(__import__('sys').argv[1],"w").write(svg)
print(gA,gB)
