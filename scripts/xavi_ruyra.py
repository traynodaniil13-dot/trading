"""Xavi Ruyra: Judas Swing con acumulación pre-market y PO3 de las aperturas de 15 min.
preregistros/2026-10-08_xavi_ruyra.md"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina
from scripts.aleix_reversion_0930 import fvg_h1, zonas_vigentes

COSTE = 0.87
IMPARES, PARES = (2019, 2021, 2023, 2025), (2020, 2022, 2024, 2026)


def e1(df, tp, filtro=True, invertir=False):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    idx = np.arange(len(df)); H, f = fvg_h1(df); filas, hist = [], []
    for s in pd.unique(ses):
        ii = idx[ses == s]; t = hm[ii]
        pm = ii[(t >= 800) & (t <= 929)]; ven = ii[(t >= 930) & (t <= 1030)]; fin = ii[t == 1559]
        if len(pm) < 80 or len(ven) < 50 or not len(fin) or t[ven[0] - ii[0]] != 930:
            continue
        rg = h[pm].max() - l[pm].min(); acum = len(hist) >= 20 and rg < np.median(hist[-20:]); hist.append(rg)
        if filtro and not acum:
            continue
        j930 = ven[0]; ap = o[j930]
        zonas = zonas_vigentes(H, f, np.datetime64(df.index[j930]))
        arriba = [z for z in zonas if z[0] == -1 and z[1] > ap]   # FVG bajista por encima
        abajo = [z for z in zonas if z[0] == 1 and z[2] < ap]     # FVG alcista por debajo
        d = 0; j_m = None
        for j in ven:
            if t[j - ii[0]] > 959:
                break
            up = any(h[j] >= z[1] for z in arriba); dn = any(l[j] <= z[2] for z in abajo)
            if up and dn:
                break
            if up or dn:
                d = -1 if up else 1; j_m = j; break
        if not d:
            continue
        for j in ven:
            if j <= j_m:
                continue
            # último FVG 1m a favor de la manipulación nacido desde las 09:30 y cerrado antes de j
            borde = None
            for i in range(j - 1, j930 + 1, -1):
                assert i - 2 >= 0
                if d == -1 and l[i] > h[i - 2]:
                    borde = h[i - 2]; break
                if d == 1 and h[i] < l[i - 2]:
                    borde = l[i - 2]; break
            if borde is None:
                continue
            if (d == -1 and c[j] < borde) or (d == 1 and c[j] > borde):
                tramo = np.arange(j930, j + 1)
                ext = h[tramo].max() if d == -1 else l[tramo].min()
                px = c[j]; r = max((ext - px) * -d, 0.0005 * px)
                if j + 1 <= fin[0]:
                    filas.append(dict(i_ent=j + 1, precio=px, dir=-d if invertir else d, riesgo=r, i_fin=fin[0], obj=tp, coste=COSTE))
                break
    return df, pd.DataFrame(filas)


def mas(hm, m):
    x = (hm // 100) * 60 + hm % 100 + m
    return (x // 60) * 100 + x % 60


def e2(df, tp):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    idx = np.arange(len(df)); filas = []
    for s in pd.unique(ses):
        ii = idx[ses == s]; t = hm[ii]; a = ii[t == 930]; fin = ii[t == 1559]
        if not len(a) or not len(fin):
            continue
        for T in (945, 1000, 1015):
            jt = ii[t == T]
            if not len(jt) or jt[0] - 1 < a[0]:
                continue
            jt = jt[0]; d = int(np.sign(c[jt - 1] - o[a[0]]))
            if not d:
                continue
            op = o[jt]; manip = False; hecho = False
            for j in range(jt, jt + 11):
                if t[j - ii[0]] != mas(T, j - jt):
                    break
                if j - jt <= 4 and ((d == -1 and h[j] > op) or (d == 1 and l[j] < op)):
                    manip = True
                if manip and ((d == -1 and c[j] < op) or (d == 1 and c[j] > op)):
                    tramo = np.arange(jt, j + 1)
                    ext = h[tramo].max() if d == -1 else l[tramo].min()
                    px = c[j]; r = max((ext - px) * -d, 0.0005 * px)
                    if j + 1 <= fin[0]:
                        filas.append(dict(i_ent=j + 1, precio=px, dir=d, riesgo=r, i_fin=fin[0], obj=tp, coste=COSTE))
                    hecho = True; break
            if hecho:
                break
    return df, pd.DataFrame(filas)


V = {"E1 Judas + acumulación · 2R": lambda df: e1(df, 2.0), "E1 Judas + acumulación · 3R": lambda df: e1(df, 3.0),
     "E2 PO3 15m · 2R": lambda df: e2(df, 2.0), "E2 PO3 15m · 3R": lambda df: e2(df, 3.0)}
carga = lambda anios: {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in anios}

if __name__ == "__main__":
    if sys.argv[1:] == ["calibrar"]:
        df = carga([2021])[2021]
        for v in V:
            asim, rr, nn = [], [], []
            for sd in range(24):
                o = mina.correr_variante(V[v], {2021: C.paseo_aleatorio(df, 700 + sd)})
                if len(o):
                    asim.append(((mina.r_obj(o) - mina.r_obj(o, True)) / 2).mean()); rr.append(mina.r_obj(o).mean()); nn.append(len(o))
            asim = np.array(asim)
            print(f"{v}: n/año {np.mean(nn):.0f} · paseo R {np.mean(rr):+.4f} · asimetría {asim.mean():+.4f} ± {asim.std(ddof=1)/np.sqrt(len(asim)):.4f}")
        sys.exit()
    D = carga(IMPARES)
    tab, sup, ops = mina.evaluar("Xavi Ruyra", V, mina.r_obj, D, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    for v, o in ops.items():
        r = mina.r_obj(o); print(f"  {v}: n={len(o)} ({len(o)/4:.0f}/año) wr {(r>0).mean():.1%} stop mediano {o.riesgo_pts.median():.1f} pts · largos {(o.dir==1).mean():.0%}")
    o = mina.correr_variante(lambda df: e1(df, 2.0, filtro=False), D); r = mina.r_obj(o)
    print(f"  Informativo E1 SIN acumulación · 2R: n={len(o)} R={r.mean():+.4f} wr {(r>0).mean():.1%}")
    if sup:
        print(f"\nVALIDACIÓN años pares para {sup} (p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = carga(PARES)
        for v in sup:
            o = mina.correr_variante(V[v], P); r = mina.r_obj(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} p1c={p:.4f} inv {mina.r_obj(o, True).mean():+.4f} años {py.round(3).to_dict()} → {'PASA' if p < 0.05/len(sup) and (py > 0).sum() >= 3 else 'NO PASA'}")
