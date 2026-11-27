# Informe: Días 5 (Tiempo), 10 (Noticias) y 28 (Sesiones) vs. `analista_ruyra.md`

Método idéntico al de Día 17/24: subtítulos automáticos `es-orig` de YouTube con timestamps.
Transcripciones completas en `dia05/dia05.es-orig.srt`, `dia10/dia10.es-orig.srt`,
`dia28/dia28.es-orig.srt`. No se descargó vídeo/frames: los tres son cámara + alguna
captura de TradingView de apoyo (indicador de sesiones en Día 28), sin ejemplos de
gráfico de estrategia que necesiten fotograma.

**Veredicto: sin contradicciones. Todo confirma el documento.** Lo más interesante es un
aviso sobre el propio título del Día 5.

---

## DÍA 5 — "Tiempo" (mBHtx-BfWWg, 13:31)

**Aviso:** el título es engañoso. El vídeo NO habla de horarios de sesión — "Tiempo" se
refiere a no perder el tiempo saltando de estrategia en estrategia ("strategy hopping").
Esto SÍ coincide con lo que el documento ya cita como "Día 5" en §10 ("No cambiar de
estrategia ni mezclar mentores"), así que el documento tiene la referencia correcta.

| Minuto | Qué dice Xavi | Dónde está en el documento |
|---|---|---|
| 1:39–1:52 | La "D" naranja junto al activo = datos con 10 min de retraso (sin datos de pago/cuenta de fondeo) | §3, cita casi literal |
| 2:17–5:16 | No intentes "aprender de más": cuenta su propia historia con TJR — cambió de estrategia, pasó 6 meses "gambleando" rompiendo reglas, perdió 9 meses por cambiar | §10 "No cambiar de estrategia ni mezclar mentores (Día 5)" — CONFIRMA |
| 5:19–5:40 | Define "strategy hopping" explícitamente con ese nombre | Mismo punto, ahora con el término exacto |
| 6:37–7:13 | No mezclar Order Flow + promediadas + ICT a la vez: los conceptos se contradicen entre sí (una estrategia dice compra, otra vende) | Relacionado con §10 "Confía en ti" y con la regla M de `CLAUDE.md` sobre no mezclar premisas — mismo principio aplicado a discrecional |
| 7:36–9:21 | Su estrategia es de ratio bajo (arriesga ~lo mismo que gana), trades rápidos, ~70% de acierto — por comodidad psicológica, no por ser "mejor" | §2 "Perfil... ratio entre 1:1 y 1:2... alrededor de un 70% de acierto (cifra de Xavi, no medida)" — CONFIRMA y además explica que el 70% es una elección subjetiva de diseño, no un dato medido objetivamente (refuerza la cautela que ya tiene el documento) |
| 9:24–10:09 | No sobrecompliques, no sobreanalices (incluido en backtesting) | Relacionado con lo añadido el 27/11 del Día 24 (sobreanálisis en backtesting) |
| 10:35–13:09 | Al principio vas a romper reglas, es normal; pero hazte responsable: ¿qué hice mal?, ¿por qué?, ¿cómo lo resuelvo? | §10 "tres preguntas" — CONFIRMA (su 3ª pregunta es "cómo lo resuelvo", el documento dice "qué haré mañana" — mismo espíritu, matiz de redacción) |

Nada nuevo que añadir aquí; todo es confirmación.

---

## DÍA 10 — Noticias (j4f8fV13GQM, 8:44)

| Minuto | Qué dice Xavi | Dónde está en el documento |
|---|---|---|
| 0:20–0:57 | Sesión NY 9:30–11:00, noticias de las 8:30 ocurren antes de abrir mercado | §2 horario — CONFIRMA |
| 2:11–2:19 | 4 cosas a vigilar: FOMC, CPI, NFP, lunes sin noticias | §9 — CONFIRMA, lista idéntica |
| 2:51–3:07 | FOMC = no opero nunca; NFP = voy con cuidado (solo si el setup es limpio); mismo cuidado en lunes sin noticias | §9 "FOMC... no se opera" y "NFP y lunes sin noticias: cuidado" — CONFIRMA casi literal |
| 2:31–2:35 | "CPI a mí me gusta" | §9 "CPI a las 8:30: operable, deja Data High y Data Low limpios" — CONFIRMA con cita directa |
| 3:16–4:25 | Forex Factory en hora de Nueva York (Eastern Time), desactivar todas las monedas menos USD, quitar carpetas amarillas (solo naranja/rojo) | §9 "Forex Factory en hora de Nueva York, solo USD, impacto naranja y rojo" — CONFIRMA, con los pasos exactos de configuración |
| 4:43–5:18 | Carpeta gris "Bank Holiday" = festivo en EE. UU., mercado cerrado, ni te presentes | §9 "FOMC o festivo bancario: no se opera" — CONFIRMA, con el detalle visual (carpeta gris) |
| 6:49–7:27 | Regla exacta: nunca operar entre 5 y 3 minutos antes de que salga una noticia (ejemplo: noticia a las 9:45, no entrar a las 9:42; noticia a las 10:00, no entrar a las 9:55-9:56) | §9 "Nunca abrir un trade 3-5 minutos antes de una noticia" — CONFIRMA literal, con ejemplo numérico |
| 7:27–7:40 | El resultado de una noticia es impredecible, por eso nunca se opera justo antes | Razón no explicitada en el documento — color útil, no cambia la regla |

Nada nuevo que añadir; todo confirma §9 punto por punto, con pasos de configuración y un
ejemplo numérico que el documento no tenía.

---

## DÍA 28 — Sesiones (CepE5r6rU00, 13:55)

| Minuto | Qué dice Xavi | Dónde está en el documento |
|---|---|---|
| 2:46–4:25 | Asia: 20:00–03:00 NY (2:00–9:00 España) | §2 "Prohibido operar Asia (20:00-03:00 NY)" — CONFIRMA exacto |
| 4:25–5:00 | Asia es la peor sesión: poca volatilidad, poco volumen, rango pequeño | Razón no explicitada — color útil |
| 5:00–5:53 | Londres: él la enseña como 03:00–05:30 NY (simplificación pedagógica suya; la sesión "real" dura más, pero esa franja es la de alta probabilidad) | §2 "Londres (03:00-05:30)" — CONFIRMA exacto, con el matiz de que es una simplificación deliberada suya, no el horario "oficial" |
| 7:34–8:42 | Nueva York: 9:30–11:00 NY / 3:30–5:00 España | §2 — CONFIRMA exacto |
| 8:42–9:04 | **Matiz importante:** Xavi SÍ opera Londres y Asia hoy en día, pero por requisitos de días mínimos de sus cuentas de fondeo y porque ya tiene capital/experiencia (2 años) — usa esas sesiones en cuentas que le importan menos | No contradice la prohibición del documento (que es para el nivel de Daniil), pero aclara que la regla no es "Xavi nunca opera eso", sino "los principiantes no deberían" |
| 9:04–9:47 | Advierte explícitamente contra copiar sus trades de Instagram en otras sesiones sin tener su capital/experiencia | Relevante para no confundirse si Daniil ve clips suyos operando fuera de NY |
| 9:51–10:13 | Sus primeros 10 retiros los sacó operando solo Nueva York | Refuerza la elección de "sesión única (Día 28)" del documento |
| 10:13–10:23 | Por qué NY: mayor volatilidad/volumen/desplazamiento de las tres sesiones, y el mejor % de acierto en su propio backtesting | Razón explícita no estaba en el documento — color útil |
| 11:25–13:31 | Premarket (18:00–20:00 NY) = preapertura de Asia, "lo peor que puedes hacer"; NY Lunch (desde ~12:00 NY) = peor hora, baja mucho el volumen; NY PM = "after" de NY AM | §2 "premarket de Asia (18:00-20:00), ... NY lunch (12:00-13:30) y NY PM" — CONFIRMA exacto, con la razón (caída de volumen) para cada uno |

### Propuesta de texto nuevo para §2 (pendiente de tu OK, solo contexto, no cambia ninguna regla)

```
- Por qué solo NY AM (Día 28): de las tres sesiones es la de mayor volatilidad, más
  órdenes y mayor desplazamiento, y la que mejor % de acierto dio en el backtesting de
  Xavi. Sus primeros 10 retiros los sacó operando solo esta sesión.
- Xavi sí opera Londres/Asia hoy (Día 28), pero por requisitos de días mínimos de sus
  cuentas de fondeo y con 2 años de experiencia/capital — no es una contradicción de la
  prohibición de este documento, que aplica al nivel actual de Daniil. No copiar sus
  clips de Instagram operando fuera de NY sin ese contexto.
```

---

## Conclusión del bloque 5/10/28

Cero conflictos, cero reglas nuevas que cambien el checklist. Solo contexto/razones que
no estaban explicitadas y una confirmación de que la referencia "(Día 5)" que ya tenía el
documento en §10 es correcta pese a que el título del vídeo despiste.
