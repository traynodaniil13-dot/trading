"""Mina NQ tanda 4 (impares → pares). preregistros/2026-10-05_mina_nq_tanda4.md"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina

COSTE = 0.87
IMPARES, PARES = (2019, 2021, 2023, 2025), (2020, 2022, 2024, 2026)


def _dias(df):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    idx = np.arange(len(df))
    for s in pd.unique(ses):
        ii = idx[ses == s]; t = hm[ii]
        yield s, ii, t, o, h, l, c


def u1(N, k):
    def fn(df):
        filas, hist = [], []   # hist: (máx, mín) RTH de cada sesión ya cerrada
        for s, ii, t, o, h, l, c in _dias(df):
            rth = ii[(t >= 930) & (t <= 1559)]; f = ii[t == 1559]; ven = ii[(t >= 935) & (t <= 1500)]
            if len(rth) < 300 or not len(f):
                continue
            if len(hist) >= N and len(ven):
                H = max(x[0] for x in hist[-N:]); L = min(x[1] for x in hist[-N:])
                for j in ven:
                    assert j - 1 >= 0
                    d = 1 if (c[j] > H and c[j - 1] <= H) else -1 if (c[j] < L and c[j - 1] >= L) else 0
                    if d:
                        if j + 1 <= f[0]:
                            px = c[j]
                            filas.append(dict(i_ent=j + 1, precio=px, dir=d, riesgo=px * k / 100, i_fin=f[0], obj=2.0, coste=COSTE))
                        break
            hist.append((h[rth].max(), l[rth].min()))
        return df, pd.DataFrame(filas)
    return fn


def u2(hora, q, k):
    def fn(df):
        filas, cierre_prev = [], None
        for s, ii, t, o, h, l, c in _dias(df):
            e = ii[t == hora]; f = ii[t == 1559]
            if not len(f):
                continue
            if cierre_prev is not None and len(e) and e[0] - 1 >= ii[0]:
                ret = c[e[0] - 1] / cierre_prev - 1
                if abs(ret) >= q / 100:
                    p = o[e[0]]
                    filas.append(dict(i_ent=e[0], precio=p, dir=int(np.sign(ret)), riesgo=p * k / 100, i_fin=f[0], obj=2.0, coste=COSTE))
            cierre_prev = c[f[0]]
        return df, pd.DataFrame(filas)
    return fn


FAMILIAS = {
    "U1 ruptura N dias": {f"N={N} k={k}%": u1(N, k) for N in (5, 10, 20) for k in (0.30, 0.50)},
    "U2 ETF apalancados": {f"{h} q={q}% k={k}%": u2(h, q, k) for h in (1530, 1545) for q in (1.0, 1.5) for k in (0.15, 0.25)},
}


def evaluar_familia(nombre):
    V = FAMILIAS[nombre]
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in IMPARES}
    tab, sup, ops = mina.evaluar(nombre, V, mina.r_obj, D, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    for v, x in ops.items():
        if len(x):
            print(f"  {v}: largos {(x.dir == 1).mean():.0%} · por año {tab.set_index('variante').loc[v, 'anios']}")
    if sup:
        print(f"\nVALIDACIÓN años pares para {sup} (umbral p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in PARES}
        for v in sup:
            o = mina.correr_variante(V[v], P); r = mina.r_obj(o)
            py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            ok = p < 0.05 / len(sup) and (py > 0).sum() >= 3
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} wr {(r>0).mean():.1%} p1c={p:.4f} inv {mina.r_obj(o, True).mean():+.4f} · años {py.round(3).to_dict()} → {'PASA' if ok else 'NO PASA'}")


if __name__ == "__main__":
    clave = sys.argv[1]
    evaluar_familia(next(n for n in FAMILIAS if n.startswith(clave)))
