# Pre-registro · Rejilla de gestión de cuenta para MOMENTO 09:40 · 02/10/2026

Escrito antes de ejecutar. Petición de Daniil: mejorar la tasa de pase / el cobro
cambiando stop, objetivo y tamaño. No es una búsqueda de ventaja: la señal no
cambia. Pero el stop sí cambia la estrategia, así que se separa diseño y control.

## Rejilla (175 celdas)
- Stop k = 0,30 · 0,40 · 0,50 · 0,60 · 0,80 % del precio (precio de hoy ~30.000).
- Ratio objetivo/stop = 1 · 1,5 · 2 · 2,5 · 3 (en evaluación, con "objetivo justo"
  en la última operación; en fondeada el mismo ratio sin ajuste).
- Tamaño: 25K con 1-3 micros; 50K con 1-4 micros (reglas de 50K supuestas).
- Simulador: MLL trailing EOD con breach intradía (MAE real), consistencia 50%,
  retiros (mín. $500), 1.500 cuentas por celda y bloques consecutivos.

## Métrica y criterio
Métrica principal: **EV por cuenta en dólares** (cobrado − precio de la evaluación).
Se reporta también pasan/10 y cobran/10.
1. Se elige la mejor celda por EV en DISEÑO (2021/2023/2025).
2. Se mira su EV y su puesto en CONTROL (2022/2024/2026), por separado.
3. Se recomienda cambiar la gestión actual (0,40% · 1:2 · 1 micro en 25K) solo si
   la celda elegida es mejor que la actual en LAS DOS mitades.
