# Pre-registro · Ruptura de PDH/PDL con cierre de 15m + retesteo con patrón de vela en 5m · 04/10/2026

Escrito ANTES de ejecutar. Fuente: vídeo youtube tEEv7-nGL98 (resumen pasado por Daniil).
Es una idea de CONTINUACIÓN (ruptura + retesteo), no de barrida y giro.

## Reglas del autor
1. Diario: máximo (PDH) y mínimo (PDL) del día anterior.
2. 15m: una vela cierra por encima del PDH → largos; por debajo del PDL → cortos.
3. 5m: el precio vuelve al nivel roto y en el nivel aparece uno de estos 4 patrones: martillo /
   envolvente alcista (largos), estrella fugaz / envolvente bajista (cortos). Sin patrón, no
   hay operación.
   - Martillo: orden stop en su máximo, SL bajo su mínimo. Estrella: espejo.
   - Envolvente: orden stop en el máximo de la vela previa, SL bajo el mínimo de la
     envolvente. Bajista: espejo.
4. TP a 2R o 3R. Primeras 2-2,5 h tras la apertura de NY.

## Mecánica (CFD NQ, hora NY)
- **Nivel:** V-SES = máx/mín de la sesión anterior (18:00-16:15, la vela diaria del futuro) o
  V-RTH = máx/mín del RTH anterior (09:30-15:59).
- **Ruptura:** la primera vela de 15m (alineada desde las 09:30) entre 09:30 y 11:45 que cierra
  fuera del nivel, con la vela de 15m anterior cerrando dentro (cruce real). La vela de 09:30
  cuenta si el cierre de las 09:29 estaba dentro. Solo la primera ruptura del día.
- **Retesteo y patrón:** desde el cierre de la vela de ruptura, velas de 5m (alineadas desde las
  09:30) que cierren hasta las 12:00. Una vela "toca" el nivel si su mínimo ≤ PDH (largos) o su
  máximo ≥ PDL (cortos).
  - Martillo: rango > 0, mecha inferior ≥ 60% del rango y mecha superior ≤ 30%, tocando el
    nivel.
  - Envolvente alcista: la previa bajista (c<o), la actual alcista con o ≤ c_previa y
    c ≥ o_previa; alguna de las dos toca el nivel.
  - Estrella fugaz y envolvente bajista: espejo.
  - Vale el primer patrón válido tras la ruptura.
- **Orden stop:** viva desde el cierre del patrón hasta las 12:30. Relleno al CIERRE de la
  primera barra M1 que toca el nivel de entrada, y esa barra no se evalúa (regla 3). Se
  cancela si antes del relleno el precio toca el SL. R medida desde el relleno real.
  Stop mínimo 0,05% del precio.
- **TP** a 2R o 3R. Cierre forzado a las 15:59. Coste 0,87 pts. Una operación al día.

## Variantes (4) → p < 0,05/4 = 0,0125 (una cola)
V-SES 1:2 · V-SES 1:3 · V-RTH 1:2 · V-RTH 1:3.

## Criterios
- **Diseño 2021/23/25:** p < 0,0125, los 3 años positivos, exceso sobre el paseo aleatorio con
  z > 2 (6 semillas), invertida ≤ 0.
- **Después, los 6 años** (a petición de Daniil, reglas del autor sin tocar): es el **uso nº12**,
  2022/24/26 solos con p < 0,05/12 = 0,0042.
- Informativo: 1:1, por tipo de patrón, largos/cortos, % de días con ruptura / patrón /
  relleno.
