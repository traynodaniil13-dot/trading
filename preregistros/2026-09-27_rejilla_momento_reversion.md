# Pre-registro · Rejilla momento/reversión a hora fija · 27/09/2026

Protocolo: `2026-09-27_protocolo_particion.md`. Búsqueda amplia declarada en
DISEÑO (2021, 2023, 2025 · CFD) y validación única de finalistas en 2022, 2024,
2026. Escrito antes de ejecutar.

Objetivo pedido: estrategias tipo 1:1,5 con ~49% de acierto o 1:2 con ~40%, es
decir ≥ +0,2R por operación neta.

## Regla

- A la hora T se compara P(T) = cierre de la barra T−1 (conocido en T) con
  P(T−L) = cierre de la barra T−L−1. Todas las barras dentro de RTH de la sesión.
- Momento: dir = signo(P(T) − P(T−L)). Reversión: dir contraria.
- Entrada a mercado en la apertura de la barra T. Stop = k% del precio de entrada.
  Objetivo = ratio × stop. Si no toca nada, cierre en la barra 15:59.
- Motor común (`src/motor.py`): vela de entrada solo adverso, stop gana en empate,
  coste 0,87 pts.

## Rejilla (504 celdas)

- T ∈ {09:40, 10:00, 10:30, 11:00, 13:00, 14:00, 15:00} (7)
- L ∈ {10, 30, 60} min (3)
- Modo ∈ {momento, reversión} (2)
- k ∈ {0,10%, 0,15%, 0,25%, 0,40%} (4)
- ratio ∈ {1,5 · 2} (2) … más ratio 1 como referencia (3 ratios) → 7×3×2×4×3 = 504

## Selección en DISEÑO

Ranking por t de la R neta media en los tres años juntos. Finalistas = las 10
primeras con R ≥ +0,10 y positivas en los tres años de diseño. Si hay menos de
10 que cumplan, van las que haya.

Nulo de la búsqueda: la rejilla entera sobre paseo aleatorio (6 semillas, misma
rejilla temporal) → distribución del MÁXIMO de R y del máximo de t (regla B/I).
Se reporta a cuántas σ está la mejor celda real del máximo del nulo.

## Validación (una sola ejecución, sin retoques)

Cada finalista, tal cual, en 2022+2024+2026:
- Éxito si R neta > 0 con p < 0,05/10 = 0,005 (una cola) Y positiva en los
  tres años por separado.
- Se reporta winrate, R, invertida y consistencia de cada finalista.

Contabilidad: esta prueba gasta 10 usos de la validación (tabla del protocolo).

## Expectativa dicha antes

La celda ganadora de diseño estará casi seguro en +0,15/+0,25R por pura
búsqueda. Si en validación las 10 caen a ~0, la familia queda cerrada con
datos limpios. Si alguna aguanta con p < 0,005 y los tres años positivos, pasa a
simulador de cuentas y forward-test en demo.
