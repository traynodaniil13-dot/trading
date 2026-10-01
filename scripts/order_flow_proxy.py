"""Ejecuta preregistros/2026-10-01_order_flow_proxy.md. Uso: diseno | validacion"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import loader, motor, premisas as P
from src.motores import momento_generico as MG

ANIOS = [2023, 2025] if sys.argv[1] == "diseno" else [2024]
nq = loader.cargar(verbose=False)
assert "v" in nq.columns
d = (nq.c - nq.o).to_numpy()
sig = pd.Series(d).rolling(1000, min_periods=1000).std().shift(1).to_numpy()   # causal
z = d / sig
nq["delta"] = nq.v.to_numpy() * (2 * stats.norm.cdf(z) - 1)

def D(a, b):
    m = (nq.hhmm >= a) & (nq.hhmm <= b)
    return nq[m].groupby("sesion").delta.sum(min_count=1)

g = P._rejilla(nq, [930, 939, 940, 1559])
D1 = D(930, 939); D2 = D(909, 939)
df = pd.DataFrame({"D": D1, "dp": g["c"][939] - g["o"][930], "y0": g["c"][1559] - g["o"][940]}).dropna()
df = df[df.index.year.isin(ANIOS)]

def rep(nom, x):
    s = np.sign(x.D); y = x.y0 * s; y = y[s != 0]
    t, p = stats.ttest_1samp(y, 0)
    anio = y.groupby(y.index.year).mean().round(2).to_dict()
    L, S = y[s[s != 0] > 0].mean(), y[s[s != 0] < 0].mean()
    ok = p < 0.0167 and len(set(np.sign(list(anio.values())))) == 1 and np.sign(L) == np.sign(S) and abs(y.mean()) > 0.87
    print(f"{nom}: n={len(y)} media={y.mean():+.2f} pts ee={y.std(ddof=1)/np.sqrt(len(y)):.2f} p={p:.4f} | años {anio} | "
          f"largos {L:+.2f} cortos {S:+.2f} -> {'PASA' if ok else 'no'}")

rep("O1 flujo apertura", df)
rep("O2 absorción", df[np.sign(df.D) != np.sign(df.dp)])

# O3 filtro para Momento
o = motor.simular(nq, MG.senales(nq, 940, 30, 0.40)); o = o[o.sesion.dt.year.isin(ANIOS)].reset_index(drop=True)
r = motor.r_neta(o, 2.0)
dd = np.sign(D2.reindex(o.sesion).to_numpy())
acu = dd == o.dir.to_numpy(); des = (dd == -o.dir.to_numpy())
t, p2 = stats.ttest_ind(r[acu], r[des], equal_var=False); p1 = p2 / 2 if t > 0 else 1 - p2 / 2
rng = np.random.default_rng(0)
p95 = np.percentile([r[rng.choice(len(r), acu.sum(), replace=False)].mean() for _ in range(1000)], 95)
ok = p1 < 0.0167 and r[acu].mean() > p95
print(f"O3 filtro Momento: base n={len(r)} R={r.mean():+.3f} | de acuerdo n={acu.sum()} R={r[acu].mean():+.3f} | "
      f"en desacuerdo n={des.sum()} R={r[des].mean():+.3f} | dif p1c={p1:.3f} | azar p95 {p95:+.3f} -> {'PASA' if ok else 'no'}")
print("   por año (de acuerdo):", pd.Series(r[acu]).groupby(o.sesion.dt.year.to_numpy()[acu]).mean().round(3).to_dict())
