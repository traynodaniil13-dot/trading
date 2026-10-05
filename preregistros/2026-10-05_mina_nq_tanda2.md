# Pre-registro · Mina NQ, tanda 2: N1 apertura de Asia · N2 días de tendencia · N3 mecanismo de OPEN_DRIVE · 05/10/2026

Escrito ANTES de ejecutar. Solo Nasdaq (CFD NQ de Dukascopy, hora NY). Marco y criterios comunes:
`mina/README.md` y `src/mina.py`. DISEÑO 2021/2023/2025 · VALIDACIÓN 2022/2024/2026 (solo para
supervivientes, Bonferroni por número de supervivientes de cada familia) · RESERVA CIEGA 2019-2020
(limpia para estas tres ideas). Coste 0,87 pts. Objetivo 2R en todas (1:2), como Momento.

## N1 · Apertura de las bolsas de Asia (8 variantes)
**Mecanismo:** cuando abre la bolsa de contado de Tokio (09:00 JST) o de Hong Kong (09:30 HKT), entra
flujo de carteras asiáticas, que se cubren o reposicionan en futuros de EE. UU. Es el mismo tipo de
efecto que Momento (impulso tras una apertura) en la única sesión que no se ha mirado.
- Hora de apertura en NY calculada cada día con los husos reales: Tokio no tiene horario de verano,
  así que en NY cae a las 20:00 en verano y a las 19:00 en invierno.
- **Señal** a la apertura + 10 min (T): signo(cierre de T−1 − cierre de T−1−L). Entrada en la
  apertura de la vela T. Stop a k% y TP a 2k%. Cierre a las 02:59 NY (antes de Londres).
- Mercado {Tokio, Hong Kong} × L {15, 30} × k {0,15%, 0,25%} = 8.

## N2 · Días de tendencia por el rango de la primera hora (8 variantes)
**Mecanismo:** una primera hora con un rango muy superior a lo normal indica que entra mucho flujo
institucional (noticias, reposicionamiento). Si ese flujo sigue, el día es de tendencia
(continuación); si fue un exceso, revierte. Es distinto de lo ya probado ("continuación de la tarde"
y "vuelta a la media de la mañana"), porque aquí la condición es el TAMAÑO relativo del rango.
- Rango de la primera hora (09:30-10:29) / mediana del mismo rango en las 20 sesiones previas ≥ q.
  Se conoce al cierre de las 10:29.
- **Dirección** = signo(c 10:29 − o 09:30), a favor (CONT) o en contra (REV). Entrada en la apertura
  de las 10:30. Stop a k% y TP a 2k%. Cierre a las 15:59.
- Modo {CONT, REV} × q {1,5, 2,0} × k {0,30%, 0,50%} = 8.

## N3 · Mecanismo de OPEN_DRIVE (6 variantes)
**Mecanismo:** la subasta de apertura deja un desequilibrio. Una primera vela con mucho cuerpo
indica órdenes institucionales en una dirección que no se completan en la subasta y siguen
entrando. OPEN_DRIVE (vela de 5 min, cuerpo > 60%) salió en NQ 2023-25 con p=0,026, pero se
descubrió en datos que se solapan con el diseño. **No es un listón limpio:** lo que decide de
verdad es la validación 2022/24/26 y la reserva ciega 2019-2020, que nunca se han mirado con esta
idea.
- Primera vela RTH de m minutos (09:30 a 09:30+m−1); cuerpo / rango > u. Entrada al cierre de esa
  vela (el seguimiento empieza en la siguiente M1), en la dirección del cuerpo. Stop = rango de la
  vela (mínimo 0,05% del precio) y TP 2R. Cierre a las 15:59.
- m {2, 3, 5} × u {0,6, 0,8} = 6.

## Criterios (los comunes, por familia)
R > p95 del máximo de la familia sobre el paseo aleatorio (12 semillas), placebo de dirección de
familia p < 0,05, R > 0 los 3 años de diseño e invertida ≤ 0. Las supervivientes van a validación
(nuevo uso del protocolo por familia). Si alguna pasa validación, va a la reserva ciega 2019-2020
antes de hablar de operarla.
