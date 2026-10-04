"""Validación F4 (MOC 15:50). preregistros/2026-10-04_validacion_moc_1550.md"""
import numpy as np, pandas as pd
from scipy import stats
from src import loader
from scripts.lote6_fomc_datos import carrera


def ops(b):
    o, h, l, c = (b[k].to_numpy() for k in ("o", "h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy(); out = []
    for s in pd.unique(ses):
        ii = np.flatnonzero(ses == s); hm = hh[ii]
        a, j, f = ii[hm == 1549], ii[hm == 1552], ii[hm == 1559]
        tr = ii[(hm > 1552) & (hm <= 1559)]
        if not (len(a) and len(j) and len(f)) or len(tr) < 5:
            continue
        j = j[0]; d = np.sign(c[j] - c[a[0]])
        if not d: continue
        res = carrera(h, l, c, j, tr, d, 0.10)
        r = res if res != 0 else (c[f[0]] - c[j]) * d / (c[j] * 0.001)
        out.append(dict(anio=pd.Timestamp(s).year, d=d, res=res, r=r, riesgo=c[j] * 0.001))
    return pd.DataFrame(out)


def informe(nom, o):
    g = o[o.res != 0]; n = len(g); a = (g.res == 1).sum()
    p = stats.binomtest(a, n, alternative="greater").pvalue
    print(f"\n=== {nom}: n={n} (de {len(o)} días) · a favor {a/n:.1%} · p1c={p:.4f}")
    print(f"  largos {(g[g.d==1].res==1).mean():.1%} · cortos {(g[g.d==-1].res==1).mean():.1%} · años " +
          " · ".join(f"{y} {(x.res==1).mean():.1%} (n={len(x)})" for y, x in g.groupby('anio')))
    for k in (1, 2):
        rn = o.r - k * 0.87 / o.riesgo
        print(f"  como estrategia 1:1, coste ×{k}: R neta {rn.mean():+.4f} (riesgo mediano {o.riesgo.median():.1f} pts)")
    return p, g


if __name__ == "__main__":
    V = [o.assign(anio=o.anio) for o in (ops(loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)) for a in (2022, 2024, 2026))]
    o = pd.concat(V); o = o[o.anio.isin([2022, 2024, 2026])]
    p, g = informe("VALIDACIÓN CFD 2022/24/26 (umbral p < 0,005)", o)
    por = g.groupby("anio").apply(lambda x: (x.res == 1).mean())
    ok = p < 0.005 and (por > 0.5).all() and (g[g.d == 1].res == 1).mean() > 0.5 and (g[g.d == -1].res == 1).mean() > 0.5
    print("  ->", "PASA" if ok else "NO PASA")
    nq = loader.cargar(verbose=False); onq = ops(nq); onq = onq[onq.anio.isin([2023, 2024, 2025])]
    informe("Informativo · NQ futuro real 2023-25", onq)
