# Pre-registro · Xavi Ruyra, "mis dos sistemas de entrada" (reel, 08/10/2026)

Escrito ANTES de ejecutar. Idea traída por Daniil. Solo NQ (CFD), coste 0,87 pts. Diseño en impares
2019/21/23/25; validación en pares 2020/22/24/26 solo para supervivientes. Hora NY.

## Escenario 1 · Judas Swing
Lo nuevo frente a lo ya probado (Fede, Aleix 09:30, Judas): la condición de **acumulación en pre-market**.
- Acumulación: rango 08:00-09:29 < mediana de ese rango en las 20 sesiones previas.
- Manipulación en el open (09:30-09:59, no antes): la primera M1 que toca un FVG H1 vigente al otro lado
  de la apertura de 09:30 (bajista por encima → cortos; alcista por debajo → largos; mismos FVG H1 que
  Aleix: nacidos y respetados hasta la vela de las 08:00). Si las dos cosas en la misma M1, nada.
- IFVG de 1 min: el último FVG de 1 min a favor de la manipulación nacido desde las 09:30; entrada al
  CIERRE de la primera M1 que cierra al otro lado de su borde lejano (largos: espejo), hasta las 10:30.
- Stop = extremo de la manipulación hasta la entrada (mín. 0,05%). TP 2R o 3R. Cierre 15:59.
- Informativo (no cuenta): lo mismo sin la condición de acumulación.

## Escenario 2 · PO3 de las aperturas de 15 min (09:45, 10:00, 10:15)
- Dirección (continuación): signo de c(T−1) − apertura de 09:30.
- Manipulación: en los 5 primeros minutos de la vela de 15m, el precio va en contra más allá de su
  apertura. Entrada al CIERRE de la primera M1 (hasta T+10) que vuelve a cerrar a favor de la apertura,
  después de la manipulación. Stop = extremo de la manipulación (mín. 0,05%). TP 2R o 3R. Cierre 15:59.
- La primera de las tres aperturas que dispare. Una operación al día.
- Simplificación declarada: "alineado con el HTF y el DOL" no tiene regla en el reel; no se añade.

## Variantes (4)
{E1, E2} × TP {2R, 3R}.

## Criterios
Los de la mina (p95 del máximo de la familia sobre el paseo aleatorio, 12 semillas; placebo de familia
p < 0,05; 4/4 años; invertida ≤ 0). Calibración en paseo aleatorio antes de mirar datos reales.
Expectativa dicha antes: el escenario 1 es la familia barrida + IFVG, medida en cero muchas veces.

## Calibración en paseo aleatorio (antes de mirar datos reales, 24 semillas, rejilla de 2021)
E1 2R −0,082 (asimetría −0,046 ± 0,022) · E1 3R −0,108 (−0,057 ± 0,028) · E2 2R −0,084 (−0,004 ± 0,020) ·
E2 3R −0,070 (−0,001 ± 0,024). E1 tiene un sesgo pesimista leve (entrar tras un giro en un extremo, regla N):
quita, no fabrica. Sin cambios en la regla.
