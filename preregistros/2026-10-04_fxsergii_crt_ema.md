# Pre-registro · CRT H1 + rotura de EMA 20 en 5m (fxsergii) · 04/10/2026

Escrito ANTES de ejecutar. Fuente: 4 reels de fxsergii, que Daniil pasó el 04/10. Los he
leído por los subtítulos y el gráfico, porque no se puede transcribir el audio.

## Lo que dice el autor (literal, subtítulos)

- "He creado la estrategia con 65% acierto… puedes hacer entradas en Asia… 100%
  backtesteada, llevo más de 50.000 en retiros en Lucid y de 70.000 en los últimos 4
  meses en empresas de fondeo." Panel: $48.276, 25 retiros desde jun-2026.
- "Lo único que debes hacer es encontrar un rango de CRT, sea desde H1 hasta diario
  prácticamente. Fíjate cómo el precio te manipula y te cierra dentro, por lo tanto
  tienes rango de CRT en compras y tu objetivo está justo aquí encima."
- "Una vez tengas esto, […] de la EMA 20. Fíjate cómo el precio rompe con cuerpo donde
  está la redondita roja, rompe con cuerpo, y justo cuando rompa con cuerpo, al cierre
  de la vela, le entras, un ratio uno a uno. Superimportante, el stop en el bajo
  protegido, que es el bajo del rango de CRT."
- Gráfico: US100, 5 min, indicador "MA (20, close)" (el subtítulo dice EMA 20).

## Mecánica (decidida aquí, antes de mirar resultados)

Datos: CFD NQ Dukascopy, hora de NY. **DISEÑO 2021/2023/2025.** No se toca 2022/24/26.

1. **Velas H1** de reloj (hh:00-hh:59), agrupando barras M1 sin usar `label` (bug nº4).
   Una vela H1 se conoce al abrir la primera M1 de la hora siguiente.
2. **CRT alcista:** dos H1 consecutivas A y B (B = A + 1 h, cada una con ≥ 30 barras M1).
   mín_B < mín_A y mín_A < cierre_B < máx_A. **Bajista:** el espejo. Si B barre los dos
   extremos, no hay setup.
3. **Ventana del gatillo:** las velas de 5 min que empiezan entre el fin de B y 60 min
   después, o sea dentro de la vela H1 siguiente ("una vez tengas esto").
4. **Gatillo:** la primera vela de 5 min que rompe la media de 20 velas de 5 min con
   cuerpo. En largos, apertura < media y cierre > media; en cortos, el espejo. La media
   es la del cierre de esa vela, y se conoce al cerrarla.
5. **Entrada** al cierre de la vela de 5 min. Relleno = cierre de su última M1; el
   seguimiento empieza en la M1 siguiente (convención del motor, reglas 2 y 3).
6. **Stop** en el "bajo protegido" = mín_B (largos) / máx_B (cortos). R medida desde el
   relleno real (regla 4).
7. **Revalidación (bug nº11):** si entre el cierre de B y el cierre de la vela gatillo el
   precio perfora mín_B (máx_B en cortos), el setup se cancela. También se cancela si
   en largos el cierre de entrada ya está ≥ máx_A (en cortos, ≤ mín_A), porque entonces
   no queda objetivo por encima.
8. **Stop mínimo** 0,03% del precio (unos 5-9 pts). Por debajo no es operable con coste.
9. **Cierre forzado** en la última barra ≤ 16:09 NY de la sesión. No se entra de
   16:10 a 17:59.
10. Todas las horas, incluida Asia, porque el autor lo dice expresamente. Se permiten
    varias operaciones al día, deduplicadas por barra de entrada.
11. Coste 0,87 pts por operación.

## Variantes declaradas (3) → Bonferroni p < 0,05/3 = 0,0167 (una cola)

- **V1 (la del vídeo):** EMA 20, objetivo 1:1, stop en mín_B/máx_B.
- **V2:** igual, pero con objetivo en el extremo opuesto del rango A ("tu objetivo está
  justo aquí encima").
- **V3:** media simple de 20 en vez de EMA (el gráfico dice "MA (20, close)").

## Criterio para pasar a validación (todos)

- p < 0,0167 en diseño, R neta > 0 en los 3 años y exceso sobre el paseo aleatorio
  (6 semillas por año, la misma mecánica) con z > 2 (regla O).
- Invertida ≤ 0 (si es positiva, hay un bug direccional).
- Si pasa, la validación 2022/24/26 sería el uso nº9, con p < 0,05/9 = 0,0056.

## Informativo (no cuenta para pasar)

Winrate a 1:1 contra el 65% que afirma el autor y el ~50-53% que hace falta para cubrir
costes. Ratios 1:1,5 y 1:2 a partir de rmax. Desglose por sesión (Asia 18:00-02:59,
Londres 03:00-09:29, NY 09:30-16:09), largos/cortos, ventana de 120 min y la otra
convención de la vela de entrada (regla A).
