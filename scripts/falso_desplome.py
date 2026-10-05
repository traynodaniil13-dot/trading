"""'Falso desplome' de la apertura de NY. preregistros/2026-10-05_falso_desplome_apertura.md"""
import numpy as np, pandas as pd
from src import controles as C, loader, mina

COSTE = 0.87


def camino_be(h, l, c, a, f, p, d, r, obj, coste):
    """Simulación minuto a minuto con BE a 1R (activo desde la barra siguiente). Barra de entrada: solo stop."""
    stop = p - d * r; tpn = p + d * obj * r; activo = False
    for k in range(a, f + 1):
        if (d == 1 and l[k] <= stop) or (d == -1 and h[k] >= stop):
            return (0.0 if activo else -1.0) - coste / r
        if k > a:
            if (d == 1 and h[k] >= tpn) or (d == -1 and l[k] <= tpn):
                return obj - coste / r
            if not activo and ((d == 1 and h[k] >= p + r) or (d == -1 and l[k] <= p - r)):
                activo = True
        if activo:
            stop = p
    return (c[f] - p) * d / r - coste / r


def senales(df, tp, be):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    idx = np.arange(len(df)); filas = []; prev_rth = None
    for s in pd.unique(ses):
        ii = idx[ses == s]; t = hm[ii]
        pre = ii[(t >= 800) & (t <= 929)]; rth = ii[(t >= 930) & (t <= 1559)]
        v = [ii[(t >= a) & (t <= a + 4)] for a in (930, 935, 940, 945)]
        f = ii[t == 1559]
        ok = len(pre) >= 80 and all(len(x) == 5 for x in v) and len(f) and len(rth) >= 300
        if ok:
            O = [o[x[0]] for x in v]; Cc = [c[x[-1]] for x in v]
            L0, H0 = l[np.r_[v[0], v[1]]].min(), h[np.r_[v[0], v[1]]].max()
            d = 0
            if Cc[0] < O[0] and Cc[1] < O[1] and L0 < l[pre].min() and Cc[2] > O[2] and Cc[3] > O[3]:
                d = 1
            elif Cc[0] > O[0] and Cc[1] > O[1] and H0 > h[pre].max() and Cc[2] < O[2] and Cc[3] < O[3]:
                d = -1
            if d:
                tramo = np.r_[v[0], v[1], v[2], v[3]]
                px = Cc[3]; stop = l[tramo].min() if d == 1 else h[tramo].max()
                r = max((px - stop) * d, 0.0005 * px)
                if tp == "4R":
                    obj = 4.0
                else:
                    if prev_rth is None:
                        obj = None
                    else:
                        nivel = prev_rth[0] if d == 1 else prev_rth[1]
                        obj = (nivel - px) * d / r if (nivel - px) * d > 0 else None
                if obj:
                    a = v[3][-1] + 1
                    fila = dict(i_ent=a, precio=px, dir=d, riesgo=r, i_fin=f[0], obj=obj, coste=COSTE, be=be)
                    if be:
                        fila["r_be"] = camino_be(h, l, c, a, f[0], px, d, r, obj, COSTE)
                        fila["r_be_inv"] = camino_be(h, l, c, a, f[0], px, -d, r, obj, COSTE)
                    filas.append(fila)
        if len(rth) >= 300:
            prev_rth = (h[rth].max(), l[rth].min())
    return df, pd.DataFrame(filas)


def r_be(o, invertida=False):
    """Con BE: resultado del camino minuto a minuto (camino_be). Sin BE: r_obj."""
    if not o["be"].any():
        return mina.r_obj(o, invertida)
    return o["r_be_inv" if invertida else "r_be"].to_numpy()


V = {f"TP {tp} · BE {'sí' if be else 'no'}": (lambda df, tp=tp, be=be: senales(df, tp, be)) for tp in ("4R", "PDH") for be in (False, True)}

if __name__ == "__main__":
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in mina.DISENO}
    tab, sup, ops = mina.evaluar("Falso desplome de la apertura", V, r_be, D, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    for v, x in ops.items():
        r = r_be(x); print(f"  {v}: por año " + str(pd.Series(r).groupby(x._a.to_numpy()).mean().round(3).to_dict()))
    o = next(iter(ops.values()))
    print(f"\nFrecuencia: {len(o)} operaciones en 3 años ({len(o)/3:.0f}/año) · largos {(o.dir==1).mean():.0%} · stop mediano {o.riesgo_pts.median():.1f} pts")
    for rt in (1.0, 2.0, 4.0):
        x = o.copy(); x["obj"] = rt; r = mina.r_obj(x)
        print(f"  informativo 1:{rt:g}: wr {(r>0).mean():.1%} R {r.mean():+.4f}")
