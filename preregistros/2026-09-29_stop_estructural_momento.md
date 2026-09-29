# Pre-registro · Stop estructural para Momento 09:40 · 29/09/2026

Escrito antes de ejecutar. Señal y entrada idénticas a la candidata (cierre 09:39
vs cierre 09:09, entrada a mercado en la apertura de 09:40, 1:2, cierre 16:00).
Solo cambia DÓNDE va el stop. Protocolo: DISEÑO 21/23/25, VALIDACIÓN 22/24/26.

## Variantes (2)
- **S1 · stop en el precio de las 09:09** (cierre de la barra 09:09, la referencia
  de la señal). Objetivo = entrada ± 2 × distancia.
- **S2 · stop en el extremo de 09:09-09:39**: mínimo de esas barras si largo,
  máximo si corto. Objetivo = 2 × distancia.
Reglas comunes (fijadas ahora): si la distancia del stop es < 0,10% del precio,
ese día NO se opera (el coste se comería la R); si la entrada ya está al otro
lado del stop (revalidación, bug nº11), tampoco.

## DISEÑO — pasa a validación la mejor que cumpla todo
1. R > +0,104 (la base con stop 0,40% en diseño).
2. R > 0 en 2021, 2023 y 2025.
3. n ≥ 50% de la base.

## VALIDACIÓN (una ejecución) — gasta 1 uso (total 5 → p < 0,01)
Éxito si R > 0 con p < 0,01 (una cola), R > base en validación (+0,086) y
positiva en 2022, 2024 y 2026.
