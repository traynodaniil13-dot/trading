# La mina de estrategias

Proceso para buscar estrategias en serie sin fabricar falsos positivos. Lo pidió Daniil el
04/10/2026. Por ahora, solo con los datos que hay sin pagar (CFD de NQ y ES de Dukascopy
2021-2026, M1; divisas diarias).

## Reglas (no se negocian)
1. **Solo familias con mecanismo.** Cada tanda explica QUIÉN está obligado a comprar o vender y
   POR QUÉ en ese momento. Nada de rejillas a ciegas: 28.512 reglas ya demostraron que eso
   solo produce ruido (`resultados/2026-10-03_rejilla_masiva_alterna.txt`).
2. **Sitios nuevos antes que el pozo viejo.** El NQ intradía con premisas simples está muy
   exprimido. Primero, mecanismos no probados o instrumentos/datos nuevos.
3. **Pre-registro de cada tanda** en `preregistros/` ANTES de ejecutar: variantes, parámetros,
   costes y criterios.
4. **Diseño 2021/2023/2025 → validación 2022/2024/2026 → reserva ciega final** (2019-2020 u otros
   años no vistos). Los años de validación solo se tocan con las supervivientes.
5. **Criterios de diseño, comunes a todas las familias** (`src/mina.py`):
   - R > p95 del MÁXIMO de la familia sobre el nulo: paseo aleatorio, o barajado conjunto si la
     familia usa varios instrumentos;
   - placebo de dirección de familia con p < 0,05;
   - R > 0 los 3 años;
   - invertida ≤ 0.
6. **Validación** con Bonferroni por nº de supervivientes, contada en
   `preregistros/2026-09-27_protocolo_particion.md`.
7. **Nada se opera con dinero** hasta pasar la reserva ciega. Y aun así, primero con tamaño
   mínimo.
8. **Coste siempre:** NQ 0,87 pts y ES 0,65 pts por operación y contrato micro (comisión + 2 ticks).

## Estado de las tandas
| Tanda | Familia | Estado |
|---|---|---|
| M1 | Valor relativo NQ-ES intradía (reversión/continuación del diferencial), 12 variantes | **MUERTA** (04/10): mejor +0,088R con n=30, por debajo del p95 del nulo (+0,200); placebo de familia p=0,44. Separaciones ≥1,5σ solo en ~20% de los días, sin dirección. |
| M2 | Desequilibrio de cierre en ES (MOC 15:50), 4 variantes | **MUERTA** (04/10): wr 45-49% a 1:1, todas negativas los 3 años (−0,08 a −0,33R con coste). |

## Próximas tandas (pendientes de datos)
- M3: Momento de apertura en el oro (08:20 NY, 9 variantes). **Pre-registrada el 04/10** (`preregistros/2026-10-04_mina_tanda3_momento_oro.md`, `scripts/mina_tanda3_oro.py`); falta bajar XAUUSD 2021/23/25.
- Después: petróleo (09:00 NY) y DAX (03:00 NY) con la misma lógica, si M3 da algo o para cerrar la familia.
