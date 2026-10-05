# Pre-registro · Rejilla coherente: diseño en años IMPARES, validación en PARES · 05/10/2026

Escrito ANTES de ejecutar. Lo pide Daniil: buscar reglas que funcionen muy bien en la mitad de los años,
intercalados, y comprobarlas en la otra mitad. Solo NQ (CFD Dukascopy, 2019-2026).

## Años
- **DISEÑO: 2019, 2021, 2023, 2025** · **VALIDACIÓN: 2020, 2022, 2024, 2026** (2026 hasta el 23/09).
- Contaminación conocida (se dice antes): la celda 09:40/L30 (Momento) ya se vio en 2020/22/24/26 y
  2019. OPEN_DRIVE no está en esta rejilla.

## Familia: momento / reversión a hora fija (el único mecanismo con algo de vida en el NQ)
`src/motores/momento_generico.py`: en T, dirección = signo(cierre T−1 − cierre T−1−L); entrada en la
apertura de T; stop k%; TP a ratio·k%; cierre a las 15:59. La reversión es la invertida.
- T: de 09:35 a 15:00 cada 5 min (66) · L: 5, 10, 15, 30, 60, 120 · k: 0,10 a 0,40% (6) ·
  ratio: 1, 1,5, 2, 3 · modo: momento / reversión → **19.008 reglas**. Sin día de la semana.
- Coste 0,87 pts.

## Filtro de COHERENCIA en diseño (todo a la vez)
1. R > 0 en los 4 años de diseño.
2. **Meseta:** de sus vecinos (T ± 5 min, L y k en el escalón anterior y posterior, mismo modo y
   ratio), al menos el 75% con R de diseño > 0.
3. Al menos 400 operaciones en diseño.
4. **Por encima del azar de la rejilla entera:** R de diseño > p95 del MÁXIMO de las 19.008 reglas
   bajo placebo de dirección (mismo sorteo por sesión para todas, 200 repeticiones; regla B).

## Finalistas y validación
- De las reglas que cumplen 1-4, las 10 con mayor R en su peor año de diseño. Si ninguna cumple el 4,
  **no se gasta la validación** y la rejilla se da por cerrada.
- **Validación (años pares):** cada finalista con p < 0,05/nº de finalistas (una cola) **y** R > 0 en al
  menos 3 de los 4 años pares. Es el uso nº16 del protocolo.
- Si alguna pasa: futuro NQ real como control y forward-test sin dinero antes de hablar de operarla.

Expectativa dicha antes: con 19.008 reglas el máximo del placebo será alto; lo más probable es que
ninguna llegue al punto 4 o que caigan en validación, como en la rejilla del 03/10.
