"""Gerard García: EMA20 M15+M30 → barrida de swing M5 a favor → límite en FVG M5, TP/SL monetario.
preregistros/2026-10-05_gerard_garcia_fvg.md"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina

COSTE = 0.87
IMPARES, PARES = (2019, 2021, 2023, 2025), (2020, 2022, 2024, 2026)
RATIO_TP = 0.625
SESIONES = {"Londres": (200, 459, 829), "NY": (930, 1059, 1159)}
_cache = []


def velas(df, m):
    g = df.index.floor(f"{m}min").to_numpy()
    corte = np.r_[True, g[1:] != g[:-1]]
    kf = np.flatnonzero(corte); kl = np.r_[kf[1:] - 1, len(df) - 1]
    h = np.maximum.reduceat(df.h.to_numpy(), kf); l = np.minimum.reduceat(df.l.to_numpy(), kf)
    c = df.c.to_numpy()[kl]
    return kl, h, l, c


def rasgos(df):
    for d, r in _cache:
        if d is df:
            return r
    kl5, h5, l5, c5 = velas(df, 5)
    tend = []
    for m in (15, 30):
        kl, _, _, c = velas(df, m); ema = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
        tend.append((kl, np.sign(c - ema)))
    j = np.arange(2, len(l5) - 2)
    piv_l = j[(l5[j] < l5[j - 1]) & (l5[j] < l5[j - 2]) & (l5[j] < l5[j + 1]) & (l5[j] < l5[j + 2])]
    piv_h = j[(h5[j] > h5[j - 1]) & (h5[j] > h5[j - 2]) & (h5[j] > h5[j + 1]) & (h5[j] > h5[j + 2])]
    j = np.arange(2, len(l5))
    fvg_up = j[l5[j] > h5[j - 2]]; fvg_dn = j[h5[j] < l5[j - 2]]
    r = dict(kl5=kl5, h5=h5, l5=l5, tend=tend, piv_l=piv_l, piv_h=piv_h, fvg_up=fvg_up, fvg_dn=fvg_dn)
    _cache.append((df, r)); del _cache[:-6]
    return r


def tendencia(R, k):
    s = []
    for kl, sg in R["tend"]:
        j = np.searchsorted(kl, k, "right") - 1     # velas cerradas en o antes de k
        if j < 20:
            return 0
        s.append(sg[j])
    return int(s[0]) if s[0] == s[1] else 0


def camino(h, l, c, d, fills, a, fin, R0):
    """fills: [(barra, precio, tamaño)], el 1º en la barra a-1. Devuelve R bruta."""
    u = [fills[0]]; pend = fills[1:]
    sl, tp = R0, RATIO_TP * R0
    for n in range(a, fin + 1):
        adv = l[n] if d == 1 else h[n]; fav = h[n] if d == 1 else l[n]
        if sum(s * (adv - p) * d for _, p, s in u) <= -sl:
            return -1.0
        if pend and pend[0][0] == n:
            u.append(pend.pop(0)); continue
        if sum(s * (fav - p) * d for _, p, s in u) >= tp:
            return RATIO_TP
    return sum(s * (c[fin] - p) * d for _, p, s in u) / R0


def variante(sesion, slp, prom):
    a0, a1, cierre = SESIONES[sesion]

    def fn(df):
        R = rasgos(df); h, l, c = (df[x].to_numpy() for x in "hlc")
        hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy(); idx = np.arange(len(df))
        kl5, h5, l5 = R["kl5"], R["h5"], R["l5"]
        filas = []
        for s in pd.unique(ses):
            ii = idx[ses == s]; t = hm[ii]; w = ii[(t >= a0) & (t <= a1)]; f = ii[t == cierre]
            if len(w) < 30 or not len(f):
                continue
            fin = f[0]; orden = None
            for k in w:
                d = tendencia(R, k)
                if not d:
                    continue
                j5 = np.searchsorted(kl5, k, "right") - 1          # última M5 cerrada
                piv = R["piv_l"] if d == 1 else R["piv_h"]
                pc = piv[(piv + 2 <= j5) & (piv >= j5 - 48)]          # confirmados
                if not len(pc):
                    continue
                pj = pc[-1]; nivel = l5[pj] if d == 1 else h5[pj]; desde = kl5[pj + 2] + 1
                if desde > k:                                       # el pivote se confirma al cierre de k: la barrida, desde k+1
                    continue
                previo = l[desde:k] if d == 1 else h[desde:k]
                barrida = (l[k] < nivel and (not len(previo) or previo.min() >= nivel)) if d == 1 else \
                          (h[k] > nivel and (not len(previo) or previo.max() <= nivel))
                if not barrida:
                    continue
                fv = R["fvg_up"] if d == 1 else R["fvg_dn"]
                fv = fv[(fv <= j5) & (fv >= j5 - 48)]
                cand = []
                for q in fv:
                    top, bot = (l5[q], h5[q - 2]) if d == 1 else (h5[q], l5[q - 2])
                    tras = l[kl5[q] + 1:k + 1] if d == 1 else h[kl5[q] + 1:k + 1]
                    if d == 1 and top < l[k] and (not len(tras) or tras.min() > top):
                        cand.append((top, bot))
                    if d == -1 and top > h[k] and (not len(tras) or tras.max() < top):
                        cand.append((top, bot))
                if cand:
                    top, bot = max(cand) if d == 1 else min(cand)
                    orden = (k, d, top, bot)
                break                                               # solo la primera barrida del día
            if orden is None:
                continue
            k, d, top, bot = orden
            m1 = next((m for m in range(k + 1, fin) if hm[m] <= a1 and ((d == 1 and l[m] <= top) or (d == -1 and h[m] >= top))), None)
            if m1 is None:
                continue
            p1 = c[m1]; R0 = slp / 100 * p1; tam = 0.5 if prom else 1.0
            fills = [(m1, p1, tam)]
            if prom:
                m2 = next((m for m in range(m1, fin) if (d == 1 and l[m] <= bot) or (d == -1 and h[m] >= bot)), None)
                if m2 == m1:
                    fills = [(m1, p1, 1.0)]                        # las dos al cierre de la misma barra
                elif m2 is not None:
                    fills.append((m2, c[m2], tam))
            if m1 + 1 > fin:
                continue
            res = {}
            for nom, dd in (("r", d), ("r_inv", -d)):
                fl = list(fills)
                bruta = camino(h, l, c, dd, fl, m1 + 1, fin, R0)
                res[nom] = bruta - COSTE * sum(x[2] for x in fl) / R0
            filas.append(dict(i_ent=m1 + 1, precio=p1, dir=d, riesgo=R0, i_fin=fin, **res))
        return df, pd.DataFrame(filas)
    return fn


V = {f"{s} SL {sl}% {'promedia' if p else 'sin promediar'}": variante(s, sl, p)
     for s in SESIONES for sl in (0.25, 0.50) for p in (False, True)}
r_fn = lambda o, invertida=False: o["r_inv" if invertida else "r"].to_numpy()
carga = lambda anios: {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in anios}


def racha(r):
    m = x = 0
    for v in r:
        x = x + 1 if v < 0 else 0; m = max(m, x)
    return m


if __name__ == "__main__":
    tab, sup, ops = mina.evaluar("Gerard García EMA20 + barrida + FVG", V, r_fn, carga(IMPARES),
                                 lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    print("\nInformativo:")
    for v, o in ops.items():
        r = r_fn(o)
        print(f"  {v}: n={len(o)} ({len(o)/4:.0f}/año) wr {(r > 0).mean():.1%} (empate sin coste 61,5%) · "
              f"racha máx. de pérdidas {racha(r)} · largos {(o.dir == 1).mean():.0%} · años {tab.set_index('variante').loc[v, 'anios']}")
    if sup:
        print(f"\nVALIDACIÓN años pares para {sup} (p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = carga(PARES)
        for v in sup:
            o = mina.correr_variante(V[v], P); r = r_fn(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} wr {(r>0).mean():.1%} p1c={p:.4f} inv {r_fn(o, True).mean():+.4f} años {py.round(3).to_dict()} → {'PASA' if p < 0.05/len(sup) and (py > 0).sum() >= 3 else 'NO PASA'}")
