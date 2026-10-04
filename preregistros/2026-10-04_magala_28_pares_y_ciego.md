# Pre-registro · Magalá con los 28 pares reales + reserva ciega 2018-2020 · 04/10/2026

Escrito ANTES de tener los datos. Reglas congeladas: `scripts/magala_fuerza.py` tal cual
(FSIP aproximado, bandas ±50, SL 5·ATR14, TP 50% en la EMA50 y 50% en la EMA100, coste 3 pips).
**Solo V1 (N=14)**, la que se fijó primero; V2 (N=20) se reporta como informativa.

## Datos
Velas diarias BID de Dukascopy de los 28 pares REALES (sin cruces sintéticos), 2017-2025.
2017 solo sirve de calentamiento.

## Pruebas
1. **Réplica 2021-2025 con datos reales.** Comprueba si el resultado del plan B (+0,027R) se
   debía a los cruces sintéticos. Informativa: esos años ya se han visto.
2. **RESERVA CIEGA 2018-2020** (señales con fecha de entrada de 2018 a 2020; nadie ha mirado
   estos años con esta idea). **Es la prueba que decide.**
   - Pasa si: R > 0 con p < 0,05 (una cola), por encima del p95 de la entrada al azar (mismas
     fechas, par y dirección al azar, 200 repeticiones), invertida ≤ 0 y al menos 2 de los 3
     años positivos.
   - Si no pasa, queda como pista muerta y no se reabre con otros N, bandas ni salidas.
Aviso que no cambia: Forex diario con operaciones de semanas, no operable en Lucid. Si pasara,
el siguiente paso sería ver cómo llevarlo a algo operable (futuros de divisas del CME o una
cuenta de Forex), no operarlo ya.
