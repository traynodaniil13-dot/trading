"""Ejecuta preregistros/2026-10-02_smt_nq_es_premisa.md (DISEÑO)."""
import numpy as np, pandas as pd
from scipy import stats
from src import loader

KS = (0.20, 0.30, 0.40)


def eventos(a):
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    idx = nq.index.intersection(es.index)
    nq, es = nq.loc[idx], es.loc[idx]
    h, l, c = (nq[k].to_numpy() for k in ("h", "l", "c"))
    eh, el = es.h.to_numpy(), es.l.to_numpy()
    hh, ses = nq.hhmm.to_numpy(), nq.sesion.to_numpy()
    out = []
    for s in pd.unique(ses):
        if pd.Timestamp(s).year != a:
            continue
        ii = np.flatnonzero(ses == s); hm = hh[ii]
        on, ven, rest = ii[(hm >= 1800) | (hm <= 929)], ii[(hm >= 930) & (hm <= 1100)], ii[(hm >= 930) & (hm <= 1559)]
        if len(on) < 300 or len(ven) < 60:
            continue
        nH, nL, eH, eL = h[on].max(), l[on].min(), eh[on].max(), el[on].min()
        for j in ven:
            arr, abj = h[j] > nH, l[j] < nL
            if arr and abj:
                break
            if arr or abj:
                d = -1 if arr else 1
                prev = ven[ven <= j]
                es_rompe = (eh[prev].max() > eH) if arr else (el[prev].min() < eL)
                tramo = rest[rest > j]
                fila = dict(ses=s, dir=d, smt=not es_rompe)
                for k in KS:
                    b = c[j] * k / 100
                    up = np.flatnonzero(h[tramo] >= c[j] + b); dn = np.flatnonzero(l[tramo] <= c[j] - b)
                    tu = up[0] if up.size else 10**9; td = dn[0] if dn.size else 10**9
                    tf, tc = (tu, td) if d == 1 else (td, tu)
                    fila[k] = 0 if tf == tc == 10**9 else (1 if tf < tc else -1)  # empate -> en contra
                out.append(fila)
                break
    return pd.DataFrame(out)


e = pd.concat([eventos(a) for a in (2021, 2023, 2025)], ignore_index=True)
print(f"eventos: {len(e)} · con SMT {e.smt.sum()} ({e.smt.mean():.0%}) · sin SMT {(~e.smt).sum()}\n")
for k in KS:
    print(f"--- barreras ±{k}% ---")
    for grupo, m in (("SMT", e.smt), ("sin SMT", ~e.smt)):
        x = e[m]
        res = x[x[k] != 0]
        fav = (res[k] == 1).sum(); n = len(res)
        p = stats.binomtest(fav, n, 0.5, alternative="greater").pvalue if n else 1
        por_dir = {("largos" if d == 1 else "cortos"): f"{(res[res.dir == d][k] == 1).mean():.1%} (n={len(res[res.dir == d])})" for d in (1, -1)}
        print(f"  {grupo:8s}: a favor {fav / n:.1%} de {n} resueltas (sin resolver {(x[k] == 0).mean():.0%}) p={p:.3f} · {por_dir}")
