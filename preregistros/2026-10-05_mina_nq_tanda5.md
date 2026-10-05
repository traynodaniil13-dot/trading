# Pre-registro · Mina NQ, tanda 5: reversión de fin de día (hipótesis de U2) · reversión de extremos de 60 min · 05/10/2026

Escrito ANTES de ejecutar. Solo NQ (CFD Dukascopy). Coste 0,87 pts. Criterios comunes de la mina
(`src/mina.py`): R > p95 del máximo de la familia sobre el paseo aleatorio (12 semillas), placebo de
dirección de familia p < 0,05, R > 0 en todos los años evaluados e invertida ≤ 0.

## V1 · Reversión del día al cierre (8 variantes) — hipótesis nacida en U2, se mide SOLO en años pares
**Origen:** en la tanda 4 (U2), las 8 variantes "a favor del movimiento del día a las 15:30/15:45" salieron
negativas los 4 años impares y sus INVERTIDAS dieron +0,05/+0,17R. Eso se vio en 2019/21/23/25, así que esos
años ya no sirven para esta hipótesis.
**Mecanismo propuesto:** en días de ±1% o más, la liquidez de cierre (MOC, creadores de mercado, ventas de
quien quiere cerrar el día) absorbe más que el flujo de los ETFs apalancados y el precio devuelve parte del día.
- Las 8 variantes de U2 exactamente (entrada 15:30/15:45 × q 1,0/1,5% × k 0,15/0,25%, TP 2k, cierre 15:59),
  con la dirección CONTRARIA al retorno del día. Nada más cambia.
- Se evalúan como familia DIRECTAMENTE en los años pares 2020/2022/2024/2026, que nunca se han usado
  para esta familia, con los criterios comunes (4/4 años positivos). Además, la mejor tiene que cumplir
  p < 0,05/8 = 0,00625.
- Antecedente en contra, dicho antes: el desequilibrio de cierre de las 15:50 (lote 6, F4) murió en validación.
- Si alguna pasa: reserva ciega 2017-2018 (por bajar, nunca vista), regla congelada, p < 0,05.

## V2 · Reversión de extremos de 60 minutos (6 variantes) — diseño en impares, validación en pares
**Mecanismo:** cuando el precio se mueve en una hora mucho más de lo normal sin noticia programada, quien
provee liquidez (creadores de mercado, fondos de reversión) se queda con inventario en contra y el precio
devuelve parte del movimiento. No es la "vela gigante" de 1 min (lote 3) ni la reversión a hora fija de las
rejillas: es condicional al tamaño del movimiento de una hora, a cualquier hora.
- r60 = ln(c_j / c_{j−60}) en barras RTH con j−60 ≥ 09:30 de la misma sesión. σ = mediana, en las 20 sesiones
  previas, de la desviación típica diaria de r60 entre 10:30 y 15:59 (todo conocido antes de la sesión).
- Primera barra entre 10:30 y 15:00 con |r60| ≥ z·σ: entrada al cierre de esa barra CONTRA el movimiento
  (el seguimiento empieza en la siguiente). Una por día. Stop k%, TP 2k%, cierre 15:59.
- z {2,0, 2,5, 3,0} × k {0,25%, 0,40%} = 6.
- Diseño 2019/21/23/25; supervivientes a 2020/22/24/26 con p < 0,05/nº de supervivientes y ≥ 3/4 años.

Total: 14 variantes. Expectativa dicha antes: lo más probable es que no pase ninguna.
