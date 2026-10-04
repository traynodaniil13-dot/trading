# Pre-registro · Lote 6: FOMC, días de dato y volatilidad previa · 04/10/2026

Escrito ANTES de ejecutar. DISEÑO CFD 2021/2023/2025. 2022/24/26 no se tocan.
Lo ya medido no se repite: seguir el dato de las 08:30 o de las 10:00 (lotes 1 y 3) y el
momentum de la última media hora (P1).

## Premisas (6 tests → p < 0,05/6 = 0,0083)

| # | Premisa | Señal (instante en que se conoce) | Medida |
|---|---|---|---|
| F1 | **Deriva previa al FOMC** (Lucca y Moench, 2015) | día de FOMC (calendario, se sabe de antemano) | retorno % del cierre de las 13:59 de la sesión previa al cierre de las 13:59 del día FOMC. Media contra la misma ventana el resto de días, t de Welch, una cola (largo) |
| F2 | **Momentum tras el FOMC** | signo(c 14:14 − o 14:00) del día FOMC (14:15) | carrera ±0,40% desde c 14:14 hasta 15:59, dos colas |
| F3a/b | **Día de dato: la apertura revierte el movimiento del dato** | día de dato = rango(08:30) > 3 × mediana del rango 08:20-08:29 (08:31). Señal −signo(c 09:29 − o 08:30) (09:30) | carrera ±0,25% y ±0,40% desde c 09:29 hasta 15:59, dos colas (continuación o reversión) |
| F4 | **Desequilibrio de cierre (MOC 15:50)** | signo(c 15:52 − c 15:49) (15:53) | carrera ±0,10% desde c 15:52 hasta 15:59, dos colas |
| F5 | **Día tras expansión de volatilidad** | rango RTH previo > 2 × mediana de las 20 sesiones previas; signo(c 09:59 − o 09:30) (10:00) | carrera ±0,40% desde c 09:59 hasta 15:59, dos colas |

- Fechas del FOMC sacadas de memoria (calendario público de la Fed). Si alguna estuviera mal
  solo añadiría ruido, no look-ahead. Daniil puede comprobarlas.
- Carreras con barreras simétricas desde una referencia que no es ninguna de las dos
  (regla 12). Separadas por dirección en el informe (regla M).
- Nulo: las mismas carreras sobre paseo aleatorio (6 semillas). F1 contra el resto de días.

## Criterio para pasar a estrategia

p < 0,0083, mismo signo los 3 años, largos y cortos del mismo lado del 50% (regla M) y
fuera del rango del paseo aleatorio. F1 y F2 tienen n ≈ 24 en diseño: solo un efecto grande
puede pasar. Expectativa dicha antes: F1 es la que tiene más literatura detrás, aunque desde
2015 el efecto se ha debilitado.
