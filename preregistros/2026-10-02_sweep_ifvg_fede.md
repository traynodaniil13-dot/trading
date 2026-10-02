# Pre-registro · Barrida + IFVG 09:30-10:10 (vídeo de Fede) · 02/10/2026

Escrito antes de ejecutar. Familia "barrida + confirmación" (cerrada por premisa
en CLAUDE.md); se mide igualmente por petición, con versión mecánica sin elegir
temporalidad ni días. DISEÑO: CFD 2021/2023/2025. Validación solo si pasa.

## Regla mecánica (todo causal)
- Niveles: máx/mín overnight = barras 18:00-09:29 de la sesión (conocidos a 09:30).
- Barrida: primera barra 09:30-10:10 con h > máx ON (→ buscar cortos) o l < mín ON
  (→ buscar largos). Solo la primera barrida del día.
- FVG a favor de la barrida (vela de 1 min, 3 barras): alcista si l[i] > h[i−2]
  (para barrida de máximos), bajista si h[i] < l[i−2] (para barrida de mínimos).
  Nace al cierre de la barra i. Se consideran los FVG nacidos desde 09:20.
- IFVG: primera barra posterior a la barrida y a un FVG ya nacido cuyo CIERRE
  atraviesa el FVG en contra (cierre < h[i−2] del FVG alcista → corto; cierre >
  l[i−2] del FVG bajista → largo). Debe ocurrir a las 10:10 o antes.
- Entrada: al cierre de esa barra (regla 3); seguimiento desde la siguiente.
- Stop: extremo de la barrida (máx/mín desde 09:30 hasta la barra de entrada,
  revalidado en la entrada). Si el riesgo < 0,05% del precio, no se opera.
- Objetivo: 1R / 1,5R / 2R (3 celdas del mismo motor). Cierre 10:59 (= 11:00).

## Criterio (umbral p < 0,05/3 = 0,0167, una cola)
R neta > 0 con p < 0,0167, positiva en 2021, 2023 y 2025, por encima del paseo
aleatorio (6 semillas) e invertida no positiva. Winrate se reporta al lado.
