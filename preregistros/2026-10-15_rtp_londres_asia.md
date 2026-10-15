# Pre-registro · RTP (Jacko) en las velas de 3h de Londres y Asia · 15/10/2026

Escrito ANTES de ejecutar. Idea de Daniil a partir del vídeo NatOlyJntdw de Jacko ("He ganado 1.067,52€ en 9 minutos
operando 1 sola vela", transcripción pegada por Daniil). En el vídeo el autor dice que la misma regla "también funciona
en Londres y en Asia". En el repo el RTP solo se ha medido en la vela de 09:00 NY (cuatro lecturas, cero; cerrada).
Las velas de Londres y Asia NUNCA se han probado: es la única parte del vídeo con listón limpio.

Expectativa declarada antes: la premisa (barrida → reversión al extremo opuesto) ya está medida en cero (regla N) y la
rejilla de la apertura europea salió como paseo aleatorio. Lo probable es que no sobreviva ninguna.

## Regla (la del autor, congelada; el motor es `src/motores/rtp.py` sin tocar)
Velas de 3h en hora NY (fronteras 18, 21, 0, 3, 6, 9, 12, 15, como el gráfico de 3h del vídeo).
- Caja = máximo/mínimo de la vela de 3h ANTERIOR, conocida al cierre de su última barra M1.
- Barrido: primera M1 de la vela operada cuyo máximo supera el de la caja (→ corto) o cuyo mínimo perfora el de la
  caja (→ largo). Si la misma barra barre los dos lados, no se opera.
- Entrada: límite al 50% de la caja. Relleno al CIERRE de la primera barra posterior al barrido que toca el 50%
  (regla 3); R desde ese cierre (regla 4).
- Stop: extremo barrido (máx./mín. desde el inicio de la vela operada hasta la barra de relleno incluida),
  revalidado en el relleno (regla 5).
- TP: extremo OPUESTO de la caja ("nunca más lejos que el extremo de liquidez opuesto"). Ratio por operación =
  distancia al extremo opuesto / riesgo.
- Cierre a mercado en la última barra de la vela operada. (El autor mueve el TP al extremo de la vela nueva cuando la
  vela cierra: es gestión discrecional y no se modela; mismo criterio que en la medición de NY.)
- Coste 0,87 pts por operación.

## Variantes (2)
- **L · Londres**: caja 00:00-02:59 NY, vela operada 03:00-05:59 (la que el autor hace coincidir con la apertura de
  Londres). Cierre 05:59.
- **A · Asia**: caja 18:00-20:59 NY, vela operada 21:00-23:59. Cierre 23:59. (La de 18:00 no se usa: su vela previa
  cruza la parada del CME.)

## Datos y partición
CFD NQ de Dukascopy (`loader.cargar_cfd`). Diseño impares 2019/2021/2023/2025. Validación pares 2020/2022/2024/2026
SOLO para supervivientes. Ningún año está gastado para estas dos velas.

## Criterios de diseño (los comunes de la mina, `src/mina.py`)
R > p95 del máximo de la familia sobre paseo aleatorio (12 semillas) · placebo de dirección de familia p < 0,05 ·
R > 0 en los 4 años de diseño · invertida ≤ 0.

## Validación (si hay supervivientes)
p 1 cola < 0,05 / nº de supervivientes (0,025 si pasan las dos) y R > 0 en ≥ 3 de 4 años pares. Contará como un
uso más en `preregistros/2026-09-27_protocolo_particion.md`.

## Informativo (no cuenta, no decide)
La vela de 09:00 NY con la misma regla y TP en el extremo opuesto, en los mismos años, solo como referencia de que el
motor reproduce el cero ya conocido.

No se prueban otras horas, otros TP, otros niveles de entrada ni la salida por tiempo. Si L y A mueren, el RTP queda
cerrado en las tres sesiones.
