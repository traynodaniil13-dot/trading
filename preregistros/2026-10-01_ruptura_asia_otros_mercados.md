# Pre-registro · Ruptura del rango asiático en PLATA y EUR/USD · 01/10/2026

Escrito ANTES de descargar ni mirar plata ni EUR/USD. Confirmación en otros
instrumentos de la premisa G4 del oro (`2026-10-01_oro_lote1.md`), con las reglas
CONGELADAS. No toca la validación del oro (2012/14/16/18), que sigue ciega.

## Datos
Ticks Dukascopy del repo público FX-Data (XAGUSD-DS, EURUSD-DS) → M1 medio con
`scripts/oro_ticks_a_m1.py` (escala de precio según instrumento). Años 2011-2018
de los dos (todos: ninguno se ha usado nunca para nada).

## Premisa congelada (idéntica a G4, sin tocar nada)
Rango = máx/mín de 19:00-02:59 NY de la sesión. Primera barra desde las 03:00
cuyo CIERRE sale del rango → dirección; entrada apertura de la barra siguiente;
salida cierre de 11:59 NY. Sin ruptura antes de las 11:00, no hay día.
Medida en unidades de rango asiático (pts / ancho del rango del día) para poder
comparar instrumentos, y en precio bruto.

## Criterio (2 contrastes → p < 0,025 cada uno, una cola)
Para cada instrumento por separado: media > 0 con p < 0,025, ≥ 5 de 8 años
positivos, largos Y cortos > 0, y z de exceso sobre paseo aleatorio (6 semillas,
misma rejilla) > 2.
- Pasa en los dos → la premisa del oro es un fenómeno general de "ruptura de
  Londres": muy fuerte a favor, se valida el oro.
- Pasa en uno → pista, nada concluyente.
- Ninguno → lo del oro pesa menos (posible casualidad o régimen bajista del oro).
