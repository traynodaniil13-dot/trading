"""Mina NQ tanda 3 (impares → pares). preregistros/2026-10-05_mina_nq_tanda3.md"""
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


def t1(modo, q, k):
    def fn(df):
        filas, hist = [], []
        for s, ii, t, o, h, l, c in _dias(df):
            on = ii[(t >= 1800) | (t <= 929)]; e = ii[t == 930]; f = ii[t == 1559]; j = ii[t == 929]
            if len(on) < 300 or not len(e) or not len(f) or not len(j):
                continue
            mv = np.log(c[j[0]] / o[on[0]])
            if len(hist) >= 20 and abs(mv) >= q * np.median(np.abs(hist[-20:])) and mv != 0:
                d = int(-np.sign(mv) if modo == "REV" else np.sign(mv)); p = o[e[0]]
                filas.append(dict(i_ent=e[0], precio=p, dir=d, riesgo=p * k / 100, i_fin=f[0], obj=2.0, coste=COSTE))
            hist.append(mv)
        return df, pd.DataFrame(filas)
    return fn


def t2(modo, k, ratio):
    def fn(df):
        filas = []
        for s, ii, t, o, h, l, c in _dias(df):
            on = ii[(t >= 1800) | (t <= 929)]; a = ii[t == 930]; j = ii[t == 959]; e = ii[t == 1000]; f = ii[t == 1559]
            if len(on) < 300 or not (len(a) and len(j) and len(e) and len(f)):
                continue
            H, L = h[on].max(), l[on].min(); op, cl = o[a[0]], c[j[0]]
            d = 0
            if op > H:
                if modo == "RECHAZO" and cl < H: d = -1
                if modo == "ACEPTACION" and cl > op: d = 1
            elif op < L:
                if modo == "RECHAZO" and cl > L: d = 1
                if modo == "ACEPTACION" and cl < op: d = -1
            if d:
                p = o[e[0]]
                filas.append(dict(i_ent=e[0], precio=p, dir=d, riesgo=p * k / 100, i_fin=f[0], obj=ratio, coste=COSTE))
        return df, pd.DataFrame(filas)
    return fn


def t3(q, ratio):
    def fn(df):
        filas, hist = [], []
        for s, ii, t, o, h, l, c in _dias(df):
            r15 = ii[(t >= 930) & (t <= 944)]; f = ii[t == 1559]; ven = ii[(t >= 945) & (t <= 1130)]
            if len(r15) != 15 or not len(f) or not len(ven):
                continue
            H, L = h[r15].max(), l[r15].min(); rg = H - L
            if len(hist) >= 20 and rg < q * np.median(hist[-20:]):
                for j in ven:
                    if c[j] > H or c[j] < L:
                        d = 1 if c[j] > H else -1; px = c[j]
                        stop = L if d == 1 else H; r = max((px - stop) * d, 0.0005 * px)
                        if j + 1 <= f[0]:
                            filas.append(dict(i_ent=j + 1, precio=px, dir=d, riesgo=r, i_fin=f[0], obj=ratio, coste=COSTE))
                        break
            hist.append(rg)
        return df, pd.DataFrame(filas)
    return fn


FAMILIAS = {
    "T1 inventario overnight": {f"{m} q={q} k={k}%": t1(m, q, k) for m in ("REV", "CONT") for q in (1.0, 1.5) for k in (0.30, 0.50)},
    "T2 rango overnight": {f"{m} k={k}% 1:{r}": t2(m, k, r) for m in ("RECHAZO", "ACEPTACION") for k in (0.25, 0.40) for r in (1.5, 2.0)},
    "T3 compresion-ruptura": {f"q={q} 1:{r}": t3(q, r) for q in (0.5, 0.7) for r in (2.0, 3.0)},
}


def evaluar_familia(nombre):
    V = FAMILIAS[nombre]
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in IMPARES}
    tab, sup, ops = mina.evaluar(nombre, V, mina.r_obj, D, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    if sup:
        print(f"\nVALIDACIÓN años pares para {sup} (umbral p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in PARES}
        for v in sup:
            o = mina.correr_variante(V[v], P); r = mina.r_obj(o)
            py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            ok = p < 0.05 / len(sup) and (py > 0).sum() >= 3
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} wr {(r>0).mean():.1%} p1c={p:.4f} · años {py.round(3).to_dict()} → {'PASA' if ok else 'NO PASA'}")


if __name__ == "__main__":
    clave = sys.argv[1]
    evaluar_familia(next(n for n in FAMILIAS if n.startswith(clave)))
