# Pre-registro · OPEN_DRIVE (vela de 5 min, cuerpo > 80%): prueba en años no vistos · 05/10/2026

Escrito ANTES de ejecutar, tras ver el diseño de la tanda 2 (N3). Una sola regla, congelada tal cual
`scripts/mina_nq_tanda2.py`, `n3(m=5, u=0.8)`:
- primera vela RTH de 5 min (09:30-09:34) con cuerpo / rango > 0,8;
- entrada al cierre de las 09:34 (el seguimiento empieza a las 09:35) en la dirección del cuerpo;
- stop = rango de la vela (mínimo 0,05% del precio), TP 2R, cierre a las 15:59, coste 0,87 pts.

## Por qué esta y no otra
En diseño (2021/23/25) las 6 variantes de N3 salieron positivas y crecían con la exigencia del
cuerpo (forma de mecanismo). Esta es la única con 3/3 años positivos. La familia NO pasó el criterio
de diseño (placebo p=0,075). Elegir la mejor de 6 tiene un precio, y se paga con un umbral corregido.

## Prueba (todo con años que esta idea no ha visto)
- **Datos:** CFD NQ de 2019, 2020, 2022, 2024 y 2026 (2026 hasta el 23/09).
- **Principal:** los 5 años juntos, R > 0 con **p < 0,05/6 = 0,0083** (una cola; corrige haber elegido
  1 de 6), **y** el mismo signo en los dos bloques (2019-2020 y 2022/24/26).
- **Controles:** paseo aleatorio (12 semillas) con z > 2 (regla O), invertida ≤ 0.
- **Informativo:** cada año, el futuro NQ real (Kaggle 2023-25) y la frecuencia.
- Gasta el uso nº15 del protocolo (validación 2022/24/26) y la reserva 2019-2020 para esta idea.
- **Si no pasa, OPEN_DRIVE queda enterrada:** no se reabre con otros m, cuerpos, stops ni ratios.

Expectativa dicha antes: ~38 operaciones al año → ~190 en total. Con una ventaja real de +0,2R, el
p estaría alrededor de 0,02-0,05; llegar a 0,0083 exige que la ventaja sea igual o mayor que en
diseño. Lo más probable, por la tasa base del proyecto, es que no llegue.
