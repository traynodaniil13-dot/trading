# Protocolo de partición para ideas NUEVAS · 27/09/2026

Fijado antes de probar ninguna idea nueva. No se cambia.

## Partición

- **DISEÑO: 2021, 2023, 2025** (sesiones de esos años naturales).
- **VALIDACIÓN: 2022, 2024, 2026.**

Fuente única: CFD Dukascopy (medio bid/ask) para todos los años. Cada fichero
anual trae el diciembre anterior solo como historia para indicadores.
Hasta tener CFD 2023-2024, esos años no se usan para ideas nuevas.

Por qué alterna: cada mitad mezcla regímenes (2022 bajista en validación; 2025
con crash en diseño), y no hay corte temporal que confunda régimen con ventaja
(regla H).

## Flujo por idea

1. Pre-registro de la idea (premisa, variantes, umbrales) ANTES de mirar DISEÑO.
2. Premisa desnuda en DISEÑO (regla Q). Si da nulo → idea muerta, no pasa a (3).
3. Estrategia y controles completos en DISEÑO (paseo aleatorio, placebo de
   dirección con máximo del nulo, invertida, consistencia).
4. Solo si pasa (3): congelar TODO y escribir el pre-registro de validación.
5. Una sola ejecución en VALIDACIÓN. Sin retoques después.
6. Comprobación en sentido inverso: la premisa (no los parámetros elegidos)
   medida en VALIDACIÓN tiene que dar el mismo signo que en DISEÑO.

## Contabilidad de la validación

VALIDACIÓN se gasta con cada idea que llega a (5). Se lleva la cuenta aquí y el
umbral de la idea k-ésima es p < 0,05 / k (Bonferroni acumulado sobre ideas
validadas, no sobre variantes de diseño, que ya se corrigen en su fase).

| # | Fecha | Idea | Resultado en validación |
|---|---|---|---|
| 1-3 | 27/09 | Rejilla momento/reversión (3 finalistas) | 09:40/L30/0,40%/1:2 mom: +0,086R p=0,049, 3/3 años + (no pasa p<0,005); las otras 2 ≈ 0 |
| 4 | 28/09 | Filtros sobre Momento % | ninguno llegó a validación (no gasta) |
| 5 | 29/09 | Stop estructural S1 (09:09) | +0,097R p=0,056 vs base +0,086 (no pasa p<0,01) |
| 6 | 02/10 | Rotura de inside day (lote 4, ±0,40%) | 51,0% a favor (25/49), p=0,50 (no pasa p<0,0083) |
| 7 | 03/10 | Rejilla masiva alterna (10 finalistas de 28.512) | 9/10 negativas; mejor 09:40 L30 martes +0,192R p=0,061 (umbral 0,00071) |

## Estado de años ya usados (antes de este protocolo)

- RTP y Momento 09:40 ya se evaluaron en 2021-2022 y 2026: no aplican aquí.
- NQ 2023-2025 (Kaggle) se usó en 574 variantes previas: para ideas nuevas se
  usa el CFD de esos años, pero una idea que sea variante de algo ya probado en
  NQ 2023-25 no cuenta como "listón limpio".
