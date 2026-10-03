# Operativa de fondeo — MNQ/NQ — Lucid Flex 25K

Repo de backtesting. Lee este archivo entero antes de escribir código.

Daniil, 19 años. Objetivo: encontrar algo con ventaja real y suficiente para que
el negocio de pasar cuentas de fondeo y cobrar retiros sea rentable. No busca la
estrategia perfecta, busca una que aguante.

**Estado a 27/09/2026: 30.127 variantes probadas (incluye 28.512 de la rejilla masiva). Con ventaja auditada y viva: CERO.**

Eso no es una razón para parar, y no lo trates como tal. El plan es seguir
buscando hasta encontrar algo. Lo que sí significa es que la tasa base es brutal:
la probabilidad a priori de que la siguiente idea funcione es baja, así que el
rigor de este repo no está para frenar la búsqueda, está para que la búsqueda
sirva de algo. Sin los controles, 563 pruebas producen media docena de falsos
positivos convincentes y cero dinero — ya pasó tres veces.

**Tu trabajo aquí es ayudarle a buscar, no a resignarse.** Propón ideas, tráele
familias que no haya tocado, discútele las que traiga él. Lo único que no se
negocia es cómo se mide, y donde hay que ser inflexible es en la sección 6:
declarar variantes antes de probarlas y pagar el precio de haber buscado
(regla I). Buscar mucho está bien; buscar mucho y no descontarlo es lo que
fabrica ilusiones.

---

## 1. Cómo trabajar

- Directo. Si un número no aguanta, dilo sin rodeos.
- Español casual. Salidas listas para copiar y pegar.
- Solo tiene 30-60 min/día delante del gráfico. Sirven mañana o tarde.
- **Separa siempre dos cosas distintas al reportar:**
  - **Ventaja** = R por operación. Decide si se gana dinero.
  - **Tasa de pase** = cuántas de 10 cuentas pasas. Depende casi solo del winrate.
  - Una estrategia sin ventaja puede pasar cuentas. Lo que no puede es cobrarlas.
    Nunca des un "pasa X de 10" sin el valor esperado en dólares al lado.
- No recalcules datos desde cero: pídeselos.

---

## 2. Datos

- `data/nq_1m.csv` — NQ 1 minuto, Kaggle `tgtanalytics/nq-futures-1min-bar-2022-2025`.
  Dic-2022 a 11/12/2025. 1.048.575 filas (el límite de Excel: viene truncado).
- **Los timestamps etiquetan el FIN de la vela, no el inicio. Réstale un minuto
  al índice al cargar.** Es el bug nº10. El loader tiene que hacerlo solo.
- `data/nq_cfd_YYYY.csv.gz` — CFD USATECHIDXUSD de Dukascopy (índice Nasdaq 100
  de contado), bid y ask, ms UTC, etiqueta el INICIO de la vela. `loader.cargar_cfd()`
  usa el medio y pasa a hora NY. Hay 2025 y 2026 (hasta 23/09). **Validado contra
  NQ en 2025**: corr. retornos 1 min 0,984; RTP 150/151 días misma dirección y
  corr. de R por op 0,994; Momento 224/228. Sirve como sustituto del NQ.
  Diferencias: base de ~700 pts, cierra a las 16:15, apertura 09:30 más brusca.
- También 2021 (desde dic-2020) y 2022 del mismo CFD. **2021-2022 ya se usaron
  como reserva el 27/09 (RTP contra sesgo y Momento): ya no son ciegos para
  esas dos.** Para ideas NUEVAS siguen limpios. 2019-2020 sin bajar.
- Falta ES 1 minuto (para SMT NQ-ES) y EUR/USD M1 (varias estrategias están
  medidas en el instrumento equivocado: sus autores operan Forex).
- **Coste obligatorio: 0,87 puntos por operación** ($0,74 comisión ida y vuelta
  por micro + 2 ticks). Sin esto los resultados son ficticios.

### Control obligatorio al cargar CUALQUIER fichero de precios

Dos chequeos, y hay que hacer los dos:

1. **El minuto más volátil del día tiene que ser el 09:30 clavado** (por
   MEDIANA del rango: con la media, en 2023 y 2024 gana el 08:30 por los días de
   IPC, también en el futuro NQ, y el chequeo daba falsa alarma). En ES el
   15:50 (desequilibrio MOC) puede ganarle al 09:30 y es real: el chequeo exige
   09:30 en el top-3 y por encima del 09:29 y del 09:31. Si sale
   09:31, los timestamps son fin de vela: resta un minuto. En este CSV, sin
   corregir sale 09:31 (28,12 pts), 08:31 (27,51) y 10:01 (26,79) — los tres
   desplazados un minuto, y los otros dos son los datos macro de 08:30 y 10:00.
2. **Histograma por HORA** solo para localizar la parada del CME (17:00-18:00 NY)
   y fijar el huso. El chequeo por hora NO sirve para el punto 1: da pico en la
   hora 10 y es correcto.
3. Timestamps duplicados: cero.

---

## 3. Reglas no negociables del motor

1. **Todo causal.** Cero decisiones que usen una vela sin cerrar. Antes de
   escribir una línea, declara para cada dato: ¿en qué instante exacto se conoce?
   - Una vela H1/H4/diaria solo se conoce cuando CIERRA.
   - Un pivote confirmado con K velas de retardo existe K velas después.
   - Un FVG de 3 velas nace al cerrar la tercera.
2. **Vela de entrada: solo se evalúa el recorrido ADVERSO.** El objetivo solo
   puede tocarse desde la vela SIGUIENTE. Nunca en la misma.
3. **Órdenes pendientes: el relleno es al CIERRE de la vela que toca el nivel, y
   esa vela no se evalúa para nada.** Es el bug nº9 y sobrevive a la corrección
   clásica del nº2. Es además lo realista con slippage.
4. **La R se mide desde el relleno REAL, no desde el nivel pedido.** El desvío
   son +0,55 pts de media, siempre en contra (2,2% de una R mediana de 24,7).
5. **Todo nivel congelado en el instante A y usado en el instante B se revalida
   en B.** Bug nº11.
6. **Guarda por operación `rmax`, `toco_sl` y `riesgo_pts`.** Con eso cualquier
   ratio se evalúa al instante (`gana = rmax >= ratio`). No reejecutes el motor
   por cada ratio.
7. **Deduplica por barra de entrada SIEMPRE** antes de cualquier contraste.
   Sistemáticamente aparecen duplicados: 2T un 8%, Aleix un 9,6%.

---

## 4. Batería de controles. Ninguna cifra positiva sale de aquí sin pasarla.

**0. Calibración contra paseo aleatorio — el más duro de todos.**
Corre el motor entero sobre series de paseo aleatorio generadas a propósito,
antes de mirar un solo dato real. Ahí la verdad se conoce: la R neta tiene que
salir igual al coste, y normal e invertida tienen que parecerse.
Es mejor que el placebo porque el placebo compara la estrategia contra otra
versión de sí misma sobre los MISMOS datos, así que un sesgo del motor está en
los dos lados y se cancela. El paseo aleatorio no tiene dónde esconderlo.
Cazó los bugs nº9 y nº11, que el placebo no veía.
- 24 semillas para auditar, 6 para reportar el nulo al lado del resultado. Con 8
  el ruido todavía da falsos positivos de 2,7σ.
