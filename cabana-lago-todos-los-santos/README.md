# Ampliación cabaña – Lago Todos los Santos

Bodega de 3,50 × 2,50 m + terraza techada de 4,75 m, adosadas a la casa existente.

## Archivos

| Archivo | Qué es |
|---|---|
| `ampliacion_cabana.pdf` | Planos completos en A3 (6 láminas) |
| `materiales_ampliacion_cabana.xlsx` | Lista de materiales valorizada (Sodimac / Easy / Imperial) |
| `1_planta.png` | Lámina 1: planta, tijerales y planchas |
| `2_isometrico.png` | Lámina 2: isométrico |
| `3_cortes.png` | Lámina 3: cortes A-A y B-B, detalles 1 y 2 (apoyos de tijerales) |
| `4_materiales.png` | Lámina 4: lista de materiales |
| `5_hojalateria.png` | Lámina 5: hojalatería de remate, detalles 3 y 4 |
| `6_ventanas.png` | Lámina 6: elevaciones con ventanas y refuerzos, detalle 5 (canaleta) |
| `generar_planos.py` | Programa que dibuja las láminas y el PDF |
| `generar_planilla.py` | Programa que arma la planilla Excel |

## Decisiones tomadas

- Tijerales pino IPV 2x6 cada 60 cm (15), alero de 40 cm, pendiente ≈ 10 %.
- Junto a la casa: tijeral de tope contra viga 2x8 apernada al muro, con soporte Simpson 2x6 ZMAX.
- Por fuera: soportes Simpson H3, uno por lado de cada tijeral.
- Muro exterior de la bodega: 2,36 m bajo el tijeral.
- Bodega con tabique 2x3 IPV c/40 cm en 3 lados (no lleva tabique contra la casa) y puerta 80x200 hacia la terraza.
- Revestimiento: SmartPanel por fuera, contrachapado ranurado por dentro.
- Cubierta trapezoidal: translúcida en la terraza e intercalada (translúcida/opaca) en la bodega.
- Tapacán 1x8, canaleta PVC café con bajada en la esquina de la bodega.
- Hojalatería: forro contra el muro existente y remates laterales.
- Alero de 40 cm; la plancha vuela 8 cm y llega a más de la mitad de la canaleta.
- Ventanas: V1 150x30 en el muro lateral (opuesto a la puerta) y V2 200x30 en el muro frente a la casa,
  borde superior ~2,0 m, con pies derechos enteros, jambas, dintel (2x6 / 2x8), antepecho doble y muñecos.
- Todo con tornillos, sin clavos.

## Pendiente

- Confirmar en tienda los precios marcados en amarillo en la planilla.

## Para regenerar los archivos

```bash
python3 generar_planos.py
```

```bash
python3 generar_planilla.py
```

Requiere `matplotlib` y `openpyxl`.
