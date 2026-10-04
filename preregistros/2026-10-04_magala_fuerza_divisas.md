# Pre-registro · Sergej Magalá, fuerza relativa de divisas (reversión, diario) · 04/10/2026

Escrito ANTES de tener los datos. Reglas como las pasa Daniil (vídeo de Álex).

## Datos
Velas diarias BID de Dukascopy, 28 pares de EUR, GBP, AUD, NZD, USD, CAD, CHF y JPY, de 2020
a 2026. 2020 solo sirve de calentamiento (EMA100). Se mide 2021 → sep-2026.

## El indicador: aproximación DECLARADA (no es el FSIP exacto)
La fórmula del FSIP no es pública, así que esto es una aproximación (regla F: si brilla, hay
que comprobarlo con el indicador real).
- Para la divisa X, en cada uno de sus 7 pares orientado con X como base: posición del cierre
  dentro del rango máx-mín de las últimas N sesiones, escalada a [−100, +100].
- **Fuerza(X)** = media de los 7 valores. Bandas ±50, como el autor.
- **Variantes:** N = 14 (V1) y N = 20 (V2) → p < 0,05/2 = 0,025.

## Reglas
1. **Señal** al cierre del día t: una divisa X CRUZA a ≤ −50 (el día anterior estaba por
   encima) o a ≥ +50.
2. **Par:** en sobreventa, X frente a la divisa Y de mayor fuerza ese día → largo X/Y. En
   sobrecompra, X frente a la de menor fuerza → corto X/Y. Se opera el par real (si es Y/X,
   en sentido contrario).
3. **Entrada** a la apertura del día t+1. **SL** = 5 × ATR14 del par (media simple del rango
   verdadero) al cierre de t.
4. **Salidas:** el 50% al tocar la EMA50 y el 50% al tocar la EMA100 del par. El nivel de cada
   día es la EMA al cierre del día anterior (causal). Si una EMA está del lado contrario al
   abrir, ese tramo se cierra igualmente al tocarla.
5. **Convención pesimista:** el día de entrada solo cuenta el SL. Cada día se mira primero el
   SL; si salta, cierra todo lo que quede abierto.
6. No se abre un par que ya tenga una operación abierta. Sin límite de tiempo: si los datos
   acaban, se cierra al último cierre.
7. Coste: 3 pips por operación (0,03 en pares con JPY), sobre un riesgo de ~5 ATR (cientos de
   pips): casi irrelevante.

## Criterio
- R > 0 con p < 0,025 (una cola), en 2021-2026.
- Superar el **p95 de la entrada al azar**: mismas fechas, mismo número de operaciones, par y
  dirección al azar, mismas salidas, 200 repeticiones.
- **Invertida ≤ 0.**
- Informativo: R por año, duración, % que llega a cada EMA.

Aviso: es Forex diario con operaciones de semanas. En Lucid (futuros) solo se podría con los
futuros de divisas del CME, y manteniendo posiciones varios días, que la cuenta no permite.
