"""Lote 6: FOMC, días de dato y volatilidad previa. preregistros/2026-10-04_lote6_fomc_datos_volatilidad.md"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader

FOMC = {  # día del comunicado (14:00 NY). De memoria, calendario público de la Fed.
    2021: ["2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15"],
    2023: ["2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13"],
    2025: ["2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10"],
}
FOMC_D = {pd.Timestamp(x) for v in FOMC.values() for x in v}


def carrera(h, l, c, j, tramo, d, k):
    b = c[j] * k / 100
    up = np.flatnonzero(h[tramo] >= c[j] + b); dn = np.flatnonzero(l[tramo] <= c[j] - b)
    tu = up[0] if up.size else 10**9; td = dn[0] if dn.size else 10**9
    tf, tc = (tu, td) if d == 1 else (td, tu)
    return 0 if tf == tc == 10**9 else (1 if tf < tc else -1)


def eventos(b, anio):
    o, h, l, c = (b[k].to_numpy() for k in ("o", "h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    F1, filas = [], []
    prev = None; rangos = []
    for s in pd.unique(ses):
        ii = np.flatnonzero(ses == s); hm = hh[ii]
        en = lambda t: ii[hm == t]
        rth = ii[(hm >= 930) & (hm <= 1559)]
        dia = pd.Timestamp(s).normalize()
        ok = len(rth) >= 300 and dia.year == anio
        if ok and prev is not None and len(en(1359)):
            F1.append(dict(fomc=dia in FOMC_D, ret=(c[en(1359)[0]] / prev["c1359"] - 1) * 100, anio=anio))
        hasta = lambda t: ii[(hm > t) & (hm <= 1559)]
        if ok:
            # F2
            if dia in FOMC_D and len(en(1400)) and len(en(1414)):
                j = en(1414)[0]; d = np.sign(c[j] - o[en(1400)[0]])
                if d: filas.append(dict(p="F2", d=d, k=0.40, res=carrera(h, l, c, j, hasta(1414), d, 0.40)))
            # F3
            pre = ii[(hm >= 820) & (hm <= 829)]
            if len(en(830)) and len(pre) == 10 and len(en(929)):
                j830 = en(830)[0]
                if h[j830] - l[j830] > 3 * np.median(h[pre] - l[pre]):
                    j = en(929)[0]; d = -np.sign(c[j] - o[j830])
                    if d:
                        for k in (0.25, 0.40):
                            filas.append(dict(p=f"F3 ±{k}", d=d, k=k, res=carrera(h, l, c, j, hasta(929), d, k)))
            # F4
            if len(en(1549)) and len(en(1552)):
                j = en(1552)[0]; d = np.sign(c[j] - c[en(1549)[0]])
                if d: filas.append(dict(p="F4", d=d, k=0.10, res=carrera(h, l, c, j, hasta(1552), d, 0.10)))
            # F5
            if prev is not None and len(rangos) >= 20 and prev["rango"] > 2 * np.median(rangos[-21:-1]) and len(en(930)) and len(en(959)):
                j = en(959)[0]; d = np.sign(c[j] - o[en(930)[0]])
                if d: filas.append(dict(p="F5", d=d, k=0.40, res=carrera(h, l, c, j, hasta(959), d, 0.40)))
        if len(rth) >= 300:
            rg = h[rth].max() - l[rth].min(); rangos.append(rg)
            prev = dict(c1359=c[en(1359)[0]] if len(en(1359)) else c[rth[-1]], rango=rg)
    fl = pd.DataFrame(filas); fl["anio"] = anio
    return pd.DataFrame(F1), fl


def tabla(fl):
    out = {}
    for p, g in fl.groupby("p"):
        g = g[g.res != 0]; n = len(g); a = (g.res == 1).sum()
        out[p] = dict(n=n, pct=a / max(n, 1), p=stats.binomtest(a, n).pvalue if n else np.nan,
                      largos=(g[g.d == 1].res == 1).mean(), cortos=(g[g.d == -1].res == 1).mean(),
                      anios={y: round((x.res == 1).mean(), 3) for y, x in g.groupby("anio")})
    return out


if __name__ == "__main__":
    A = (2021, 2023, 2025)
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in A}
    R = [eventos(D[a], a) for a in A]
    f1 = pd.concat([r[0] for r in R]); fl = pd.concat([r[1] for r in R])
    x, y = f1[f1.fomc].ret, f1[~f1.fomc].ret
    t, p2 = stats.ttest_ind(x, y, equal_var=False)
    print(f"F1 deriva pre-FOMC (13:59 previa → 13:59 FOMC): FOMC n={len(x)} media {x.mean():+.3f}% (sd {x.std():.2f}) · resto n={len(y)} media {y.mean():+.3f}%")
    print(f"   diferencia {x.mean()-y.mean():+.3f}% · p1c={p2/2 if t>0 else 1-p2/2:.4f} · positivas {(x>0).mean():.0%} · por año {f1[f1.fomc].groupby('anio').ret.mean().round(3).to_dict()}")
    print(f"   en puntos NQ ~20.000: {x.mean()*200:+.0f} pts por evento")
    nul = {}
    for sem in range(6):
        Rn = [eventos(C.paseo_aleatorio(D[a], 9000 * a + sem), a)[1] for a in A]
        for p, v in tabla(pd.concat(Rn)).items():
            nul.setdefault(p, []).append(v["pct"])
    print("\nCarreras (a favor de la señal, % sin contar empates):")
    for p, v in tabla(fl).items():
        print(f"  {p}: n={v['n']} a favor {v['pct']:.1%} p={v['p']:.4f} · largos {v['largos']:.1%} cortos {v['cortos']:.1%} · años {v['anios']} · paseo {np.mean(nul[p]):.1%} [{min(nul[p]):.1%}-{max(nul[p]):.1%}]")
