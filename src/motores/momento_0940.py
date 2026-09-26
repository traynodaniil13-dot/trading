"""MOMENTO 09:40 NY (CLAUDE.md sección 7).

Instantes de conocimiento (índice = inicio de vela):
- "precio de las 09:40" = cierre de la barra 09:40, conocido a las 09:41.
- "precio de las 09:10" = cierre de la barra 09:10, conocido a las 09:11.
- Entrada a mercado en la apertura de la barra 09:41 (i_ent = esa barra).
- Salida: cierre de la barra 15:59 (= 16:00) si no toca nada.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def senales(barras: pd.DataFrame, t_señal: int = 940, t_ref: int = 910, stop: float = 30.0,
            t_salida: int = 1559) -> pd.DataFrame:
    hhmm = barras["hhmm"].to_numpy()
    ses = barras["sesion"].to_numpy()
    c, o = barras["c"].to_numpy(float), barras["o"].to_numpy(float)
    pos = pd.DataFrame({"ses": ses, "hhmm": hhmm, "i": np.arange(len(barras))})
    # Solo RTH del día de la sesión: las dos cotas (bug nº6).
    rth = pos[(pos.hhmm >= 930) & (pos.hhmm <= 1600)]
    tabla = rth.pivot_table(index="ses", columns="hhmm", values="i", aggfunc="first")
    ent_t = t_señal + 1 if (t_señal + 1) % 100 < 60 else t_señal + 41
    necesarias = [t_ref, t_señal, ent_t, t_salida]
    if t_ref < 930:  # la referencia puede caer antes de RTH, misma sesión
        pre = pos[(pos.hhmm == t_ref)].set_index("ses")["i"]
        tabla[t_ref] = pre.reindex(tabla.index)
    tabla = tabla[necesarias].dropna().astype(int)
    i_ref, i_sen, i_ent, i_fin = (tabla[t].to_numpy() for t in necesarias)
    assert (i_ref < i_sen).all() and (i_sen < i_ent).all() and (i_ent <= i_fin).all()
    assert (i_ent == i_sen + 1).all()  # barra de entrada contigua a la de la señal
    d = np.sign(c[i_sen] - c[i_ref]).astype(int)
    ok = d != 0
    return pd.DataFrame({"i_ent": i_ent[ok], "precio": o[i_ent[ok]], "dir": d[ok],
                         "riesgo": stop, "i_fin": i_fin[ok]})