- Genera con la MISMA rejilla temporal que el dato real (sesiones, killzones,
  buckets idénticos) y el máximo/mínimo de cada minuto de un puente browniano de
  12 subpasos, para que el rango intravela sea realista.
- Comprueba el generador antes de usarlo: desde puntos al azar, la carrera a
  barreras simétricas tiene que dar 50/50 (medido 50,03/49,97 con 20.000 casos).
- **La ventaja real se mide como EXCESO SOBRE ESE NULO, no sobre cero.** Un motor
  honesto puede perder más que el coste sobre datos aleatorios, porque la
  convención pesimista dentro de la vela cuesta dinero.

**1. Placebo.** Aleatoriza la DIRECCIÓN, no el instante (ver regla B abajo).
Mínimo 15 reps, 200 si es un filtro de sesgo. Menos de 3 desviaciones no es una
ventaja.

**2. Invertida.** Misma entrada, misma distancia de stop, dirección contraria.
Si da positivo hay un bug direccional. Si da cero, el motor está limpio y la
estrategia no contiene información.
- Mira la SUMA normal+invertida: debería rondar dos veces la fricción. Suma
  simétrica con resta grande = sesgo direccional fabricado (bug nº9). Suma muy
  negativa = motor pesimista de más, calíbralo con el control 0.

**3. Consistencia.** % de meses positivos, R total quitando los 3 mejores meses,
racha máxima de perdedoras, drawdown máximo en R.

**4. Reserva ciega** en datos nunca usados para diseñar. Y ojo: **el fuera de
muestra NO detecta look-ahead.** Si el bug está en el código, está en todos los
años. 2T pasó 2025 con un 74,4% porque el bug también estaba en 2025.

**5. Pre-registro.** Declara cuántas variantes vas a probar ANTES de probarlas y
corrige por ese número. Escribe el pre-registro en `preregistros/` con fecha
antes de ejecutar. Bonferroni: `p_umbral = 0,05 / nº_variantes`.

---

## 5. Los 12 bugs ya encontrados. Repásalos como checklist.

1. Temporalidad mayor leída de la vela EN CURSO. Fabrica +0,15R y 5 puntos de
   winrate sobre población de expectancy cero.
2. Ganancia fantasma en la vela de entrada. Costaba 4,3 puntos de winrate en 2T.
   Corregirlo NO basta: ver el nº9.
3. EMA y pivotes de marco superior leídos de velas sin cerrar.
4. Timestamp del resample. Con `label="left"` el timestamp es el INICIO de la
   vela. Fabricó +0,545R en CRT H4 y +0,481R en otro motor.
   **Mejor que corregirlo: no uses nunca el label.** Agrupa las barras M1 y toma
   como instante de conocimiento la barra M1 SIGUIENTE a la última de la vela.
5. Arranque del seguimiento una barra más tarde. Regala un minuto sin riesgo.
   Valía +0,072R en NR_BREAK. Ha reincidido.
6. La hora del día no ordena la sesión. La sesión de futuros empieza a las 18:00,
   así que "primera barra con hora >= 09:30" devuelve las 18:01. Cualquier
   "primera barra de X" necesita las DOS cotas. Afectó a 4 de 6 familias.
7. **Elegir la candidata siguiente porque la anterior "no se llena nunca".**
   Saber que una orden no se rellenará en todo el día es futuro. Fabricó TODA la
   ventaja de 2T (95% de objetivos a 1:2). Los placebos no lo detectan.
   Reincidió en otra forma: **tomar como instante de observación el EXTREMO de
   una ventana** en vez de la primera barra que cumple la condición. Desde el
   mínimo de una ventana el precio no puede bajar más dentro de ella, por
   definición. Daba un 96% de reversión.
8. Índice negativo en numpy. `C[:, k-30]` con k=29 da `C[:, -1]`: el cierre del
   MISMO día. No da error. Escribe todas las ventanas `k-N` con un assert de
   `k-N >= 0`.
9. **El cierre de la vela de entrada como punto de partida.** Si la orden se
   rellena exactamente en el nivel y empiezas a medir en la siguiente, la
   operación arranca desde el cierre, que ya se movió a favor, mientras el stop
   se sigue midiendo desde el nivel. Medido sobre paseo aleatorio puro: +0,087R
   a 6,4σ, las 8 semillas del mismo signo, invertida perfectamente antisimétrica.
   El placebo no lo ve.
10. Timestamps de fin de vela en el fichero de origen. Ver sección 2.
11. **Stop congelado con disparo diferido.** El único de la lista que DESTRUYE
    ventaja en vez de fabricarla, y por eso es el más fácil de no buscar. Si el
    stop se ancla a un extremo en A y la entrada llega en B (hasta 120 min
    después), el precio puede haberse comido el stop por el camino. Sobre paseo
    aleatorio: 63,1% de stops y asimetría emparejada −0,143R con t=−4,27.
12. **Medir desde el propio extremo.** No es look-ahead, es un contraste sin
    nulo: si la referencia ES el SL, está a distancia cero y gana casi siempre.
    Cualquier carrera a barreras se monta con barreras SIMÉTRICAS desde una
    referencia que no sea ninguna de las dos.

**Regla de oro: si un backtest da ventaja grande y robusta a la primera, audita
el código ANTES de celebrarlo.** Solo se auditaban los resultados malos, y los
bugs casi siempre hacen ganar. Los cinco últimos aparecieron en motores que ya
habían pasado la batería entera anterior. La tasa a la que aparecen bugs nuevos
NO está bajando.

---

## 6. Reglas de método

**A.** La convención de la vela de entrada cambia el resultado. Si el caso es
ambiguo, reporta las dos cotas.

**B.** El placebo de entrada aleatoria NO sirve de nulo si la ventaja es
direccional: hereda la dirección y se lleva la ventaja puesta. **Aleatoriza la
DIRECCIÓN, no el instante.** Para una familia de configuraciones, aplica el MISMO
sorteo a todas a la vez (conserva la correlación) y compara el MÁXIMO real contra
la distribución del MÁXIMO del nulo. Es el control que más mata: con 16 celdas y
muestras de 100-900 ops, el máximo del nulo se planta en +0,19R de media.
Y menos celdas NO baja el listón: al pasar de 16 a 8 el máximo del nulo SUBIÓ
(+0,190 → +0,197), porque las muestras eran la mitad de grandes. Lo que manda no
es el número de celdas, es la varianza de cada celda.

**C.** Si ganan las dos direcciones, no es ventaja direccional.
`común = (normal + invertida)/2` · `direccional = (normal − invertida)/2`

**D.** "El ratio bajo mata" es un efecto del COSTE, no una ley. Muere cuando el
coste pesa mucho sobre la R.

**E.** Un winrate DECENAS de puntos por debajo del azar en todos los ratios es un
motor roto. 1-5 puntos por debajo es solo una estrategia sin ventaja pagando
costes.

**F.** Una variante que brilla pero no cumple la descripción del autor es
muestreo múltiple, no un hallazgo.

