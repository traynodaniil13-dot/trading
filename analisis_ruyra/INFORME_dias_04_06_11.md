# Informe: Días 4, 6 y 11 (Velas y Liquidez) vs. `analista_ruyra.md` §4

Método: subtítulos automáticos de YouTube (`es-orig`) con timestamps. Sin fotogramas de
gráfico esta vez: los tres vídeos son pizarra/dibujo en vivo sobre TradingView, pero el
contenido verbal ya reconstruye los ejemplos con precisión suficiente; no hubo nada
ambiguo que requiriera confirmación visual.

**Veredicto global: sin conflictos.** Los tres días son casi una fuente directa del texto
de §4 (coincidencias casi literales en varios puntos). Hay 3 matices nuevos, ninguno
contradice nada existente.

---

## Día 4 — Candles (SuRgJd8ONIc, 21:15)

| Minuto | Qué dice Xavi | Estado |
|---|---|---|
| 3:08–4:06 | Vela alcista abre abajo/cierra arriba; bajista al revés | CONFIRMA |
| 2:11–2:36 | Mecha = wick, cuerpo = rectángulo | CONFIRMA |
| 11:20–11:30 | Sin mecha en un extremo = abrió/cerró en el máximo o mínimo | CONFIRMA |
| 7:44–8:35, 20:08–20:47 | "El precio es fractal"; mayor temporalidad = mayor importancia | CONFIRMA (match casi literal con §2) |
| 11:51–12:09, 12:44–13:00 | Precio en escalera (sube, retrocede, respira); si no, es acumulación | CONFIRMA (match casi literal con §2) |
| 15:23–16:05, 16:29–16:41 | Alto = alcista+bajista, se marca la mecha más alta de las dos (da igual de cuál vela) | CONFIRMA |
| 18:25–18:31 | Dos velas bajistas seguidas no forman ni alto ni bajo | CONFIRMA |
| 18:58–20:06 | "Altos más altos y bajos más altos" (alcista) / "bajos más bajos y altos más bajos" (bajista) | CONFIRMA (casi literal) |

Nada nuevo, nada en conflicto. Xavi mismo dice al final que liquidez es "el próximo vídeo" (no tocado aquí).

---

## Día 6 — Liquidity pt1 (7HOAf7vHMqU, 21:25)

| Minuto | Qué dice Xavi | Estado |
|---|---|---|
| 1:21–2:20 | Temporalidades altas = liquidez más importante (una vela de 1h "contiene" 60 de 1m) | CONFIRMA (match con §2) |
| 2:22–2:53 | Swing high/low = altos/bajos que "despuntan" en los extremos del rango | CONFIRMA |
| 3:02–5:55 | Mecanismo: instituciones necesitan liquidez (stops) para rellenar sus órdenes; el precio va a esos stops y luego gira | CONFIRMA (match con §4, "Las instituciones llevan el precio a esos stops...") |
| 9:18–12:31 | "Billetes": cada barrida deja un solo billete en ese lado y acumula varios en el contrario; a veces se barre dos veces antes del movimiento fuerte | CONFIRMA casi literal |
| 19:27–19:56 | Recap: marca BSL/SSL → espera a que se quite → opera hacia la contraria si todo alinea | CONFIRMA (framework general ya en el documento) |

**NUEVO (1):** 6:26–7:29 — Xavi aclara que un alto/bajo **no necesita ser exactamente el par "vela alcista + vela bajista" en la temporalidad que estás mirando**: si en una temporalidad no se ve un patrón limpio (ej. varias velas seguidas del mismo color), hay que bajar de temporalidad hasta encontrar el alto/bajo que SÍ forme el patrón limpio, y usar ese. Él dice textualmente que siempre busca "el bajo/alto de la temporalidad más baja" cuando el patrón no es limpio en la que está mirando. Esto no contradice el documento, lo matiza: la regla de "vela alcista seguida de bajista" sigue siendo correcta, pero falta esta instrucción práctica de "si no lo ves limpio aquí, baja de timeframe".

