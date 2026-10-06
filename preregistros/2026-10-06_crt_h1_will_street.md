# Pre-registro · CRT de Will Street en H1 (vídeo BvU8Aanzue0, "8 conceptos") · 06/10/2026

Escrito ANTES de ejecutar. Idea traída por Daniil. Solo NQ (CFD), coste 0,87 pts.
Diseño en impares 2019/21/23/25; validación en pares 2020/22/24/26 solo para supervivientes.

## Qué hay ya y qué es nuevo
La versión DIARIA (vela 1/2/3 diarias + PO3 + breaker 5m 09:00-10:30) se probó el 04/10 y murió
(diseño −0,18R; 6 años = paseo aleatorio). En este vídeo el autor dice que el modelo es FRACTAL y su
ejemplo en vivo es un **rango de 1 hora** en la sesión de NY (desde las 09:00). Eso es lo nuevo: la
misma mecánica en H1. Sin break-even (no lo menciona aquí), TP "como mucho 3R".
No se prueban NWOG/NDOG (es un "bonus" de imán/soporte sin regla de entrada).

## Mecánica común (hora NY, velas H1 de reloj, velas 5m agrupadas desde M1 sin label)
- **Breaker (largos):** tras la manipulación (mínimo de las 5m desde el inicio de la vela operativa),
  máximo del pivote de 5m más reciente (por encima de la anterior y la siguiente, confirmado al cerrar
  la siguiente) anterior a la vela del mínimo; se recalcula con cada mínimo nuevo. **Orden stop** en el
  breaker; relleno al CIERRE de la M1 que lo toca (regla 3). Cortos: espejo.
- **Stop** = extremo desde el inicio de la vela operativa hasta la barra de relleno (mín. 0,05%).
- Se cancela si el objetivo (extremo opuesto de la vela de rango) se toca antes del relleno.
- Cierre a las 15:59. Una operación al día.

## Lectura A — la vela que barre es la operativa (PO3 dentro de la vela)
Vela de rango = H1 anterior; vela operativa = H1 de las 09:00 (y si no hay operación, la de las 10:00).
Dirección: el primer extremo de la vela de rango que se perfora dentro de la operativa (si los dos en la
misma M1, nada). La manipulación tiene que estar más allá de ese extremo y de la apertura de la vela
operativa; la orden tiene que llenarse dentro de esa hora.

## Lectura B — vela 1/2/3 como en la diaria
Vela 1 = H1 de las 08:00; vela 2 = H1 de las 09:00, que barre UN extremo de la 1 y cierra dentro.
Vela 3 = H1 de las 10:00: manipulación más allá de su apertura, breaker y relleno dentro de esa hora.

## Variantes (4)
{A, B} × TP {mín(3R, extremo opuesto de la vela de rango), 3R fijo}.

## Criterios
Los comunes de la mina sobre los 4 años impares (p95 del máximo de la familia sobre el paseo aleatorio,
12 semillas; placebo de familia p < 0,05; 4/4 años; invertida ≤ 0). Supervivientes a pares con
p < 0,05/nº y ≥ 3/4 años. Calibración en paseo aleatorio antes de mirar datos reales.
Expectativa dicha antes: la diaria y el CRT H1 de fxsergii murieron; lo probable es que esta también.

## Calibración en paseo aleatorio (antes de mirar datos reales, rejilla de 2021)
24 semillas: A mín −0,011 ± 0,013 · A 3R −0,046 ± 0,020 · B mín +0,099 ± 0,048 · B 3R +0,127 ± 0,082.
B, 48 semillas más: +0,041 ± 0,032 (solo ~15 operaciones/año en el paseo: ruido grande). Posible sesgo
leve en B (~2σ juntando todo). No se toca la regla: el criterio compara con el máximo del paseo
aleatorio, que lleva ese sesgo dentro, y cualquier superviviente de B se tendrá que juzgar como exceso
sobre su nulo.
