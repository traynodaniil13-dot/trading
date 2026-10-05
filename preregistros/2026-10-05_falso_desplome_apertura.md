# Pre-registro · "Falso desplome" de la apertura de NY (vídeo xaZeNPHwKDw) · 05/10/2026

Escrito ANTES de ejecutar. Fuente: resumen del vídeo (análisis de UNA operación ganadora). Solo NQ.
Marco y criterios comunes: `src/mina.py`. DISEÑO 2021/2023/2025, CFD NQ.

## Lo que se puede programar del vídeo
A las 09:30, dos velas de 5 min bajistas agresivas perforan los mínimos internos ("falso
desplome"); inmediatamente después, dos velas de 5 min alcistas → compra. Stop bajo el mínimo
estructural; TP a 1:4 o en el máximo del día anterior (PDH); break-even al barrer el primer
máximo local. Cortos: espejo ("falsa subida").
No se puede programar: la lectura de 4H/1H ("order block", "equal highs") ni la "inducción" en
1 min, que son criterio suyo.

## Mecánica
- Mínimos internos = mínimo de 08:00 a 09:29 (preapertura). Espejo: máximo.
- **Falso desplome:** las velas de 5 min de las 09:30 y 09:35 son bajistas (c < o) y el mínimo de
  09:30-09:39 < el mínimo de la preapertura.
- **Rechazo:** las velas de 09:40 y 09:45 son alcistas. **Entrada** al cierre de la vela de las 09:45
  (el seguimiento empieza a las 09:50).
- **Stop** = mínimo de 09:30-09:49, con un mínimo del 0,05% del precio. Cierre a las 15:59.
  Coste 0,87 pts.
- **Variantes (4):** TP {4R, PDH (máximo RTH del día anterior), si queda por encima} × break-even
  {no, sí al tocar +1R desde la barra siguiente}.

## Criterios
Los comunes de la mina: p95 del máximo de la familia sobre el paseo aleatorio (12 semillas),
placebo de familia p < 0,05, 3/3 años, invertida ≤ 0. Si alguna sobrevive: validación 2022/24/26
y después reserva ciega 2019-2020.
Expectativa dicha antes: patrón poco frecuente (unas pocas veces al mes) y de la familia barrida +
giro, medida en cero muchas veces.

## Corrección (05/10, tras la 1ª ejecución, antes de interpretar)
La 1ª ejecución calculaba el break-even con rmax, sin el camino: daba por ganadas operaciones que
volvían a la entrada (BE) antes de llegar al TP. Era optimista (sesgo a favor). Se rehace con una
simulación minuto a minuto (`camino_be`). Las variantes y los criterios no cambian; el resultado
válido es el de la 2ª ejecución.
