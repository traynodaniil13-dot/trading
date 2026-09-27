# Pre-registro · Lote 2 de premisas desnudas · 27/09/2026

Protocolo: `2026-09-27_protocolo_particion.md`. Fase: premisa en DISEÑO
(2021, 2023, 2025 · CFD). Escrito antes de calcular nada. Mismo formato y
criterios que el lote 1 (s ∈ {−1,+1} conocida antes de entrar; y = puntos a
favor de s, brutos; entrada en la apertura de la barra siguiente a la señal).

RTH = barras 09:30-15:59 de la misma sesión. "Cierre del día" = c 15:59.

## Premisas (7)

| # | Nombre | Señal (se conoce en) | Entrada → salida | Idea |
|---|---|---|---|---|
| Q1 | Vuelta a la media de la mañana | dev = c 10:59 − media de los precios típicos (h+l+c)/3 de 09:30-10:59; si \|dev\| > 0,5 × rango 09:30-10:59: s = −signo(dev) (11:00) | o 11:00 → c 12:59 | reversión a VWAP (sin volumen: media simple) |
| Q2 | Expansión tras NR7 | solo días cuya sesión PREVIA fue NR7 (rango RTH menor que las 6 anteriores); s = signo(c 09:59 − o 09:30) (10:00) | o 10:00 → c 15:59 | compresión → expansión con dirección |
| Q3 | Continuación de la tarde | s = signo(c 12:59 − o 09:30) (13:00) | o 13:00 → c 15:59 | tendencia de la mañana sigue por la tarde (operable 19-22h España) |
| Q4 | Cierre en extremo | pos = (c 15:59 − mín)/(máx − mín) del RTH previo; si pos > 0,8: s=+1; si < 0,2: s=−1 (cierre previo) | o 09:30 → c 15:59 | cierre fuerte = continuación al día siguiente |
| Q5 | Momentum de 10 días | s = signo(c 15:59 previa − c 15:59 de 10 sesiones antes) (cierre previo) | o 09:30 → c 15:59 | momentum diario de series temporales |
| Q6 | Reversión tras día extremo | ret = (c 15:59 − o 09:30)/o 09:30 del día previo; si \|ret\| > 1,5%: s = −signo(ret) (cierre previo) | o 09:30 → c 15:59 | reversión a corto plazo |
| Q7 | Día de la semana | y = retorno RTH (o 09:30 → c 15:59), largo; ANOVA entre los 5 días | — | estacionalidad semanal |

Q7 no es direccional con señal: se contrasta con ANOVA de una vía (p del F).

## Criterio para pasar a fase de estrategia (igual que lote 1)

1. p bilateral < 0,05/7 = 0,0071 en los tres años de diseño.
2. Mismo signo en 2021, 2023 y 2025.
3. Mismo signo en s=+1 y s=−1 (regla M; importa en Q4-Q6, donde la deriva
   alcista de NQ puede fabricar un efecto "de largos").
4. |media| > 0,87 pts.
5. Paseo aleatorio (6 semillas) ~0.

Q7 pasa solo si F con p < 0,0071 y el mejor/peor día tiene el mismo signo
relativo a la media en los tres años.
