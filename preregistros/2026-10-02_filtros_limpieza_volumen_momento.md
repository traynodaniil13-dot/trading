# Pre-registro · 2 filtros más sobre MOMENTO 09:40 stop 0,40% 1:2 · 02/10/2026

Escrito antes de ejecutar. Idea de Daniil tras quemar una cuenta en el replay:
operar solo los días "limpios" o con más volumen. Solo información anterior a
la entrada (las 09:40). Que el día "vaya en una dirección" después de entrar no
se puede usar: es futuro (bug nº7).

Base y protocolo idénticos a `2026-09-28_filtros_momento_pct.md` (DISEÑO
2021/2023/2025). Con esos 4 filtros ya probados, la familia de filtros va por 6.

## Filtros (se opera solo si se cumple)
- **F5 tramo limpio**: eficiencia = |c 09:39 − c 09:09| / Σ |c_t − c_{t−1}| de
  las barras 09:10…09:39. Se opera si es mayor que la mediana de esa misma
  cantidad en las 60 sesiones ANTERIORES.
- **F6 volumen alto**: volumen de ticks 09:30…09:39 mayor que la mediana de ese
  mismo tramo en las 60 sesiones anteriores.

## Criterios en DISEÑO (todos, como el 28/09)
1. R filtrada > R base y winrate filtrado > winrate base.
2. n filtrada ≥ 35% de la base.
3. R filtrada > percentil 95 de 1.000 subconjuntos al azar del mismo tamaño.
Informativo (regla P): R por terciles de cada variable, para ver si es monótono.

## VALIDACIÓN (solo si alguno pasa; una ejecución)
Uso nº6 del protocolo → p < 0,05/6 = 0,0083 (una cola), más R > base y >
percentil 95 de subconjuntos al azar.
