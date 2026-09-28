# Pre-registro · MOMENTO 09:40 stop 0,40% en S&P 500 (ES/MES) · 28/09/2026

Escrito ANTES de descargar ni mirar ningún dato de ES. El ES no se ha usado
nunca en este proyecto: es una validación en otro instrumento.

## Datos
CFD USA500IDXUSD de Dukascopy (medio bid/ask), sesiones 2021-2026. Mismos
chequeos del loader que el NQ (09:30 por mediana, hora 17 vacía, sin duplicados).

## Regla (congelada, idéntica a la candidata en NQ)
Señal: signo(cierre 09:39 − cierre 09:09). Entrada a mercado en la apertura de
09:40. Stop = 0,40% del precio de entrada. Objetivo = 2 × stop. Cierre 15:59.
Motor común. Coste para MES: $0,74 ida y vuelta / $5 por punto + 2 ticks
(0,5 pts) = **0,65 pts por operación**.

## Prueba (una sola hipótesis)
- Éxito si R neta > 0 con p < 0,05 (una cola) sobre 2021-2026 juntos Y al menos
  4 de 6 años positivos.
- Informativo: R por año, invertida, largos/cortos, paseo aleatorio (6 semillas),
  y correlación día a día con la misma estrategia en NQ.

## Cómo se lee
- Pasa: la candidata gana una confirmación independiente fuerte y se estudia
  operar NQ + ES (dos operaciones al día) en el simulador de cuentas.
- No pasa con mismo signo: sigue viva en NQ, sin confirmación.
- Signo contrario: pesa mucho en contra de la candidata en NQ.
