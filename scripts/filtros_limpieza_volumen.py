"""Ejecuta preregistros/2026-10-02_filtros_limpieza_volumen_momento.md (DISEÑO)."""
import numpy as np, pandas as pd
from src import loader, motor
from src.motores import momento_generico as MG

def ops_anio(a):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(b, MG.senales(b, 940, 30, 0.40))
    c, v, hh, ses = b.c.to_numpy(), b.v.to_numpy(), b.hhmm.to_numpy(), b.sesion.to_numpy()
    filas = {}
    for s in pd.unique(ses):
        ii = np.flatnonzero(ses == s)
        hm = hh[ii]
        t = ii[(hm >= 909) & (hm <= 939)]
        vv = ii[(hm >= 930) & (hm <= 939)]
        if len(t) != 31 or hh[t[0]] != 909 or len(vv) != 10:
            continue
        mov = np.abs(np.diff(c[t])).sum()
        filas[s] = (abs(c[t[-1]] - c[t[0]]) / mov if mov > 0 else np.nan, v[vv].sum())
    x = pd.DataFrame.from_dict(filas, orient="index", columns=["efic", "vol"]).sort_index()
    # umbral causal: mediana de las 60 sesiones ANTERIORES (shift 1)
    for k in ("efic", "vol"):
        x[k + "_med"] = x[k].shift(1).rolling(60, min_periods=60).median()
    o = o.merge(x, left_on="sesion", right_index=True, how="left")
    return o[(o.sesion.dt.year == a) & o.efic_med.notna() & o.vol_med.notna()]

o = pd.concat([ops_anio(a) for a in (2021, 2023, 2025)], ignore_index=True)
r = motor.r_neta(o, 2.0); wr = lambda z: np.mean(z > 0)
print(f"BASE n={len(r)} R={r.mean():+.3f} wr={wr(r):.1%}")
rng = np.random.default_rng(7)
for nom, m in (("F5 tramo limpio", o.efic > o.efic_med), ("F6 volumen alto", o.vol > o.vol_med)):
    m = m.to_numpy(); rf = r[m]
    p95 = np.percentile([r[rng.choice(len(r), m.sum(), replace=False)].mean() for _ in range(1000)], 95)
    py = pd.Series(rf).groupby(o.sesion.dt.year.to_numpy()[m]).mean().round(3).to_dict()
    ok = rf.mean() > r.mean() and wr(rf) > wr(r) and m.mean() >= 0.35 and rf.mean() > p95
    print(f"{nom}: n={m.sum()} ({m.mean():.0%}) R={rf.mean():+.3f} wr={wr(rf):.1%} | resto R={r[~m].mean():+.3f} | p95 azar {p95:+.3f} | años {py} -> {'PASA' if ok else 'no pasa'}")
for k, nom in (("efic", "eficiencia"), ("vol", "volumen")):
    q = pd.qcut(o[k] / o[k + "_med"], 3, labels=["bajo", "medio", "alto"])
    print(f"  terciles {nom}: " + " · ".join(f"{t} R={r[(q == t).to_numpy()].mean():+.3f} wr={wr(r[(q == t).to_numpy()]):.0%}" for t in ("bajo", "medio", "alto")))
