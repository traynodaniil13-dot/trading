"""Rango de la 1ª vela de 5 min + FVG 1m fuera del rango + retroceso + envolvente
(pre-registro 2026-10-03_primera_vela_5m_fvg)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def senales(b: pd.DataFrame, min_riesgo_pct: float = 0.0005) -> pd.DataFrame:
    o, h, l, c = (b[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    hh, ses = b["hhmm"].to_numpy(), b["sesion"].to_numpy()
    idx = np.arange(len(b)); filas = []
    for s in pd.unique(ses):
        m = ses == s; ii, hm = idx[m], hh[m]
        r5 = ii[(hm >= 930) & (hm <= 934)]
        ven = ii[(hm >= 935) & (hm <= 1159)]
        fin = ii[hm == 1559]
        if len(r5) != 5 or len(ven) < 100 or len(fin) == 0:
            continue
        H, L, i_fin = h[r5].max(), l[r5].min(), fin[0]
        # 1) primer FVG fuera del rango (i desde 09:37 hasta 11:00)
        sel = None
        for i in ven:
            if hh[i] > 1100:
                break
            if i - 2 < r5[-1] + 1:
                continue
            if l[i] > h[i - 2] and c[i] > H:
                sel = (i, 1, h[i - 2], l[i]); break       # zona [suelo, techo]
            if h[i] < l[i - 2] and c[i] < L:
                sel = (i, -1, h[i], l[i - 2]); break
        if sel is None:
            continue
        i, d, suelo, techo = sel
        # 2) retroceso a la zona, 3) envolvente
        t = None
        for j in ven[ven > i]:
            if (d == 1 and c[j] < suelo) or (d == -1 and c[j] > techo):
                break                                        # zona invalidada
            if t is None and ((d == 1 and l[j] <= techo) or (d == -1 and h[j] >= suelo)):
                t = j
            if t is not None and j > t - 0 and j - 1 >= t - 1:
                prev = j - 1
                env = (c[j] > o[j] and o[prev] > c[prev] and c[j] >= o[prev] and o[j] <= c[prev]) if d == 1 else \
                      (c[j] < o[j] and o[prev] < c[prev] and c[j] <= o[prev] and o[j] >= c[prev])
                if env and j >= t:
                    tramo = np.arange(t, j + 1)
                    stop = l[tramo].min() if d == 1 else h[tramo].max()
                    riesgo = (c[j] - stop) * d
                    if riesgo >= min_riesgo_pct * c[j] and j + 1 <= i_fin:
                        filas.append({"i_ent": j + 1, "precio": c[j], "dir": d, "riesgo": riesgo, "i_fin": i_fin})
                    break
    return pd.DataFrame(filas)
