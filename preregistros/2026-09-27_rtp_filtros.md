# Pre-registro · RTP · filtros de mecanismo distinto · 27/09/2026

Escrito ANTES de ejecutar ninguno de los filtros. Base ya medida (réplica nº3):
n=495, −0,010R, invertida −0,063R, caja 85,8, stop medio 75,1.

## Qué se prueba

La base de RTP no tiene información (normal e invertida en cero). Ninguna gestión
la rescata. Solo se prueba si existe un SUBCONJUNTO, definido por un mecanismo que
no sea "barrida + confirmación", donde sí la haya.

Salida fija: cierre a las 12:00 (como la base). **No se barre ratio, ni el 50%,
ni la caja, ni horarios.** Cada filtro tiene un único umbral, fijado aquí.

## Variantes (11 filtros + base = 12 celdas)

Todo dato se conoce en el relleno o antes.

| # | Filtro | Mecanismo | Se conoce en |
|---|---|---|---|
| F1 | caja < mediana de las cajas de las 20 sesiones previas | compresión → expansión | 09:00 |
| F2 | caja ≥ esa mediana | complementaria de F1 | 09:00 |
| F3 | barrido antes de las 09:30 | preapertura, poca liquidez | barrido |
| F4 | barrido a partir de las 09:30 | con la apertura de contado | barrido |
| F5 | dirección = signo(cierre 08:59 − cierre 15:59 sesión anterior) | a favor del sesgo overnight | 09:00 |
| F6 | dirección contraria a ese signo | contra el sesgo | 09:00 |
| F7 | relleno después de 09:41 y dirección = signo(c 09:40 − c 09:10) | fusión con Momento 09:40 | 09:41 |
| F8 | rango de la barra 08:30 > 3 × mediana del rango de 08:20-08:29 | día con dato macro (proxy) | 08:31 |
| F9 | lo contrario de F8 | día sin dato | 08:31 |
| F10 | riesgo / caja < mediana (0,70 fijado a priori como aproximación) | barrido corto | relleno |
| F11 | riesgo / caja ≥ 0,70 | barrido largo | relleno |

## Criterio de éxito (todo tiene que cumplirse)

1. Máximo real de la familia por encima del percentil 95 del máximo del nulo
   (placebo de dirección, mismo sorteo por sesión para las 12 celdas, 1.000 reps).
2. p de la mejor celda < 0,05/12 = 0,0042 (Bonferroni).
3. Exceso sobre paseo aleatorio (6 semillas, misma celda) a ≥ 3σ (regla O).
4. Positiva en los tres años 2023, 2024, 2025 (regla H).
5. Si el filtro es una mitad (F1/F2, F3/F4…), la otra mitad no puede ser igual de
   buena (si lo es, no es el filtro).

Si no se cumple todo: RTP queda enterrada también por la vía de los filtros, y se
anota en CLAUDE.md.

## Potencia (dicho antes de mirar)

Mitades de ~250 ops con sd ~1,3R → ee ≈ 0,085R. Con 12 celdas correlacionadas,
el máximo del nulo esperado ronda +0,15R. Un efecto real por debajo de ~+0,25R
no se podrá distinguir con estos datos. Es una prueba de "¿hay algo grande?".
