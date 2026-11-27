# Informe: Días 15 (Key Levels), 19 (Equilibrium) y 21 (Daily Bias + DOL) vs. `analista_ruyra.md`

Método: subtítulos automáticos de YouTube (`es-orig`) con timestamps, transcripciones
completas en `dia15/dia15.es-orig.srt`, `dia19/dia19.es-orig.srt`, `dia21/dia21.es-orig.srt`
(versión legible en `diaNN_texto.txt`). Fotogramas de confirmación en `dia19/frames/` y
`dia21/frames/`.

**Veredicto general: ningún conflicto en los tres días.** Confirman la sección 6 de
`analista_ruyra.md` ("Sesgo, DOL y key levels", incluyendo el bloque Equilibrium Día 19)
casi palabra por palabra. Hay 3 añadidos genuinamente nuevos, detallados al final.

---

## DÍA 15 — Key Levels (J7Dh-aj9-e0, ~21:27)

| Minuto | Qué dice Xavi | Dónde está en el documento |
|---|---|---|
| 1:32–2:02 | Solo usa dos cosas para encontrar key levels: FVGs y liquidez | §6, toda la sección se basa en esto |
| 2:02–2:18 | FVGs de 15m, 1h y 4h sirven como key level. **Un FVG de 5m, nunca** | §6, "Los de 5m nunca (como key level)" — cita casi literal |
| 2:18–2:49 | Los de 15m no son "peores", se usan cuando el movimiento está esponsoreado por un gap de 1h/4h; normalmente los de 15m se usan como condición, no como key level | §6, "Los de 15m solo si los apoya una reacción previa de 1h o 4h" + preview del "Gap esponsoreado" (Día 25) |
| 2:49–4:06 | Necesito que el FVG de 1h/4h tenga un alto o bajo DENTRO (liquidez). Explica el mecanismo: ese alto/bajo interno es un imán, el precio lo barre y continúa | §6, "Altos o bajos internos dentro... es el patrón preferido" (confirma + explica el porqué, que el documento no explicita) |
| 4:06–4:39 | Si el FVG de 1h da buena reacción, no hace falta bajar de temporalidad ni esperar horas | §6, "Al tocar un FVG de 1h no hace falta esperar horas... ya se ve la barrida" — cita casi literal |
| 6:45–8:11 | Si NO hay reacción y el precio consolida pegado al FVG, al abrir la siguiente vela horaria SÍ conviene esperar el re-sweep del bajo cercano | §6, "Si el precio consolida una hora entera pegado al extremo de un FVG de 1h sin despegar, al abrir la nueva vela horaria se exige un re-sweep" — match exacto |
| 9:18–11:43 | Segundo ejemplo: sin FVG de 1h/4h fresco cerca, un bajo interno dentro de un FVG de 1h ya marcado sigue siendo el mejor key level disponible | §6, "patrón preferido" — confirma |
| 13:16–15:20 | Entrar en cuanto aparece un IFVG SIN que se haya tocado aún el key level es "entrar antes de tiempo"; hay que esperar a que se limpie toda la liquidez en contra antes de la reacción real | §7, "El precio ha completado la Manipulation Leg y ha tocado el key level... Prohibido entrar antes" — confirma con ejemplo vívido |

**Nuevo (no conflictivo):** el mecanismo del "imán" (2:49–4:06) — por qué un alto/bajo
interno de un FVG es tan buen key level (liquidez = dinero esperando, el precio lo barre
y sigue) — explica el "por qué" de una regla que el documento ya tiene pero no justifica.

---

## DÍA 19 — Equilibrium (56ES-W1d0xw, ~15:56)

| Minuto | Qué dice Xavi | Dónde está en el documento |
|---|---|---|
| 2:05–3:28 | En una pierna con varios FVGs, se descarta el que esté en zona contraria (discount para ventas, premium para compras) y se prioriza el alineado con la zona correcta | §6 "Equilibrium (Día 19)", filtro de key levels — match casi exacto |
| 3:44–3:59 | "¿Hay alguna confirmación más aparte del inverse fair value?" — "Ahí entráis. El inverse fair value es la confirmación" | §7, el IFVG es la entrada — confirma |
| 4:17–4:50 | Explica el mecanismo institucional: venden más arriba (premium) para conseguir más puntos de caída, por eso buscan ese precio antes de girar | No está el "por qué" en el documento — añade contexto, no regla nueva |
| 7:14–8:33 | Ejemplo clave: el PRIMER FVG tocado está en zona incorrecta (discount buscando compra) — **no se opera**, aunque rebote. El precio barre a los que sí entraron ahí y da la reacción real en la zona correcta (premium) | §6, "Se descartan compras en FVGs por encima del 50% y ventas por debajo" — confirma con ejemplo real (ver `dia19/frames/t8_15_descarte_discount.png`) |
| 10:22–10:54 | Si el precio nunca toca la zona de equilibrium correcta, no se persigue: "no te conviene porque no es de alta probabilidad" — tu stop quedaría justo en una zona que se puede volver a barrer | §7 regla 1 "Prohibido entrar antes" / §10 filosofía de selectividad — confirma |
| 14:17–15:51 | Resume el método completo: marco key levels (FVG 1h/4h) → ¿busco reversal o continuación? → continuación = FVG dentro de equilibrium + confirmación IFVG + objetivo BSL/SSL | Coincide con la arquitectura completa de §6-§7, no añade regla nueva, confirma el diseño |

