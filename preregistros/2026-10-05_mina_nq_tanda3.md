# Pre-registro · Mina NQ, tanda 3: inventario overnight · aceptación/rechazo del rango overnight · compresión → ruptura · 05/10/2026

Escrito ANTES de ejecutar. Solo NQ (CFD Dukascopy). Método pedido por Daniil: **DISEÑO en años impares
(2019, 2021, 2023, 2025) y VALIDACIÓN en pares (2020, 2022, 2024, 2026)**. Criterios comunes de la mina
(`src/mina.py`): R > p95 del máximo de la familia sobre el paseo aleatorio (12 semillas), placebo de
dirección de familia p < 0,05, R > 0 los 4 años de diseño e invertida ≤ 0. Las supervivientes van a los
años pares con p < 0,05/nº de supervivientes y al menos 3/4 años positivos (nuevo uso del protocolo por
familia). Coste 0,87 pts. Rango overnight (ON) = 18:00-09:29 de la sesión.

## T1 · Inventario overnight (8 variantes)
**Mecanismo:** quien compra o vende fuerte por la noche (poca liquidez) acumula inventario; en la apertura
de contado entra la liquidez real y ese inventario se deshace. Documentado en futuros de índices como
reversión de la apertura.
- Movimiento ON = ln(c 09:29 / o primera barra de la sesión). Condición: |ON| ≥ q × mediana de |ON| en las
  20 sesiones previas.
- REV: contra el signo del ON · CONT: a favor. Entrada en la apertura de las 09:30. Stop k%, TP 2k%,
  cierre a las 15:59.
- Modo {REV, CONT} × q {1,0, 1,5} × k {0,30%, 0,50%} = 8.

## T2 · Aceptación o rechazo del rango overnight (8 variantes)
**Mecanismo (teoría de subasta):** si el precio abre fuera del rango ON y en la primera media hora vuelve a
entrar, el mercado RECHAZA esos precios y tiende al otro lado del rango; si se queda fuera y se aleja, los
ACEPTA y sigue.
- Solo días en que la apertura de las 09:30 está fuera del rango ON.
- RECHAZO: c 09:59 vuelve dentro del rango → se opera hacia dentro. ACEPTACIÓN: c 09:59 sigue fuera y más
  lejos que la apertura → se opera hacia fuera.
- Entrada en la apertura de las 10:00. Stop k%, TP ratio·k%, cierre a las 15:59.
- Modo {RECHAZO, ACEPTACIÓN} × k {0,25%, 0,40%} × ratio {1,5, 2} = 8.

## T3 · Compresión → ruptura (4 variantes)
**Mecanismo:** una apertura muy estrecha deja órdenes acumuladas a ambos lados; cuando el precio sale
del rango, se disparan y hay expansión.
- Rango 09:30-09:44 < q × mediana de ese rango en las 20 sesiones previas.
- Primera barra de 1 min, entre las 09:45 y las 11:30, que CIERRA fuera del rango: entrada a ese cierre
  (el seguimiento empieza en la barra siguiente) hacia el lado de la ruptura. Stop en el otro lado del
  rango (mínimo 0,05% del precio). TP ratio·R. Cierre a las 15:59.
- q {0,5, 0,7} × ratio {2, 3} = 4.

Expectativa dicha antes: por la tasa base del proyecto, lo más probable es que no sobreviva ninguna.

## Nota tras ejecutar (05/10): T2 estaba mal especificada
Con el rango ON definido como 18:00-09:29, la apertura de las 09:30 casi nunca queda fuera de él (el
mercado cotiza seguido y el rango incluye la vela de las 09:29): solo 1 caso en 4 años. No es un
resultado, es un error de diseño mío. No se rehace: la versión con sentido (apertura fuera del rango
del día ANTERIOR, aceptación o rechazo) ya está cubierta por familias probadas (apertura fuera del rango
previo en el lote 4, barrida de PDH/PDL de Kasen y ruptura de PDH/PDL con retesteo).
