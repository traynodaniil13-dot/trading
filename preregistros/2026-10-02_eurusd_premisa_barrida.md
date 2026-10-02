# Pre-registro · EUR/USD · Premisa desnuda de la familia "barrida" · 02/10/2026

Escrito ANTES de ejecutar. Primer paso para rejuzgar David Sánchez, 2T y LIT en
el instrumento de sus autores (pendiente nº7). Sus motores y reglas exactas no
están en el repo, así que se empieza por la premisa en la que se apoyan (regla Q):
**"tras barrer un nivel de liquidez, el precio revierte"**. En NQ está medida y es
cero (regla N). EUR/USD 2011-2018 nunca se ha usado para esta premisa (solo para
confirmar la ruptura asiática del oro, otra premisa).

## Datos
`data/eurusd_YYYY.csv.gz` (ticks Dukascopy → M1 medio), `loader.cargar_dukas`,
precio en pips. Partición: DISEÑO 2011/2013/2015/2017; VALIDACIÓN 2012/2014/2016/2018
sin tocar.

## Niveles (causales)
- **ASIA**: máx/mín de 19:00-02:59 NY de la sesión (≥ 300 barras), conocido a las 03:00.
- **PD**: máx/mín de la sesión ANTERIOR completa (sesión del loader, corte 18:00 NY,
  ≥ 1.000 barras), conocido al empezar la sesión. Cada lado solo cuenta si el nivel
  sigue INTACTO entre 18:00 y 02:59 (si ya se rompió antes de la ventana, la
  primera barra de la ventana fuera del nivel no es una barrida).

## Evento (ventana 03:00-10:59 NY: Londres + apertura de NY)
- **Def R ("rompe")**: primera barra de la ventana con h > máximo (barrida arriba) o
  l < mínimo (barrida abajo). Cada lado por separado: un día puede dar las dos.
- **Def C ("rompe y cierra dentro")**: primera barra de la ventana con h > máximo
  y c ≤ máximo (arriba), o l < mínimo y c ≥ mínimo (abajo).
- Referencia = CIERRE de esa barra (conocido al cerrarla; no es el extremo: bug
  nº7/nº12). Carrera desde la barra SIGUIENTE hasta el final de la sesión, a
  barreras SIMÉTRICAS ref ± X pips, X ∈ {5, 10, 20}. Reversión = toca primero la
  barrera del lado contrario a la barrida. Barra que toca las dos: se descarta
  (se cuenta). Sin toque antes del fin de sesión: se descarta (se cuenta).

## Celdas: 2 niveles × 2 definiciones × 3 barreras = 12
Medida: % de reversión, separado por lado (barrida arriba / abajo, regla M) y junto.
Nulo: el mismo procedimiento sobre `controles.paseo_aleatorio` (6 semillas por año,
semilla 21000+10·s+i), regla N: los extremos tienen inclinación propia.
z = (real − nulo)/raíz(ee_real² + ee_nulo²) (regla O).

## Criterio (Bonferroni 12 → p < 0,0042 una cola, z > 2,64)
Una celda PASA si: z > 2,64 en el % de reversión conjunto, los DOS lados por
encima de su nulo, y ≥ 3 de 4 años de diseño por encima del 50%.
- Alguna pasa → hay premisa en EUR/USD: se piden a Daniil las reglas exactas de
  David Sánchez, 2T y LIT y se programan con su propio pre-registro.
- Ninguna pasa → la familia barrida también es cero en EUR/USD: David Sánchez y
  LIT quedan muertas en su instrumento sin programarlas. 2T (si no se apoya en una
  barrida) queda pendiente de sus reglas.
Si sale una reversión MENOR que el nulo de forma significativa (continuación), se
reporta, pero no cuenta como pase: sería otra premisa, a pre-registrar aparte.

Contador: 12 variantes → 1.136.