Propuesta de texto para §4 (al final del párrafo de "Alto"/"Bajo"):
```
Si en la temporalidad que miras el patrón alcista+bajista (o bajista+alcista) no
se ve limpio porque hay varias velas seguidas del mismo color, baja de
temporalidad hasta encontrar el par que sí lo forme limpio, y marca ese alto/bajo.
```

---

## Día 11 — Liquidity pt2 (OtYATAfCfRA, 18:22)

Este es el vídeo que enumera los 5 tipos de liquidez tal cual aparecen en §4, punto por punto, casi como fuente directa.

| Minuto | Qué dice Xavi | Estado |
|---|---|---|
| 1:13–3:11 | PDH/PDL: alto/bajo del día anterior, en diario, sirve de objetivo y zona de giro | CONFIRMA casi literal |
| 3:38–4:46 | EQH/EQL (misma altura exacta) y REH/REL (casi igual); si el segundo ya barrió al primero, no cuenta | CONFIRMA |
| 5:18–5:46, 6:02–6:14 | Indicador: "Equal highs and lows" de **JZS Tour**, configurado a **14 minutos** | CONFIRMA literal (coincide con §3 palabra por palabra) |
| 6:39–7:20 | "Nunca operar en contra de equal highs/lows" — el stop ahí no está protegido, es un caramelo para el mercado | CONFIRMA |
| 9:24–10:34 | Data High/Data Low: alto y bajo que deja una noticia | CONFIRMA, con matiz (ver NUEVO 2) |
| 12:17–14:53 | NDOG/NWOG: hueco en la apertura diaria/semanal, actúa de imán (como FVG), "nunca, nunca, nunca operar en contra" | CONFIRMA (triple énfasis de Xavi) |
| 14:53–17:33 | LRL: escalera lenta de muchos altos/bajos sin barrer, normal en 1-5m, se atraviesa de golpe al tocar un key level, nunca el stop detrás | CONFIRMA, con matiz (ver NUEVO 3) |

**NUEVO (2):** 9:40–10:34 — Xavi aclara que el Data High/Data Low **no es exclusivo de la noticia de las 8:30**: cualquier noticia programada (pone de ejemplo una de las 10:00) crea su propio alto/bajo que funciona igual. El documento actual (§4, punto 3) lo redacta como "la vela de 5m de las 8:30 NY cuando hay noticia", lo cual suena a que solo aplica a esa noticia concreta.

Propuesta de ajuste a §4, punto 3:
```
3. Data High / Data Low: máximo y mínimo que deja CUALQUIER noticia programada
   (no solo la de las 8:30 NY; también aplica, por ejemplo, a la de las 10:00).
   Patrón típico: barrida de uno en la apertura y giro hacia el otro. También
   sirven de objetivo.
```

**NUEVO (3):** 15:59–16:04 — Xavi dice que el LRL, aunque "normalmente" se da en 1-5m, **también puede aparecer en 1 hora** (raro) y en ese caso tiene **más importancia** que uno de 1-5m. El documento actual restringe el LRL a "1m–5m" sin más matiz.

Propuesta de ajuste a §4, punto 5:
```
5. LRL: escalera lenta de 4-6 altos o bajos sin barrer, normalmente en 1m–5m
   (puede aparecer, más raramente, en 1h: ahí pesa más que uno de 1-5m). Se
   atraviesa de golpe al tocar un key level. Nunca stop detrás. Se mira en LOS
   DOS índices: una LRL en el hermano anula la True Manipulation (punto 8).
```

---

## Resumen para quien solo lee esto

- **Sin conflictos** en los tres días.
- **3 matices nuevos**, todos ampliaciones menores de reglas ya correctas, no correcciones.
- No se tocó `analista_ruyra.md` ni se hizo ningún commit.
