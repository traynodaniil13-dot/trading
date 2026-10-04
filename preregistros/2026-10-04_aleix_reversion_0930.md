# Pre-registro · Aleix Andreu, "modelo de reversión de las 09:30" · 04/10/2026

Escrito ANTES de ejecutar. Fuente: reel de Aleix (transcripción pegada por Daniil).
"Top 100 de Topstep."

## Lo que dice

1. En H1, fijarse en qué FVG respeta el precio. Si en la apertura el precio barre los
   mínimos, buscar una reversión al alza (y al revés con los máximos).
2. En 15m, a las 09:30 la apertura tiene que barrer el objetivo y estar dentro de un FVG.
3. En 1m: acumulación, manipulación con un FVG dentro, barrida y cierre por encima de los
   FVG. Stop por debajo, TP en el siguiente alto (o un FVG de 15m).
(La parte "si abre alcista sin tocar mínimos, ventas hasta ahí" no tiene entrada
explicada: no se prueba.)

## Mecánica (CFD NQ, hora NY, DISEÑO 2021/2023/2025)

- **Mínimos/máximos** = mínimo/máximo overnight (18:00-09:29). Es la misma liquidez que en
  la estrategia de Fede (`sweep_ifvg`), y la reutilizo.
- **Barrida:** primera barra de 09:30-10:00 que perfora el mínimo (largo) o el máximo
  (corto) overnight. Si perfora los dos a la vez, no hay setup.
- **FVG H1:** velas H1 de reloj agrupando M1. Un FVG alcista nace al cerrar la 3ª vela si
  mín3 > máx1, con zona [máx1, mín3]. Vale si nació en las 120 H1 anteriores a las 09:00
  (la vela de las 09:00 no ha cerrado a las 09:30) y ningún cierre H1 posterior, hasta
  las 08:59, ha caído por debajo de máx1 ("respetado"). El bajista es el espejo.
- **Condición FVG:** al disparar la entrada, el mínimo de 09:30→entrada (en largos) está
  dentro de la zona de algún FVG alcista H1 vigente. En cortos, el máximo dentro de un FVG
  bajista.
- **Gatillo 1m (IFVG):** desde la barrida y hasta las 10:30, la primera barra cuyo cierre
  queda por encima del techo de TODOS los FVG bajistas de 1m nacidos desde las 09:30, con
  al menos uno existente. En cortos, el espejo.
- **Entrada** al cierre de esa barra (el seguimiento empieza en la siguiente). **Stop** en
  el extremo 09:30→entrada. Stop mínimo 0,05% del precio. Cierre forzado a las 15:59.

## Variantes (3) → p < 0,05/3 = 0,0167 (una cola)

- **V1:** TP en el "siguiente alto" = máximo de 09:30→entrada (en cortos, el mínimo). Si
  ese nivel no queda a favor de la entrada, no se opera.
- **V2:** misma entrada, TP fijo a 1:1,5.
- **V3:** como V1, pero la liquidez es el mínimo/máximo de la sesión RTH anterior
  (09:30-15:59) en vez del overnight.

## Pasa a validación si

p < 0,0167, los 3 años positivos, exceso sobre el paseo aleatorio con z > 2 (6 semillas),
invertida ≤ 0. Validación: uso nº9, p < 0,0056.

## Informativo

La misma regla sin la condición del FVG H1 (lo que aporta el filtro), ratios 1:1 y 1:2,
y largos/cortos.

## Adenda (04/10, ANTES de ejecutar estas variantes): segunda parte del vídeo

Daniil pasó el resto del reel. El "mínimo" es un **DOL marcado en H1**: un mínimo de swing
anterior, no el overnight. El ejemplo de 1m es acumulación (A) → manipulación (M) con FVG →
barrida → cierre por encima del FVG (iFVG), y TP en un FVG de 15m lejano (varias R).

Variantes nuevas. Con las 3 anteriores suman **6 en la familia: p < 0,05/6 = 0,0083**.
- **DOL H1:** pivote H1 (mínimo por debajo de las 2 velas anteriores y las 2 siguientes),
  confirmado al cerrar la 2ª vela posterior, con la vela de las 08:00 como última. Tiene que
  seguir sin barrer hasta las 09:29 y estar dentro de las 120 H1 anteriores. Se toma el más
  cercano por debajo de la apertura de las 09:30 (largos) o por encima (cortos). El resto
  igual que V1-V3.
- **V4:** DOL H1 con TP en el siguiente alto · **V5:** DOL H1 a 1:1,5 · **V6:** DOL H1 a 1:3
  (aproxima el TP en el FVG de 15m del ejemplo).

## Adenda 2 (04/10, ANTES de ejecutar): los 6 años, a petición de Daniil

Las reglas son del autor y no se han ajustado con datos, así que se miden las 6 variantes,
sin cambiar nada, sobre 2021-2026 (2026 hasta el 23/09). Esto gasta el **uso nº9 de la
validación** para esta familia.
- Criterio, 6 años juntos: p < 0,0083 (familia de 6), los 6 años con R > 0 en al menos 5,
  invertida ≤ 0 y exceso sobre el paseo aleatorio con z > 2.
- Criterio, solo 2022/24/26: p < 0,0056.

## Adenda 3 (04/10, ANTES de ejecutar): TP a 1:5, como el ejemplo del vídeo ($200 → $1.000)

Misma entrada, TP fijo a 5R, cierre a las 15:59 si no toca nada. Las tres liquidez
(overnight, RTH previo, DOL H1), sobre los 6 años: **V7, V8, V9**. La familia pasa a 9:
**p < 0,05/9 = 0,0056**. Mismos criterios que la adenda 2, con 6 semillas de paseo aleatorio.

## Adenda 4 (04/10, ANTES de ejecutar): TP en puntos estructurales

Daniil aclara que el TP no es un ratio: es "el siguiente alto o el siguiente FVG". Se definen
dos TP estructurales, conocidos en el instante de entrada (solo velas de 15m ya cerradas,
vistas en las ~500 velas de 15m anteriores):
- **TP-FVG15:** límite inferior del FVG bajista de 15m más cercano por encima de la entrada,
  sin tocar desde que nació (en cortos, el espejo).
- **TP-PIV15:** máximo de swing de 15m (por encima de las 2 velas anteriores y las 2
  siguientes, confirmado al cerrar la 2ª) más cercano por encima de la entrada y sin barrer.
Si no hay nivel, no se opera. Se aplican a las entradas overnight (V10, V11) y DOL H1 (V12,
V13), sobre los 6 años. La familia pasa a 13: **p < 0,05/13 = 0,0038**. Mismos criterios.
