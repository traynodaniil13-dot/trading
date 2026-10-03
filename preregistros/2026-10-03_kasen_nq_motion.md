# Pre-registro · "NQ Motion Model" (Kasen) · 03/10/2026

Escrito antes de ejecutar. Versión mecánica del setup de REVERSIÓN (el insignia). Familia
barrida + SMT + IFVG (cerrada por premisa en CLAUDE.md); lo nuevo es el nivel 4H 06:00-10:00.
DISEÑO CFD 2021/2023/2025, NQ y ES Dukascopy alineados por minuto.

## Regla (causal)
- Vela 4H previa = barras 06:00-09:59 NY (alineada con la sesión de 18:00), conocida a las 10:00.
- Ventana 10:00-13:00: primera barra en que NQ rompe el máximo o el mínimo de esa vela 4H.
  Si rompe los dos en la misma barra, fuera.
- SMT: hasta esa barra (desde 10:00), ES NO ha roto su extremo equivalente de la vela 4H.
- Descuento/prima: largo solo si la entrada queda por debajo del 50% del rango 06:00-10:00
  (corto, por encima). Dealing range = esa vela 4H.
- IFVG: tras la barrida, FVG de 1 min a favor de la barrida (nacido en las 30 barras
  anteriores o después de ella, desde 06:00) invertido por un cierre en sentido de la
  reversión, antes de las 13:00. Entrada al cierre de esa barra (i_ent = j+1).
- Stop: extremo de la barrida (mín./máx. desde 10:00 hasta j). Riesgo mínimo 0,05%.
- Objetivo: 1:2 (principal), 1:1 y 1:1,5 informativos, y "extremo opuesto de la vela 4H"
  como objetivo estructural (informativo). Cierre 15:59. Sin break-even (la gestión no crea
  ventaja; se comenta aparte).

## Criterio (1 variante principal: 1:2 → p < 0,05)
R > 0 con p < 0,05, positiva los 3 años, invertida ≤ 0, y mejor que la MISMA regla sin el
filtro SMT (control).
