# Plan maestro — de backtest a retiros cobrados

Escrito el 01/10/2026. Se revisa al cerrar cada fase, no antes.

## El punto de partida, sin adornos

- Ventaja auditada: **ninguna**. La mejor pista (Momento 09:40, stop 0,40%) da
  +0,05/+0,06R realista, validación p=0,049, ES no la confirma, y es frágil a la
  ejecución (U8: entrando en el peor precio de la vela → −0,072R).
- El dato más importante del repo no es de una estrategia, es del negocio:
  `resultados/2026-09-29_comparar_cuentas.txt` dice que en la 25K con 1 micro
  **la moneda al aire ya da EV +$42/cuenta**, y la candidata +$81.
  O sea: hoy, si el modelo es correcto, la mitad del dinero sale de las REGLAS
  de la firma y la otra mitad de la estrategia.
- Ese "+$42 con ventaja cero" es la cifra que más hay que desconfiar (regla de
  oro: si sale positivo a la primera, auditar antes de celebrar). Depende de
  reglas que están SIN VERIFICAR: mínimo/máximo de retiro, suelo del MLL tras
  solicitar, escalado de la fondeada.

Conclusión estratégica: hay dos palancas, no una.
1. **Palanca reglas**: elegir firma, tamaño y sizing donde el EV sea máximo.
   Barata, rápida, y no necesita encontrar ventaja.
2. **Palanca ventaja**: seguir buscando. Lenta, tasa base brutal, pero es la
   que convierte +$42 en +$200-300 por cuenta.

El plan trabaja las dos en paralelo y solo pone dinero cuando la palanca 1 está
verificada.

---

## FASE 0 — Auditar el negocio (semana 1, ~3 h tuyas)

Objetivo: saber si el +$42/+$81 por cuenta es real o un artefacto del simulador.

| Quién | Tarea | Entregable |
|---|---|---|
| Tú | Mandar a soporte de Lucid las preguntas pendientes (abajo) | Respuestas por escrito, captura |
| Tú | Captura de "Funded Rules" de 25K y 50K | Imagen al repo |
| Yo | Auditar `src/cuentas.py`: moneda al aire contra teoría de la ruina, qué pasa tras el 1er retiro, tope de 5 retiros, reset | Informe + tests |
| Yo | Rehacer `comparar_cuentas.py` con las reglas verificadas | Tabla EV final |
| Tú + yo | Meter 3-4 firmas más en el simulador (Topstep, Apex, Tradeify, Take Profit Trader…). Tú me pasas las reglas con captura, yo las modelo | Ranking de firmas por EV con ventaja 0 y +0,05R |

Preguntas a Lucid (copiar y pegar):
1. ¿Un breach intradía del MLL (sin cerrar el día) quema la cuenta, o solo cuenta el balance EOD?
2. Importe mínimo y máximo de cada retiro en Flex 25K y 50K.
3. Al solicitar un retiro, ¿a qué nivel queda el MLL exactamente?
4. ¿El tope de 10 micros en fondeada hasta +$1.000 aplica en Flex 25K? ¿Y en 50K cuál es?
5. ¿Está permitido operar siempre a la misma hora con la misma regla (estrategia mecánica / copy trading entre cuentas propias)?

**Puerta de salida de la Fase 0:**
- EV con ventaja 0, reglas verificadas, en la mejor firma/tamaño: anotado.
- Si es ≤ 0 en todas → el negocio depende 100% de encontrar ventaja; se salta
  la Fase 2 hasta que haya una aprobada.
- Si es > 0 → hay negocio de reglas, la Fase 2 se puede abrir con presupuesto pequeño.

---

## FASE 1 — Ensayo de ejecución sin dinero (semanas 1-6, 10 min/día)

Lo que se prueba aquí NO es la ventaja (con 40 operaciones la sd de la R media
es ±0,24R; no se puede distinguir +0,05 de 0). Se prueba que **tú ejecutas lo
mismo que el backtest**, que es justo lo que mató U8.

| Quién | Tarea |
|---|---|
| Tú | Momento 09:40 en demo/paper cada día de mercado. Orden a mercado en el segundo 0 de las 09:40 NY, stop 0,40%, objetivo 2× stop, cierre 16:00 NY |
| Tú | Apuntar cada operación con el skill de diario (precio de entrada real, hora exacta) |
| Yo | Cada viernes: cruzar tus entradas con el backtest del mismo día (CFD). Slippage medio, señal coincide sí/no, R real vs R de backtest |
| Tú | En paralelo y cuando puedas: las 60 operaciones a mano en FX Replay sobre 2022 (pendiente nº2 de CLAUDE.md) |

Horario en España: **15:40** normalmente. **Ojo: del 25/10 al 31/10/2026 es
14:40** (Europa cambia de hora una semana antes que EE. UU.). Lo mismo en marzo.

**Puerta de salida (pre-registrada ahora):**
- ≥ 30 operaciones registradas.
- Señal idéntica al backtest ≥ 95% de los días.
- Slippage medio en contra ≤ 2 pts (el backtest asume coste total 0,87).
- Si falla cualquiera → no se compra nada hasta arreglar la ejecución (automatizar
  la orden, p. ej.).

---

## FASE 2 — Primera tanda real, pequeña y con tope (mes 2-3)

Solo si la Fase 0 dio EV > 0 con reglas verificadas y la Fase 1 pasó.

- **Presupuesto cerrado: el precio de 5 evaluaciones** (~$250 en la 25K a $50,30,
  o lo que salga mejor en la Fase 0). Ese dinero se da por perdido el día que se
  gasta. No se repone si se pierde.
