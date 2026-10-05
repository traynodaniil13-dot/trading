# Pre-registro · Gerard García, "Mi estrategia para retirar 75.000$ de Apex" (L5w_tUcnMfM) · 05/10/2026

Escrito ANTES de ejecutar. Idea traída por Daniil. Solo NQ (CFD Dukascopy), coste 0,87 pts por contrato.
Diseño en años impares 2019/21/23/25; validación en pares 2020/22/24/26 solo para supervivientes.

## Qué se prueba (la versión detallada del vídeo, no el clip de la apertura)
El clip de la apertura (romper una "zona de acumulación" a las 09:30 y piramidar) es la familia ORB /
compresión → ruptura (T3) / OPEN_DRIVE, ya medida: no se repite. Se prueba la regla del vídeo detallado:
1. **Dirección:** EMA 20 en M15 Y en M30, solo con velas YA CERRADAS (conocidas en la barra M1 siguiente
   a su última, bug nº4). Largos si el cierre de la última M15 y el de la última M30 están por encima de
   su EMA 20; cortos si los dos están por debajo. Si no coinciden, no se opera.
2. **Barrida a favor de tendencia (M5):** pivote de M5 (2 velas a cada lado, confirmado al cerrar la 2ª
   posterior). En tendencia alcista, la primera barra M1 que perfora el último mínimo de swing confirmado
   (de las 48 M5 previas) es la barrida. Espejo en cortos.
3. **Imbalance:** al cierre de esa barra se busca el FVG alcista de M5 (mín. vela 3 > máx. vela 1, nacido
   al cerrar la 3ª, de las 48 M5 previas) más cercano por DEBAJO del precio y todavía sin tocar. Orden
   límite de compra en su borde superior. Si no hay FVG, no hay orden. Una orden por día, la primera
   (no se elige otra si esa no se llena: bug nº7).
4. **Promediada (variante):** segunda orden límite en el borde inferior del mismo FVG.
5. **Relleno:** al CIERRE de la barra M1 que toca el nivel; esa barra no se evalúa (regla 3). R desde
   el relleno real.
6. **Salida monetaria sobre la posición total:** stop = SL% del precio (en dinero de 1 contrato), TP =
   0,625 × stop (su $500 contra $800). Con promediada, cada orden es medio contrato y el stop/TP en dinero
   no cambia. En la barra en que entra la 2ª orden no se cuenta TP (no se sabe el orden intrabarra) y el
   stop se mira primero (pesimista).
7. Cierre por tiempo si no toca nada.

## Variantes (8)
Sesión {Londres: órdenes 02:00-04:59 NY, cierre 08:29 · Apertura NY: órdenes 09:30-10:59, cierre 11:59}
× SL {0,25%, 0,50%} × promediada {no, sí}.
Él opera "principalmente Londres"; la apertura NY la menciona como ocasional.

## Criterios
Los comunes de la mina sobre los 4 años impares: R > p95 del máximo de la familia sobre el paseo
aleatorio (12 semillas), placebo de dirección de familia p < 0,05, R > 0 los 4 años, invertida ≤ 0
(invertida = mismos rellenos, dirección contraria, mismo stop/TP en dinero). Supervivientes a los años
pares con p < 0,05/nº de supervivientes y ≥ 3/4 años.
Informativo: winrate (él vende "alta probabilidad"; con TP 0,625R el empate está en 61,5% sin coste),
racha máxima de stops seguidos y frecuencia.

## Avisos dichos antes
- Usa una barrida + FVG, pero A FAVOR de tendencia (continuación tras retroceso), no la barrida como
  giro, que es la familia cerrada por premisa. Por eso se prueba.
- Ratio < 1:1 = winrate alto por construcción. El winrate no dice nada; solo cuenta la R neta.
- Su modelo de negocio (20 cuentas de Apex con copiador) multiplica la varianza; no la ventaja.

## Calibración en paseo aleatorio (antes de mirar datos reales, 24 semillas, rejilla de 2021)
Asimetría direccional (normal − invertida)/2: Londres SL 0,25% sin promediar +0,003 ± 0,013 · NY SL 0,25%
con promediada +0,027 ± 0,013 (2σ, posible ruido con 2 pruebas). Sin cambios en la regla: el criterio de la
familia ya compara contra el máximo del paseo aleatorio, que lleva ese sesgo dentro.

## Corrección 1 (05/10, tras la 1ª ejecución, ANTES de volver a ejecutar) — auditoría visual
Al dibujar las operaciones del 29/09, 30/09 y 01/10/2026 (`resultados/graficos_gerard/`), los FVG elegidos
miden 0,6-2,3 pts: microhuecos de 5 min que ningún trader marcaría como "imbalance", pegados al precio, que se
llenan al instante. Es un fallo de MI interpretación, no del autor. Corrección única, fijada sin mirar
resultados: el FVG tiene que medir al menos el **0,04% del precio** (~12 pts a 30.000, ~8 a 20.000). Todo lo
demás igual. Son 8 variantes nuevas: **la familia pasa a 16** y el umbral de validación se divide por 16.
Criterios iguales (p95 del máximo de las 8 nuevas sobre el paseo aleatorio, placebo, 4/4 años, invertida ≤ 0).
No se harán más correcciones de tamaño de FVG.
