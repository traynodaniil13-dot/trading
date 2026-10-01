# Pre-registro · NQ · Lote 3: días de evento · 01/10/2026

Escrito ANTES de mirar retornos. Protocolo de partición: DISEÑO 2021/2023/2025
(CFD), VALIDACIÓN 2022/2024/2026 sin tocar. 4 premisas → umbral p < 0,0125.
Puntos brutos por operación; pasa si p < 0,0125, mismo signo los 3 años y, con
dirección variable, largos Y cortos con el mismo signo (regla M).

## Calendario FOMC (comunicado a las 14:00 NY; se conoce con meses de antelación → causal)
2021: 27/01 17/03 28/04 16/06 28/07 22/09 03/11 15/12
2023: 01/02 22/03 03/05 14/06 26/07 20/09 01/11 13/12
2025: 29/01 19/03 07/05 18/06 30/07 17/09 29/10 10/12
Comprobación previa permitida (solo volatilidad, no dirección): el rango de la
barra 14:00 de esos días tiene que ser muy superior al de días normales.

## Premisas
- **F1 · Reacción al FOMC (dos colas).** Días FOMC. Dirección = signo(c 14:04 −
  c 13:59). Entrada apertura 14:05, salida cierre 15:59. Se contrasta media ≠ 0
  (continuación si > 0, reversión si < 0), p dos colas < 0,0125.
- **F2 · Deriva previa al FOMC (Lucca-Moench 2015).** Días FOMC: largo de la
  apertura de 09:30 al cierre de 13:59. Control: misma ventana el resto de días
  (exceso = FOMC − media de días normales del mismo año).
- **F3 · Dato de las 10:00 bien medido.** Días con rango(barra 10:00) > 2 × media
  del rango de 09:50-09:59 del mismo día. Dirección = signo(c − o de la barra
  10:00); entrada 10:01, salida cierre 10:59.
- **F4 · Víspera de festivo.** Sesiones cuya siguiente sesión cae > 1 día hábil
  después (festivo de mercado conocido de antemano). Largo de 09:30 a 15:59.
  Control: exceso sobre la media de días normales del mismo año.

## Corrección de medida (01/10, tras la 1ª ejecución, sin cambiar la definición)
F4 salió con n=2: el CFD cotiza en los festivos de EE. UU., así que "siguiente
sesión > 1 día hábil" no los detecta. Se usa el calendario de festivos de la
NYSE (Año Nuevo, MLK, Presidentes, Viernes Santo, Memorial, Juneteenth desde
2022, 4 de julio, Labor Day, Acción de Gracias, Navidad, con traslado de fin de
semana). Víspera = último día hábil anterior al festivo. Los festivos se quitan
también de los días normales del control.