**H.** Un fuera de muestra CONTIGUO no prueba nada si hay régimen. Elegir con
2023-24 y validar en 2025 daba 10 de 10 positivas; elegir con 2024 y validar en
2023 daba 0 de 10. **Valida cruzando a un periodo no contiguo y EN LOS DOS
SENTIDOS.** Si solo funciona hacia delante, es régimen, no ventaja.

**I.** Buscar tiene un precio y hay que pagarlo. Con 760 ops a 1:2 y cero
ventaja, la sd de la R media es 0,051R. Probando N variantes, la mejor da por
puro azar: 10 → +0,069R · 100 → +0,120R · 300 → +0,139R · 1.000 → +0,159R ·
5.000 → +0,182R. El listón no es "¿la mejor es positiva?" sino "¿supera al
máximo del nulo de la MISMA familia?".

**J.** Cuando un modelo de cuentas no cuadra, calíbralo contra la moneda al aire
(expectancy cero). No depende de la estrategia. Así se encontró el MLL estático.

**L.** **La frecuencia no es dirección.** Que el precio vuelva mucho a un nivel
(el 78% en la reentrada de RTP) no dice nada de hacia dónde sigue. Una frecuencia
alta es justo lo que hace que una idea parezca buena mirando el gráfico. Separa
siempre: cada cuánto se da el setup, y qué rinde.

**M.** **Nunca agregues un estadístico direccional sobre largos y cortos a la
vez.** "Con qué frecuencia toca +riesgo antes que −riesgo" promediado da 50/50
POR CONSTRUCCIÓN, porque +riesgo es el stop de uno y el objetivo del otro. Salió
49,3/50,6 y casi cerró una auditoría; separado por dirección era 36,9/63,1. Un
contraste que no puede fallar no es un control.
Corolario: cuando un contraste y el motor discrepan, cruza operación a operación
con tabla de confusión ANTES de tocar el motor.

**N.** **Entrar en extremos locales tiene inclinación propia.** Sobre paseo
aleatorio, desde un mínimo local de 60 min la carrera a barreras simétricas da
47,95/52,05, o sea leve CONTINUACIÓN. Descuéntalo antes de llamarlo ventaja.
Confirmado en dato real: tras una barrida de Londres, ±20/40/60 pts desde el
cierre del primer minuto que rompe da 45,9-51,2% de reversión (p de 0,16 a 0,92,
n=316-379 por celda). El dato real se comporta como el paseo aleatorio.

**O.** Un exceso sobre un nulo se divide por LOS DOS errores, no solo por el del
nulo. `z = exceso / raíz(ee_real² + ee_nulo²)`. Dividiendo solo por el del nulo
salían +5,64σ donde había +2,19σ.

**P.** **Un filtro real es monótono; un pico es ruido.** Barre el umbral entero y
mira la FORMA. Si el efecto crece con la exigencia, es un mecanismo. Si hay un
máximo que se cae a los dos lados, o si el signo cambia entre dos submuestras del
mismo dato, es ruido, por bueno que sea el p-valor en el óptimo. Pondera por
POTENCIA: la submuestra grande manda. Y contrasta el filtro contra un SUBCONJUNTO
AL AZAR DEL MISMO TAMAÑO de la misma población.

