"""Barrida del overnight + IFVG en 09:30-10:10 (pre-registro 2026-10-02_sweep_ifvg_fede)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def senales(b: pd.DataFrame, min_riesgo_pct: float = 0.0005) -> pd.DataFrame:
    h, l, c = (b[k].to_numpy(float) for k in ("h", "l", "c"))
    hh, ses = b["hhmm"].to_numpy(), b["sesion"].to_numpy()
    idx = np.arange(len(b))
    filas = []
    for s in pd.unique(ses):
        m = ses == s
        ii, hm = idx[m], hh[m]
        on = ii[(hm >= 1800) | (hm <= 929)]
        ven = ii[(hm >= 930) & (hm <= 1010)]
        fin = ii[hm == 1059]
        base = ii[(hm >= 920) & (hm <= 1010)]
        if len(on) < 300 or len(ven) < 30 or len(fin) == 0 or len(base) < 3:
            continue
        onH, onL, i_fin = h[on].max(), l[on].min(), fin[0]
        arriba, abajo = h[ven] > onH, l[ven] < onL
        k = np.flatnonzero(arriba | abajo)
        if k.size == 0 or (arriba[k[0]] and abajo[k[0]]):
            continue
        j_sw = ven[k[0]]
        d = -1 if arriba[k[0]] else 1
        b0 = base[0]
        hecho = False
        for j in ven[ven > j_sw]:
            # FVG nacidos en barras i (b0+2 <= i < j), a favor de la barrida
            for i in range(max(b0 + 2, j - 60), j):
                if d == -1 and l[i] > h[i - 2] and c[j] < h[i - 2]:      # FVG alcista invertido -> corto
                    hecho = True; break
                if d == 1 and h[i] < l[i - 2] and c[j] > l[i - 2]:       # FVG bajista invertido -> largo
                    hecho = True; break
            if hecho:
                tramo = np.arange(ven[0], j + 1)
                stop = h[tramo].max() if d == -1 else l[tramo].min()
                riesgo = (stop - c[j]) if d == -1 else (c[j] - stop)
                if riesgo >= min_riesgo_pct * c[j] and j + 1 <= i_fin:
                    filas.append({"i_ent": j + 1, "precio": c[j], "dir": d, "riesgo": riesgo, "i_fin": i_fin})
                break
    return pd.DataFrame(filas)
