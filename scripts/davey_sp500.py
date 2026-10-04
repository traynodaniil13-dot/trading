"""Kevin Davey inside bar + EMA40, solo largos, 2xATR21 1:1. preregistros/2026-10-04_davey_sp500.md"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader


def diarias(b):
    pos = np.arange(len(b))
    g = pd.DataFrame({"s": b.sesion.to_numpy(), "o": b.o.to_numpy(), "h": b.h.to_numpy(), "l": b.l.to_numpy(),
                      "c": b.c.to_numpy(), "p": pos}).groupby("s", sort=True)
    d = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "p0": g.p.first(), "n": g.p.size()})
    d = d[d.n >= 300].copy()
    pc = d.c.shift(1)
    tr = np.maximum(d.h - d.l, np.maximum((d.h - pc).abs(), (d.l - pc).abs()))
    d["atr"] = tr.rolling(21).mean(); d["ema"] = d.c.ewm(span=40, adjust=False).mean()
    return d


def senales(d, solo_tendencia=False):
    H, L, Cc = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    out = []
    for k in range(60, len(d) - 1):  # warm-up de 60 sesiones
        assert k - 2 >= 0
        ok = Cc[k] > d.ema.iat[k]
        if not solo_tendencia:
            ok = ok and H[k - 2] > H[k - 1] and L[k - 2] < L[k - 1] and Cc[k] > H[k - 1]
        if ok:
            out.append((int(d.p0.iat[k + 1]), 2 * d.atr.iat[k], d.index[k + 1]))
    return out


def simular(b, sen, coste):
    h, l, c, o = (b[k].to_numpy(float) for k in ("h", "l", "c", "o"))
    res, libre = [], -1
    for a, delta, ses in sen:
        if a <= libre:
            continue
        p = o[a]; sl, tp = p - delta, p + delta
        hit_sl = np.flatnonzero(l[a:] <= sl); hit_tp = np.flatnonzero(h[a + 1:] >= tp) + 1
        ks = hit_sl[0] if hit_sl.size else 10**12; kt = hit_tp[0] if hit_tp.size else 10**12
        if ks == kt == 10**12:
            break  # sigue abierta al final de los datos
        r = (-1.0 if ks <= kt else 1.0) - coste / delta
        libre = a + min(ks, kt)
        res.append(dict(ses=ses, r=r, dias=(b.index[libre] - b.index[a]).days, riesgo=delta))
    return pd.DataFrame(res)


def informe(nom, b, coste):
    d = diarias(b)
    o = simular(b, senales(d), coste); base = simular(b, senales(d, True), coste)
    s, sb = C.resumen(o.r.to_numpy()), C.resumen(base.r.to_numpy())
    t, p2 = stats.ttest_ind(o.r, base.r, equal_var=False)
    print(f"\n=== {nom}: n={s['n']} ({s['n']/5.75:.1f}/año) · wr {s['wr']:.1%} · R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · "
          f"duración mediana {o.dias.median():.0f} días · riesgo mediano {o.riesgo.median():.0f} pts")
    print("  por año: " + " · ".join(f"{y} {m:+.2f} (n={int(n)})" for y, (m, n) in o.groupby(o.ses.dt.year).r.agg(['mean', 'size']).iterrows()))
    print(f"  base solo tendencia: n={sb['n']} wr {sb['wr']:.1%} R={sb['R']:+.4f} · diferencia {s['R']-sb['R']:+.4f} p1c={p2/2 if t>0 else 1-p2/2:.3f}")
    return s, d


def continuo(pref):
    """Concatena los ficheros anuales (cada uno trae el diciembre previo) sin duplicados."""
    partes = [loader.cargar_cfd([r], verbose=False) for r in sorted(loader.RAIZ.glob(f"data/{pref}_cfd_202*.csv.gz"))]
    df = pd.concat(partes); df = df[~df.index.duplicated(keep="last")].sort_index()
    assert not df.index.duplicated().any()
    return df


if __name__ == "__main__":
    es = continuo("es")
    s, _ = informe("DAVEY · S&P 500 CFD 2021-2026", es, 0.65)
    rn = []
    for sem in range(6):
        P = C.paseo_aleatorio(es, 13000 + sem)
        o = simular(P, senales(diarias(P)), 0.65); rn.append(o.r.to_numpy())
    sn = C.resumen(np.concatenate(rn))
    print(f"  paseo aleatorio: R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={sn['n']}) · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")
    print("  ->", "PASA" if s["R"] > 0 and s["p_1cola"] < 0.05 else "NO PASA")
    nq = continuo("nq")
    informe("Informativo · el mismo en NQ CFD 2021-2026", nq, 0.87)
