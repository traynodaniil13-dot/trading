# Informe: Día 17 (SMTs y True Manipulation) y Día 24 (Perder es normal) vs. `analista_ruyra.md`

Método: subtítulos automáticos de YouTube en español (`es-orig`, generados por el propio
YouTube, no por mí) con timestamps, más fotogramas extraídos del vídeo en los momentos
de gráfico citados. Transcripciones completas en `dia17/dia17.es-orig.srt` y
`dia24/dia24.es-orig.srt`. Fotogramas en `dia17/frames/`.

---

## DÍA 17 — SMTs y True Manipulation (sTS-iWJvTf0, 21:57)

**Veredicto: no encuentro contradicciones.** El documento ya incorporó este vídeo el
12/11/2026 y el contenido coincide casi punto por punto. Lo que sigue son las
confirmaciones con minuto exacto (por si quieres contrastarlas tú mismo) y dos matices
que no están escritos explícitamente.

### Confirma lo que ya está en el documento

| Minuto | Qué dice Xavi | Dónde está en `analista_ruyra.md` |
|---|---|---|
| 0:58–1:46 | SMT = divergencia entre NQ/ES, correlacionados, se mide en key levels | §8 SMT, definición |
| 1:46–2:31 | Ejemplo SMT alcista: ambos crean SSL en la subida, uno la vuelve a barrer en el retroceso y el otro no | §8, "SMT alcista" |
| 2:31–2:59 | Si un índice toca la zona y reacciona, "es como si" el otro la hubiese tocado — **salvo True Manipulation** | §6 y §8 (implícito en la "trampa típica") |
| 3:05–3:19 | Da igual cuál de los dos índices es el que barre | §8, "Da igual cuál de los dos barre" (cita casi literal) |
| 3:19–3:39 | El SMT NO es obligatorio; si los dos tocan y barren a la vez, el trade es igual de bueno | §8, "El SMT NO es obligatorio" |
| 4:36–6:28 | Ejemplo real "de ayer" (10/11/2026): SMT bajista con gap de 15m, aclara que esa inversión concreta no es operable por ser de 15m, no de 1–5m | §5, "IFVG de entrada... solo de 30s a 5m" |
| 9:48–10:44 | Definición de True Manipulation: los dos índices en spot de distribución, cada uno con motivo propio | §8, primera frase de True Manipulation (cita casi literal) |
| 10:48–12:33 | Ejemplo MALO: SP500 toca el FVG de 4h pero deja 4 altos/bajos sin barrer (LRL) detrás — SMT inválido aunque el Nasdaq sí reaccione limpio | §8, condición 2 "Sin liquidez en contra" y NO HAY TRADE SI "el índice hermano tiene una LRL sin barrer" |
| 12:33–16:37 | Ejemplo BUENO: basta con que el índice hermano esté tocando como mínimo un FVG de 5m (o mayor) sin invertir, aunque no haya reaccionado todavía | §8, condición 1, umbral "FVG de 5m o mayor" (cita literal) |
| 16:40–18:13 | Ejemplo con gaps de 15m y 30m en ambos índices; menciona de pasada que el NWOG no se respetó ese día concreto sin saber muy bien por qué | No es una regla, es una anécdota suya — no toca nada del documento |
| 18:53–20:15 | Ejemplo INVENTADO: SP500 respeta su FVG de 15m y sube, pero el Nasdaq ya invirtió su único FVG de 5m — SMT anulado | §8, condición 3 "Sin inversión asimétrica" (match casi exacto) |
| 20:28–20:43 | Deberes: buscar SMTs con y sin True Manipulation, comprobar que las horas cuadren | §8, "Regla de la misma hora exacta" |
| 20:45–21:03 | Dice explícitamente que ya NO explica "cuándo se anula la True Manipulation con una doble SMT" porque no lo usa | §8, "Xavi ya NO usa el doble SMT que cancela la True Manipulation" (confirmación directa) |
| 21:36–21:46 | Dice explícitamente que no usa breakaway gaps | §8, "...ni opera breakaway gaps" (confirmación directa) |

### Matices que no están escritos tal cual (propuesta, no los toco sin que me digas)

1. **El mecanismo detrás del SMT (2:31–2:59 y 8:57–9:22):** Xavi explica por qué basta con
   que un solo índice toque la zona — es la correlación NQ/ES, "si el SP llega antes y
   reacciona, el Nasdaq sube por inercia". Ahora mismo el documento usa esto sin explicar
   el porqué. Podría añadirse una frase en §6 o §8.
2. **A mí me costó un año entender esto (9:53–10:28):** anécdota, sin valor de regla,
   la omito.

Capturas de referencia: `t1_46_smt_alcista1.png` (diagrama SMT alcista/bajista),
`t12_33_true_manip_buena.png` (diagrama "los dos índices en spot de distribución"),
`t19_10_condicion3_invertido.png` (gráfico real NQ/ES del ejemplo recreado).

---

## DÍA 24 — Perder es normal (9QkzkdspTko, 10:04)

