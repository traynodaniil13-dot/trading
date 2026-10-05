"""Mina NQ tanda 5. preregistros/2026-10-05_mina_nq_tanda5.md"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina
from scripts.mina_nq_tanda4 import _dias, COSTE, IMPARES, PARES


def v1(hora, q, k):
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
                    filas.append(dict(i_ent=e[0], precio=p, dir=-int(np.sign(ret)), riesgo=p * k / 100, i_fin=f[0], obj=2.0, coste=COSTE))
            cierre_prev = c[f[0]]
        return df, pd.DataFrame(filas)
    return fn


def v2(z, k):
    def fn(df):
        filas, hist = [], []
        for s, ii, t, o, h, l, c in _dias(df):
            rth = ii[(t >= 930) & (t <= 1559)]; f = ii[t == 1559]
            if len(rth) < 300 or not len(f):
                continue
            lc = np.log(c[rth]); r60 = np.full(len(rth), np.nan); r60[60:] = lc[60:] - lc[:-60]
            tr = t[(t >= 930) & (t <= 1559)]
            if len(hist) >= 20:
                sig = np.median(hist[-20:])
                for m in np.where((tr >= 1030) & (tr <= 1500) & ~np.isnan(r60))[0]:
                    assert m - 60 >= 0
                    if abs(r60[m]) >= z * sig:
                        j = rth[m]; d = -int(np.sign(r60[m])); px = c[j]
                        if j + 1 <= f[0]:
                            filas.append(dict(i_ent=j + 1, precio=px, dir=d, riesgo=px * k / 100, i_fin=f[0], obj=2.0, coste=COSTE))
                        break
            sel = (tr >= 1030) & ~np.isnan(r60)
            if sel.sum() > 30:
                hist.append(np.std(r60[sel]))
        return df, pd.DataFrame(filas)
    return fn


V1 = {f"REV {h} q={q}% k={k}%": v1(h, q, k) for h in (1530, 1545) for q in (1.0, 1.5) for k in (0.15, 0.25)}
V2 = {f"z={z} k={k}%": v2(z, k) for z in (2.0, 2.5, 3.0) for k in (0.25, 0.40)}
carga = lambda anios: {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in anios}
nulo = lambda df, sd: C.paseo_aleatorio(df, sd)

if __name__ == "__main__":
    if sys.argv[1] == "V1":
        tab, sup, ops = mina.evaluar("V1 reversion del dia al cierre (AÑOS PARES)", V1, mina.r_obj, carga(PARES), nulo, semillas=12)
        best = tab.sort_values("R", ascending=False).iloc[0]
        print(f"\nMejor: {best.variante} p1c={best.p1c:.4f} (umbral 0,00625) · años {best.anios}")
        print("Pasa V1:", bool(sup) and tab.set_index("variante").loc[sup, "p1c"].min() < 0.00625)
    else:
        tab, sup, ops = mina.evaluar("V2 reversion de extremos de 60 min", V2, mina.r_obj, carga(IMPARES), nulo, semillas=12)
        for v, x in ops.items():
            print(f"  {v}: n={len(x)} largos {(x.dir == 1).mean():.0%} · años {tab.set_index('variante').loc[v, 'anios']}")
        if sup:
            print(f"\nVALIDACIÓN años pares para {sup} (p < {0.05/len(sup):.4f} y ≥3/4 años):")
            P = carga(PARES)
            for v in sup:
                o = mina.correr_variante(V2[v], P); r = mina.r_obj(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
                p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
                print(f"  {v}: n={len(o)} R={r.mean():+.4f} p1c={p:.4f} inv {mina.r_obj(o, True).mean():+.4f} años {py.round(3).to_dict()} → {'PASA' if p < 0.05/len(sup) and (py > 0).sum() >= 3 else 'NO PASA'}")
