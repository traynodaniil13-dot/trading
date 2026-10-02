"""DOL por FVG de 15 min + retroceso + IFVG de 1 min (pre-registro 2026-10-02_aleix_dol_fvg_ifvg).

Instantes de conocimiento:
- Vela de 15 min = barras M1 de la sesión agrupadas por (minuto de sesión)//15.
  Se conoce en la primera barra M1 de un cubo posterior (sin label de resample, bug nº4).
- FVG de 15 min nace al cerrar su tercera vela; invalidación = cierre de 15 min
  posterior al otro lado de la zona.
- FVG de 1 min nace al cerrar la barra i; la inversión es el cierre de la barra j > i.
  Entrada al cierre de j -> i_ent = j+1, precio = c[j] (regla 3).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def senales(b: pd.DataFrame, min_riesgo_pct: float = 0.0005) -> pd.DataFrame:
    h, l, c = (b[k].to_numpy(float) for k in ("h", "l", "c"))
    hh, ses = b["hhmm"].to_numpy(), b["sesion"].to_numpy()
    mins = (b.index.hour * 60 + b.index.minute).to_numpy()
    cubo_all = ((mins - 1080) % 1440) // 15          # 18:00 -> cubo 0
    idx = np.arange(len(b))
    CUBO_0930 = ((570 - 1080) % 1440) // 15            # 62
    filas = []
    for s in pd.unique(ses):
        m = ses == s
        ii, hm, cu = idx[m], hh[m], cubo_all[m]
        if len(ii) < 600:
            continue
        # velas de 15 min cerradas antes de las 09:30 (bug nº6: todo dentro de la sesión)
        cub = np.unique(cu[cu < CUBO_0930])
        if len(cub) < 3:
            continue
        H = np.array([h[ii[cu == q]].max() for q in cub])
        L = np.array([l[ii[cu == q]].min() for q in cub])
        C = np.array([c[ii[cu == q][-1]] for q in cub])
        zonas = []  # (dir, suelo, techo, k_nacimiento)
        for k in range(len(cub)):
            # primero invalida con el cierre de k las zonas ya vivas, luego añade la nueva
            zonas = [z for z in zonas if not ((z[0] == 1 and C[k] < z[1]) or (z[0] == -1 and C[k] > z[2]))]
            if k >= 2 and L[k] > H[k - 2]:
                zonas.append((1, H[k - 2], L[k], k))
            elif k >= 2 and H[k] < L[k - 2]:
                zonas.append((-1, H[k], L[k - 2], k))
        if not zonas:
            continue
        d, suelo, techo, _ = zonas[-1]
        ven = ii[(hm >= 930) & (hm <= 1059)]
        fin = ii[hm == 1159]
        if len(ven) < 60 or len(fin) == 0:
            continue
        i_fin = fin[0]
        # retroceso: primera barra que toca la zona; antes, revalidar con cada 15 min cerrado
        t = None
        cub_vistos = set(cub)
        for j in ven:
            q_act = cubo_all[j]
            for q in sorted(set(cu[(cu < q_act) & (cu >= CUBO_0930)]) - cub_vistos):
                cub_vistos.add(q)
                cq = c[ii[cu == q][-1]]
                if (d == 1 and cq < suelo) or (d == -1 and cq > techo):
                    t = -1
                    break
            if t == -1:
                break
            if (d == 1 and l[j] <= techo) or (d == -1 and h[j] >= suelo):
                t = j
                break
        if t is None or t == -1:
            continue
        # IFVG de 1 min en contra del sesgo, nacido en i >= t, invertido por cierre a favor
        fvgs = []
        for j in ven[ven > t]:
            if any((d == 1 and c[j] > lim) or (d == -1 and c[j] < lim) for lim in fvgs):
                tramo = np.arange(t, j + 1)
                stop = l[tramo].min() if d == 1 else h[tramo].max()
                riesgo = (c[j] - stop) * d
                if riesgo >= min_riesgo_pct * c[j] and j + 1 <= i_fin:
                    filas.append({"i_ent": j + 1, "precio": c[j], "dir": d, "riesgo": riesgo, "i_fin": i_fin})
                break
            # FVG que nace al cerrar j (se usa desde la barra siguiente)
            if j - 2 >= t:
                if d == 1 and h[j] < l[j - 2]:
                    fvgs.append(l[j - 2])       # techo del FVG bajista
                elif d == -1 and l[j] > h[j - 2]:
                    fvgs.append(h[j - 2])       # suelo del FVG alcista
    return pd.DataFrame(filas)
