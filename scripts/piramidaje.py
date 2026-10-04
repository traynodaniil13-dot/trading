"""Piramidaje vs entrada única vs promedio a la baja. preregistros/2026-10-04_piramidaje_investcoin.md"""
import numpy as np, pandas as pd
from scipy import stats
from scripts.davey_sp500 import continuo, diarias


def sistema(O, H, L, Cc, modo):
    """Devuelve lista de (i_entrada, resultado en R0, peor punto en R0) por setup."""
    n = len(Cc)
    pc = np.r_[np.nan, Cc[:-1]]
    tr = np.maximum(H - L, np.maximum(np.abs(H - pc), np.abs(L - pc)))
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    res = pd.Series(H).shift(1).rolling(20).max().to_numpy()
    out = []
    t = 21
    while t < n - 1:
        if not (Cc[t] > res[t] and np.isfinite(atr[t])):
            t += 1; continue
        R = res[t]; sl0 = R - 0.5 * atr[t]
        # primera compra: retesteo t+1..t+5
        f = None
        for k in range(t + 1, min(n, t + 6)):
            if L[k] <= R:
                f = k; break
        if f is None:
            t += 1; continue
        e0 = min(O[f], R); R0 = e0 - sl0
        if R0 <= 0:
            t = f + 1; continue
        unidades = [e0]; stop = sl0; ultimo = R
        pend = None  # (nivel límite, vence) para añadir
        if modo == "C":
            stop = e0 - 3 * atr[t]; R0 = e0 - sl0
            esc = [e0 - atr[t], e0 - 2 * atr[t]]
        k = f; peor = 0.0; salida = None
        while k < n:
            # stop primero (el día del relleno solo cuenta el stop)
            if L[k] <= stop:
                px = min(O[k], stop) if k > f else stop
                salida = sum(px - u for u in unidades) / R0; break
            if k > f:
                if modo == "C":
                    for lv in list(esc):
                        if L[k] <= lv and len(unidades) < 3:
                            unidades.append(min(O[k], lv)); esc.remove(lv)
                if modo == "B" and pend is not None:
                    lv, vence = pend
                    if L[k] <= lv and len(unidades) < 3:
                        unidades.append(min(O[k], lv)); pend = None
                    elif k >= vence:
                        pend = None
            peor = min(peor, sum(L[k] - u for u in unidades) / R0)
            # ruptura nueva al cierre de k: sube el trailing (y en B prepara añadido)
            if k > f and np.isfinite(res[k]) and Cc[k] > res[k] and res[k] > ultimo:
                ultimo = res[k]
                stop = max(stop, res[k] - 0.5 * atr[k])
                if modo == "B" and len(unidades) < 3:
                    pend = (res[k], k + 5)
            k += 1
        if salida is None:  # fin de datos
            salida = sum(Cc[-1] - u for u in unidades) / R0; k = n - 1
        out.append((f, salida, peor, len(unidades)))
        t = k + 1
    return out


def mercados():
    m = {}
    for pref in ("nq", "es"):
        d = diarias(continuo(pref)); m[pref.upper()] = d[["o", "h", "l", "c"]]
    try:
        from scripts.magala_fuerza import cargar
        W = cargar()
        for par in W["c"].columns:
            df = pd.DataFrame({k: W[k][par] for k in ("o", "h", "l", "c")}).dropna()
            m[par] = df
    except Exception as e:
        print("sin divisas:", e)
    return m


def correr(m):
    filas = []
    for nom, df in m.items():
        O, H, L, Cc = (df[k].to_numpy(float) for k in ("o", "h", "l", "c"))
        r = {x: sistema(O, H, L, Cc, x) for x in "ABC"}
        # emparejar por fecha de primera entrada (A, B y C comparten la primera compra)
        ia = {f: v for f, *v in r["A"]}; ib = {f: v for f, *v in r["B"]}; ic = {f: v for f, *v in r["C"]}
        for f in sorted(set(ia) & set(ib) & set(ic)):
            filas.append(dict(m=nom, fecha=df.index[f], A=ia[f][0], B=ib[f][0], C=ic[f][0], peorA=ia[f][1], peorB=ib[f][1],
                              peorC=ic[f][1], nB=ib[f][2], nC=ic[f][2]))
    return pd.DataFrame(filas)


def barajar(df, rng):
    """Reordena los días: conserva rangos y retornos diarios, destruye la tendencia."""
    pc = df.c.shift(1)
    rel = pd.DataFrame({k: np.log(df[k] / pc) for k in "ohlc"}).dropna().to_numpy()
    rel = rel[rng.permutation(len(rel))]
    c0 = df.c.iat[0]; lvl = c0 * np.exp(np.cumsum(rel[:, 3]))
    prev = np.r_[c0, lvl[:-1]]
    return pd.DataFrame({k: prev * np.exp(rel[:, i]) for i, k in enumerate("ohlc")}, index=df.index[1:])


if __name__ == "__main__":
    m = mercados()
    x = correr(m)
    print(f"setups {len(x)} en {x.m.nunique()} mercados · índices {x.m.isin(['NQ','ES']).sum()} · divisas {(~x.m.isin(['NQ','ES'])).sum()}")
    for v in "ABC":
        print(f"  {v}: media {x[v].mean():+.3f} R0 · mediana {x[v].median():+.3f} · positivas {(x[v]>0).mean():.0%} · peor operación {x[v].min():+.1f} · "
              f"peor punto medio {x['peor'+v].mean():+.2f} · total {x[v].sum():+.0f}")
    print(f"  unidades medias: B {x.nB.mean():.2f} · C {x.nC.mean():.2f}")
    d = x.B - x.A; t, p2 = stats.ttest_1samp(d, 0)
    print(f"H1 B − A: {d.mean():+.3f} R0 por setup · p1c={p2/2 if t>0 else 1-p2/2:.4f}")
    for grupo, msk in (("índices", x.m.isin(["NQ", "ES"])), ("divisas", ~x.m.isin(["NQ", "ES"]))):
        g = x[msk]
        print(f"  {grupo}: n={len(g)} · A {g.A.mean():+.3f} · B {g.B.mean():+.3f} · C {g.C.mean():+.3f}")
    por = x.groupby(x.fecha.dt.year)[["A", "B", "C"]].mean().round(3)
    print("  por año:\n" + por.to_string())
    for v in "ABC":
        s = x.sort_values("fecha")[v].cumsum().to_numpy(); dd = (np.maximum.accumulate(np.r_[0, s]) - np.r_[0, s]).max()
        print(f"  drawdown máximo de la suma {v}: {dd:.1f} R0")
    rng = np.random.default_rng(1); nul = []
    for rep in range(50):
        mb = {k: barajar(df, rng) for k, df in m.items()}
        nul.append(correr(mb).B.mean())
    nul = np.array(nul); ee = x.B.std() / np.sqrt(len(x))
    z = (x.B.mean() - nul.mean()) / np.sqrt(ee**2 + nul.std()**2)
    print(f"H2 B real {x.B.mean():+.3f} vs barajado {nul.mean():+.3f} ± {nul.std():.3f} · z={z:+.2f}")
