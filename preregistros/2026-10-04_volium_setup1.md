# Pre-registro · TRADING VOLIUM, setup 1 (1D → barrida H1 → V + IFVG en 5m, 1:2) · 04/10/2026

Escrito ANTES de ejecutar. Fuente: youtube pPynrVyQ5x8 (resumen pasado por Daniil).
Solo el setup 1: el 2 (scalping M1) es discrecional y el autor lo dejó, y el 3 (swing) mantiene
semanas, imposible en Lucid. El autor opera el GER40; aquí se prueba en NQ, porque no hay
datos del DAX (él afirma que vale para otros activos).

## Mecánica (CFD NQ, hora NY)
1. **Tendencia diaria** (aproxima "¿quién domina en el diario?"): con las velas de sesión hasta
   la anterior, alcista si cierre > EMA20 diaria y EMA20 > EMA20 de 5 sesiones antes; bajista
   al revés. Si no, "diario confuso" → no se opera.
2. **Barrida H1 a favor:** pivotes H1 (2 velas a cada lado, confirmados al cerrar la 2ª
   posterior). En tendencia alcista, el mínimo de swing H1 más reciente, confirmado y sin
   barrer. Barrida = la primera M1 entre las 08:00 y las 11:30 que lo perfora. El TP es el
   máximo de swing H1 más reciente anterior a la barrida (donde empezó el retroceso), y tiene
   que estar por encima del precio. Bajista: espejo.
3. **Confirmación 5m** (velas alineadas desde las 08:00), hasta las 12:00: la primera vela de
   5m que cumpla las dos cosas a la vez:
   - cierra por encima del techo de algún FVG bajista de 5m nacido desde el máximo del retroceso
     (IFVG con cuerpo);
   - el cierre recupera ≥ 30% del tramo de manipulación (de ese máximo al mínimo desde la
     barrida).
4. **Entrada** al cierre de esa vela; el seguimiento empieza en la M1 siguiente. **SL natural** =
   mínimo desde la barrida hasta la entrada. R:R natural = (TP − entrada) / (entrada − SL).
5. **Variantes (2) → p < 0,05/2 = 0,025:**
   - **V1 (la del autor):** solo si el R:R natural ≥ 2. El SL se ensancha para que el TP quede
     a 2R exactos (SL = entrada − (TP − entrada)/2).
   - **V2:** solo si el R:R natural ≥ 2, con el SL natural y el TP estructural.
6. Stop mínimo 0,05% del precio. Cierre a las 15:59. Una operación al día. Sin break-even.
   Coste 0,87 pts.

## Criterios
- **Diseño 2021/23/25:** p < 0,025, los 3 años positivos, exceso sobre el paseo aleatorio con
  z > 2 (6 semillas), invertida ≤ 0 (V1).
- **Después, los 6 años** (reglas fijadas): **uso nº14**, 2022/24/26 solos con
  p < 0,05/14 = 0,0036.
- Informativo: winrate frente al "70-80%" que afirma, frecuencia, largos/cortos.
