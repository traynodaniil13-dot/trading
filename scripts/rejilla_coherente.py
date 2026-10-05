"""Rejilla coherente: diseño en impares (2019/21/23/25), validación en pares (2020/22/24/26).
preregistros/2026-10-05_rejilla_coherente_impares_pares.md"""
import itertools
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy import stats
from src import loader, motor
from src.motores import momento_generico as MG

TS = [h * 100 + m for h in range(9, 16) for m in range(0, 60, 5) if 935 <= h * 100 + m <= 1500]
LS = [5, 10, 15, 30, 60, 120]; KS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]; RAT = [1.0, 1.5, 2.0, 3.0]
DIS, VAL = (2019, 2021, 2023, 2025), (2020, 2022, 2024, 2026)
B = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in DIS + VAL}


def celda(args):
    T, L, k = args
    out = {}
    for a, b in B.items():
        o = motor.simular(b, MG.senales(b, T, L, k)); o = o[o.sesion.dt.year == a]
        out[a] = dict(ses=o.sesion.to_numpy(),
                      mom=np.array([motor.r_neta(o, r) for r in RAT], dtype=np.float32),
                      rev=np.array([motor.r_neta(o, r, True) for r in RAT], dtype=np.float32))
    return (T, L, k), out


if __name__ == "__main__":
    with Pool(3) as p:
        res = dict(p.map(celda, list(itertools.product(TS, LS, KS)), chunksize=8))
    # tabla de reglas
    filas = []
    for (T, L, k), out in res.items():
        for modo in ("mom", "rev"):
            for ir, rt in enumerate(RAT):
                rd = {a: out[a][modo][ir] for a in DIS}; rv = {a: out[a][modo][ir] for a in VAL}
                xd = np.concatenate(list(rd.values())); xv = np.concatenate(list(rv.values()))
                filas.append(dict(T=T, L=L, k=k, modo=modo, ratio=rt, n_dis=len(xd), R_dis=xd.mean(),
                                  anios_dis=sum(v.mean() > 0 for v in rd.values()), min_dis=min(v.mean() for v in rd.values()),
                                  n_val=len(xv), R_val=xv.mean(), anios_val=sum(v.mean() > 0 for v in rv.values()),
                                  p_val=stats.ttest_1samp(xv, 0, alternative="greater").pvalue))
    t = pd.DataFrame(filas)
    # meseta
    clave = {(r.T, r.L, r.k, r.modo, r.ratio): r.R_dis for r in t.itertuples()}
    def meseta(r):
        iT, iL, ik = TS.index(r.T), LS.index(r.L), KS.index(r.k); vec = []
        for dT, dL, dk in ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)):
            a, b, c = iT + dT, iL + dL, ik + dk
            if 0 <= a < len(TS) and 0 <= b < len(LS) and 0 <= c < len(KS):
                vec.append(clave[(TS[a], LS[b], KS[c], r.modo, r.ratio)] > 0)
        return np.mean(vec) if vec else 0
    t["meseta"] = [meseta(r) for r in t.itertuples()]
    # placebo de dirección de la rejilla entera en diseño (mismo sorteo por sesión)
    rng = np.random.default_rng(0)
    ses_all = np.unique(np.concatenate([out[a]["ses"] for out in res.values() for a in DIS]))
    REPS = 200; F = rng.random((REPS, len(ses_all))) < 0.5
    maxs = np.full(REPS, -np.inf)
    for (T, L, k), out in res.items():
        ses = np.concatenate([out[a]["ses"] for a in DIS]); ix = np.searchsorted(ses_all, ses)
        f = F[:, ix]; n = len(ix)
        for ir in range(len(RAT)):
            m = np.concatenate([out[a]["mom"][ir] for a in DIS]); r_ = np.concatenate([out[a]["rev"][ir] for a in DIS])
            s_mom = (np.where(f, r_, m)).sum(axis=1) / n      # momento con dirección sorteada
            s_rev = (np.where(f, m, r_)).sum(axis=1) / n      # reversión con dirección sorteada
            maxs = np.maximum(maxs, np.maximum(s_mom, s_rev))
    p95 = np.percentile(maxs, 95)
    t.to_csv("resultados/2026-10-05_rejilla_coherente.csv", index=False)
    pd.set_option("display.width", 250)
    print(f"reglas {len(t):,} · placebo (máximo de la rejilla, 200 reps): media {maxs.mean():+.4f} · p95 {p95:+.4f}")
    c1 = t[(t.anios_dis == 4)]; c12 = c1[c1.meseta >= 0.75]; c123 = c12[c12.n_dis >= 400]; c1234 = c123[c123.R_dis > p95]
    print(f"4/4 años de diseño: {len(c1):,} ({len(c1)/len(t):.1%}; azar puro ~6%) · + meseta: {len(c12):,} · + n≥400: {len(c123):,} · + > p95 del placebo: {len(c1234):,}")
    print("\nMejores coherentes por R mínima anual (1-3, informativo):")
    print(c123.sort_values("min_dis", ascending=False).head(15)[["T", "L", "k", "modo", "ratio", "n_dis", "R_dis", "min_dis", "meseta"]].round(3).to_string(index=False))
    if len(c1234) == 0:
        print("\nNinguna supera el p95 del placebo de la rejilla → NO se gasta la validación. Rejilla cerrada.")
    else:
        fin = c1234.sort_values("min_dis", ascending=False).head(10).copy(); kf = len(fin)
        fin["PASA"] = (fin.p_val < 0.05 / kf) & (fin.anios_val >= 3)
        print(f"\n{kf} FINALISTAS → VALIDACIÓN años pares (umbral p < {0.05/kf:.4f} y ≥3/4 años):")
        print(fin[["T", "L", "k", "modo", "ratio", "n_dis", "R_dis", "min_dis", "meseta", "n_val", "R_val", "anios_val", "p_val", "PASA"]].round(4).to_string(index=False))
        print(f"\nInformativo: corr(R diseño, R validación) en las 4/4+meseta: {c12.R_dis.corr(c12.R_val):+.2f} · todas: {t.R_dis.corr(t.R_val):+.2f}")
