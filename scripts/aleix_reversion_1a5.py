"""Aleix reversión 09:30 a 1:5 en 2021-2026 (adenda 3 del pre-registro)."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from scripts.aleix_reversion_0930 import correr

D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in range(2021, 2027)}
V = {"V7 overnight": "on", "V8 RTH previo": "rth", "V9 DOL H1": "h1"}
res = {}
for nom, liq in V.items():
    o = correr(D, liq=liq, tp="r5"); res[nom] = o
    r = motor.r_neta(o, 5.0); s = C.resumen(r); yr = o.sesion.dt.year.to_numpy()
    py = pd.Series(r).groupby(yr).agg(["mean", "size"])
    tp = (o.rmax >= 5).mean(); sl = (~(o.rmax >= 5) & o.toco_sl).mean()
    print(f"\n=== {nom} 1:5: n={len(o)} · TP {tp:.1%} · SL {sl:.1%} · cierre 15:59 {1-tp-sl:.1%} · wr {s['wr']:.1%}")
    print(f"  R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · invertida {motor.r_neta(o, 5.0, True).mean():+.4f} · R total {s['R_total']:+.1f}")
    print("  por año: " + " · ".join(f"{y} {m:+.3f} (n={int(n)})" for y, (m, n) in py.iterrows()))
    rs = np.sort(r)[::-1]; print(f"  sin las 3 mejores operaciones: R={rs[3:].mean():+.4f}")
print("\n=== PASEO ALEATORIO (6 semillas × 6 años)")
nulo = {k: [] for k in V}
for sem in range(6):
    P = {a: C.paseo_aleatorio(df, 4000 * a + sem) for a, df in D.items()}
    for nom, liq in V.items():
        o = correr(P, liq=liq, tp="r5")
        if len(o): nulo[nom].append(motor.r_neta(o, 5.0))
for nom in V:
    rn = np.concatenate(nulo[nom]); sn = C.resumen(rn); s = C.resumen(motor.r_neta(res[nom], 5.0))
    print(f"  {nom}: nulo R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={len(rn)}) · real {s['R']:+.4f} · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")
