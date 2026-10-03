"""NQ Motion Model (Kasen), setup de reversión. Pre-registro 2026-10-03_kasen_nq_motion."""
from __future__ import annotations

import numpy as np
import pandas as pd


def senales(nq: pd.DataFrame, es: pd.DataFrame, exigir_smt: bool = True, min_riesgo_pct: float = 0.0005) -> pd.DataFrame:
    o, h, l, c = (nq[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    eh, el = es["h"].to_numpy(float), es["l"].to_numpy(float)
    hh, ses = nq["hhmm"].to_numpy(), nq["sesion"].to_numpy()
    idx = np.arange(len(nq)); filas = []
    for s in pd.unique(ses):
        m = ses == s; ii, hm = idx[m], hh[m]
        v4 = ii[(hm >= 600) & (hm <= 959)]
        ven = ii[(hm >= 1000) & (hm <= 1300)]
        fin = ii[hm == 1559]
        if len(v4) < 200 or len(ven) < 150 or len(fin) == 0:
            continue
        H, L = h[v4].max(), l[v4].min(); EH, EL = eh[v4].max(), el[v4].min(); mid = (H + L) / 2
        i_fin = fin[0]
        sw = None
        for j in ven:
            arr, abj = h[j] > H, l[j] < L
            if arr and abj:
                break
            if arr or abj:
                prev = ven[ven <= j]
                es_rompe = (eh[prev].max() > EH) if arr else (el[prev].min() < EL)
                if exigir_smt and es_rompe:
                    break
                sw = (j, -1 if arr else 1); break
        if sw is None:
            continue
        js, d = sw
        lim = []  # niveles de FVG a favor de la barrida que, al cruzarse, invierten
        desde = max(v4[0] + 2, js - 30)
        for i in range(desde, js + 1):
            if d == 1 and h[i] < l[i - 2]:
                lim.append(l[i - 2])          # FVG bajista: techo
            if d == -1 and l[i] > h[i - 2]:
                lim.append(h[i - 2])          # FVG alcista: suelo
        for j in ven[ven > js]:
            if lim and ((d == 1 and c[j] > min(lim)) or (d == -1 and c[j] < max(lim))):
                if (d == 1 and c[j] >= mid) or (d == -1 and c[j] <= mid):
                    break                     # fuera de descuento/prima
                tramo = np.arange(ven[0], j + 1)
                stop = l[tramo].min() if d == 1 else h[tramo].max()
                riesgo = (c[j] - stop) * d
                if riesgo >= min_riesgo_pct * c[j] and j + 1 <= i_fin:
                    obj = (H - c[j]) / riesgo if d == 1 else (c[j] - L) / riesgo
                    filas.append({"i_ent": j + 1, "precio": c[j], "dir": d, "riesgo": riesgo, "i_fin": i_fin, "obj_estr": obj})
                break
            if d == 1 and h[j] < l[j - 2]:
                lim.append(l[j - 2])
            if d == -1 and l[j] > h[j - 2]:
                lim.append(h[j - 2])
    return pd.DataFrame(filas)
