# Pre-registro · Rejilla momento/reversión en la apertura europea · 02/10/2026

Escrito antes de ejecutar. Sitio NUEVO (CLAUDE.md §9): horario operable por la
mañana en España (08:00-11:00 ES ≈ 02:00-05:00 NY). Mismo motor y misma lógica
que la rejilla de NY del 27/09 (`momento_generico`), en hora de NY. Ojo: en las
~4 semanas al año de desfase de horario de verano, la apertura de Londres cae una
hora distinta en hora de NY; se acepta.

## Regla
P(T) = cierre de la barra T−1; P(T−L) = cierre de la barra T−L−1 (misma sesión).
Momento: dir = signo(P(T) − P(T−L)); reversión: la contraria. Entrada a mercado en
la apertura de T. Stop = k% del precio. Objetivo = ratio × stop. Si no toca nada,
cierre en la barra 08:29 NY (antes de los datos de las 08:30; 14:29 en España).

## Rejilla (432 celdas)
- T ∈ {02:10, 02:30, 03:10, 03:30, 04:00, 05:00} NY (Frankfurt abre 02:00, Londres 03:00)
- L ∈ {10, 30, 60} · modo ∈ {momento, reversión}
- k ∈ {0,10 · 0,15 · 0,25 · 0,40}% · ratio ∈ {1 · 1,5 · 2}

## DISEÑO (CFD NQ 2021/2023/2025)
- Nulo: la rejilla entera sobre paseo aleatorio, 6 semillas → máximo de R y de t.
  Se reporta a cuántas σ está la mejor celda real.
- Finalistas: hasta 3 celdas por t con R ≥ +0,10, positivas los 3 años, y SOLO si
  la mejor celda real supera la media + 2σ del máximo del nulo. Si no, se cierra.

## VALIDACIÓN (2022/2024/2026, una ejecución, solo si hay finalistas)
Uso nº6 del protocolo: p < 0,05/6/nº_finalistas (una cola), positiva los 3 años.
