"""Noise Area (Zarattini, Aziz, Barbon 2024). Pre-registro: preregistros/2026-10-01_noise_area.md

Instantes: P(T) = cierre de la barra T−1, conocido en T. σ usa solo sesiones
anteriores. Entrada a mercado en la apertura de la barra T.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CONTROLES = [1000, 1030, 1100, 1130, 1200, 1230, 1300, 1330, 1400, 1430, 1500, 1530]


def _menos1(t):
    m = (t // 100) * 60 + t % 100 - 1
    return (m // 60) * 100 + m % 60


def tabla(b: pd.DataFrame, n_dias: int = 14) -> pd.DataFrame:
    """Una fila por sesión con índices de barras y la señal (si la hay)."""
    mins = [930, 1559] + CONTROLES + [_menos1(t) for t in CONTROLES]
    m = b["hhmm"].isin(mins).to_numpy()
    pos = pd.DataFrame({"ses": b["sesion"].to_numpy()[m], "hh": b["hhmm"].to_numpy()[m], "i": np.flatnonzero(m)})
    tab = pos.pivot_table(index="ses", columns="hh", values="i", aggfunc="first").reindex(columns=mins).dropna().astype(int)
    tab = tab.sort_index()
    o, c = b["o"].to_numpy(float), b["c"].to_numpy(float)
    o930 = o[tab[930].to_numpy()]
    pc = np.r_[np.nan, c[tab[1559].to_numpy()][:-1]]
    P = np.column_stack([c[tab[_menos1(t)].to_numpy()] for t in CONTROLES])
    mov = np.abs(P / o930[:, None] - 1)
    n = len(tab)
    sig = np.full_like(mov, np.nan)
    for k in range(n):
        if k - n_dias >= 0:
            assert k - n_dias >= 0
            sig[k] = mov[k - n_dias:k].mean(axis=0)
    ub = np.maximum(o930, pc)[:, None] * (1 + sig)
    lb = np.minimum(o930, pc)[:, None] * (1 - sig)
    filas = []
    for k in range(n):
        if np.isnan(pc[k]) or np.isnan(sig[k]).any():
            continue
        arriba, abajo = P[k] > ub[k], P[k] < lb[k]
        cual = np.flatnonzero(arriba | abajo)
        if cual.size == 0:
            continue
        j = cual[0]
        d = 1 if arriba[j] else -1
        i_ent = int(tab.iloc[k][CONTROLES[j]])
        assert int(tab.iloc[k][_menos1(CONTROLES[j])]) + 1 == i_ent
        # salida NA-autor: primer control posterior con P al otro lado de su banda
        i_sal = int(tab.iloc[k][1559]); sal_open = False
        for jj in range(j + 1, len(CONTROLES)):
            if (d == 1 and P[k, jj] < ub[k, jj]) or (d == -1 and P[k, jj] > lb[k, jj]):
                i_sal = int(tab.iloc[k][CONTROLES[jj]]); sal_open = True; break
        filas.append(dict(ses=tab.index[k], i_ent=i_ent, dir=d, precio=o[i_ent], i_fin=int(tab.iloc[k][1559]),
                          base=max(o930[k], pc[k]) if d == 1 else min(o930[k], pc[k]),
                          i_sal=i_sal, sal_open=sal_open, control=CONTROLES[j]))
    return pd.DataFrame(filas)
