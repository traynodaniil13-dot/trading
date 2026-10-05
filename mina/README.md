# La mina de estrategias

Proceso para buscar estrategias en serie sin fabricar falsos positivos. Lo pidió Daniil el
04/10/2026. Por ahora, solo con los datos que hay sin pagar (CFD de NQ y ES de Dukascopy
2021-2026, M1; divisas diarias).

## Reglas (no se negocian)
1. **Solo familias con mecanismo.** Cada tanda explica QUIÉN está obligado a comprar o vender y
   POR QUÉ en ese momento. Nada de rejillas a ciegas: 28.512 reglas ya demostraron que eso
   solo produce ruido (`resultados/2026-10-03_rejilla_masiva_alterna.txt`).
2. **Solo Nasdaq (NQ/MNQ): es lo único que Daniil quiere operar (05/10).** Otros mercados no se
   descargan ni se prueban salvo que él lo pida. Dentro del NQ, sitios nuevos antes que el pozo viejo. El NQ intradía con premisas simples está muy
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

| NQ-2 | N1 apertura de Asia (8) · N2 días de tendencia (8) · N3 OPEN_DRIVE (6) | N1 y N2 **MUERTAS**; N3 no pasa (placebo p=0,075), la mejor regla dio +0,196R en años no vistos con p=0,039 (umbral 0,0083) |
| Rejilla | Momento/reversión a hora fija, impares→pares, 19.008 reglas | **CERRADA**: 0 por encima del p95 del placebo de la rejilla; validación sin gastar |

| NQ-3 | T1 inventario overnight (8) · T2 rango overnight (8) · T3 compresión → ruptura (4), impares→pares | T1 **MUERTA**; T3 no pasa (+0,186R, 4/4 años, < p95 nulo); T2 mal especificada (1 caso), no se rehace |
| NQ-4 | U1 ruptura de máx./mín. de N días (6) · U2 rebalanceo de ETFs apalancados al cierre (8), impares→pares | U1 **MUERTA** (−0,06 a −0,12R, placebo p=0,80) · U2 **MUERTA** (−0,07 a −0,24R, 0/4 años; la invertida sale +0,05/+0,17, solo como dato) |
| NQ-5 | V1 reversión del día al cierre (8, hipótesis de U2, medida SOLO en pares) · V2 reversión de extremos de 60 min (6, impares→pares) | V1 **MUERTA** (mejor +0,013R, p=0,43; 2020/22 negativos) · V2 **MUERTA** (todas ≤ 0, placebo p=0,90) |

## Próximas tandas (pendientes de datos)
- M3 (oro): **CANCELADA el 05/10** sin ejecutar, porque Daniil solo opera Nasdaq. El pre-registro queda archivado, la descarga se paró y no se mira el resultado. **Pre-registrada el 04/10** (`preregistros/2026-10-04_mina_tanda3_momento_oro.md`, `scripts/mina_tanda3_oro.py`); falta bajar XAUUSD 2021/23/25.
- Petróleo y DAX: descartados (no son Nasdaq).