Sin conflictos. Confirma el documento con ejemplos reales muy claros.

---

## DÍA 21 — Daily Bias + DOL (MQyNBiw-QVo, ~32:17, el más largo)

| Minuto | Qué dice Xavi | Dónde está en el documento |
|---|---|---|
| 0:47–2:49 | Define Daily Bias (análisis 15 min antes de apertura), DOL (el alto/bajo literal que quiero que se barre, NO una meta en $) y Narrativa (combinar todo en una historia) | DOL ya está en §12 Glosario ("la liquidez hacia la que va el precio ese día") — confirma. **"Narrativa" no aparece como término en el documento** |
| 4:38–5:56 | Checklist de 4 pasos para el Daily Bias: (1) mirar HTF (D/4h/1h) sin marcar nada, (2) ¿qué hace el precio? sube o baja, (3) ¿qué invalidamos y qué respetamos?, (4) ¿dónde están los key levels? | **NUEVO** — el documento tiene el concepto (§6 "Método de 3 niveles", Nivel 1 "Afirmaciones") pero no este desglose paso a paso |
| 5:10–7:16 | Timing: se hace ~15-10 min antes de apertura (9:20 NY / 3:20 España) | **NUEVO** detalle operativo — el documento no fija esta ventana exacta |
| 6:45–7:31 | Ejemplo: invalidar FVGs bajistas + respetar FVGs alcistas = sesgo alcista | §6, "Respeta alcistas e invierte bajistas = sesgo alcista" — match casi literal |
| 13:13–13:29 | "La gran mayoría de veces, nunca operes en contra del high time frame" — en timeframes bajos las velas "parecen grandes pero no lo son" | §6, "No tomar un giro de apertura... contra el DOL de 4h" — confirma, buena frase para citar |
| 17:34–17:49 | Si el sesgo resulta equivocado a media sesión: "¿qué hago ese día? No opero. No pasa nada, me he equivocado" | §6, "Si el mercado invierte mi FVG clave, el sesgo ha cambiado (Día 20)" — confirma y añade la consecuencia práctica: no se persigue la reversión, se cierra el día |
| 23:22–23:37 | Si un día va claramente en contra del sesgo HTF, mejor saltárselo entero y esperar al día siguiente con buena estructura, en vez de intentar cazar el movimiento contrario | Relacionado con §10 "Xavi opera 1 de cada 6-7 días" — confirma con ejemplo concreto |
| 25:13–25:28 | Un día con velas de cierre fuerte y contrario al sesgo: no se opera | Relacionado, no idéntico, a §7 "mechas largas solapadas sin FVGs limpios" — matiz nuevo |
| 25:45–26:32 | Un retroceso fuerte en 1h contra el sesgo puede ser solo un REBALANCEO hacia el equilibrium del DIARIO, dentro de una tendencia mayor intacta — no necesariamente un cambio de sesgo | **NUEVO**, conecta Equilibrium (Día 19) con Daily Bias (Día 21); ver `dia21/frames/t26_15_rebalanceo_equilibrium.png` |

### Propuesta de texto nuevo para §6 (pendiente de tu OK, no lo he aplicado)

```
### Cómo determinar el Daily Bias (Día 21)
15-10 min antes de la apertura (9:20 NY), sin marcar nada todavía:
1. Mirar el high timeframe: Diario, 4h, 1h.
2. ¿Qué está haciendo el precio? Sube o baja, pregunta literal y simple.
3. ¿Qué estamos invalidando (FVGs contrarios) y qué estamos respetando (FVGs a favor)?
4. ¿Dónde están los key levels?
Si a media sesión el sesgo resulta equivocado: no se opera ese día, no se persigue la
reversión. Antes de dar el sesgo por cambiado, comprobar si el movimiento en contra es
solo un rebalanceo hacia el equilibrium del DIARIO (retroceso normal dentro de una
tendencia mayor intacta) y no un cambio de sesgo real.
```

### Pendiente

- No he tocado `analista_ruyra.md`. Reporto al hilo principal para que decida si aplica
  esto junto con el resto de informes de los otros bloques de días.
- No he hecho `git add`/`commit`/`push`.
