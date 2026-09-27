"""RTP (Jacko), la versión medida en CLAUDE.md sección 7.

Reglas:
- Caja: barras 06:00-08:59 NY de la sesión. Máx/mín conocidos al cierre de la
  barra 08:59 (= 09:00).
- Barrido: primera barra desde las 09:00 cuyo h > máx caja (-> corto) o l < mín
  caja (-> largo). Si una misma barra barre los dos lados, se descarta el día.
- Entrada: limit al 50% de la caja, colocada al cierre de la barra de barrido.
  Relleno al CIERRE de la primera barra posterior que toca el 50% (regla 3); esa
  barra no se evalúa. R desde ese cierre (regla 4).
- Stop: extremo barrido = máximo (corto) / mínimo (largo) desde las 09:00 hasta
  la barra de relleno incluida, conocido al cierre de esa barra. Se revalida en
  el relleno (regla 5): si el cierre ya está más allá del stop, no hay operación.
- Cierre: barra 11:59 (= 12:00) a mercado. Sin relleno antes, no hay operación.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def senales(barras: pd.DataFrame, caja=(600, 859), desde=900, hasta=1159, frac=0.5) -> pd.DataFrame:
    h, l, c = (barras[k].to_numpy(float) for k in ("h", "l", "c"))
    hhmm = barras["hhmm"].to_numpy()
    ses = barras["sesion"].to_numpy()
    idx = np.arange(len(barras))
    ventana = (hhmm >= caja[0]) & (hhmm <= hasta)  # dos cotas (bug nº6)
    filas = []
    df = pd.DataFrame({"ses": ses[ventana], "i": idx[ventana], "hh": hhmm[ventana]})
    for s, g in df.groupby("ses", sort=True):
        ii, hh = g["i"].to_numpy(), g["hh"].to_numpy()
        enc = ii[(hh >= caja[0]) & (hh <= caja[1])]
        post = ii[(hh >= desde) & (hh <= hasta)]
        if len(enc) < 150 or len(post) < 2 or hh[-1] != hasta:
            continue
        assert enc[-1] < post[0]
        top, bot = h[enc].max(), l[enc].min()
        mid = bot + frac * (top - bot)
        arriba = h[post] > top
        abajo = l[post] < bot
        cual = np.flatnonzero(arriba | abajo)
        if cual.size == 0:
            continue
        k = cual[0]
        if arriba[k] and abajo[k]:
            continue
        d = -1 if arriba[k] else 1
        # relleno: primera barra POSTERIOR al barrido que toca el 50%
        resto = post[k + 1:]
        if resto.size == 0:
            continue
        toca = np.flatnonzero(l[resto] <= mid) if d == -1 else np.flatnonzero(h[resto] >= mid)
        if toca.size == 0:
            continue
        i_rell = resto[toca[0]]
        if i_rell >= post[-1]:  # hace falta al menos una barra viva después
            continue
        precio = c[i_rell]
        tramo = np.arange(post[0], i_rell + 1)
        stop = h[tramo].max() if d == -1 else l[tramo].min()
        riesgo = stop - precio if d == -1 else precio - stop
        if riesgo <= 0:
            continue
        filas.append({"i_ent": i_rell + 1, "precio": precio, "dir": d, "riesgo": riesgo,
                      "i_fin": post[-1], "caja": top - bot, "i_barrido": post[k], "mid": mid})
    return pd.DataFrame(filas)
