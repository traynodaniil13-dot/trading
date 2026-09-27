# Pre-registro · Pruebas duras de MOMENTO 09:40 stop 0,40% 1:2 · 27/09/2026

Escrito antes de ejecutar. Ninguna prueba cambia los parámetros de la candidata
(T=09:40, L=30, stop 0,40%, 1:2, cierre 16:00). Su única función es intentar
romperla. Datos: CFD 2021-2026 salvo donde se indique.

| # | Prueba | Aprueba si |
|---|---|---|
| T1 | **Otro instrumento**: NQ futuro real (Kaggle 2023-25), el que se opera de verdad | R > 0 y correlación de R por operación con el CFD ≥ 0,8 en días comunes |
| T2 | **Vecindario de parámetros** (regla P): stop 0,30/0,35/0,45/0,50%, L 20/40, T 09:35/09:45, ratio 1,75/2,25 (uno cada vez) | ≥ 8 de 10 vecinos con R > 0 (meseta, no pico) |
| T3 | **Placebo de dirección** (1.000 sorteos) | la real ≥ 2,5σ sobre la media del placebo |
| T4 | **Otra convención de vela de entrada** (regla A) | R > 0 |
| T5 | **Ejecución peor**: coste ×2 (1,74 pts) y ×3 (2,61 pts); entrada 1 min tarde (09:41) | R > 0 en las tres |
| T6 | **Ventanas móviles de 12 meses** | ≥ 70% de ventanas con R > 0 |
| T7 | **Por dirección** (regla M): largos y cortos por separado | los dos con R > 0 |
| T8 | **Look-ahead por truncado**: recalcular la señal de cada día borrando TODAS las barras desde las 09:40 | 100% de señales idénticas |
| T9 | **Bootstrap por bloques mensuales** (10.000) | IC 95% de R con cota inferior > 0 |

Además (no puntúa): 10 operaciones al azar con fecha, hora, precio, stop y
objetivo para cruzar a mano en TradingView/FX Replay (sección 11).

Veredicto: aprueba las pruebas duras solo si pasa las 9. Aunque pase, sigue sin
estar "aprobada" como ventaja: la validación dio p=0,049 > 0,005. Pasarlas
significa "no hay bug ni fragilidad detectable", no "ventaja demostrada".