- Configuración: la que gane en la Fase 0 (hoy: 25K con 1 micro, o 50K con 2).
- Evaluación y fondeada con las reglas de la sección 8: evaluación a ratio bajo
  si el simulador lo confirma, fondeada a 1:2.
- Se escalonan: no se compran las 5 a la vez, se compran de 1 en 1 o de 2 en 2
  para que una racha mala no las queme todas el mismo día (las cuentas están
  correlacionadas al 100%: misma operación).

Lo que hay que tener presente ANTES de empezar:
- Con EV +$81/cuenta, **1 de cada 4 tandas de 10 pierde dinero**. Con 5 cuentas
  la probabilidad de no cobrar nada es alta. Eso NO es señal de nada.
- Por eso esta fase no decide si la estrategia funciona. Decide si el circuito
  completo (comprar → pasar → fondear → solicitar → cobrar) funciona y si las
  reglas eran las que creíamos.

**Puerta de salida:**
- Al menos un retiro solicitado y cobrado → el circuito funciona, pasamos a la Fase 3.
- Presupuesto agotado sin retiro → se para, se compara lo ocurrido con la
  distribución del simulador (¿estaba dentro de lo esperable?). Si estaba dentro,
  se decide con calma si otra tanda igual; si estaba fuera, el modelo está mal y
  se vuelve a la Fase 0.

---

## FASE 3 — Escalar con reglas fijas (mes 3-6)

- Reinvertir **solo beneficio cobrado**, nunca dinero nuevo: cada retiro paga N
  evaluaciones nuevas. El tamaño crece al ritmo de lo que se cobra.
- Diversificar entre 2 firmas si la Fase 0 dice que la segunda tiene EV parecido
  (baja la varianza, no sube la media — regla R).
- Revisión mensual: R real de las operaciones vs backtest, cobros vs simulador.
- **Criterio de parada pre-registrado**: si tras 20 evaluaciones el dinero
  cobrado queda por debajo del percentil 10 del simulador con ventaja 0, se para
  todo: o las reglas no son las que creemos, o la ejecución destruye la ventaja.

---

## Vía paralela, siempre activa — LA BÚSQUEDA (1-2 tardes/semana mías)

Es lo que convierte esto de "negocio de márgenes finos" a "negocio que aguanta".
Con +0,15R real el EV por cuenta se multiplica. Se busca donde el listón está
limpio (sección 11 de CLAUDE.md), en este orden:

| # | Sitio | Por qué | Coste |
|---|---|---|---|
| 1 | **OPEN_DRIVE: mecanismo, no variantes.** P4 dice que la meseta solo está en 2025. Medir la premisa en 2022/2024/2026 (sin tocar) con el protocolo de partición | Es la única forma tipo meseta que hay; o vive o se entierra en un día | 1 tarde |
| 2 | **Datos macro 08:30 / 10:00 NY.** Calendario real de IPC/NFP/ISM (hay que conseguirlo). Premisas: continuación del primer minuto, reversión a los 15 min, rango previo comprimido | Los dos minutos más volátiles del día, sin explotar | 1-2 tardes |
| 3 | **SMT NQ-ES.** Ya tenemos ES CFD 2021-2026 en `data/`. Divergencia en máximos/mínimos de la apertura | Mecanismo distinto a "barrida + confirmación": relativo entre índices | 1-2 tardes |
| 4 | **EUR/USD M1** (Dukascopy, gratis). Rejuzgar David Sánchez, 2T causal y LIT en su instrumento | Estrategias medidas en el instrumento equivocado | 2 tardes (descarga + validar loader) |
| 5 | **Killzone de Londres en NQ** (08:00-11:00 España) | Horario que puedes operar por la mañana | 1 tarde |

Reglas de la vía de búsqueda (no negociables):
- Cada lote: pre-registro con fecha, ≤ 10 premisas, premisa desnuda primero (regla Q).
- Diseño en 2021/23/25, validación en 2022/24/26, una sola vez.
- Contador de variantes actualizado en CLAUDE.md en cada commit.
- Lo que pase la validación entra a Fase 1 (ensayo de ejecución) por su cuenta,
  y luego se añade a las cuentas como segunda estrategia.

---

## Calendario resumido

| Semana | Tú (30-60 min/día) | Yo |
|---|---|---|
| 1 | Mandar preguntas a Lucid, capturas de reglas, empezar demo 15:40 | Auditar simulador de cuentas; lote OPEN_DRIVE (mecanismo) |
| 2 | Demo diario + diario; reglas de 2-3 firmas más | Firmas en el simulador; lote macro (si hay calendario) |
| 3-4 | Demo + FX Replay a ratos | Ranking de firmas con reglas verificadas; lote SMT NQ-ES |
| 5-6 | Demo (≥30 ops). Decisión Fase 2 | Cruce semanal demo vs backtest; descarga EUR/USD |
| 7-12 | Tanda de 5 cuentas, escalonada | Seguimiento vs simulador; lotes EUR/USD y Londres |
| 13+ | Fase 3 si hubo cobro | Revisión mensual + búsqueda |

## Qué cuenta como "algo tangible"

1. **Semana 1:** reglas reales verificadas y un EV por cuenta en el que confiar.
2. **Semana 6:** 30 operaciones ejecutadas igual que el backtest.
3. **Mes 2-3:** el primer retiro cobrado (aunque sean $500).
4. **Mes 6:** saber, con números, si esto es un negocio de márgenes (EV de reglas)
   o uno con ventaja propia. Las dos respuestas sirven para decidir.
