# Pre-registro · Mina, tanda M3: Momento de apertura en el oro (XAUUSD) · 04/10/2026

Escrito ANTES de bajar los datos (nadie ha visto el oro en este proyecto). Marco y criterios:
`mina/README.md` y `src/mina.py`. (La tanda M2 fue el MOC del ES; esta es la M3.)

## Mecanismo
Momento 09:40 es lo único con algo de vida en el NQ: el impulso de los primeros minutos tras la
apertura del mercado principal sigue unas horas, por el flujo de órdenes que entra con la
apertura. Si es un fenómeno de "apertura del mercado principal" y no una casualidad del NQ,
debería aparecer en otro mercado en su propia apertura. Para el oro, la referencia histórica es
la apertura de COMEX a las 08:20 NY, que además coincide casi con los datos de las 08:30.
Que salga en un segundo mercado haría mucho menos probable la casualidad.

## Datos
CFD XAUUSD de Dukascopy, velas de 1 minuto BID y ASK, precio medio, hora NY. DISEÑO 2021, 2023 y
2025 (cada fichero trae diciembre del año anterior para calentar). Chequeos antes de usarlos:
- cero duplicados y OHLC coherente;
- la parada de 17:00-18:00 NY vacía en verano y en invierno (huso correcto);
- el minuto 08:30 (datos macro) más volátil que el 08:29 y el 08:31, por mediana del rango (si
  saliera el 08:31, son timestamps de fin de vela).

## Reglas (Momento trasladado al oro)
- Señal: cierre de las 08:19 contra el cierre de las 08:19−L. Si es mayor, largo; si es menor,
  corto. Entrada a mercado en la apertura de la vela de las 08:20.
- Stop a k% del precio y TP a 2k% (1:2). Cierre a las 13:29 (cierre histórico de COMEX).
- Coste: micro oro MGC, 0,10 $/oz por tick y comisión ≈ 0,74 $ → ~0,25 $/oz por operación
  (0,07 de comisión + 2 ticks de 0,10 sobre 10 oz), en unidades de precio del oro.
- **Variantes:** L ∈ {15, 30, 60} × k ∈ {0,20%, 0,30%, 0,40%} = 9.

## Criterios
Los comunes de la mina, sobre DISEÑO: p95 del máximo de la familia sobre el paseo aleatorio
del oro (12 semillas), placebo de dirección de familia p < 0,05, 3/3 años y invertida ≤ 0.
Las supervivientes van a 2022/2024/2026 (datos aún sin bajar), con Bonferroni por
supervivientes y contadas en el protocolo de partición.
Informativo: lo mismo a las 09:30 y 09:40 NY (apertura de la bolsa de NY), solo como
descripción, sin decidir nada.

## Adenda (05/10, ANTES de tener los datos del oro)
Dukascopy va a ~100 ficheros/hora. Para que la descarga no dure 18 h: (1) solo precio BID (el
"medio" pasa a ser el BID; el coste de 0,25 $/oz ya incluye el diferencial) y (2) sin el
diciembre previo, porque esta regla no usa indicadores que necesiten calentar. La regla, las
variantes y los criterios no cambian.
