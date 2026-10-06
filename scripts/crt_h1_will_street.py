"""CRT de Will Street en H1. preregistros/2026-10-06_crt_h1_will_street.md"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina

COSTE = 0.87
IMPARES, PARES = (2019, 2021, 2023, 2025), (2020, 2022, 2024, 2026)


def mas(hm, minutos):
    t = (hm // 100) * 60 + hm % 100 + minutos
    return (t // 60) * 100 + t % 60


def gatillo(o, h, l, c, ii, hm, d, ini, fin_hora, objetivo, barrido, fin):
    """PO3 + breaker dentro de [ini, fin_hora]. Devuelve la operación o None."""
    t = hm
    zona = ii[(t >= mas(ini, -60)) & (t <= fin_hora)]
    bloques = {}
    for j in zona:
        tj = t[j - ii[0]]
        bloques.setdefault((tj // 100) * 60 + (tj % 100) // 5 * 5, []).append(j)
    V = [(k, b[0], b[-1], h[b].max(), l[b].min()) for k, b in sorted(bloques.items())]
    j0 = ii[t == ini]
    if not len(j0):
        return None
    j0 = j0[0]; ap = o[j0]; t0 = (ini // 100) * 60 + ini % 100
    extremo = breaker = None
    for m, (k, a, z, vh, vl) in enumerate(V):
        if k < t0:
            continue
        if breaker is not None:
            for j in range(a, z + 1):
                if (d == 1 and l[j] < extremo) or (d == -1 and h[j] > extremo):
                    extremo = l[j] if d == 1 else h[j]
                if (d == 1 and h[j] >= breaker) or (d == -1 and l[j] <= breaker):
                    px = c[j]
                    if (objetivo - px) * d <= 0 or j + 1 > fin:
                        return None
                    tramo = np.arange(j0, j + 1)
                    stop = l[tramo].min() if d == 1 else h[tramo].max()
                    r = max((px - stop) * d, 0.0005 * px)
                    return dict(i_ent=j + 1, precio=px, dir=d, riesgo=r, i_fin=fin, obj_ext=(objetivo - px) * d / r)
        if (d == 1 and vh >= objetivo) or (d == -1 and vl <= objetivo):
            return None
        if (d == 1 and (extremo is None or vl < extremo)) or (d == -1 and (extremo is None or vh > extremo)):
            extremo = vl if d == 1 else vh
            mas_alla = (d == 1 and extremo < ap and (barrido is None or extremo < barrido)) or \
                       (d == -1 and extremo > ap and (barrido is None or extremo > barrido))
            breaker = None
            if mas_alla:
                for q in range(m - 1, 0, -1):
                    if d == 1 and V[q][3] > V[q - 1][3] and V[q][3] > V[q + 1][3]:
                        breaker = V[q][3]; break
                    if d == -1 and V[q][4] < V[q - 1][4] and V[q][4] < V[q + 1][4]:
                        breaker = V[q][4]; break
    return None


def hora(ii, hm, h, l, H):
    b = ii[(hm >= H) & (hm <= H + 59)]
    return (h[b].max(), l[b].min(), b) if len(b) >= 50 else None


def senales(df, lectura, tp):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    idx = np.arange(len(df)); filas = []
    for s in pd.unique(ses):
        ii = idx[ses == s]; t = hm[ii]; f = ii[t == 1559]
        if not len(f):
            continue
        tt = t  # horas de la sesión (índices de ii)
        op = None
        if lectura == "A":
            for H in (900, 1000):
                r1, op2 = hora(ii, tt, h, l, H - 100), hora(ii, tt, h, l, H)
                if r1 is None or op2 is None:
                    continue
                H1, L1, _ = r1; d = 0
                for j in op2[2]:
                    up, dn = h[j] > H1, l[j] < L1
                    if up and dn:
                        break
                    if up or dn:
                        d = -1 if up else 1; break
                if not d:
                    continue
                op = gatillo(o, h, l, c, ii, tt, d, H, H + 59, H1 if d == 1 else L1, L1 if d == 1 else H1, f[0])
                if op:
                    break
        else:
            r1, r2, r3 = hora(ii, tt, h, l, 800), hora(ii, tt, h, l, 900), hora(ii, tt, h, l, 1000)
            if r1 and r2 and r3:
                H1, L1, _ = r1; H2, L2, b2 = r2; c2 = c[b2[-1]]
                baj, alc = L2 < L1, H2 > H1
                if baj != alc and L1 < c2 < H1:
                    d = 1 if baj else -1
                    op = gatillo(o, h, l, c, ii, tt, d, 1000, 1059, H1 if d == 1 else L1, None, f[0])
        if op:
            op["obj"] = min(3.0, op["obj_ext"]) if tp == "min" else 3.0
            op["coste"] = COSTE
            filas.append(op)
    return df, pd.DataFrame(filas)


V = {f"Lectura {le} · TP {'mín(3R, extremo)' if tp == 'min' else '3R fijo'}": (lambda df, le=le, tp=tp: senales(df, le, tp))
     for le in ("A", "B") for tp in ("min", "3R")}
carga = lambda anios: {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in anios}

if __name__ == "__main__":
    if sys.argv[1:] == ["calibrar"]:
        df = carga([2021])[2021]
        for v in V:
            asim, rr = [], []
            for sd in range(24):
                o = mina.correr_variante(V[v], {2021: C.paseo_aleatorio(df, 900 + sd)})
                if len(o):
                    asim.append(((mina.r_obj(o) - mina.r_obj(o, True)) / 2).mean()); rr.append(mina.r_obj(o).mean())
            asim = np.array(asim)
            print(f"{v}: paseo R {np.mean(rr):+.4f} · asimetría {asim.mean():+.4f} ± {asim.std(ddof=1)/np.sqrt(len(asim)):.4f}")
        sys.exit()
    tab, sup, ops = mina.evaluar("CRT H1 Will Street", V, mina.r_obj, carga(IMPARES), lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    for v, o in ops.items():
        r = mina.r_obj(o)
        print(f"  {v}: n={len(o)} ({len(o)/4:.0f}/año) wr {(r>0).mean():.1%} · TP extremo mediano {o.obj_ext.median():.2f}R · stop mediano {o.riesgo_pts.median():.1f} pts · largos {(o.dir==1).mean():.0%}")
    if sup:
        print(f"\nVALIDACIÓN años pares para {sup} (p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = carga(PARES)
        for v in sup:
            o = mina.correr_variante(V[v], P); r = mina.r_obj(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} p1c={p:.4f} inv {mina.r_obj(o, True).mean():+.4f} años {py.round(3).to_dict()} → {'PASA' if p < 0.05/len(sup) and (py > 0).sum() >= 3 else 'NO PASA'}")
