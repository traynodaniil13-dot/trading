"""ICT 2025 Venom Model. preregistros/2026-10-10_ict_venom.md"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina

COSTE = 0.87
IMPARES, PARES = (2019, 2021, 2023, 2025), (2020, 2022, 2024, 2026)


def senales(df, modo):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    idx = np.arange(len(df)); filas = []
    for s in pd.unique(ses):
        ii = idx[ses == s]; t = hm[ii]
        rg = ii[(t >= 800) & (t <= 929)]; ven = ii[(t >= 930) & (t <= 1100)]; fin = ii[t == 1559]
        if len(rg) < 80 or len(ven) < 60 or not len(fin) or t[ven[0] - ii[0]] != 930:
            continue
        RH, RL = h[rg].max(), l[rg].min(); j930 = ven[0]; fin = fin[0]
        d = 0; js = None
        for j in ven:
            up, dn = h[j] > RH, l[j] < RL
            if up and dn:
                break
            if up or dn:
                d = -1 if up else 1; js = j; break
        if not d:
            continue
        # FVG a favor de la barrida (alcistas si d=-1) y en contra, nacidos desde las 09:30 (índice de la 3ª vela)
        def fvg_favor(i):   # zona (abajo, arriba) del FVG a favor de la barrida nacido en i
            if d == -1 and l[i] > h[i - 2]: return (h[i - 2], l[i])
            if d == 1 and h[i] < l[i - 2]: return (h[i], l[i - 2])
            return None
        def fvg_contra(i):
            if d == -1 and h[i] < l[i - 2]: return (h[i], l[i - 2])
            if d == 1 and l[i] > h[i - 2]: return (h[i - 2], l[i])
            return None
        favor = []; bpr = None; op = None
        for j in range(j930 + 2, ven[-1] + 1):
            assert j - 2 >= 0
            z = fvg_favor(j)
            if z: favor.append(z)
            if j <= js:
                continue
            # --- gatillo 2: envolvente que invierte el último FVG a favor
            if modo in ("G2", "G12") and favor and op is None:
                ab, ar = favor[-1]
                env = (d == -1 and c[j] < o[j] and c[j - 1] > o[j - 1] and o[j] >= c[j - 1] and c[j] <= o[j - 1] and c[j] < ab) or \
                      (d == 1 and c[j] > o[j] and c[j - 1] < o[j - 1] and o[j] <= c[j - 1] and c[j] >= o[j - 1] and c[j] > ar)
                if env:
                    px = c[j]; r = max(abs(px - o[j]), 0.0005 * px); tp = px + d * 2 * r
                    if (d == -1 and tp >= RL) or (d == 1 and tp <= RH):
                        op = dict(i_ent=j + 1, precio=px, dir=d, riesgo=r)
            # --- gatillo 1: BPR (nace un FVG en contra que solapa uno a favor) y su retest
            if modo in ("G1", "G12") and op is None:
                if bpr is not None:
                    zb, slv, tp0, nace = bpr
                    toca = (d == -1 and h[j] >= zb) or (d == 1 and l[j] <= zb)
                    if toca and j > nace:
                        px = c[j]; tramo = np.arange(js, j + 1)
                        sl = h[tramo].max() if d == -1 else l[tramo].min()
                        r = max((sl - px) * -d, 0.0005 * px); tp = px + d * 2 * r
                        if (d == -1 and tp >= RL) or (d == 1 and tp <= RH):
                            op = dict(i_ent=j + 1, precio=px, dir=d, riesgo=r)
                        else:
                            bpr = None
                    elif (d == -1 and l[j] <= tp0) or (d == 1 and h[j] >= tp0):
                        bpr = None                      # tocó el 2R antes del retest: no hay trade
                if bpr is None:
                    zc = fvg_contra(j)
                    if zc:
                        for zf in reversed(favor):
                            lo, hi = max(zc[0], zf[0]), min(zc[1], zf[1])
                            if lo < hi:
                                zb = lo if d == -1 else hi
                                tramo = np.arange(js, j + 1)
                                slv = h[tramo].max() if d == -1 else l[tramo].min()
                                tp0 = zb + d * 2 * abs(slv - zb)
                                bpr = (zb, slv, tp0, j); break
            if op:
                break
        if op and op["i_ent"] <= fin:
            op.update(i_fin=fin, obj=2.0, coste=COSTE); filas.append(op)
    return df, pd.DataFrame(filas)


V = {"G1 BPR": lambda df: senales(df, "G1"), "G2 Venom Breakout": lambda df: senales(df, "G2"),
     "G1+G2": lambda df: senales(df, "G12")}
carga = lambda anios: {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in anios}

if __name__ == "__main__":
    if sys.argv[1:] == ["calibrar"]:
        df = carga([2021])[2021]
        for v in V:
            asim, rr, nn = [], [], []
            for sd in range(24):
                o = mina.correr_variante(V[v], {2021: C.paseo_aleatorio(df, 1300 + sd)})
                if len(o):
                    asim.append(((mina.r_obj(o) - mina.r_obj(o, True)) / 2).mean()); rr.append(mina.r_obj(o).mean()); nn.append(len(o))
            asim = np.array(asim)
            print(f"{v}: n/año {np.mean(nn):.0f} · paseo R {np.mean(rr):+.4f} · asimetría {asim.mean():+.4f} ± {asim.std(ddof=1)/np.sqrt(len(asim)):.4f}")
        sys.exit()
    tab, sup, ops = mina.evaluar("ICT Venom", V, mina.r_obj, carga(IMPARES), lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    for v, o in ops.items():
        r = mina.r_obj(o); print(f"  {v}: n={len(o)} ({len(o)/4:.0f}/año) wr {(r>0).mean():.1%} stop mediano {o.riesgo_pts.median():.1f} pts · largos {(o.dir==1).mean():.0%}")
    if sup:
        print(f"\nVALIDACIÓN pares para {sup} (p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = carga(PARES)
        for v in sup:
            o = mina.correr_variante(V[v], P); r = mina.r_obj(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} p1c={p:.4f} inv {mina.r_obj(o, True).mean():+.4f} años {py.round(3).to_dict()} → {'PASA' if p < 0.05/len(sup) and (py > 0).sum() >= 3 else 'NO PASA'}")
