# Informe: Días 23 (Manipulation legs), 25 (Conditions + Sponsorship) y 29 (Putting It All Together / backtest) vs. `analista_ruyra.md`

Método: subtítulos automáticos de YouTube en español (`es-orig`) con timestamps.
Transcripciones completas en `dia23/dia23.es-orig.srt`, `dia25/dia25.es-orig.srt`,
`dia29/dia29.es-orig.srt`. No se extrajeron fotogramas: los tres vídeos son charla +
pizarra dibujada a mano o TradingView en vivo narrado paso a paso; el texto por sí solo
ya describe con precisión cada ejemplo (coordenadas de precio exactas no visibles en
subtítulos, pero la lógica sí).

---

## DÍA 23 — Manipulation Legs (JO1xDEW2Lhg, 20:07)

**Hallazgo importante: el documento mezcla dos conceptos distintos bajo un solo
encabezado.** La sección 8 de `analista_ruyra.md` tiene un bloque llamado
**"Manipulation Legs / Judas Swing (Día 23)"** que describe específicamente el *Judas
Swing* (movimiento falso en la apertura o cambio de hora). Pero el vídeo del Día 23 real
trata de un concepto MÁS GENERAL y mecánico: qué es una Manipulation Leg (en cualquier
momento de la sesión, no solo en la apertura) y cómo usarla para encontrar la entrada.
**POSIBLE CONFLICTO / cosa a reconciliar (no lo resuelvo yo, decisión tuya):** o bien el
bloque actual describe Judas Swing y hace falta un bloque nuevo separado para
Manipulation Leg general, o bien hay que fusionar y dejar claro que Judas Swing es un
CASO PARTICULAR (en la apertura) de la Manipulation Leg general.

| Minuto | Qué dice Xavi | Estado |
|---|---|---|
| 2:09–3:00 | Manipulación = cuando las instituciones barren los stops de la gente que entró antes de tiempo en un key level, para entrar ellas a mejor precio | CONFIRMA §4 "Liquidez = stops pendientes" |
| 5:36–6:09 | **Definición mecánica exacta**: la Manipulation Leg es el rango del swing high al swing low **del movimiento que ha quitado el último bajo/alto** | NUEVO — no está escrito así de preciso en el documento |
| 3:12–3:40 | La manipulación es obligatoria, siempre, está atada al PO3 (alineación con el tiempo) | CONFIRMA §7 "True Manipulation cumplida... obligatoria siempre" |
| 6:09–9:19, 11:39–14:07, 15:16–19:00 | Metodología paso a paso: desde la temporalidad más alta hacia abajo (5m→3m→2m→1m→30s) dentro del rango de la ML, se busca si YA EXISTE un FVG formado en cada temporalidad (ojo con el timing: un gap de 3m no existe hasta que cierra la 3ª vela de 3m); se entra en el PRIMERO que exista, de la temporalidad más alta disponible | CONFIRMA el principio (ya en §7 punto 4 y §6 Día 25 punto 3), pero el procedimiento de escaneo top-down explícito es NUEVO como aclaración de método |
| 14:08–14:51 | Si la ML no llega a invertir y el precio genera OTRA manipulación (ML extendida/nueva), hay que actualizar y repetir el escaneo top-down desde la nueva ML, no forzar el plan viejo | NUEVO, matiz de procedimiento |
| 19:00–19:58 | **Matiz importante**: Xavi admite que ÉL MISMO, con su nivel actual de discreción, no siempre espera al IFVG de la temporalidad más alta — entra antes por convicción/draw on liquidity/PO3. Pero dice explícitamente que ESTA REGLA (esperar la más alta) la hace **obligatoria para los que empiezan** ("os lo hago obligatorio"), y que la discreción se gana con el tiempo | Aclaración de contexto, no conflicto: la regla del documento (§7 punto 4) es la versión disciplinada/de estudiante que Xavi mismo recomienda seguir mientras no se tenga su experiencia |
| 9:22–9:49 | Tiene que ser en key levels, combinado con el tiempo (PO3) y otras confluencias (equilibrium, SMT) para mayor probabilidad | CONFIRMA filosofía de confluencias de §6/§8 |

