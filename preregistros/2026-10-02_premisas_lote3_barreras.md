# Pre-registro · Lote 3 de premisas en NQ, solo TP-vs-SL · 02/10/2026

Escrito antes de ejecutar. Petición de Daniil: seguir en NQ, ventaja que venga de tocar
TP antes que SL. DISEÑO CFD 2021/2023/2025. Medida única para todas (regla Q/nº12):
desde el cierre de la barra de referencia, carrera a barreras SIMÉTRICAS ±k% hasta 15:59;
% de resueltas a favor de d (empate en la misma barra = en contra). k ∈ {0,15·0,25·0,40}.
Se prueba a dos colas (si sale < 50%, la estrategia es la contraria).

| # | Evento (barra de referencia) | d |
|---|---|---|
| L1 | Dato 08:30: barra 08:34 | signo(c 08:34 − o 08:30) |
| L2 | Dato 10:00: barra 10:04 | signo(c 10:04 − o 10:00) |
| L3 | Vela gigante: 1ª barra 10:00-15:00 con rango > 4× mediana de las 20 previas | signo(c − o) de esa barra |
| L4 | Vuelta al VWAP (desde 09:30): todo 10:00-10:29 a un lado; 1er toque después de 10:30 | rebote (lado del que venía) |
| L5 | Número redondo: 1er toque de un múltiplo de 250 pts en 10:00-15:00 | dirección con la que llega |
| L6 | Tarde: barra 15:29 | signo(c 15:29 − c 12:29) |
| L7 | Mediodía: barra 11:59 | −signo(c 11:59 − o 09:30) (reversión de la mañana) |
| L8 | Hueco: barra 09:30 | signo(cierre 15:59 previo − o 09:30) (cerrar el hueco) |

## Criterio (24 tests → p < 0,05/24 = 0,0021, binomial dos colas)
Una celda pasa si: p < 0,0021; el mismo lado de 50% en largos Y en cortos (regla M);
y |%a favor − 50%| supera el p95 del MÁXIMO de las 24 celdas sobre paseo aleatorio
(6 semillas, misma rejilla). Si pasa → pre-registro de estrategia y validación (uso nº6).
