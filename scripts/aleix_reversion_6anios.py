"""Aleix reversión 09:30, las 6 variantes sin cambios en 2021-2026 (adenda 2 del pre-registro)."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from scripts.aleix_reversion_0930 import VARS, correr, rv

D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in range(2021, 2027)}
res = {}
for var, kw in VARS.items():
    o = correr(D, **kw); res[var] = o
    r = rv(o, var); s = C.resumen(r); yr = o.sesion.dt.year.to_numpy()
    py = pd.Series(r).groupby(yr).agg(["mean", "size"])
    val = np.isin(yr, [2022, 2024, 2026]); sv = C.resumen(r[val])
    inv = motor.r_neta(o, 1.5, True).mean()
    print(f"\n=== {var} {kw}: {len(o)} ops ({len(o)/5.75:.0f}/año) · obj mediano {o.obj.median():.2f}R")
    print(f"  6 AÑOS: R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} · invertida 1:1,5 {inv:+.3f}")
    print("  por año: " + " · ".join(f"{y} {m:+.3f} (n={int(n)})" for y, (m, n) in py.iterrows()))
    print(f"  solo 22/24/26: n={sv['n']} R={sv['R']:+.4f} p1c={sv['p_1cola']:.4f} wr {sv['wr']:.1%}")
    for rt in (1.0, 1.5, 2.0, 3.0):
        rr = motor.r_neta(o, rt)
        print(f"    1:{rt}: wr {(rr>0).mean():.1%} R {rr.mean():+.4f} · invertida {motor.r_neta(o, rt, True).mean():+.4f}")
print("\n=== PASEO ALEATORIO (6 semillas × 6 años)")
nulo = {v: [] for v in VARS}
for sem in range(6):
    P = {a: C.paseo_aleatorio(df, 3000 * a + sem) for a, df in D.items()}
    for var, kw in VARS.items():
        o = correr(P, **kw)
        if len(o): nulo[var].append(rv(o, var))
for var in VARS:
    rn = np.concatenate(nulo[var]); sn = C.resumen(rn); s = C.resumen(rv(res[var], var))
    print(f"  {var}: nulo R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={len(rn)}) · real {s['R']:+.4f} wr {s['wr']:.1%} · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")