### Propuesta de texto nuevo (pendiente de tu OK)
```
### Manipulation Leg (definición general, Día 23)
Distinta del Judas Swing (caso concreto en la apertura, ver más abajo): es el rango de
precio del swing high al swing low del movimiento que acaba de barrer el último alto o
bajo en un key level, en CUALQUIER momento de la sesión.
Procedimiento: dentro de ese rango, escanear de la temporalidad más alta a la más baja
(ej. 5m→3m→2m→1m→30s). Entrar en el IFVG del PRIMER timeframe que ya tenga un FVG
formado (ojo con el timing: un FVG de 3m no existe hasta que cierra su 3ª vela).
Si la ML no invierte y se genera otra manipulación (ML extendida), repetir el escaneo
desde la nueva ML.
Nota de Xavi: esta regla (esperar siempre la temporalidad más alta) es la versión
obligatoria para quien empieza; con experiencia él mismo prioriza draw on liquidity/PO3
y entra antes.
```

---

## DÍA 25 — Conditions + Sponsorship (E3uwP18EYWI, 21:40)

**Confirma el "Método de 3 niveles" y el "Gap esponsoreado" de la sección 6 casi palabra
por palabra**, con ejemplos en vivo muy claros.

| Minuto | Qué dice Xavi | Estado |
|---|---|---|
| 0:46–2:47 | Afirmaciones = 1h/4h/diario, en pre-market, para daily bias/DOL/tendencia | CONFIRMA §6 punto 1 |
| 2:52–9:00 | Condiciones = gaps de 5m/15m que confirman sin adivinar: "si toca X y cierra por encima/abajo, el precio me dice qué quiere hacer" | CONFIRMA §6 punto 2, varios ejemplos en vivo |
| 4:02–4:20 | Las condiciones también sirven para la psicología: preparas mentalmente "si pasa X, haré Y" en vez de reaccionar nervioso a una vela grande | NUEVO (matiz de psicología, menor) |
| 10:57–11:02, 17:38–17:45 | Ejecuciones = IFVG de la temporalidad más alta dentro de la ML | CONFIRMA §6 punto 3 |
| 18:40–20:02 | Gap esponsoreado = primer FVG de CADA temporalidad tras tocar un key level de 1h/4h; coincide a menudo con equilibrium; el segundo gap de la misma temporalidad no está esponsorizado y suele ser peor | CONFIRMA §6 "Gap esponsoreado" casi literal, incluyendo que es "por temporalidad" (el documento ya lo decía bien) |
| 16:29–16:34 | **NUEVO — regla de desempate**: cuando se tocan a la vez un FVG bajista (con mecha) Y un FVG alcista en conflicto, Xavi dice: "yo normalmente le hago caso al FVG más reciente que se ha tocado", y además pone condiciones en ambos para desambiguar | NUEVO, no está en el documento |

### Propuesta de texto nuevo (pendiente de tu OK)
```
- Desempate entre FVGs contrarios simultáneos (Día 25): si se tocan a la vez un FVG a
  favor y uno en contra, por defecto se prioriza el más recientemente tocado, y además
  se pone una condición en la temporalidad menor para confirmar antes de decidir.
```

---

## DÍA 29 — Putting It All Together / dónde y cómo hacer backtesting (nxlZJ6abOYA, 25:48)

Aclara qué es "backtesting" en el contexto de `analista_ruyra.md`: es backtesting
**discrecional/visual** con una herramienta de replay (gráfico con velas que avanzan una
a una, NQ+ES en paralelo), NO el motor cuantitativo de este mismo repo sobre datos
históricos (`CLAUDE.md`, sección 2-7) — son dos cosas distintas con el mismo nombre.
Recomiendo añadir una frase aclaratoria en `analista_ruyra.md` para que no se confundan
(útil también para quien use este repo sin contexto).

