# Pre-registro · Mina, tanda 1: M1 valor relativo NQ-ES · M2 desequilibrio de cierre en ES · 04/10/2026

Escrito ANTES de ejecutar. Marco común y criterios: `mina/README.md` y `src/mina.py`.
Datos: CFD NQ y ES de Dukascopy, solo minutos en los que existen los dos.
DISEÑO 2021/2023/2025.

## M1 · Valor relativo NQ-ES (12 variantes)
**Mecanismo:** NQ y ES se mueven juntos (correlación diaria ~0,9). Cuando uno se separa del otro
durante el día, el arbitraje de índices y los rebalanceos de carteras indexadas tienden a
cerrar la brecha (reversión). La alternativa es que la separación refleje información
sectorial (tecnología) que sigue (continuación). Nunca se ha probado en este repo.
- **β diaria:** pendiente MCO del retorno RTH (09:30-15:59) del NQ sobre el del ES en las 20
  sesiones previas. Se conoce antes de abrir.
- **Diferencial** d(t) = ln(NQ_t / NQ_09:29) − β·ln(ES_t / ES_09:29), con cierres de 1 minuto.
- **σ** = desviación típica del d de cierre (15:59) en las 20 sesiones previas.
- **Señal:** el primer minuto, desde la hora de inicio y hasta las 15:00, con |d| ≥ k·σ.
  - REVERSIÓN: se opera contra el signo de d (si d > 0: corto NQ / largo β·ES).
  - CONTINUACIÓN: se opera a favor.
- **Entrada** al cierre del minuto de la señal; el seguimiento empieza en el minuto siguiente.
  **Stop** a 0,5·k·σ en contra (sobre d). **TP** a 2R: en reversión equivale a volver a d = 0.
  Cierre a las 15:59.
- La serie del diferencial solo tiene cierres de 1 minuto (o = h = l = c), así que los toques
  dentro del minuto no se ven. Afecta igual al real y al nulo.
- **Coste:** las dos patas, NQ 0,87 pts / precio NQ + β·0,65 pts / precio ES (en unidades de d).
- **Variantes:** modo {REVERSIÓN, CONTINUACIÓN} × k {1,5, 2,0, 2,5} × inicio {10:00, 12:00} = 12.
- **Nulo:** barajado conjunto. Dentro de cada sesión se reordenan al azar los pares de retornos de
  1 minuto (NQ, ES): se conserva la correlación contemporánea y la volatilidad, y se destruye
  cualquier dinámica del diferencial. 12 semillas.

## M2 · Desequilibrio de cierre en ES (4 variantes)
**Mecanismo:** la publicación del desequilibrio de órdenes de cierre (15:50) mueve más al S&P
500 que al Nasdaq (en ES, el minuto 15:50 puede superar en volatilidad al de las 09:30; ver la
sección 2 de CLAUDE.md). En NQ, F4 dio 55% en diseño y murió en validación. Se prueba en el
instrumento donde el mecanismo es más fuerte.
- **Señal:** signo(c_15:52 − c_15:49) (L3) o signo(c_15:51 − c_15:50) (L1). Entrada al cierre de
  la última barra de la señal.
- **Stop y TP** simétricos a ±k% (1:1) desde la entrada; cierre a las 15:59. k ∈ {0,05%, 0,10%}.
- 2 señales × 2 k = 4 variantes. Coste 0,65 pts. Nulo: paseo aleatorio del ES, 12 semillas.

## Criterios
Los comunes de la mina (p95 del máximo del nulo de la familia, placebo de familia p < 0,05,
3/3 años, invertida ≤ 0). Las supervivientes van a 2022/24/26 con Bonferroni por número de
supervivientes. Esa validación sería el uso nº15 (M1) y nº16 (M2), p < 0,05/15 y 0,05/16 por
idea, sin contar la de Magalá, que va aparte.
