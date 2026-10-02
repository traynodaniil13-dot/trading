"""Ejecuta preregistros/2026-10-02_premisas_lote3_barreras.md."""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader

KS = (0.15, 0.25, 0.40); ANIOS = (2021, 2023, 2025)
NOMBRES = ["L1 dato 08:30", "L2 dato 10:00", "L3 vela gigante", "L4 vuelta al VWAP",
           "L5 número redondo", "L6 tarde 12:30-15:30", "L7 reversión mediodía", "L8 cerrar hueco"]


def carrera(h, l, c, j, tramo, d, k):
    b = c[j] * k / 100
    up = np.flatnonzero(h[tramo] >= c[j] + b); dn = np.flatnonzero(l[tramo] <= c[j] - b)
    tu = up[0] if up.size else 10**9; td = dn[0] if dn.size else 10**9
    tf, tc = (tu, td) if d == 1 else (td, tu)
    return 0 if tf == tc == 10**9 else (1 if tf < tc else -1)


def eventos(b, anio):
    o, h, l, c = (b[k].to_numpy() for k in ("o", "h", "l", "c"))
    v = b["v"].to_numpy() if "v" in b else np.ones(len(b))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    filas, cierre_prev = [], None
    for s in pd.unique(ses):
        ii = np.flatnonzero(ses == s); hm = hh[ii]
        en = lambda t: ii[hm == t]
        rest = ii[(hm >= 930) & (hm <= 1559)]
        if len(rest) < 300 or len(en(830)) == 0 or len(en(834)) == 0:
            cierre_prev = c[rest[-1]] if len(rest) else cierre_prev
            continue
        ev = []  # (premisa, j, d)
        j = en(834)[0]; ev.append((0, j, np.sign(c[j] - o[en(830)[0]])))
        if len(en(1000)) and len(en(1004)):
            j = en(1004)[0]; ev.append((1, j, np.sign(c[j] - o[en(1000)[0]])))
        rng_ = h - l
        for j in ii[(hm >= 1000) & (hm <= 1500)]:
            prev = ii[(ii < j)][-20:]
            if len(prev) == 20 and rng_[j] > 4 * np.median(rng_[prev]) and c[j] != o[j]:
                ev.append((2, j, np.sign(c[j] - o[j]))); break
        rth = ii[(hm >= 930)]
        cv = np.cumsum((c * v)[rth]); vv = np.cumsum(v[rth]); vw = pd.Series(cv / np.maximum(vv, 1e-12), index=rth)
        w = ii[(hm >= 1000) & (hm <= 1029)]
        if len(w) == 30:
            lado = np.sign(c[w] - vw[w].to_numpy())
            if (lado == lado[0]).all() and lado[0] != 0:
                for j in ii[(hm >= 1030) & (hm <= 1500)]:
                    if l[j] <= vw[j] <= h[j]:
                        ev.append((3, j, int(lado[0]))); break
        for j in ii[(hm >= 1000) & (hm <= 1500)]:
            piso = np.floor(c[j - 1] / 250) * 250; techo = piso + 250
            if h[j] >= techo and c[j - 1] < techo:
                ev.append((4, j, 1)); break
            if l[j] <= piso and c[j - 1] > piso:
                ev.append((4, j, -1)); break
        if len(en(1529)) and len(en(1229)):
            j = en(1529)[0]; ev.append((5, j, np.sign(c[j] - c[en(1229)[0]])))
        if len(en(1159)) and len(en(930)):
            j = en(1159)[0]; ev.append((6, j, -np.sign(c[j] - o[en(930)[0]])))
        if cierre_prev is not None and len(en(930)):
            j = en(930)[0]; ev.append((7, j, np.sign(cierre_prev - o[j])))
        cierre_prev = c[rest[-1]]
        if pd.Timestamp(s).year != anio:
            continue
        for p, j, d in ev:
            if d == 0:
                continue
            tramo = rest[rest > j]
            fila = {"p": p, "dir": int(d)}; fila.update({k: carrera(h, l, c, j, tramo, int(d), k) for k in KS}); filas.append(fila)
    return pd.DataFrame(filas)


def tabla(datos):
    e = pd.concat([eventos(b, a) for a, b in datos.items()], ignore_index=True)
    f = []
    for p in range(8):
        for k in KS:
            x = e[(e.p == p) & (e[k] != 0)]
            fav = (x[k] == 1).sum(); n = len(x)
            pl = (x[x.dir == 1][k] == 1).mean(); pc = (x[x.dir == -1][k] == 1).mean()
            f.append(dict(premisa=NOMBRES[p], k=k, n=n, favor=fav / n if n else np.nan, largos=pl, cortos=pc,
                          sin_resolver=(e[(e.p == p)][k] == 0).mean(),
                          p=stats.binomtest(fav, n, 0.5).pvalue if n else 1.0))
    return pd.DataFrame(f)


if __name__ == "__main__":
    dis = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in ANIOS}
    t = tabla(dis)
    nul = []
    for sem in range(6):
        tn = tabla({a: C.paseo_aleatorio(b, 19000 + 10 * sem + a % 10) for a, b in dis.items()})
        nul.append((tn.favor - 0.5).abs().max()); print(f"nulo semilla {sem}: máx |favor−50%| {nul[-1]:.3f}", flush=True)
    p95 = np.percentile(nul, 95) if len(nul) > 1 else nul[0]
    umbral_nulo = np.mean(nul) + 1.645 * np.std(nul, ddof=1)
    t["dev"] = (t.favor - 0.5).abs()
    t["mismo_lado"] = np.sign(t.largos - 0.5) == np.sign(t.cortos - 0.5)
    t["PASA"] = (t.p < 0.05 / 24) & t.mismo_lado & (t.dev > umbral_nulo)
    pd.set_option("display.width", 250)
    print(f"\nnulo: máx |favor−50%| media {np.mean(nul):.3f} ± {np.std(nul, ddof=1):.3f} → umbral {umbral_nulo:.3f}\n")
    print(t.sort_values("p").round(3).to_string(index=False))
    print("\nPASAN:", ", ".join(f"{r.premisa} ±{r.k}%" for r in t[t.PASA].itertuples()) or "ninguna")
