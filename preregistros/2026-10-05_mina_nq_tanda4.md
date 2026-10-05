# Pre-registro · Mina NQ, tanda 4: ruptura de máximos/mínimos de N días · rebalanceo de ETFs apalancados · 05/10/2026

Escrito ANTES de ejecutar. Solo NQ (CFD Dukascopy). Igual que la tanda 3: **DISEÑO en años impares
(2019, 2021, 2023, 2025) y VALIDACIÓN en pares (2020, 2022, 2024, 2026)**. Criterios comunes de la mina
(`src/mina.py`): R > p95 del máximo de la familia sobre el paseo aleatorio (12 semillas), placebo de
dirección de familia p < 0,05, R > 0 los 4 años de diseño e invertida ≤ 0. Las supervivientes van a los
años pares con p < 0,05/nº de supervivientes y al menos 3/4 años positivos. Coste 0,87 pts. RTH = 09:30-15:59.

## U1 · Ruptura de máximos/mínimos de N días (6 variantes)
**Mecanismo:** los seguidores de tendencia (CTA, sistemas Donchian) tienen entradas y stops en los
máximos/mínimos de N días. Cuando el precio los cruza dentro de la sesión, se disparan esas órdenes a la
vez y empujan en la dirección de la ruptura. No es la ruptura del día anterior (PDH/PDL, ya probada con
retesteo): es un nivel de varios días que mira otro tipo de participante.
- Nivel = máximo (mínimo) de las barras RTH de las N sesiones anteriores, conocido desde las 09:30.
- Primera barra de 1 min entre 09:35 y 15:00 que CIERRA por encima del máximo (por debajo del mínimo)
  habiendo cerrado la barra anterior por dentro (cruce de verdad, no apertura ya fuera). Entrada a ese
  cierre (el seguimiento empieza en la barra siguiente), en la dirección de la ruptura. Una por día (la primera).
- Stop k% del precio, TP 2k%, cierre a las 15:59.
- N {5, 10, 20} × k {0,30%, 0,50%} = 6.

## U2 · Rebalanceo de ETFs apalancados al cierre (8 variantes)
**Mecanismo:** los ETFs apalancados sobre el Nasdaq (TQQQ, SQQQ, QLD…) tienen que comprar al cierre en
los días alcistas y vender en los bajistas, en una cantidad proporcional al retorno del día
(Cheng-Madhavan 2009; Baltussen-Da-Soebhag 2021, "end-of-day momentum"). El flujo es mecánico, se sabe
de antemano hacia dónde va y solo es grande los días de movimiento grande.
- Retorno del día = c (barra anterior a la entrada) / c 15:59 de la sesión anterior − 1 (cierre a cierre,
  como rebalancea el ETF).
- Si |retorno| ≥ q: entrada a la apertura de la barra de entrada a favor del signo del retorno.
- Stop k% del precio, TP 2k%, cierre a las 15:59.
- Entrada {15:30, 15:45} × q {1,0%, 1,5%} × k {0,15%, 0,25%} = 8.
- Relación con lo ya probado: P1 del lote 1 (Gao et al.) usaba el signo de la primera media hora, sin
  umbral, para operar 15:30-15:59; la rejilla de hora fija llegaba hasta las 15:00 con L ≤ 120 min. U2 usa
  el retorno del día entero y solo los días grandes, que es donde el mecanismo dice que está el flujo.

Total: 14 variantes en 2 familias.
Expectativa dicha antes: por la tasa base del proyecto, lo más probable es que no sobreviva ninguna.
