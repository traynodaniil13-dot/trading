# Pre-registro · 4 filtros de NIVELES (PDH/PDL/overnight) sobre MOMENTO 09:40 stop 0,40% 1:2 · 02/10/2026

Escrito ANTES de ejecutar. Idea de Daniil: confirmar la señal con la liquidez del
día anterior y del overnight. Segundo lote de filtros sobre esta candidata (el
primero, 28/09, 4 filtros, ninguno pasó). Base: la candidata tal cual (NQ CFD).
Partición: DISEÑO 2021/2023/2025, VALIDACIÓN 2022/2024/2026.

## Niveles (todos causales, conocidos antes de la apertura de 09:40)
- **PDH/PDL**: máximo/mínimo de las barras 09:30-15:59 de la sesión ANTERIOR
  (conocidos a las 16:00 del día previo).
- **ONH/ONL**: máximo/mínimo de las barras 18:00-09:29 de la sesión actual
  (conocidos a las 09:30).
- **Señal**: c(09:39) (conocido en la apertura de 09:40). Entrada = o(09:40),
  objetivo = entrada + dir · 2 · riesgo (riesgo = 0,40% del precio).
Si un nivel no existe (primera sesión del fichero), el filtro no se cumple.

## Filtros (se opera solo si se cumple; dir = dirección de Momento)
- **N1 camino libre**: ninguno de PDH, PDL, ONH, ONL está estrictamente entre la
  entrada y el objetivo.
- **N2 rango previo roto**: largo si c(09:39) > PDH; corto si c(09:39) < PDL.
- **N3 tercio overnight**: pos = (c(09:39) − ONL)/(ONH − ONL). Largo si pos > 2/3,
  corto si pos < 1/3 (pos puede salir de [0,1]: cuenta).
- **N4 barrida en contra**: largo si alguna barra de 18:00-09:39 tuvo l < PDL y
  c(09:39) > PDL; corto si alguna tuvo h > PDH y c(09:39) < PDH. (Familia
  "barrida": premisa medida en cero, regla N. Se incluye a petición.)

## Criterios en DISEÑO (todos)
1. R filtrada > R base y winrate filtrado > winrate base.
2. n filtrada ≥ 20% de la base (~50 ops/año; el 28/09 era 35%: se baja porque
   N2/N4 son raros por construcción, y se declara aquí antes de ver nada).
3. R filtrada por encima del percentil 95 de 1.000 subconjuntos al azar del mismo
   tamaño (regla P).
Si varios cumplen, va a validación SOLO el de mayor R. Si ninguno, se cierra y se
opera Momento sin filtros.

## VALIDACIÓN (una sola ejecución, solo si algo pasa)
5º uso de la validación en el protocolo → umbral p < 0,05/5 = 0,01. Éxito si:
R filtrada > 0 con p < 0,01 (una cola), R filtrada > R base, winrate > base, y
R filtrada > percentil 95 de subconjuntos al azar.

Contador: 4 variantes → 1.124.

## Resultado DISEÑO (02/10): NINGUNO PASA → se cierra, validación sin gastar
Base +0,104R (n=739, wr 41,9%). N1 camino libre +0,100 (24%, p95 azar +0,261,
2025 −0,117) · N2 rango previo roto +0,065 (26%, 2025 −0,125) · N3 tercio
overnight +0,136 (57%, wr 43,3%, p95 azar +0,177, 3/3 años) · N4 barrida en
contra +0,022 (27%). Niveles comprobados a mano (14/06/2023).
`resultados/2026-10-02_filtros_niveles_momento_diseno.txt`.
