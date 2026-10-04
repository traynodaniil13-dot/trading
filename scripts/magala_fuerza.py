"""Magalá, fuerza relativa de divisas. preregistros/2026-10-04_magala_fuerza_divisas.md"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C
from scripts.descargar_fx_diario import RAIZ, DIV, PARES


def cruces_sinteticos():
    """Plan B: 28 pares desde los 7 contra el dólar. Valor de cada divisa en USD; par A/B = vA/vB.
    Cierre y apertura exactos (salvo diferencial). Máximo/mínimo APROXIMADOS: el máximo de A/B se
    toma como max(o, c, hA/mB, mA/lB) con m = media de apertura y cierre (no se sabe si A y B
    hicieron su extremo a la vez)."""
    df = pd.read_csv(RAIZ / "data/fx_diario_usd.csv.gz", parse_dates=["fecha"])
    df["fecha"] = df.fecha.dt.normalize()
    W = {k: df.pivot_table(index="fecha", columns="par", values=k) for k in ("o", "h", "l", "c")}
    v = {}
    for x in DIV:
        if x == "USD":
            uno = pd.Series(1.0, index=W["c"].index); v[x] = dict(o=uno, h=uno, l=uno, c=uno)
        elif x + "USD" in W["c"]:
            p = x + "USD"; v[x] = {k: W[k][p] for k in "ohlc"}
        else:
            p = "USD" + x
            v[x] = dict(o=1 / W["o"][p], c=1 / W["c"][p], h=1 / W["l"][p], l=1 / W["h"][p])
    filas = []
    for par in PARES:
        a, b = v[par[:3]], v[par[3:]]
        o, c = a["o"] / b["o"], a["c"] / b["c"]
        ma, mb = (a["o"] + a["c"]) / 2, (b["o"] + b["c"]) / 2
        h = pd.concat([o, c, a["h"] / mb, ma / b["l"]], axis=1).max(axis=1)
        l = pd.concat([o, c, a["l"] / mb, ma / b["h"]], axis=1).min(axis=1)
        filas.append(pd.DataFrame({"par": par, "fecha": o.index, "o": o.values, "h": h.values, "l": l.values, "c": c.values}))
    return pd.concat(filas).dropna()


def cargar():
    if (RAIZ / "data/fx_diario.csv.gz").exists():
        df = pd.read_csv(RAIZ / "data/fx_diario.csv.gz", parse_dates=["fecha"])
    else:
        df = cruces_sinteticos()
    df["fecha"] = df.fecha.dt.normalize()
    W = {k: df.pivot_table(index="fecha", columns="par", values=k) for k in ("o", "h", "l", "c")}
    fechas = W["c"].dropna(thresh=20).index  # días con casi todos los pares
    return {k: v.reindex(fechas).ffill() for k, v in W.items()}


def fuerza(W, N):
    c, h, l = W["c"], W["h"], W["l"]
    pos = {}
    for p in PARES:
        hi, lo = h[p].rolling(N).max(), l[p].rolling(N).min()
        pos[p] = 100 * (2 * (c[p] - lo) / (hi - lo) - 1)
    F = pd.DataFrame(index=c.index)
    for x in DIV:
        cols = [pos[p] if p.startswith(x) else -pos[p] for p in PARES if x in p]
        F[x] = pd.concat(cols, axis=1).mean(axis=1)
    return F


def indicadores(W):
    c, h, l = W["c"], W["h"], W["l"]
    pc = c.shift(1)
    tr = np.maximum(h - l, np.maximum((h - pc).abs(), (l - pc).abs()))
    return tr.rolling(14).mean(), c.ewm(span=50, adjust=False).mean(), c.ewm(span=100, adjust=False).mean()


def senales(F, desde="2021-01-01"):
    out = []
    v = F.to_numpy(); fechas = F.index
    for t in range(1, len(F) - 1):
        if fechas[t] < pd.Timestamp(desde) or np.isnan(v[t]).any() or np.isnan(v[t - 1]).any():
            continue
        for i, x in enumerate(DIV):
            if v[t, i] <= -50 < v[t - 1, i]:
                y = DIV[int(np.argmax(v[t]))]; lado = 1   # largo X/Y
            elif v[t, i] >= 50 > v[t - 1, i]:
                y = DIV[int(np.argmin(v[t]))]; lado = -1  # corto X/Y
            else:
                continue
            if y == x:
                continue
            par = x + y if x + y in PARES else y + x
            d = lado if par == x + y else -lado
            out.append((t, par, d))
    return out


def simular(W, ind, sen, invertir=False):
    atr, e50, e100 = ind
    o, h, l, c = (W[k] for k in ("o", "h", "l", "c"))
    res, libre = [], {}
    for t, par, d in sen:
        if invertir:
            d = -d
        a = t + 1
        if libre.get(par, -1) >= a:
            continue
        p = o[par].iat[a]; R = 5 * atr[par].iat[t]
        if not np.isfinite(R) or R <= 0:
            continue
        coste = 0.03 if par.endswith("JPY") else 0.0003
        sl = p - d * R; abiertos = {"e50": 0.5, "e100": 0.5}; pnl = 0.0; k = a
        llegan = set()
        while abiertos and k < len(c):
            if (d == 1 and l[par].iat[k] <= sl) or (d == -1 and h[par].iat[k] >= sl):
                pnl += sum(abiertos.values()) * (-1.0); abiertos = {}; break
            if k > a:
                for nom, ema in (("e50", e50), ("e100", e100)):
                    if nom in abiertos:
                        nivel = ema[par].iat[k - 1]
                        if l[par].iat[k] <= nivel <= h[par].iat[k]:
                            pnl += abiertos.pop(nom) * (nivel - p) * d / R; llegan.add(nom)
            k += 1
        if abiertos:  # fin de datos
            k = len(c) - 1; pnl += sum(abiertos.values()) * (c[par].iat[k] - p) * d / R
        res.append(dict(fecha=c.index[a], par=par, d=d, r=pnl - coste / R, dias=(c.index[min(k, len(c) - 1)] - c.index[a]).days,
                        e50="e50" in llegan, e100="e100" in llegan))
        libre[par] = k
    return pd.DataFrame(res)


if __name__ == "__main__":
    W = cargar(); ind = indicadores(W); rng = np.random.default_rng(0)
    for nom, N in (("V1 N=14", 14), ("V2 N=20", 20)):
        sen = senales(fuerza(W, N)); o = simular(W, ind, sen)
        s = C.resumen(o.r.to_numpy()); inv = simular(W, ind, sen, invertir=True)
        print(f"\n=== {nom}: n={s['n']} ({s['n']/5.7:.0f}/año) · wr {s['wr']:.1%} · R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · "
              f"duración mediana {o.dias.median():.0f} días · llega a EMA50 {o.e50.mean():.0%} · EMA100 {o.e100.mean():.0%}")
        print("  por año: " + " · ".join(f"{y} {m:+.3f} (n={int(n)})" for y, (m, n) in o.groupby(o.fecha.dt.year).r.agg(['mean', 'size']).iterrows()))
        print(f"  invertida: R={inv.r.mean():+.4f} (n={len(inv)})")
        azar = []
        for rep in range(200):
            sa = [(t, PARES[rng.integers(len(PARES))], int(rng.choice([-1, 1]))) for t, _, _ in sen]
            azar.append(simular(W, ind, sa).r.mean())
        azar = np.array(azar)
        print(f"  entrada al azar (200): media {azar.mean():+.4f} · p95 {np.percentile(azar, 95):+.4f} · real {s['R']:+.4f} · p azar {(azar >= s['R']).mean():.3f}")
        ok = s["R"] > 0 and s["p_1cola"] < 0.025 and s["R"] > np.percentile(azar, 95) and inv.r.mean() <= 0
        print("  ->", "PASA" if ok else "NO PASA")
