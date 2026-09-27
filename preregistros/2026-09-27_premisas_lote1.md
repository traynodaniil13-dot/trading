# Pre-registro · Lote 1 de premisas desnudas · 27/09/2026

Protocolo: `2026-09-27_protocolo_particion.md`. Fase: premisa en DISEÑO
(2021, 2023, 2025 · CFD). Escrito antes de calcular nada.

Nota operativa: CFD 2023 aún no ha llegado. Se ejecuta primero con 2021+2025
(preliminar) y el veredicto de diseño se da con los tres años. Nada se cambia
entre una ejecución y otra.

## Formato común

Cada premisa da, por sesión, una señal s ∈ {−1, +1} conocida en t0, y un
resultado y = (precio de salida − precio de entrada) · s, en puntos brutos.
Entrada = apertura de la barra siguiente a t0. Salida = cierre de la barra final.
Todas las horas son NY, inicio de vela, dentro de la misma `sesion` (bug nº6).

## Premisas (7)

| # | Nombre | Señal (se conoce en) | Entrada → salida | Fuente de la idea |
|---|---|---|---|---|
| P1 | Momentum última media hora | signo(c 09:59 − c 15:59 sesión previa) (10:00) | o 15:30 → c 15:59 | Gao-Han-Li-Zhou 2018 |
| P2 | Dato macro 08:30 | solo días con rango(08:30) > 3 × mediana rango(08:20-08:29); signo(c−o de 08:30) (08:31) | o 08:31 → c 08:59 | CLAUDE.md, sin explotar |
| P3 | Dato macro 10:00 | días con rango(10:00) > 3 × mediana rango(09:50-09:59); signo(c−o de 10:00) (10:01) | o 10:01 → c 10:29 | CLAUDE.md, sin explotar |
| P4 | Primera M5 con cuerpo | cuerpo(09:30-09:34) > 60% del rango; signo del cuerpo (09:35) | o 09:35 → c 10:59 | mecanismo de OPEN_DRIVE (NO es listón limpio) |
| P5 | Gap de apertura | \|o 09:30 − c 15:59 previa\| ≥ 0,1% del precio; signo(gap) (09:30) | o 09:31 → c 15:59 | clásico gap-and-go / gap fill |
| P6 | Cambio de mes | días de cambio de mes (último hábil y 3 primeros) vs resto | o 09:30 → c 15:59 (largo) | efecto documentado en índices |
| P7 | Momentum de Londres | signo(c 04:59 − o 02:00) (05:00) | o 05:00 → c 07:59 | killzone de Londres, poco explorada |

P6 no es direccional con señal: se contrasta media(y) en días de cambio de mes
menos media(y) en el resto, con y = retorno largo.

## Criterio para pasar a fase de estrategia (todo a la vez)

1. p bilateral < 0,05/7 = 0,0071 sobre los tres años de diseño.
2. Mismo signo en 2021, 2023 y 2025 por separado.
3. Separado por dirección (regla M): el efecto tiene el mismo signo en s=+1 y s=−1.
4. |media| > 0,87 pts (si no cubre el coste, no es operable aunque sea real).
5. Sobre paseo aleatorio (6 semillas, misma rejilla) la misma premisa da ~0.

Momentum o reversión cuentan igual (por eso bilateral): el signo lo decide el dato.
