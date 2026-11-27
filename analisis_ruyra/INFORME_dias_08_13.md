# Informe: Día 8 (FVGs) y Día 13 (IFVG) vs. `analista_ruyra.md` §5

Método: subtítulos automáticos de YouTube (`es-orig`) con timestamps. Transcripciones
completas en `dia08/dia08.es-orig.srt` y `dia13/dia13.es-orig.srt`. No hizo falta sacar
fotogramas: ambos vídeos son explicación con dibujo/pizarra sobre el propio gráfico de
TradingView, sin ejemplos que requieran captura aparte de lo que ya dice el texto.

**Veredicto: confirma la sección 5 casi palabra por palabra. Cero conflictos.**

## Confirma lo que ya está escrito

| Minuto (día) | Qué dice Xavi | Dónde está en `analista_ruyra.md` |
|---|---|---|
| 0:34–1:13 (D8) | FVG = secuencia de 3 velas, da igual el color/orden, el tamaño no importa | §5, primera frase (match literal: "el tamaño no importa") |
| 1:29–1:40 (D8) | Construcción: punto más alto de la vela 1, punto más bajo de la vela 3 | §5 "Alcista: de la mecha alta de la vela 1 a la mecha baja de la 3" |
| 7:27–7:47 (D8) | Construcción bajista: parte baja de la vela 1, parte alta de la vela 3 | §5 "Bajista: de la mecha baja de la 1 a la mecha alta de la 3" |
| 3:54–4:02 y 19:31–19:52 (D8) | Si no hay hueco entre las mechas, no hay FVG (dos ejemplos, uno de ellos un falso positivo visual donde una vela "pasa por debajo de la otra") | §5 "Si las mechas se tocan, no hay FVG" |
| 8:56–12:04 (D8) | Respetado = el precio lo visita y el CUERPO nunca cierra por debajo, aunque la mecha lo atraviese entero | §5 "Respetado" (match casi verbatim) |
| 12:22–12:43 (D8) | Invalidado = el cuerpo cierra al otro lado | §5 "Invalidado" |
| 13:43–15:36 (D8) y 6:38–8:13 (D13) | Un FVG solo se valida/invalida en SU temporalidad — ejemplo real: 1m cierra por debajo pero la vela de 5m no, por tanto sigue vivo en 5m | §5 "Un FVG solo se valida o invalida en la temporalidad en la que se creó" — confirmado en los DOS vídeos por separado |
| 16:37–17:20 (D8) | IFVG = FVG invertido = esperas que el precio gire | §5 "Invalidado... pasa a ser IFVG" |
| 2:56–3:40 (D13) | "Siempre, siempre, siempre" necesito un IFVG para entrar | §5 "Toda entrada es por IFVG" |
| 0:28–0:36 (D13) | Explícitamente decide NO explicar CSD/CISD ese día: "de cada 100 trades igual lo uso una vez" | §8 "Se usa poco" — **ahora con cifra exacta: ~1/100** |
| 10:45–11:20 (D13) | Entradas solo de IFVG entre 30s y 5 minutos, nunca de 15 minutos | §5 regla 1 "Solo de 30s... Nunca de 15m" |
| 17:56–18:53 (D13) | Un IFVG no puede tardar más de 3-4 velas en darse, buscando "una vela fuerte" | §5 regla 3 "Creado e invertido en 3-4 velas... con una vela decidida" (match casi literal) |
| 15:37–15:47 (D13, ejemplo real) | No interesa tener un equal high/low en el stop loss | §4 y §10 "nunca detrás de EQH/EQL" |

## Sobre la corrección sensible del "mareo pre-market" (§5, regla 3)

**Ninguno de los dos vídeos la menciona, ni a favor ni en contra.** Xavi no habla de
pre-market en absoluto en Día 8 ni Día 13 — es normal, en el bootcamp los key levels y
el horario de sesión se explican en otros días (15, 17, 21...). Esta corrección de Daniil
sigue sin confirmar ni contradecir desde la fuente original; habría que mirarla en el
vídeo de Key Levels (Día 15) o en el de Daily Bias (Día 21), que caen en otro bloque.

## Novedades (no están escritas, no conflictivas)

1. **FVGs actúan como imán** que hace que el precio continúe en su dirección (D8,
   0:49–1:17) — mecanismo que hoy está implícito en §4 pero no dicho así de explícito.
2. **Tiempo típico en el trade: 1 a 10 minutos, raro pasar de 20-30** (D13, 11:36–11:52).
   Matiza el §2 actual ("trades rápidos, de 1 a 15 minutos") — no es conflicto, es un
   poco más conservador que lo escrito.
3. Aviso visual: a veces una forma "parece" FVG pero las velas se solapan y no hay
   hueco real — vale la pena como recordatorio de comprobación (D8, 19:31–19:52).

Ninguna de las tres amerita tocar `analista_ruyra.md` por sí sola; la única que valdría
la pena pegar tal cual es la cifra del CISD (~1/100 trades) en §8.
