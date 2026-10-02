# Diario · forward-test en demo de Momento 09:40

`momento_0940_demo.csv`: una fila por día operado. Columnas del trading-ledger +
5 propias del forward-test:

| Columna | Qué es |
|---|---|
| `p_0909` | Cierre de la vela de 09:09 NY (referencia) |
| `p_0939` | Cierre de la vela de 09:39 NY (señal) |
| `precio_pedido` | Precio en pantalla al lanzar la orden (apertura de 09:40) |
| `entry_price` | Precio REAL de relleno |
| `deslizamiento_pts` | (relleno − pedido) en contra de ti, en puntos. Positivo = te costó |
| `riesgo_pts` | 0,40% del precio de relleno (distancia al stop) |

## Rutina (2 minutos)
1. **A las 15:40 España (09:40 NY)** mira el cierre de 09:09 y el de 09:39.
   09:39 > 09:09 → largo; 09:39 < 09:09 → corto.
   ⚠ **Del 26 al 30 de octubre de 2026 es a las 14:40** (Europa cambia de hora el
   25/10 y EE. UU. el 01/11). Lo mismo en marzo.
2. Orden **a mercado en el segundo 0 de las 09:40**, sin perseguir precio
   (prueba U8: entrar en el peor precio de la vela hunde la ventaja a −0,07R).
3. Stop = relleno ∓ 0,40% del relleno. Objetivo = relleno ± 0,80%.
4. Si no toca ninguno, cierra a las 16:00 NY (22:00 España).
5. Dímelo así: *"corto 1 MNQ, 09:09 21510, 09:39 21480, pedí 21478, me lo dieron
   en 21476, stop 21562, objetivo 21304, tranquilo"* — y al cerrar: *"cerrado en
   21304"* o *"stop"*.

## Qué vamos a mirar
- A las **40-60 operaciones**: R medio real vs backtest (+0,05/+0,10R esperado),
  deslizamiento medio (si pasa de ~3-4 pts, se come la ventaja), y % según plan.
- La demo NO aprueba la estrategia (60 ops tienen un error de ±0,2R); sirve para
  medir la ejecución y cazar un bug nº13 si los números no se parecen en nada.
