"""Momento/reversión a hora fija (rejilla del pre-registro 2026-09-27).

- P(T) = cierre de la barra T−1 (conocido en T). P(T−L) = cierre de la barra
  T−L−1. Misma sesión; la referencia puede ser pre-RTH.
- dir = signo(P(T) − P(T−L)) (momento). La reversión es la invertida del motor.
- Entrada: apertura de la barra T. Stop = k% del precio de entrada. Salida 15:59.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _menos(hhmm: int, minutos: int) -> int:
    t = (hhmm // 100) * 60 + hhmm % 100 - minutos
    assert t >= 0
    return (t // 60) * 100 + t % 60


def senales(b: pd.DataFrame, T: int, L: int, k_pct: float, salida: int = 1559) -> pd.DataFrame:
    t_sen, t_ref = _menos(T, 1), _menos(T, L + 1)
    mins = [t_ref, t_sen, T, salida]
    assert t_ref < t_sen < T <= salida < 1700
    sub = b[b["hhmm"].isin(mins)]
    pos = pd.DataFrame({"ses": sub["sesion"].to_numpy(), "hh": sub["hhmm"].to_numpy(),
                        "i": np.flatnonzero(b["hhmm"].isin(mins).to_numpy())})
    tab = pos.pivot_table(index="ses", columns="hh", values="i", aggfunc="first").reindex(columns=mins).dropna().astype(int)
    i_ref, i_sen, i_ent, i_fin = (tab[m].to_numpy() for m in mins)
    assert (i_ref < i_sen).all() and (i_sen + 1 == i_ent).all() and (i_ent <= i_fin).all()
    c, o = b["c"].to_numpy(float), b["o"].to_numpy(float)
    d = np.sign(c[i_sen] - c[i_ref]).astype(int)
    ok = d != 0
    precio = o[i_ent[ok]]
    return pd.DataFrame({"i_ent": i_ent[ok], "precio": precio, "dir": d[ok],
                         "riesgo": precio * k_pct / 100, "i_fin": i_fin[ok]})
