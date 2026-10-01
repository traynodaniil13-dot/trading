# Pre-registro · Simulador de cuentas con las reglas del bot de Lucid · 01/10/2026

No es un contraste de estrategia: es recalcular el valor esperado por cuenta con
las reglas que ha dado el bot de soporte de Lucid hoy. No hay p-valores ni umbral.

## Cambios respecto a `comparar_cuentas.py` (29/09)
- Fondeada sin tope reducido: 20 micros (25K) / 40 micros (50K) desde el día 1.
- 50K: retiro mínimo $500 (antes supuesto $1.000), máximo $2.000.
- Tras 5 retiros la cuenta pasa a "live": el simulador para ahí (conservador:
  no se cuenta nada de la fase live).
- MLL: el bot dice "End-of-Day drawdown" pero no aclara si un toque intradía
  quema. Se reportan LAS DOS cotas (regla A): intradía (MAE real, como hasta
  ahora) y solo cierre (la operación es una al día y cierra a las 16:00, así que
  equivale a MAE = 0).
- Sin cambios: MLL $1.000 / $2.000 que se congela en inicial+$100, objetivo
  $1.250 / $3.000, consistencia 50% (mejor día ≤ 50% del beneficio), reparto
  90%, 5 días con ≥$100 (25K) / ≥$200 (50K, supuesto) para pedir retiro.

## Escenarios
Momento 09:40 stop 0,40% (116 pts a NQ ~29.000), R por operación desplazada a:
+0,05R (realista), 0 (ventaja nula) y −0,0075R (moneda al aire pagando coste).
Micros 1-6. 3.000 cuentas simuladas por celda, secuencias por bloques.

## Añadido (01/10, tras confirmar el bot que el breach es intradía)
Política de retiro: solicitar solo cuando el importe llegue a X ∈ {500, 750, 1000}
(25K) y {500, 1000, 1500, 2000} (50K). MLL intradía. 4.000 cuentas por celda.
Script: `scripts/cuentas_umbral_retiro.py`.

## Añadido 2 (01/10): negocio de 12 meses con copiador
Dato del usuario: copiador permitido, máx. 5 fondeadas a la vez (10 cuentas total).
Todas las cuentas operan la misma secuencia diaria. K ∈ {1, 2, 3, 5} evaluaciones
vivas a la vez, 250 sesiones, 2.000 años simulados. Script: `scripts/negocio_12m.py`.
