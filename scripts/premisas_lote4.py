"""Ejecuta preregistros/2026-10-02_premisas_lote4_barreras.md."""
import numpy as np, pandas as pd
from scipy import stats
from src import loader
from scripts.premisas_lote3 import carrera, KS

NOMBRES = ["M1 3 días seguidos (reversión)", "M2 día previo enorme", "M3 1ª vela 5m con cuerpo",
           "M4 rotura de inside day", "M5 apertura fuera del rango previo", "M6 lunes"]


def eventos(b, anio):
    o, h, l, c = (b[k].to_numpy() for k in ("o", "h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    dias = []
    for s in pd.unique(ses):
        ii = np.flatnonzero(ses == s); hm = ii[(hh[ii] >= 930) & (hh[ii] <= 1559)]
        if len(hm) < 300:
            continue
        dias.append(dict(s=s, ii=ii, rth=hm, O=o[hm[0]], H=h[hm].max(), L=l[hm].min(), C=c[hm[-1]]))
    filas = []
    for t in range(21, len(dias)):
        D, P = dias[t], dias[t - 1]
        if pd.Timestamp(D["s"]).year != anio:
            continue
        rth, ii = D["rth"], D["ii"]; j0 = rth[0]; ev = []
        cs = [dias[t - q]["C"] for q in range(1, 5)]  # C[t-1], C[t-2], C[t-3], C[t-4]
        if cs[0] < cs[1] < cs[2] < cs[3]:
            ev.append((0, j0, 1))
        elif cs[0] > cs[1] > cs[2] > cs[3]:
            ev.append((0, j0, -1))
        rngs = [dias[t - q]["H"] - dias[t - q]["L"] for q in range(2, 22)]
        if P["H"] - P["L"] > 2 * np.mean(rngs) and P["C"] != P["O"]:
            ev.append((1, j0, np.sign(P["C"] - P["O"])))
        j5 = rth[4]; cuerpo = c[j5] - o[j0]; rg = h[rth[:5]].max() - l[rth[:5]].min()
        if rg > 0 and abs(cuerpo) > 0.6 * rg:
            ev.append((2, j5, np.sign(cuerpo)))
        PP = dias[t - 2]
        if P["H"] < PP["H"] and P["L"] > PP["L"]:
            for j in rth[hh[rth] <= 1100]:
                if h[j] > P["H"] and l[j] < P["L"]:
                    break
                if h[j] > P["H"] or l[j] < P["L"]:
                    ev.append((3, j, 1 if h[j] > P["H"] else -1)); break
        if D["O"] > P["H"]:
            ev.append((4, j0, 1))
        elif D["O"] < P["L"]:
            ev.append((4, j0, -1))
        if pd.Timestamp(D["s"]).dayofweek == 0:
            pre = ii[hh[ii] == 929]
            if len(pre):
                ev.append((5, pre[0] + 1, np.sign(c[pre[0]] - P["C"])))
        for p, j, d in ev:
            if d == 0:
                continue
            tramo = rth[rth > j]
            fila = {"p": p, "dir": int(d)}; fila.update({k: carrera(h, l, c, j, tramo, int(d), k) for k in KS}); filas.append(fila)
    return pd.DataFrame(filas)


e = pd.concat([eventos(loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False), a) for a in (2021, 2023, 2025)], ignore_index=True)
f = []
for p in range(6):
    for k in KS:
        x = e[(e.p == p) & (e[k] != 0)]; fav = (x[k] == 1).sum(); n = len(x)
        pl = (x[x.dir == 1][k] == 1).mean(); pc = (x[x.dir == -1][k] == 1).mean()
        pv = stats.binomtest(fav, n, 0.5).pvalue if n else 1.0
        f.append(dict(premisa=NOMBRES[p], k=k, n=n, favor=fav / n if n else np.nan, largos=pl, cortos=pc, p=pv,
                      PASA=pv < 0.05 / 18 and np.sign(pl - 0.5) == np.sign(pc - 0.5)))
t = pd.DataFrame(f); pd.set_option("display.width", 250)
print(t.sort_values("p").round(3).to_string(index=False))
print("\nPASAN:", ", ".join(f"{r.premisa} ±{r.k}%" for r in t[t.PASA].itertuples()) or "ninguna")