| Minuto | Qué dice Xavi | Estado |
|---|---|---|
| 0:50–1:24 | Backtesting discrecional = práctica de repetición visual del método, no sustituye hacer muchas horas, hay que journalear cada repetición | CONFIRMA §10 "Journal" y la filosofía de practicar el checklist |
| 3:00–8:00, 12:30–14:20, 19:00–25:00 | Walkthroughs completos del método de 3 niveles en vivo, día a día: 4h/1h → condición 15m/5m → ejecución 1m/30s, varias veces, incluyendo trades ganadores y perdedores | CONFIRMA el método completo (§6) con ejemplos reales, nada nuevo mecánicamente |
| 7:08–7:48 | Al tocar una zona ambigua a mitad de camino del trade (FVG opuesto no resuelto), se mueve a breakeven rápido | CONFIRMA §10 "Break even solo en zona de conflicto... si barre un alto o bajo interno situado dentro de un FVG opuesto" |
| 9:54–9:58 | "Si no tenemos ese IFVG, no entramos" | CONFIRMA §5 "Toda entrada es por IFVG" |
| 17:31–18:22 | **Matiz (no conflicto duro, pero afecta a la rigidez de Equilibrium en §6)**: un trade con TODO alineado salvo que el precio no llegó a tocar exactamente el nivel de equilibrium funcionó igual de bien. Xavi: "¿Significa que sea un mal trade? No necesariamente... no vas a encontrar nunca trades que tengan todo." Dice que saber cuándo exigir equilibrium estrictamente y cuándo no "se aprende con horas de backtesting" | **POSIBLE CONFLICTO/matiz** — el documento (§6 Equilibrium) no deja explícito que el toque exacto de equilibrium sea opcional si el resto está alineado. Decisión tuya si matizarlo. |
| 19:00–21:00 repetido en 20:30 | Confirma que NO hace falta un daily bias fijo: "¿Tengo un bias para hoy? No... solo tengo puntos de reacción" | CONFIRMA §6 "El sesgo no se adivina" / filosofía de condiciones |
| 21:59–23:06 | Ejemplo de perder un trade con checklist perfecto, y en el SIGUIENTE giro (tras barrer a los que entraron antes) el mismo setup funciona | CONFIRMA §7 "Es el primer IFVG tras una caída/subida vertical... esperar el re-sweep" y el mensaje de Día 24 (perder con buen checklist es normal) |

### Propuesta de texto nuevo (pendiente de tu OK)
```
- Aclaración (Día 29): "backtesting" en este documento es la práctica discrecional con
  replay visual (no el motor cuantitativo de CLAUDE.md sobre datos históricos, que es
  un proceso distinto de este mismo repo).
- Equilibrium no siempre es un requisito estricto de toque exacto (Día 29): si el resto
  de confluencias (key level, condición, IFVG, SMT) están alineadas y la reacción es
  clara, un trade puede funcionar aunque el precio no llegue a tocar el 50% exacto.
  Saber cuándo exigirlo estrictamente y cuándo no se afina con horas de backtesting.
```

---

## Resumen para el fork padre

- **CONFIRMA** (sin tocar nada): la gran mayoría del contenido técnico de los 3 días
  coincide con `analista_ruyra.md`, con ejemplos en vivo que lo respaldan.
- **NUEVO** (añadir si Daniil da el OK): definición mecánica precisa de Manipulation Leg
  + procedimiento de escaneo top-down (Día 23); regla de desempate entre FVGs contrarios
  simultáneos (Día 25); aclaración de qué es "backtesting" aquí (Día 29).
- **POSIBLE CONFLICTO (destacar, no resuelvo)**: (1) el bloque "Manipulation Legs /
  Judas Swing (Día 23)" del documento en realidad describe Judas Swing, no la
  Manipulation Leg general que enseña este vídeo — hace falta reconciliar los dos
  conceptos. (2) Equilibrium: el documento no dice explícitamente que el toque exacto
  sea opcional cuando todo lo demás está alineado; el Día 29 sugiere que sí puede serlo.

No he tocado `analista_ruyra.md` ni `CLAUDE.md`, ni he hecho commit/push.
