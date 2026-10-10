# Pre-registro · 6 estrategias en PDF de FX Replay · 10/10/2026

Escrito ANTES de ejecutar. Traídas por Daniil ("todas easy y funcionan en índices"). PDF originales en
`preregistros/fuentes_fxreplay/`. Índices: **NQ (CFD)** es el que decide; ES (CFD) informativo cuando el autor usa
el S&P. Coste 0,87 pts NQ / 0,65 ES. Hora NY. Diseño impares 2019/21/23/25 (ES: 2021/23/25); validación pares solo
para supervivientes. Criterios comunes de la mina por familia (p95 del máximo del paseo aleatorio, 12 semillas;
placebo de familia p < 0,05; todos los años de diseño positivos; invertida ≤ 0). Relleno de órdenes pendientes al
CIERRE de la M1 que toca el nivel (regla 3). Stop mínimo 0,05% del precio. Una operación al día por variante
salvo que se diga. Cierre forzado 15:59 (las intradía).

## 1 · Bernd's Globex (5m)
Rango Globex 18:00-09:29. Barrida en 09:30-15:00 (mín. → largos, máx. → cortos). Tras la barrida, la primera zona
de demanda (oferta) que se forma en 5m: base de 1-5 velas de cuerpo ≤ 50% de su rango seguida de ≥ 2 velas impulsivas
a favor (cuerpo ≥ 60% del rango). Zona = mínimo de la base a cuerpo más alto (oferta: máximo a cuerpo más bajo). Si se
forma otra antes del relleno, la sustituye. Límite en el borde cercano; stop 33% de la altura de la zona más allá.
**Variantes:** TP 2R con BE a 1R · TP 4R con BE a 2R. (Filtro de tendencia HTF no aplicado: discrecional.)

## 2 · JJ Simon Fair Value Theory (1m)
Valor justo = apertura de 09:30 (mañana) y de 14:00 (tarde). Señal = vela de desplazamiento (contra-mecha < 20% de la
distancia de la apertura al extremo contrario) que cierra rompiendo el último pivote de 1m confirmado (2+2).
Primeros 10-15 min (09:33-09:44 / 14:03-14:14): continuación alejándose del valor justo; después (09:45-11:00 /
14:15-15:00): reversión hacia el valor justo. Entrada a mercado; stop por ATR(14) de 1m: > 20 → 50 pts · 7-20 → 25 ·
< 7 → 16,5; TP 1,5R. **Variantes:** ventana de mañana · ventana de tarde.

## 3 · Toto Capital SBL Reversal (15m)
Solo cortos si EMA50 < EMA100 < EMA200 (15m cerradas); largos al revés. Ventana Londres 03:00-04:59 (nivel: Asia =
00:00-05:00 UTC) o NY 08:00-10:29 (niveles: Asia y Londres 03:00-04:59). Si el nivel se barrió antes de la ventana,
hace falta barrer el extremo posterior ("segundo barrido"). Tras la barrida a favor de tendencia, primera vela de 15m
que cierra a favor → orden stop en su extremo (se actualiza con cada vela a favor nueva); stop en el extremo de la
barrida; TP 2R. **Variantes:** ventana Londres · ventana NY. (El autor usa S&P: ES informativo.)

## 4 · Omar Agag EBP (4H, swing)
Velas de 4H desde las 18:00. EBP alcista: barre el mínimo de la anterior y cierra por encima del cuerpo de la anterior.
Fuerte (cierre a ≤ 15% del máximo): límite al 25% de retroceso, stop al 75%. Indeciso: límite al 50%, stop en el mínimo
de la vela; si cerró por debajo del 50%, a mercado. TP 2R; BE cuando el precio supera el máximo de la vela EBP. Orden
válida 6 velas de 4H; operación máxima 30 velas; una a la vez. **Variantes:** fuerte · indeciso. Aviso: mantiene días,
no operable en Lucid; se mide igual.

## 5 · ORB (NY, 15m)
Rango 09:30-09:44. Primera vela de 5m (hasta 12:00) que cierra fuera. Stop en el punto medio del rango, TP a 1 desviación
(borde + altura del rango). Si a mercado no da ≥ 1R, límite en el borde del rango (retest), cancelado si toca el TP antes.
(Invalidaciones por niveles cercanos y el "2 pérdidas/1 ganancia" no se aplican: una operación al día.)
**Variantes:** autor (mercado o retest) · solo a mercado.

## 6 · Doyle Exchange Supply & Demand (5m)
EMA200 de 5m: largos por encima, cortos por debajo. Demanda = última vela roja antes de un impulso (las 2 siguientes
alcistas y el cierre de la 2ª ≥ 1 rango de la vela por encima de su máximo); zona = su rango, válida 48 velas. Una vela
"pequeña" (rango ≤ 1,5× la mediana de 20) entra con la mecha en la zona sin cerrar dentro → orden stop en su máximo
(válida 3 velas); stop en el mínimo local; BE a 1R; TP 3R. Oferta: espejo. **Variantes:** ventana NY 09:30-12:00 ·
Londres 03:00-06:00.

Total 12 variantes en 6 familias. Expectativa dicha antes: por la tasa base, lo probable es que no sobreviva ninguna.