**Este día no está en el documento.** Es un vídeo de psicología pura, sin gráficos (lo
comprobé, es cámara todo el rato). Propongo añadirlo a §10. Nada de lo que dice contradice
ninguna regla existente; son matices nuevos.

| Minuto | Qué dice Xavi | ¿Ya está en el documento? |
|---|---|---|
| 0:14–1:08 | No siempre se gana; perder haciendo trading no es gambling si cumples tu sistema | Implícito, no explícito |
| 1:48–2:01 | Él mismo cierra el ordenador tras perder en directo (delante de 1000 personas) | **Ya está**: "Si salta el stop: se cierra TradingView" — ahora con ejemplo real suyo |
| 2:52–3:23 | "Siempre vas a tener algo en tu stop loss, siempre. Si buscas un motivo para el cual el trade ha fallado, siempre lo vas a encontrar" | **Nuevo.** No estaba escrito así de explícito |
| 3:23–3:41 | Un 30% de trades falla sin que signifique nada malo, si cumplen todos los parámetros | Relacionado con la cifra del 70% en §2, pero él mismo dice "me lo invento" — confirma que el dato no es medido, como ya advierte el documento |
| 4:18–4:33 | Sobreanalizar cada trade lleva a ajustes de estrategia que se contradicen entre sí | **Nuevo**, relacionado con §10 "Confía en ti" pero más específico |
| 4:40–4:51 | Método de repaso: balanza de pros vs. contras del trade. "8 a favor y 2 en contra = buen trade, olvídate" | **Nuevo**, complementa las "tres preguntas" de §10 |
| 5:00–5:24 | En backtesting tampoco hay que sobreanalizar cada pérdida: mirar si cumple parámetros y pasar al siguiente día | **Nuevo** |
| 5:33–6:20 | En fondeo se hacen cosas que en backtesting no (alargar TP, journaling excesivo, quedarse mirando el mercado tras perder). Técnica: preguntarte "¿qué haría mi yo de backtest?" | **Nuevo**, técnica concreta de autocontrol en vivo |
| 7:05–8:05 | Narra cómo una buena racha en backtesting se rompe en vivo: sobreanalizar un stop → revenge trading → abandonar el sistema | Ya cubierto por "Revenge trading" y "Freno de emergencia" en §10, esto es solo la narrativa que lo conecta |
| 7:34–7:49 | Define "estás gambleando" como: salirte de la gestión de riesgo, del horario, meter más de un trade al día | Son reglas ya existentes (riesgo, horario, un trade al día) — **nuevo es la etiqueta**: romper cualquiera de ellas = estás apostando, no operando |
| 8:21–8:58 | A veces no vas a entender por qué perdiste, y está bien — "es lo bonito del deporte" | **Nuevo**, matiza las "tres preguntas" (a veces el "por qué" no tiene respuesta clara) |
| 8:58–9:29 | Anécdota sobre operar en directo con gente copiándole | No aplica a ti (tú no haces trading en streaming) |
| 9:33–9:55 | Adelanta próximos temas: condiciones, sponsorships, stop hunts, PO3s, AMDs | Aviso de contenido futuro, no regla |

### Propuesta de texto para añadir a §10 de `analista_ruyra.md` (pendiente de tu OK)

```
- Siempre vas a tener algo en contra en el stop (Día 24): si buscas un motivo para
  invalidar un trade que cumplía el checklist, siempre lo vas a encontrar. Eso no
  convierte un buen trade en malo.
- Repaso rápido post-trade (Día 24): balanza de a favor vs. en contra. Si gana
  claramente el "a favor", es un buen trade aunque haya perdido: no le des más vueltas.
- Backtesting sin sobreanálisis (Día 24): igual que en vivo, no mirar el detalle
  pequeño de por qué falló una operación de backtest. Cumple parámetros, siguiente día.
- "¿Qué haría mi yo de backtest?" (Día 24): check mental en vivo para detectar si
  estás alargando el TP, sobreanalizando o quedándote mirando el mercado tras un stop,
  cosas que en backtesting nunca harías.
- Definición de gambling (Día 24): romper la gestión de riesgo, el horario de sesión
  o el límite de un trade al día es apostar, aunque sigas "tu sistema" en lo demás.
- A veces no hay un "por qué" claro en una pérdida (Día 24), y está bien: no fuerces
  una explicación donde solo hay varianza estadística.
```

---

## Pendiente si quieres seguir

- No he tocado `analista_ruyra.md`: dime si quieres que aplique la propuesta de §10
  tal cual, la edites tú, o la dejemos solo como este informe.
- Quedan sin ver el resto de días que ya están resumidos en el Documento Maestro
  (1-23, 25-29) si en algún momento quieres una pasada de verificación igual que esta.
- Los vídeos y audios (`dia17/dia17.webm`, `dia17/dia17.mp3`, etc.) pesan ~100MB en
  total; no están en git (hay que añadir `analisis_ruyra/` al `.gitignore` si quieres
  evitar subirlos sin querer).
