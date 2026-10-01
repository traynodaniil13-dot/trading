# Pre-registro · Order flow aproximado (BVC) · 01/10/2026

Escrito antes de ejecutar. Idea nueva (microestructura de volumen, sitio sin
explorar). Sin datos tick: se aproxima el volumen agresor con Bulk Volume
Classification (Easley, López de Prado y O'Hara 2012) sobre barras de 1 minuto
del NQ futuro (Kaggle, volumen real de CME).

## Aproximación
Por barra: z = (c − o) / σ, con σ = desviación típica de (c − o) de las 1.000
barras ANTERIORES (causal). Delta estimado = v · (2·Φ(z) − 1).
Delta acumulado D(a→b) = suma de deltas de las barras a..b de la sesión.

## Partición
Protocolo alterno con los años del NQ disponibles: DISEÑO 2023 y 2025,
VALIDACIÓN 2024 (solo si algo pasa en diseño).

## Premisas (3) · umbral p < 0,05/3 = 0,0167 (bilateral salvo O3)
- **O1 · El flujo de la apertura predice el día**: s = signo(D 09:30→09:39);
  y = (c 15:59 − o 09:40)·s en puntos.
- **O2 · Absorción** (flujo y precio en desacuerdo de 09:30 a 09:39): solo días
  con signo(D) ≠ signo(c 09:39 − o 09:30); s = signo(D); y igual que O1.
  Si y < 0 de forma significativa, es que gana el precio (no hay absorción útil).
- **O3 · Filtro para Momento 09:40 (stop 0,40%, 1:2)**: R de los días en que
  signo(D 09:09→09:39) = dirección de Momento, frente a los días en que no.
  Éxito si R(de acuerdo) − R(en desacuerdo) > 0 con p < 0,0167 (una cola) y el
  subconjunto "de acuerdo" supera el percentil 95 de subconjuntos al azar del
  mismo tamaño.

Para O1/O2 además: mismo signo en 2023 y 2025, y en largos y cortos (regla M),
|media| > 0,87 pts.