**Q.** **Mide la premisa desnuda ANTES de programar la estrategia.** Aísla la
afirmación de una frase en la que se apoya todo ("tras barrer X, el precio
revierte") y mídela sola: barreras simétricas, referencia causal, separada por
dirección. Cuesta 20 líneas y cierra familias enteras. Si la premisa está en el
nulo, ninguna mecánica de entrada la rescata y todas las variantes que pruebes
después son cronometraje del mismo cero. Esto había que haberlo hecho con Judas,
RTP y LIT antes de gastar seis baterías en la misma familia.

**R.** **Juntar dos estrategias sin ventaja no crea ventaja.**
- Como CARTERA: la esperanza de una suma es la suma de las esperanzas. Dos ceros
  dan cero. Diversificar baja la VARIANZA, nunca sube la MEDIA.
- Como FUSIÓN (una filtra a la otra): sí puede cambiar la esperanza, porque la
  selección condicional es un objeto nuevo. Pero es una variante más, declarada y
  corregida. Y si las dos se apoyan en la MISMA premisa, no añade información:
  solo cambia el cronometraje. Comprueba primero si comparten premisa (regla Q).

---

## 7. Estado de las estrategias

### Con ventaja auditada: NINGUNA.

### En vigilancia (ni descartadas ni aprobadas)

**OPEN_DRIVE · 1:2 → +0,167R · p=0,026 · 93 ops/año**
Primera vela M5 de RTH con cuerpo >60% del rango, entrada al cierre en su
dirección, stop = rango de la vela.
A favor: es una MESETA, no un pico. Funciona en todo el rango de umbral de cuerpo
para velas de 2 a 5 minutos, y no para 1, 10 ni 15. La familia entera a p=0,015.
En contra: no pasa el listón pre-registrado ni las 3 desviaciones (+2,86). 2023
por debajo del equilibrio y 2025 el año fuerte: patrón típico de falso positivo.

**MOMENTO 09:40 NY · 1:2 → +0,137R · p=0,0047 · 253 ops/año**
1. A las 09:40 NY compara el precio con el de las 09:10 NY (30 min antes).
2. 09:40 > 09:10 → largo. 09:40 < 09:10 → corto.
3. Entra a mercado en la vela que abre a las 09:41 NY.
4. Stop 30 puntos, objetivo 60 puntos (1:2).
5. Si no toca nada, cierra a las 16:00 NY. Una operación al día.

A favor: única de las 528 del barrido que sobrevive a la prueba de régimen.
Positiva los tres años y su año fuerte es 2023, no 2025. Invertida −0,1225, motor
limpio. Reserva ciega 2026: +0,094R con p=0,21.
En contra: corregida por las 528 probadas, p=0,91. Solo pasa si se corrige por
las 6 familias declaradas (p=0,030). **Y la ventaja decae año a año: 2022 +0,47R
· 2023 +0,21R · 2024 +0,08R · 2025 +0,19R · 2026 +0,09R.** Eso es el retrato de
un patrón que el mercado va arbitrando. Es la objeción más seria que tiene.
Veredicto: demo y forward-test. No meter dinero todavía.
**27/09 — réplica con el motor nuevo (calibrado sobre paseo aleatorio): +0,064R,
p=0,12, n=734, a 1,6σ del nulo.** El "2022 +0,47R" son 4 operaciones (el CSV
empieza el 26/12/2022): no hay decaimiento, el resultado es plano (~+0,06/año).
Pendiente cruzar operación a operación con el motor original para ver cuál
tiene el bug. 2026 en CFD con el motor nuevo: +0,178R, p=0,054, n=179 (no ciego).
**Reserva ciega 2021-2022 (CFD, pre-registrada): −0,008R, n=501, p=0,55,
invertida +0,024. 2021 −0,031 · 2022 +0,015. NO PASA.** Cero fuera de 2023-26:
en el mejor caso es régimen actual, no ventaja. No se opera con dinero.

**CANDIDATA NUEVA (27/09) · MOMENTO 09:40 con stop en % · 1:2**
Señal igual que Momento 09:40 (cierre 09:39 vs cierre 09:09), entrada a mercado
en la apertura de 09:40, **stop = 0,40% del precio** (~55 pts en 2021, ~115 en
2026), objetivo 2× stop, cierre 16:00. Salió de una rejilla pre-registrada de
504 celdas en DISEÑO (`preregistros/2026-09-27_rejilla_momento_reversion.md`),
3 finalistas a validación:
- DISEÑO 21/23/25: +0,104R (wr 41,9%). La rejilla entera NO supera al nulo: la
  mejor celda real (+0,111R) = el máximo del paseo aleatorio (+0,111R).
- **VALIDACIÓN 22/24/26: +0,086R, wr 40,3%, p=0,049, positiva los tres años
  (+0,126 · +0,052 · +0,078).** No pasa el umbral pre-registrado (p < 0,005).
- 6 años juntos: +0,096R, n=1.416, 6 de 6 años positivos, 70% de meses
  positivos, +100R quitando los 3 mejores meses, invertida −0,062.
- Paseo aleatorio (96 semillas): −0,010R, asimetría direccional +0,004 ± 0,006.
- Las otras 2 finalistas cayeron a ~0 en validación.
- Ojo: la señal 09:40/09:10 viene de conocimiento previo (barrido de 528 en NQ
  2023-25) y 2022/2026 ya se habían mirado con el stop fijo de 30 pts
  (2021-22: −0,008R). La validación de esta celda no es 100% virgen.
**Pruebas duras pre-registradas (27/09): pasa 9/9.** NQ futuro real 2023-25 +0,059R
(corr 0,92 con CFD; 2024 ≈ 0) · vecindario 10/10 positivo (meseta) · placebo de
dirección +2,55σ · otra convención de vela +0,096 · coste ×3 +0,069 · entrada
09:41 +0,096 · 98% de ventanas de 12 meses positivas · largos +0,129 / cortos
+0,063 · señal idéntica con datos truncados en 09:40 (1416/1416) · bootstrap
mensual IC95% [+0,037, +0,154]. `resultados/2026-09-27_pruebas_duras_momento_pct.txt`.
Ventaja realista para planificar: **+0,05/+0,06R** (lo que da en el futuro).
Veredicto: la mejor pista del proyecto, sin bug ni fragilidad detectable, **pero
no aprobada** (validación p=0,049). Siguiente: forward-test en demo.
**Validación en otro instrumento, ES/S&P 500 (28/09, pre-registrada, reglas
congeladas, ES nunca usado): +0,023R, n=1.329, p=0,24, 3 de 6 años positivos
(2021 +0,05 · 2022 −0,01 · 2023 +0,09 · 2024 −0,05 · 2025 −0,04 · 2026 +0,13).
NO PASA.** Mismo signo y +2,1σ sobre su paseo aleatorio (−0,053), pero sin
confirmación. Cartera NQ+ES: +0,058R con corr 0,44 (no mejora a NQ solo).
Lectura: el efecto, si existe, es cosa del NQ; el ES no lo confirma. Pesa en contra.
**4 filtros pre-registrados (28/09, diseño 21/23/25): ninguno pasa**, validación
sin gastar. A favor del día previo +0,167R (wr 44,0%) y a favor del gap +0,149R
(wr 43,3%) mejoran la base (+0,104R, 41,9%) pero NO superan el percentil 95 de
subconjuntos al azar del mismo tamaño (+0,181 y +0,190). ES de acuerdo +0,094R
(peor que la base) e impulso fuerte +0,051R (peor). Se opera sin filtros.
**2 filtros más (02/10, pre-registrados, diseño 21/23/25, idea de Daniil): ninguno pasa.**
F5 tramo 09:09-09:39 "limpio" (eficiencia > mediana de 60 sesiones): +0,055R, PEOR que
la base (+0,105); terciles no monótonos (+0,02 · +0,26 · +0,04). F6 volumen 09:30-09:39
alto: +0,151R pero < p95 al azar (+0,195); terciles monótonos pero suaves (+0,08 · +0,09 ·
+0,14) y el winrate NO cambia (42%): solo como pista débil. Van 6 filtros, cero pasan.
`resultados/2026-10-02_filtros_limpieza_volumen.txt`.
**Familia de 9 filtros / 18 variantes (02/10, pre-registrada, diseño): NO PASA.** Mejor
"no a favor de la apertura 09:30" +0,312R (n=74, 11%) vs máximo del nulo p95 +0,362 (p
familia 0,11). Pistas sin valor operativo (por debajo del máximo del nulo): barra 08:30
amplia +0,215 vs −0,004 · a favor de la media de 20 días +0,172 vs +0,031. Bug propio
cazado antes de leer: rolling con min_periods completos tiraba ~50% de días (cierres
anticipados). Van 24 variantes de filtro sobre Momento, cero pasan: se opera sin filtro.
`resultados/2026-10-02_familia_filtros_momento.txt`.
**Saltar el día tras un TP (03/10, pre-registrado, idea de Daniil): NO PASA.** P(TP | ayer TP)
26,6% vs P(TP | ayer no TP) 27,0% (diseño): los TP no se agrupan ni se repelen, cada día es
independiente. Operando solo tras no-TP +0,110R vs base +0,104 (p95 azar +0,155); días saltados
+0,089 con signo cambiante por año (2021 +0,23 · 2023 −0,10 · 2025 +0,18). Saltarlos solo quita
operaciones positivas. `resultados/2026-10-03_saltar_dia_tras_tp.txt`.
**Pruebas duras II (29/09, pre-registradas): pasa 8/9.** Premisa desnuda con
barreras simétricas 53,4% largos / 51,9% cortos · quitando cualquier año
+0,088/+0,105 · 11/12 semestres positivos (solo 2024-S1 −0,07) · volatilidad
alta +0,118 / baja +0,091 · 4/5 días (viernes −0,004) · salida 12:00 +0,075 y
14:00 +0,100 · stop 5 pts peor +0,054 · sin los 10 mejores días +0,082.
**FALLA U8: entrando en el peor precio de la vela de 09:40 → −0,072R.** La
ventaja es muy sensible a la ejecución: orden a mercado en el segundo 0 de las
09:40 (entrar a las 09:41 en la apertura da igual, +0,096), sin perseguir precio.
`resultados/2026-09-29_pruebas_duras_II_momento_pct.txt`.
**Stop estructural (29/09, pre-registrado):** S1 stop en el cierre de 09:09 (se
salta el día si < 0,10%) pasa diseño (+0,127R vs +0,104, 3/3 años, 70% de días)
pero en VALIDACIÓN da +0,097R vs base +0,086, p=0,056 (umbral 0,01), 2026
+0,002 → NO PASA. Equivalente a la base, no mejor. S2 (extremo 09:09-09:39)
peor que la base en diseño. Se mantiene el stop del 0,40%.
**Comparación de cuentas (29/09, `scripts/comparar_cuentas.py`, stop 116 pts =
NQ ~29.000, ventaja realista +0,05R):** 25K ($50,30) con 1 micro → 4,1/10 pasan,
1,8/10 cobran, EV +$81/cuenta, 24% de tandas de 10 en pérdidas; 2+ micros en la
25K es mala idea (EV ≤ +$18). 50K ($90,20) con 2 micros → 3,7/10, 1,9/10, EV
+$148, 28% de tandas en pérdidas (**02/10, corregido el retiro mínimo de la 50K a
$500 según soporte; antes se suponía $1.000 y daba +$175**). Por dólar invertido
25K 1 micro (1,61) ≈ 50K 2 micros (1,64): empate; la 25K es más barata y con
menos tandas en pérdidas. `resultados/2026-10-02_comparar_cuentas.txt`.
100K: peor por dólar invertido. Con ventaja cero: 25K 1 micro +$42, 50K 2 micros +$54.
**Rejilla de gestión (02/10, pre-registrada, 175 celdas: stop 0,30-0,80% × ratio 1-3 ×
micros; elegir en 21/23/25, comprobar en 22/24/26):** la gestión actual **0,40% · 1:2 · 1
micro en 25K** es la nº1 en tasa de pase (5,2/10 diseño · 5,5/10 control) y la nº2 en EV
de control (+$183; diseño +$157). La mejor de diseño (0,30% · 1:1,5 · 1 micro, +$189) es
peor en control (+$178) → NO se cambia. 2 micros con stop 0,80% y TP 1,60% (idea de Daniil):
2,2-2,6/10 pasan, EV +$5/+$22. En 50K la rejilla depende del supuesto "día ≥$200" de la
fondeada (sin verificar): no se saca conclusión. Ventaja histórica (realista: menos).
`resultados/2026-10-02_rejilla_cuentas_momento.txt`.
**Simulador de cuentas (`src/cuentas.py`, 27/09):** moneda al aire con coste da
2,0-3,0/10 según stop y riesgo ($500 óptimo, $833 de lo peor: cuadra con lo de
arriba, nivel algo más alto que el 2,09 antiguo). Con esta candidata y riesgo
$250/op (1-2 micros): ventaja histórica → 4,7/10 pasan, 2,2/10 cobran, $192
cobrados por evaluación comprada; ventaja realista +0,05R → 4,1/10, 1,6/10,
$129; ventaja cero → 3,6/10, 1,0/10, $73-98. **El EV depende del precio de la
evaluación**, que falta en este documento. `resultados/2026-09-27_cuentas_momento_pct.txt`.

### Order flow APROXIMADO (01/10, BVC sobre barras de 1 min del NQ, diseño 2023+2025)
`preregistros/2026-10-01_order_flow_proxy.md`. Ninguna de 3 pasa: flujo de la
apertura +5,6 pts p=0,53 · absorción −13 pts p=0,59 (n=70) · como filtro de
Momento, "de acuerdo" +0,087R vs "en desacuerdo" +0,109R. **Límite clave:** el
BVC se calcula desde el propio precio, así que coincide con la dirección de
Momento el 85% de los días: casi no añade información. Esto NO prueba nada sobre
el order flow real; para eso hacen falta datos tick con lado agresor (Databento).

### Rejilla apertura europea (02/10, pre-registrada, 432 celdas, diseño CFD 21/23/25) — CERRADA
`preregistros/2026-10-02_rejilla_londres.md`. Momento/reversión a T ∈ {02:10, 02:30, 03:10,
03:30, 04:00, 05:00} NY, L 10/30/60, stop 0,10-0,40%, ratio 1-2, cierre 08:29 NY. Mejor
celda +0,058R (t 1,53); máximo del paseo aleatorio +0,072 ± 0,019 (t 1,94): la mejor real
está a −0,72σ DEBAJO del nulo. R medio de la rejilla −0,028 (nulo −0,038). Ninguna hora
ni modo positivo en media. La apertura europea en NQ se comporta como un paseo aleatorio:
no hay "Momento de Londres". `resultados/2026-10-02_rejilla_londres_diseno.txt`.

### Premisa SMT NQ-ES (02/10, pre-registrada, diseño CFD 21/23/25) — NO PASA
`preregistros/2026-10-02_smt_nq_es_premisa.md`. Primera rotura del máximo/mínimo overnight
de NQ en 09:30-11:00; SMT = ES no lo rompe. Carrera a barreras simétricas ±0,2/0,3/0,4%
desde el cierre de la barra (reversión). SMT: 53,1 / 52,9 / 51,7% a favor (p 0,13-0,29),
largos 48-49% (por debajo de 50) y cortos 54-57%. Sin SMT: 48-51%. No cumple (largos < 50%,
p > 0,0167). Única hipótesis para el futuro: cortos tras rotura del máximo con SMT (57%,
n=189), sin valor por sí sola. `resultados/2026-10-02_smt_nq_es_premisa.txt`.

### Lote 3 de premisas, solo TP-vs-SL (02/10, pre-registrado, 24 celdas, diseño 21/23/25) — NINGUNA
`preregistros/2026-10-02_premisas_lote3_barreras.md`. Barreras simétricas ±0,15/0,25/0,40%.
Mínimo p = 0,050 (umbral 0,0021). Lo más cercano: L2 dato 10:00 (continuación de 10:00-10:04)
53,2% a ±0,25% (largos 54,3 / cortos 52,0, p 0,095); L6 tarde 12:30-15:30 al revés (reversión
54-59%, n pequeño). Dato 08:30, vela gigante, VWAP, número redondo, mediodía, hueco: 47-52%.
El nulo de paseo aleatorio salió degenerado (celdas con n mínimo dan 50%): irrelevante, nada
pasa ni el Bonferroni. `resultados/2026-10-02_premisas_lote3_barreras.txt`.

### Lote 4 de premisas, contexto de días previos, TP-vs-SL (02/10, pre-registrado, 18 celdas) — NINGUNA
`preregistros/2026-10-02_premisas_lote4_barreras.md`. 3 días seguidos (reversión), día previo
enorme, 1ª vela 5m con cuerpo (53%), apertura fuera del rango previo, lunes: 43-53%. Pista:
rotura de inside day 57-62% en los 3 k y ambas direcciones (n≈60, p 0,09). **Validación
2022/24/26 (uso nº6, pre-registrada): ±0,40% → 51,0% (25/49), p=0,50 → NO PASA. Muerta.**
Contabilidad del protocolo: uso nº6 gastado (el siguiente, p < 0,05/7).
`resultados/2026-10-02_premisas_lote4_barreras.txt` · `..._validacion_inside_day.txt`.

### Demostración de sobreajuste (03/10, pre-registrada, NO es candidata)
19.008 reglas de momento/reversión a hora fija × stop × día de la semana, buscadas en 2021+2023,
medidas en 2025. La mejor: 14:10 jueves, 1:2, +0,500R (wr 53%) en la búsqueda. Las 100 mejores:
+0,344R de media en la búsqueda → **+0,011R en 2025, 52% positivas (moneda al aire)**; correlación
búsqueda-2025 de todas las reglas: 0,00. Es el retrato de la regla I con números de este repo.
`resultados/2026-10-03_demo_sobreajuste.txt`.

### Rejilla masiva con años alternos (03/10, pre-registrada, idea de Daniil) — NINGUNA PASA
28.512 reglas (momento/reversión a hora fija × L × stop × día de la semana, 1:2). Diseño 21/23/25:
2.240 positivas los 3 años; finalistas = 10 con mayor R mínima (+0,27 a +0,39R el peor año).
**Validación 22/24/26 (uso nº7): 9 de 10 NEGATIVAS** (jueves 14:10 −0,22/−0,32R; viernes 10:40
−0,03/−0,09). La única positiva: 09:40 L30 0,25% martes +0,192R (p 0,061) — la familia Momento.
Top-100 robustas: +0,269R en diseño → −0,039R en validación (32% positivas). Corr diseño-validación
+0,08. Exigir 3/3 años positivos en diseño NO protege contra el sobreajuste con 28.000 reglas.
`resultados/2026-10-03_rejilla_masiva_alterna.txt`.
Perfil por hora (mom, L30, 0,40%, todos los días, diseño/validación): 09:35 +0,02/+0,10 · **09:40
+0,10/+0,09** · 09:45 +0,05/+0,08 · 09:50-10:30 ≈ 0 · **10:40 −0,01/−0,02** (la que Daniil operó por
error en el replay de marzo, una hora tarde por el cambio de hora). Solo 09:35-09:45 es positivo
en las dos mitades: el efecto vive en los primeros 15 minutos tras la apertura y luego se apaga.
De las 223 reglas positivas los 6 años, las que operan todos los días son casi todas 09:35-09:45.

### Lote 1 de premisas nuevas (27/09, protocolo de partición, diseño 2021/23/25 CFD)

Ver `preregistros/2026-09-27_premisas_lote1.md` y `protocolo_particion.md`.
Ninguna pasa (umbral p < 0,0071):
- **P1 última media hora (reversión): −3,3 pts, p=0,054**, negativa los 3 años y
  en largos y cortos. Near-miss. La versión "días de movimiento grande" (vista en
  2021+2025) se probó limpia en 2023: +1,6 pts → muerta. P1 queda sin estrategia.
- **P4 primera M5 con cuerpo (mecanismo de OPEN_DRIVE): +8,8 pts, p=0,10**, pero
  2021 +2,4 · 2023 −1,8 · 2025 +24,7 y un pico en el umbral 0,6 que cae a los dos
  lados. **Pesa en contra de OPEN_DRIVE: la "meseta" no aparece fuera de 2025.**
- Gap, dato 08:30, dato 10:00 (mal medido, 48 días), Londres, cambio de mes: ruido.
- 2022, 2024 y 2026 siguen SIN TOCAR para ideas nuevas (validación).

### Lote 2 de premisas (27/09, mismo protocolo) — ninguna pasa
`preregistros/2026-09-27_premisas_lote2.md`. Vuelta a la media de la mañana (solo
30 casos, umbral demasiado exigente), NR7 + dirección de la 1ª media hora
(−18 pts, p=0,16, mismo signo los 3 años: la única con forma, sin potencia),
continuación de la tarde, cierre en extremo, momentum 10 días, reversión tras
día >1,5% (+69 pts, p=0,046, pero 2023 negativo y todo es el rebote de abril
2025), día de la semana (F p=0,29). Q4 y Q5 muestran largos>cortos: es la deriva
alcista, no señal (regla M).
**Balance de los lotes 1-2: 14 premisas direccionales simples en NQ intradía,
cero pasan.** El NQ intradía se comporta, a este nivel de simplicidad, como un
paseo aleatorio con deriva.

### Enterradas — no reabrir sin justificar qué añaden

- **2T (Lozano FX)**: el +0,256R era el bug nº7. Causal: **−0,055R** (n=1.258) en
  NY, +0,044R en 2026. Además ese motor no era la 2T del vídeo (9 divergencias) y
  él opera EUR/USD.
- **RTP (Jacko)**: cuatro lecturas, cuatro ceros. La invertida da cero, o sea
  cero información en ninguna dirección, y **ninguna gestión crea información
  donde no la hay**: solo cambia la forma de cobrar el mismo cero, y el cero
  menos comisiones es negativo. Por eso las rejillas salen planas en vez de tener
  un máximo. No reabrir con otro ratio, otra gestión ni otra reentrada.
  **27/09: réplica nº3 con el motor calibrado** (495 ops, caja 85,8, stop 75,1):
  −0,010R, invertida −0,063R. **Y 11 filtros de mecanismo distinto pre-registrados**
  (compresión, hora del barrido, sesgo overnight, fusión con Momento, días macro,
  profundidad del barrido): ninguno pasa. Mejor celda F11 barrido largo +0,102R,
  a 0,27σ del máximo del nulo (p=0,36). Ver `preregistros/2026-09-27_rtp_filtros.md`.
  Dos contrastes a ~2,3σ (contra sesgo overnight vs a favor; barrido largo vs corto)
  quedan SOLO como hipótesis para la reserva 2026, sin tocar nada más.
  **Reserva 2026 (CFD, pre-registrada):** barrido largo se da la vuelta (+0,002 vs
  corto +0,392) → muerta. **Contra sesgo overnight: +0,266R (n=62, p=0,12),
  diferencia con "a favor" +0,255 (p=0,20), la misma que en 2023-25 (+0,275).**
  No pasa, pero es la única pista de RTP que sobrevive a una reserva ciega.
  **Reserva 2021-2022 (CFD, pre-registrada): contra sesgo −0,120R (n=194),
  diferencia con "a favor" −0,105 → SIGNO CONTRARIO, ENTERRADA.** RTP base en
  2021-22: −0,089R (n=340). Según el pre-registro, "el mercado ha cambiado" no
  vale como excusa: como mucho es régimen 2023-26, y eso no se opera.
  **RTP queda cerrada del todo. No reabrir.**
- **LIT / inducción de liquidez**: dos baterías (16 + 8 celdas). Dio el R más alto
  del proyecto (+0,2405R, n=146) y no significaba nada: máximo real a +0,40σ del
  máximo del nulo. El displacement es un pico de ruido y va al REVÉS en la
  submuestra con potencia. Se salva un filtro reutilizable: **no operar la primera
  barrida de un nivel** (fase1 −0,153R · fase2 +0,058R · fase3+ +0,070R, la
  diferencia a +2,50σ). Quita operaciones malas, no crea buenas.
- **Híbrido Judas+RTP** (informe externo, 26/09): 20 celdas negativas, placebo a
  −0,48σ. Y con él cae la familia entera por la vía de la premisa (regla N).
- **Barrida overnight + IFVG 09:30-10:10 ("80% winrate", vídeo de Fede, 02/10,
  pre-registrado, diseño CFD 21/23/25):** 503 ops (62% de días), winrate 48,9% a
  1:1 · R −0,050 (1:1) · −0,050 (1:1,5) · −0,021 (1:2), invertidas negativas,
  todo al nivel del paseo aleatorio. Su propio vídeo: 16 ops, 64,7% real, un día
  perdedor saltado y cambio de temporalidad hasta ver el gap "limpio". Séptimo
  intento de la familia barrida + confirmación: cero, como dice la premisa.
  Los 6 años (informativo, no es una validación): 974 ops, winrate 49,5% a 1:1,
  R −0,039 (1:1) · −0,017 (1:1,5) · −0,001 (1:2); máximo anual 53,5% de winrate.
- **Aleix Andreu, DOL + FVG 15m + IFVG 1m ("mejor estrategia 2026", 02/10,
  pre-registrado, diseño CFD 21/23/25):** sesgo = último FVG de 15 min vivo a las
  09:30, retroceso a la zona, IFVG de 1 min a favor, stop en el extremo. 606 ops
  (74% de días): 1:1 −0,078 · 1:1,5 −0,068 (wr 41,4%) · 1:2 −0,059, los 3 años
  negativos, invertidas ≈ 0, todo por debajo del paseo aleatorio (−0,04). Su gestión
  ($1.000 de riesgo sobre MLL $2.000 en 50K) es justo el sizing ÓPTIMO PARA UNA
  MONEDA AL AIRE: con ventaja cero es el que mejor EV da (+$83 vs +$4 a $500); con
  ventaja +0,10R es el peor (+$325 vs +$490 a $250). Maximiza varianza: tiene sentido
  solo si no tienes ventaja. `resultados/2026-10-02_aleix_dol_fvg_ifvg.txt`.
- **"Regla de la primera vela" (vídeo, 03/10, pre-registrado, diseño CFD 21/23/25):** rango
  09:30-09:34, primer FVG de 1 min con cierre fuera del rango, retroceso a la zona y
  envolvente; stop en el extremo, 1:2. 198 ops (24% de días): 1:2 +0,009R (TP 30% · SL 59%),
  p=0,46, años +0,24 / −0,22 / −0,04; 1:1 TP 46% vs SL 48% (R −0,045). Invertida negativa,
  paseo −0,03. Cero, como el ORB. `resultados/2026-10-03_primera_vela_5m_fvg.txt`.
- **NQ Motion Model de Kasen (03/10, pre-registrado, diseño CFD 21/23/25):** barrida del
  máx./mín. de la vela 4H 06:00-10:00 en 10:00-13:00 + SMT con ES + descuento/prima + IFVG
  1m; stop en el extremo. 292 ops (1,8/semana): 1:2 +0,053R (wr 37%, p 0,27; 2021 +0,04 ·
  2023 −0,01 · 2025 +0,15) · 1:1 53,4% · objetivo extremo opuesto 4H +0,064R. NO PASA.
  Control sin SMT: −0,090R (615 ops). El SMT mejora +0,14R (z≈1,4, no significativo):
  segunda vez que el SMT apunta algo débil (ver premisa SMT). Pista, no estrategia.
  `resultados/2026-10-03_kasen_nq_motion.txt`.
- **Kasen, vídeo "This ONE candle makes me 100k/m" (03/10, pre-registrado):** barrida de PDH/PDL
  (09:30-11:00) + cierre al otro lado de la apertura de las 10:00 (≤12:00); stop en el extremo.
  352 ops: 1:2 +0,047R (p 0,25), 2021 −0,06 · 2023 −0,06 · **2025 +0,25** (todo de un año: patrón
  de falso positivo). NO PASA. Informativo con SMT de ES: 116 ops, 1:2 +0,154R (p 0,11, 3/3 años
  positivos, 2025 el más fuerte); objetivo PDL/PDH +0,208R. TERCERA vez que añadir SMT mejora la
  misma regla (premisa SMT, Kasen 4H, Kasen PDH). Candidato a hipótesis para la reserva 2019-2020.
  `resultados/2026-10-03_kasen_pdh_10am.txt`.
- Judas Swing, CRT H4, ORB (5m/15m/1m), Alex Ruiz, Open Market, Aleix Andreu,
  Santiago Amado, David Sánchez, Joaco Trader, Robins, y ~500 configuraciones de
  los lotes 2-6 y del barrido de 528.

### La familia "barrida de un nivel + confirmación" está cerrada

Seis intentos: David Sánchez, Santiago Amado, Judas Swing, Aleix Andreu, LIT y el
híbrido. Y desde el 26/09 no se cierra contando fracasos, se cierra con un número:
**la premisa está medida y es cero** (regla N). La barrida no predice la
reversión. Eso deja vivas las variantes que añadan un mecanismo DISTINTO, y mata
todas las que solo cambien gatillo, descuento, ratio o gestión.
Es el patrón más enseñado del mundillo y el que más veces se ha quedado a medias
aquí. No es casualidad: la barrida es frecuente y vistosa, y no predice nada.

---

## 8. Reglamento Lucid Flex 25K

**Verificado en el panel de Lucid (27/09/2026):** evaluación $65,30 con cupón
($89 sin él; a 29/09 bajó a $50,30), pago único, reset $65. Eval: objetivo $1.250, MLL $1.000 EOD,
consistencia 50%, 2 mini o 20 micros, DLL opcional (off), mínimo 2 días.
Fondeada: MLL $1.000, **DLL $600**, sin consistencia, 2 mini o 20 micros,
**5 días para retiro**, plan de escalado sí (el tope de 10 micros hasta +$1.000
de abajo sería ese escalado; sin confirmar). 50K Flex: $90,20, objetivo $3.000,
MLL $2.000, 40 micros. 100K Flex: $170,60, objetivo $6.000, MLL $3.000, 60 micros.
**Soporte de Lucid (chat con su IA, 01-02/10, sin enlaces a artículos):** MLL con
nivel fijado al cierre EOD pero **el breach es intradía sobre equity abierta** (tocarlo
quema aunque cierres por encima) · retiro mínimo $500 en 25K Y en 50K, máximo $1.000
(25K) / $2.000 (50K), hasta 50% del beneficio por ciclo · al SOLICITAR el retiro el
MLL se fija en inicial+$100 · **5 retiros por cuenta y luego pasa a cuenta LIVE** (no
"revisión manual") · topes 20 micros (25K) / 40 (50K), sin mencionar escalado ·
DLL en fondeada "opcional" (contradice el $600 del panel: comprobar en el panel).
**Máximo 5 cuentas fondeadas a la vez** (lo sabe Daniil, 02/10).
Sin respuesta: cálculo exacto de la consistencia, máximo de evaluaciones, copy
trading entre cuentas propias, estrategias/horarios restringidos, cuotas de la
fondeada. Es un bot: lo que no salga en el panel o en un artículo, no es firme.

- **MLL trailing**: sube solo con el cierre EOD del balance. Se congela al llegar
  a +$1.100 de colchón (queda fijo en inicial+$1.000+$100).
- **Breach intradía quema la cuenta.**
- Regla de consistencia 50%, solo en evaluación.
- Tope de contratos: 20 micros en evaluación. En fondeada 10 hasta +$1.000 de
  beneficio, luego 20. **El tope por sí solo mueve la tasa de pase de 3,75 a 2,06
  de 10.**
- Objetivo de evaluación: +$1.250.
- Retiro: mínimo $500, máximo 50% del beneficio (tope $1.000) por solicitud.
  Requiere 5 días con ≥$100 netos en el ciclo y beneficio neto del ciclo > 0.
  **Al SOLICITAR el retiro** (no al cobrarlo) el suelo del MLL salta a +$100.
  Reparto 90/10. Máximo 5 retiros; después la cuenta pasa a LIVE (soporte, 02/10).

### Números del negocio

- Con ventaja CERO, el techo de pasar una evaluación es ~44% por teoría de la
  ruina, y las demás reglas de Lucid lo bajan más.
- Con MLL trailing real y sizing óptimo, **la moneda al aire pasa 2,09 de 10.**
  Ese es el suelo contra el que comparar cualquier tasa de pase.
- **Sizing óptimo bajo la regla real: $500 por operación** (11-12 micros con stop
  mediano). $833 es de los peores.
- El trailing castiga más a quien no tiene ventaja que a quien la tiene.
- Separación de gestiones: **evaluación a ratio bajo** (pasar depende del
  winrate), **fondeada a 1:2** (cobrar depende de la ventaja). Nunca al revés.
- "Un SL y fuera" es la decisión más cara del plan: baja el pase a 1,5 de 10. El
  primer disparo sí es a vida o muerte; a partir del segundo no.
- Dispersión: comprando 10 cuentas, **una de cada cuatro tandas va a parecer que
  la estrategia no funciona aunque funcione.** Presupuéstalo antes de asustarse.
- Con Momento 09:40 a la ventaja realista del holdout (+0,09R): ~3,9 de 10 pasan,
  ~1,1 de 10 llegan a cobrar, EV ≈ +$150/cuenta, y ~46% de las tandas de 10
  pierden dinero.

---

## 9. Pendiente, por orden de impacto

1. **Montar la infraestructura de la sección 10.** Es lo que hace que buscar
   salga barato: con loader, controles y simulador de cuentas hechos, probar una
   estrategia nueva pasa de un día a una hora, y probar diez es una tarde. Es la
   inversión que más acelera la búsqueda, y por eso va primero.
2. **Validar Momento 09:40 a mano en FX Replay**, 60 operaciones sobre 2022 (año
   nunca usado en ningún backtest). Es la única validación sin look-ahead posible,
   porque la hace él, no el código. Esperado ~+5R, rango plausible −9R a +19R. Si
   no se parece, hay un bug nº13 sin descubrir. Va en paralelo: la hace él a mano
   mientras tú sigues con código, no se bloquea nada esperándola.
3. Conseguir **2026 completo**. Sin reserva ciega nada puede aprobarse, y ahora
   mismo es el cuello de botella de TODA la búsqueda: cualquier cosa que
   encuentres en 2023-25 se queda en "prometedora" sin él.
4. Probar el filtro "no operar la primera barrida" sobre los motores de David
   Sánchez, Santiago Amado y Aleix Andreu (ya escritos, cuesta poco). Si sube los
   tres a la vez es un hallazgo de familia; si sube uno, es ruido.
5. Rehacer el valor esperado por cuenta con el MLL trailing.
6. Mandar a soporte de Lucid las 4 preguntas pendientes. La del breach intradía
   decide el sizing.
7. EUR/USD M1 para juzgar a David Sánchez, 2T y LIT en el instrumento de sus
   autores. En NQ esa familia ya está agotada.
8. Dataset de ES 1 minuto para el SMT NQ-ES.

### Dónde buscar, por relación entre lo que cuesta y lo que puede dar

Esto es la parte viva del documento. Lo de arriba es fontanería; esto es la
búsqueda.

**Lo más prometedor, porque está sin tocar:**
- **Otro instrumento.** David Sánchez, 2T y LIT están medidas en NQ y sus autores
  operan Forex. Son tres estrategias juzgadas en el instrumento equivocado. Con
  EUR/USD M1 se rejuzgan las tres sin inventar nada nuevo. Es el mejor
  coste-beneficio del proyecto ahora mismo.
- **Otra ventana temporal.** 2026 completo convierte cinco "prometedoras" en
  aprobadas o enterradas. Sin él la búsqueda no puede cerrar nada.
- **Otro horario.** La killzone de Londres (08:00-11:00 españolas) es operable y
  está mucho menos explorada que la de NY. Él puede operar mañana o tarde.
- **Familias que no son "barrida + confirmación".** Esa está cerrada por premisa
  (sección 7). Lo que queda sin explorar: microestructura de volumen y VWAP más
  allá de las dos variantes probadas, comportamiento alrededor de datos macro
  (08:30 y 10:00 NY son los dos minutos más volátiles del día y no se han
  explotado), estacionalidad intradía que no sea la apertura, y relaciones entre
  índices (el SMT NQ-ES, que necesita el dataset de ES).
- **OPEN_DRIVE es la pista más cálida que hay.** Es una MESETA, que es la forma
  que tiene un mecanismo de verdad (regla P). Merece que se le busque el mecanismo
  en vez de más variantes: ¿por qué funciona en velas de 2-5 min y no en 1, 10 ni
  15? Si hay una razón, ahí puede haber una familia entera.

**Lo que no merece más tiempo, y decírselo si lo propone:**
- Más variantes de la familia "barrida de un nivel + confirmación" en NQ. Seis
  intentos y la premisa medida en cero.
- Otra gestión, otro ratio u otra reentrada sobre RTP. La invertida da cero: no
  hay información que ninguna gestión pueda cobrar.
- Más umbrales de displacement. Es un pico de ruido y va al revés donde hay
  potencia.
- Barridos masivos de parámetros sobre NQ 2023-25. Ese pozo está seco: 528
  configuraciones y el máximo del nulo sube más rápido que la mejor celda.

---

## 10. Estructura del repo

```
data/                 CSVs de precios. No se versionan (.gitignore).
src/loader.py         Carga + los dos controles de la sección 2. Punto único de entrada.
src/motores/          Un módulo por estrategia. Devuelven ops con rmax/toco_sl/riesgo_pts.
src/controles.py      Placebo, invertida, paseo aleatorio, consistencia, Bonferroni.
src/cuentas.py        Simulador de Lucid Flex 25K con MLL trailing.
preregistros/         YYYY-MM-DD_nombre.md, escrito ANTES de ejecutar.
resultados/           Salida de cada corrida, con el pre-registro que le corresponde.
```

Nada entra en `resultados/` sin su pre-registro en `preregistros/`.

---

## 11. Lo que esto no demuestra

Un backtest sirve para descartar ideas malas, no para demostrar que una es buena.
"No descartada" no es "confirmada". Van doce bugs, y los cinco últimos aparecieron
en motores que ya habían pasado la batería entera; el nº11 en un motor escrito
desde cero aplicando la lista completa de entrada. La tasa no baja. Cualquier
número que salga de este repo hay que cruzarlo a mano antes de poner dinero.

Y la lección de las dos baterías de LIT, que vale para la siguiente estrategia
que llegue recomendada: la segunda dio el R más alto del proyecto y no
significaba nada. Un R alto en muestra pequeña, en el pico de un umbral, con el
año más reciente como el más fuerte, es el retrato exacto de un falso positivo.

De ahí sale la única conclusión operativa que importa, y no es "deja de buscar":
**buscar más variantes del mismo sitio sube el listón más rápido de lo que sube
la mejor celda; buscar en un sitio nuevo no.** Una idea nueva en EUR/USD, en 2026
o en la killzone de Londres entra con el listón limpio. La variante número 529
sobre NQ 2023-25 entra ya debiendo dinero. Es la misma cantidad de trabajo y no
vale lo mismo, y ahí es donde tienes que empujar cuando te traiga algo.
