"""Aleix reversión 09:30 con TP estructural (FVG 15m / pivote 15m), 2021-2026 (adenda 4)."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from scripts.aleix_reversion_0930 import correr, r_obj

D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in range(2021, 2027)}
V = {"V10 overnight · TP FVG15": ("on", "fvg15"), "V11 overnight · TP pivote15": ("on", "piv15"),
     "V12 DOL H1 · TP FVG15": ("h1", "fvg15"), "V13 DOL H1 · TP pivote15": ("h1", "piv15")}
res = {}
for nom, (liq, tp) in V.items():
    o = correr(D, liq=liq, tp=tp); res[nom] = o
    r = r_obj(o); s = C.resumen(r); yr = o.sesion.dt.year.to_numpy()
    py = pd.Series(r).groupby(yr).agg(["mean", "size"])
    gana = (o.rmax >= o.obj).mean(); sl = (~(o.rmax >= o.obj) & o.toco_sl).mean()
    q = o.obj.quantile([.25, .5, .75]).round(2).tolist()
    print(f"\n=== {nom}: n={len(o)} · TP a {q[1]}R de mediana (p25 {q[0]} · p75 {q[2]}) · toca TP {gana:.1%} · SL {sl:.1%} · cierre {1-gana-sl:.1%}")
    print(f"  R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} · R total {s['R_total']:+.1f}")
    print("  por año: " + " · ".join(f"{y} {m:+.3f} (n={int(n)})" for y, (m, n) in py.iterrows()))
print("\n=== PASEO ALEATORIO (6 semillas × 6 años)")
nulo = {k: [] for k in V}
for sem in range(6):
    P = {a: C.paseo_aleatorio(df, 5000 * a + sem) for a, df in D.items()}
    for nom, (liq, tp) in V.items():
        o = correr(P, liq=liq, tp=tp)
        if len(o): nulo[nom].append(r_obj(o))
for nom in V:
    rn = np.concatenate(nulo[nom]); sn = C.resumen(rn); s = C.resumen(r_obj(res[nom]))
    print(f"  {nom}: nulo R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={len(rn)}) · real {s['R']:+.4f} wr {s['wr']:.1%} · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")
