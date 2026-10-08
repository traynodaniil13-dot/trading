"""Mina NQ tanda 6. preregistros/2026-10-08_mina_nq_tanda6.md"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina
from scripts.mina_nq_tanda4 import _dias, COSTE, IMPARES, PARES


def ruptura(rango_sel, ventana, cierre, q, ratio):
    def fn(df):
        filas, hist = [], []
        for s, ii, t, o, h, l, c in _dias(df):
            rg_i = ii[rango_sel(t)]; ven = ii[(t >= ventana[0]) & (t <= ventana[1])]; f = ii[t == cierre]
            if len(rg_i) < 60 or not len(ven) or not len(f):
                continue
            H, L = h[rg_i].max(), l[rg_i].min(); rg = H - L
            if len(hist) >= 20 and rg < q * np.median(hist[-20:]):
                for j in ven:
                    assert j - 1 >= 0
                    d = 1 if (c[j] > H and c[j - 1] <= H) else -1 if (c[j] < L and c[j - 1] >= L) else 0
                    if d:
                        px = c[j]; stop = L if d == 1 else H; r = max((px - stop) * d, 0.0005 * px)
                        if j + 1 <= f[0]:
                            filas.append(dict(i_ent=j + 1, precio=px, dir=d, riesgo=r, i_fin=f[0], obj=ratio, coste=COSTE))
                        break
            hist.append(rg)
        return df, pd.DataFrame(filas)
    return fn


asia = lambda t: (t >= 1800) | (t <= 159)
manana = lambda t: (t >= 930) & (t <= 1129)
FAMILIAS = {
    "W1 Asia-Londres": {f"q={q} 1:{r}": ruptura(asia, (200, 500), 829, q, r) for q in (0.7, 1.0) for r in (2.0, 3.0)},
    "W2 manana-tarde": {f"q={q} 1:{r}": ruptura(manana, (1300, 1500), 1559, q, r) for q in (0.6, 0.8) for r in (2.0, 3.0)},
}

if __name__ == "__main__":
    nombre = next(n for n in FAMILIAS if n.startswith(sys.argv[1])); V = FAMILIAS[nombre]
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in IMPARES}
    tab, sup, ops = mina.evaluar(nombre, V, mina.r_obj, D, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    for v, x in ops.items():
        print(f"  {v}: n={len(x)} wr {(mina.r_obj(x)>0).mean():.1%} · años {tab.set_index('variante').loc[v, 'anios']}")
    if sup:
        print(f"\nVALIDACIÓN pares para {sup} (p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in PARES}
        for v in sup:
            o = mina.correr_variante(V[v], P); r = mina.r_obj(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} p1c={p:.4f} inv {mina.r_obj(o, True).mean():+.4f} años {py.round(3).to_dict()} → {'PASA' if p < 0.05/len(sup) and (py > 0).sum() >= 3 else 'NO PASA'}")
