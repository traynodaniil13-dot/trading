# Pre-registro · CRT de Will Street (vela diaria + PO3 + breaker 5m) · 04/10/2026

Escrito ANTES de ejecutar. Fuente: resumen del vídeo "Domina la Teoría del Rango de Velas (CRT)
Guía Completa 2026" (youtube sZEoSEttM3A), pasado por Daniil.

## Reglas del autor
- Vela 1 = rango diario. Vela 2 = barre un extremo de la vela 1 y cierra dentro. Vela 3 = se
  opera hacia el extremo opuesto de la vela 1.
- Entrada en la vela 3, en 5m, de 09:00 a 10:30 NY. Tras la mecha de manipulación (PO3),
  orden stop en el breaker (el último máximo de swing que originó el mínimo de la
  manipulación). Sin FVG, iFVG, CISD ni OB.
- Stop en el extremo de la manipulación. TP en el extremo opuesto de la vela 1, como mucho
  3R. Break-even obligatorio al llegar a 1R.
- Solo NY, solo Nasdaq.

## Mecánica (CFD NQ, hora NY)
1. **Velas diarias = sesiones** (18:00 → cierre de 16:15 del CFD), con ≥ 300 barras M1. Para
   operar el día D: vela 1 = sesión D-2, vela 2 = sesión D-1.
   CRT alcista: mín2 < mín1 y mín1 < cierre2 < máx1. Bajista: espejo. Si la vela 2 barre los
   dos extremos, no hay setup.
2. **Ventana:** de 09:00 a 10:30 (la orden tiene que llenarse antes de las 10:30).
3. **Manipulación (alcista):** mínimo de las barras de 5m desde las 09:00, por debajo de la
   apertura de las 09:00. **Breaker:** máximo del pivote de 5m más reciente (por encima de la
   vela anterior y de la siguiente, pivotes desde las 08:00) que sea anterior a la vela del
   mínimo. Se recalcula si se hace un mínimo nuevo.
4. **Orden stop** en el breaker, viva desde que cierra la vela de 5m del mínimo. Relleno al
   CIERRE de la barra M1 que toca el nivel, y esa barra no se evalúa (regla 3).
5. **Stop** = mínimo desde las 09:00 hasta la barra de relleno, incluida. Stop mínimo 0,05%
   del precio. Si el precio ya llegó al máximo de la vela 1 antes del relleno, se cancela.
   Cortos: espejo.
6. **TP** según la variante. **Break-even:** al tocar +1R el stop pasa a la entrada desde la
   barra SIGUIENTE (convención pesimista). Cierre forzado a las 15:59. Coste 0,87 pts.
7. Una operación por día como máximo.

## Variantes (3) → p < 0,05/3 = 0,0167 (una cola)
- **V1 (la del autor):** TP = mín(3R, extremo opuesto de la vela 1) + break-even a 1R.
- **V2:** igual sin break-even.
- **V3:** TP en el extremo opuesto de la vela 1 sin tope de 3R, con break-even.

No se prueba la "entrada de continuación a mitad de rango": es discrecional ("cuando cotiza en
torno al 50%").

## Criterios
- **Diseño 2021/23/25:** p < 0,0167, los 3 años positivos, exceso sobre el paseo aleatorio
  (6 semillas) con z > 2, e invertida ≤ 0 (V2).
- **Después, los 6 años:** como las reglas son del autor, se miden también 2021-2026 sin
  cambiar nada (lo pide Daniil). Es el **uso nº11**: 2022/24/26 solos con p < 0,05/11 =
  0,0045.
- **Informativo:** 1:1, 1:2, largos/cortos, % de días con setup y % de setups que llegan a
  entrar.
