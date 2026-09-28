# Pre-registro · 4 filtros sobre MOMENTO 09:40 stop 0,40% 1:2 · 28/09/2026

Escrito antes de ejecutar. Base: la candidata tal cual (NQ CFD). Protocolo de
partición: DISEÑO 2021/2023/2025, VALIDACIÓN 2022/2024/2026.

## Filtros (se opera solo si se cumple; dir = dirección de Momento)
- **F1 ES de acuerdo**: signo(ES c 09:39 − ES c 09:09) = dir (CFD USA500).
- **F2 a favor del gap**: signo(o 09:30 − c 15:59 sesión previa) = dir.
- **F3 a favor del día previo**: signo(c 15:59 − o 09:30 de la sesión previa) = dir.
- **F4 impulso fuerte**: |c 09:39 − c 09:09| / precio > mediana de esa misma
  cantidad en las 60 sesiones ANTERIORES (causal, sin mirar el futuro).

## Criterios en DISEÑO (todos)
1. R filtrada > R base y winrate filtrado > winrate base.
2. n filtrada ≥ 35% de la base.
3. R filtrada por encima del percentil 95 de 1.000 subconjuntos al azar del mismo
   tamaño (regla P).
Si varios cumplen, va a validación el de mayor R. Si ninguno, se cierra aquí.

## VALIDACIÓN (una sola ejecución)
Gasta 1 uso más (total 4 en el protocolo) → umbral p < 0,05/4 = 0,0125.
Éxito si: R filtrada > 0 con p < 0,0125 (una cola), R filtrada > R base, winrate
filtrado > base, y R filtrada > percentil 95 de subconjuntos al azar.
