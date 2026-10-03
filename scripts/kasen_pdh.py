import numpy as np, pandas as pd
from src import controles as C, loader, motor

def senales(nq, es, smt=False):
    o, h, l, c = (nq[k].to_numpy() for k in ("o", "h", "l", "c")); eh, el = es.h.to_numpy(), es.l.to_numpy()
    hh, ses = nq.hhmm.to_numpy(), nq.sesion.to_numpy(); filas = []; prev = None
    for s in pd.unique(ses):
        ii = np.flatnonzero(ses == s); hm = hh[ii]
        rth = ii[(hm >= 930) & (hm <= 1559)]
        if len(rth) < 300:
            prev = None; continue
        if prev is not None:
            PH, PL, EPH, EPL = prev
            o10 = ii[hm == 1000]; fin = ii[hm == 1559]
            if len(o10) and len(fin):
                O10, sw = o[o10[0]], None
                for j in ii[(hm >= 930) & (hm <= 1100)]:
                    a, b = h[j] > PH, l[j] < PL
                    if a and b: break
                    if a or b:
                        d = -1 if a else 1; js = j
                        if smt:
                            ven = ii[(ii >= rth[0]) & (ii <= j)]
                            if (a and eh[ven].max() > EPH) or (b and el[ven].min() < EPL): break
                        sw = (js, d); break
                if sw:
                    js, d = sw
                    for j in ii[(ii > js) & (hm >= 1001) & (hm <= 1200)]:
                        if (d == -1 and c[j] < O10 <= c[j - 1]) or (d == 1 and c[j] > O10 >= c[j - 1]):
                            tramo = np.arange(js, j + 1)
                            stop = h[tramo].max() if d == -1 else l[tramo].min()
                            r = (c[j] - stop) * d
                            if r >= 0.0005 * c[j]:
                                obj = ((c[j] - PL) if d == -1 else (PH - c[j])) / r
                                filas.append(dict(i_ent=j + 1, precio=c[j], dir=d, riesgo=r, i_fin=fin[0], obj=obj))
                            break
        prev = (h[rth].max(), l[rth].min(), eh[rth].max(), el[rth].min())
    return pd.DataFrame(filas)

def datos(a):
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    ix = nq.index.intersection(es.index); return nq.loc[ix], es.loc[ix]
D = {a: datos(a) for a in (2021, 2023, 2025)}
for etq, smt in (("REGLA DEL VÍDEO", False), ("+ SMT con ES (info)", True)):
    oo = []
    for a, (nq, es) in D.items():
        o = motor.simular(nq, senales(nq, es, smt)); oo.append(o[o.sesion.dt.year == a])
    o = pd.concat(oo, ignore_index=True)
    print(f"\n=== {etq}: {len(o)} ops · stop mediano {o.riesgo_pts.median():.0f} pts · objetivo PDL/PDH mediano {o.obj.median():.1f}R · cortos {(o.dir==-1).mean():.0%}")
    for rt in (2.0, 1.0, 1.5):
        r = motor.r_neta(o, rt); s = C.resumen(r); py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
        tp = (o.rmax >= rt).mean(); sl = (~(o.rmax >= rt) & o.toco_sl).mean()
        print(f"  1:{rt}: wr {s['wr']:.1%} (TP {tp:.0%} · SL {sl:.0%}) R={s['R']:+.3f} p1c={s['p_1cola']:.3f} años {py} invertida {motor.r_neta(o, rt, True).mean():+.3f}")
    rr = np.where(o.rmax >= o.obj, o.obj, np.where(o.toco_sl, -1.0, np.minimum(o.r_cierre, o.obj))) - 0.87 / o.riesgo_pts
    print(f"  objetivo = PDL/PDH opuesto: R={rr.mean():+.3f} wr {np.mean(rr > 0):.1%}")
