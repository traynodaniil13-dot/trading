# Pre-registro · "Continuación de la apertura" (estrategia propia) · 08/10/2026

Escrito ANTES de ejecutar. Pedido por Daniil: una estrategia desde cero. Solo NQ (CFD), coste 0,87 pts.

## Origen (dicho antes, para que se descuente)
Es la INVERTIDA exacta del escenario 1 de Xavi Ruyra (`preregistros/2026-10-08_xavi_ruyra.md`), que en los
años impares 2019/21/23/25 dio +0,13R a 3R (n=335). La hipótesis se vio en esos años, así que esos años no
cuentan. Encaja con la única pista repetida del proyecto (el movimiento de apertura continúa: OPEN_DRIVE,
Momento 09:40).

## Regla (UNA versión, congelada)
1. Acumulación en pre-market: rango 08:00-09:29 NY < mediana de ese rango en las 20 sesiones previas.
2. Impulso de apertura: la primera M1 entre 09:30 y 09:59 que toca un FVG H1 vigente al otro lado de la
   apertura de 09:30 (por encima → impulso alcista; por debajo → bajista). Si toca ambos en la misma M1, nada.
3. Retroceso: primera M1 (hasta 10:30) que cierra al otro lado del borde lejano del último FVG de 1 min a
   favor del impulso nacido desde las 09:30. **Entrada al cierre de esa M1 A FAVOR del impulso.**
4. Distancia de stop = distancia de la entrada al extremo del impulso (mín. 0,05% del precio), al otro lado.
   TP 3R. Cierre 15:59. Una operación al día.

## Prueba (única)
Solo en los años PARES 2020/2022/2024/2026, nunca usados para esta regla.
Pasa si: R > 0 con p < 0,05 (una cola), ≥ 3/4 años positivos, y exceso sobre el paseo aleatorio (12 semillas,
misma regla) con z > 1,65. Si no pasa, muere sin variantes.
Si pasa: reserva ciega 2017-2018 (por bajar) y forward test, antes de cualquier dinero.
