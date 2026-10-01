"""Ejecuta preregistros/2026-10-01_nq_lote3_eventos.md en DISEÑO. No cambiar nada."""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader

FOMC = {2021: "0127 0317 0428 0616 0728 0922 1103 1215", 2023: "0201 0322 0503 0614 0726 0920 1101 1213",
        2025: "0129 0319 0507 0618 0730 0917 1029 1210"}
UMBRAL = 0.0125


def pos(b, hh):
    m = b.hhmm.to_numpy() == hh
    s = pd.Series(np.flatnonzero(m), index=b.sesion.to_numpy()[m]); return s[~s.index.duplicated()]


filas = {k: [] for k in ("F1", "F2", "F3", "F4")}
for a, fs in FOMC.items():
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o, h, l, c = (b[k].to_numpy() for k in "ohlc")
    fom = set(pd.to_datetime([f"{a}{m}" for m in fs.split()]))
    P = {t: pos(b, t) for t in (930, 950, 1000, 1001, 1059, 1359, 1404, 1405, 1559)}
    ses = sorted(set.intersection(*[set(v.index) for v in P.values()]))
    ses = [s for s in ses if pd.Timestamp(s).year == a]
    todas = sorted(set(b.sesion[b.sesion.dt.year == a]))
    for s in ses:
        if s in fom:
            d = np.sign(c[P[1404][s]] - c[P[1359][s]])
            if d != 0: filas["F1"].append((s, int(d), (c[P[1559][s]] - o[P[1405][s]]) * d))
        filas["F2"].append((s, s in fom, c[P[1359][s]] - o[P[930][s]]))
        k = P[1000][s]; pre = np.arange(P[950][s], k)
        assert len(pre) == 10 and (b.hhmm.to_numpy()[pre] >= 950).all()
        if (h[k] - l[k]) > 2 * np.mean(h[pre] - l[pre]) and c[k] != o[k]:
            d = 1 if c[k] > o[k] else -1
            filas["F3"].append((s, d, (c[P[1059][s]] - o[P[1001][s]]) * d))
        i = todas.index(s)
        if i + 1 < len(todas):
            gap = np.busday_count(pd.Timestamp(s).date(), pd.Timestamp(todas[i + 1]).date())
            filas["F4"].append((s, gap > 1, c[P[1559][s]] - o[P[930][s]]))


def linea(nombre, x, anios, dos_colas=False, dirs=None):
    s = C.resumen(x); t = s["t"]
    p = 2 * stats.t.sf(abs(t), s["n"] - 1) if dos_colas else s["p_1cola"]
    sig = {a: round(float(np.mean(x[anios == a])), 1) for a in sorted(set(anios))}
    mismo = len({np.sign(v) for v in sig.values()}) == 1
    extra = ""
    if dirs is not None:
        L, S = x[dirs == 1].mean(), x[dirs == -1].mean(); extra = f" · largos {L:+.1f} cortos {S:+.1f}"
        mismo = mismo and np.sign(L) == np.sign(S) == np.sign(s["R"])
    ok = p < UMBRAL and mismo
    print(f"{nombre:34s} n={s['n']:4d} media={s['R']:+.2f} pts p={p:.4f}{' (2c)' if dos_colas else ''} años {sig}{extra}  → {'PASA' if ok else 'no pasa'}")


print("== NQ · LOTE 3 · EVENTOS · DISEÑO 2021/23/25 · umbral p < 0,0125 ==")
f1 = pd.DataFrame(filas["F1"], columns=["s", "d", "p"]); y = pd.to_datetime(f1.s).dt.year.to_numpy()
linea("F1 reacción FOMC 14:05→15:59", f1.p.to_numpy(), y, True, f1.d.to_numpy())
f2 = pd.DataFrame(filas["F2"], columns=["s", "fomc", "p"]); f2["y"] = pd.to_datetime(f2.s).dt.year
base = f2[~f2.fomc].groupby("y").p.mean(); ex = f2[f2.fomc].apply(lambda r: r.p - base[r.y], axis=1)
linea("F2 deriva pre-FOMC (exceso)", ex.to_numpy(), f2[f2.fomc].y.to_numpy())
f3 = pd.DataFrame(filas["F3"], columns=["s", "d", "p"])
linea("F3 dato 10:00 (10:01→10:59)", f3.p.to_numpy(), pd.to_datetime(f3.s).dt.year.to_numpy(), False, f3.d.to_numpy())
f4 = pd.DataFrame(filas["F4"], columns=["s", "pre", "p"]); f4["y"] = pd.to_datetime(f4.s).dt.year
base4 = f4[~f4.pre].groupby("y").p.mean(); ex4 = f4[f4.pre].apply(lambda r: r.p - base4[r.y], axis=1)
linea("F4 víspera de festivo (exceso)", ex4.to_numpy(), f4[f4.pre].y.to_numpy())
