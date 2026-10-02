# Pre-registro · Familia de 9 filtros (18 variantes) sobre MOMENTO 09:40 0,40% 1:2 · 02/10/2026

Escrito antes de ejecutar. Búsqueda amplia propuesta por Claude: mecanismos NO
probados antes (ya probados: día previo, gap, ES, impulso, tramo limpio, volumen).
Todo con barras hasta la 09:39 (conocido a las 09:40). Umbrales causales: mediana
de las 60 sesiones ANTERIORES. DISEÑO 2021/2023/2025. dir = dirección de Momento.

| # | Filtro ("se cumple") |
|---|---|
| F7  | Rango overnight (18:00-09:29)/precio > mediana 60 |
| F8  | Rango 09:30-09:39 / precio > mediana 60 |
| F9  | signo(c 09:39 − VWAP de ticks 18:00-09:39) = dir |
| F10 | signo(c 09:39 − o 09:30) = dir |
| F11 | c 09:39 por encima del punto medio del RTH previo si largo (debajo si corto) |
| F12 | signo(c 09:39 − media de cierres 15:59 de las 20 sesiones previas) = dir |
| F13 | 1ª vela de 5 min (09:30-09:34) en la dirección de dir |
| F14 | c 09:39 en el 25% extremo a favor del rango 09:09-09:39 |
| F15 | Rango de la barra 08:30 / precio > mediana 60 (proxy de día con dato) |

Cada filtro se prueba en sus dos lados ("cumple" y "no cumple"): 18 variantes.

## Criterio en DISEÑO
La mejor variante (máxima R a 1:2) pasa solo si:
1. Supera el percentil 95 del MÁXIMO del nulo: 2.000 repeticiones en las que cada
   filtro se sustituye por un subconjunto al azar del mismo tamaño (y su
   complemento), tomando el máximo de las 18 (regla B/I).
2. R > base, winrate > base, n ≥ 35% de la base, positiva en los 3 años.
Si pasa, una ejecución en VALIDACIÓN (uso nº6, p < 0,0083 una cola, R > base).
Informativo: tabla completa de las 18.
