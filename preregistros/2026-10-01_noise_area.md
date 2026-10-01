# Pre-registro · Noise Area (Zarattini, Aziz, Barbon 2024) · 01/10/2026

Escrito ANTES de mirar ningún dato con esta idea. Protocolo de partición
(`2026-09-27_protocolo_particion.md`): DISEÑO 2021/2023/2025, VALIDACIÓN
2022/2024/2026, CFD Dukascopy. Idea nº6 del protocolo → umbral de validación
p < 0,05/6 = 0,0083.

## Fuente
"Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)",
SFI Research Paper 24-97 (2024). 4º premio Quantpedia 2025. SPY 2007-2024: 19,6%
anual neto, Sharpe 1,33. No consta réplica independiente en NQ.

## Por qué es listón (casi) limpio
No es "barrida + confirmación", ni ORB, ni gap, ni Gao (P1, ya muerta). Se
parece a Momento en que es continuación, pero la condición es distinta: un
movimiento ANORMAL respecto a lo que se mueve habitualmente el precio a esa hora,
no el signo de 30 minutos. Se declara solapamiento parcial con Momento.

## Definición (todo causal)
- o = apertura de la barra 09:30 de la sesión. pc = cierre de la barra 15:59 de
  la sesión previa. Si falta alguna, no hay día.
- Puntos de control T ∈ {10:00, 10:30, …, 15:30}. Precio en T = cierre de la
  barra T−1 (conocido en T).
- mov(s, T) = |P(T)/o − 1|. σ(s, T) = media de mov en las 14 sesiones ANTERIORES
  (sin la actual; assert de índices ≥ 0, bug nº8).
- UB = max(o, pc)·(1+σ). LB = min(o, pc)·(1−σ).
- Señal: el PRIMER T del día con P(T) > UB → largo, P(T) < LB → corto
  (primera barra que cumple, no el extremo: bug nº7). Entrada a mercado en la
  apertura de la barra T. Una operación por día (desviación declarada: el
  autor permite reentradas).

## Premisa desnuda (regla Q)
Puntos desde la entrada hasta el cierre de 15:59, con signo de la señal, BRUTOS.
Separado por dirección (regla M). Pasa si: media > 0 con p < 0,05 (una cola),
positiva en los 3 años de diseño, y largos y cortos ambos > 0.
Si no pasa → idea muerta, no se miran las estrategias.

## Estrategias (2 variantes, solo si pasa la premisa)
- **NA-autor**: salida en el primer punto de control posterior con P(T') al otro
  lado de UB(T') (largo) / LB(T') (corto), a la apertura de T'; si no, 15:59.
  Desviación declarada: sin VWAP (el CFD no tiene volumen). En puntos netos (−0,87).
- **NA-1:2** (para la regla B de riesgo): stop = max(o, pc) si largo /
  min(o, pc) si corto (la base de la zona de ruido), objetivo 2× la distancia,
  cierre 15:59. Se salta el día si la distancia < 0,10% del precio o si la
  entrada ya está al otro lado del stop (regla 5).
Pasa diseño si: R (o pts) > 0 con p < 0,025 (0,05/2), 3/3 años positivos, y
exceso sobre paseo aleatorio (6 semillas) con z > 2 (regla O).
Solo la mejor que pase va a validación, una ejecución, umbral p < 0,0083.

## Pendiente, NO se prueba aquí
VWAP trend (Zarattini-Aziz 2023, QQQ): necesita volumen y el CFD no lo tiene.
