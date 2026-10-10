"""Toto con mantener hasta SL/TP (corrección 1, uso nº16). preregistros/2026-10-10_pdfs_fxreplay.md"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, mina
from scripts.pdfs_fxreplay import toto, carga, r_fn, COSTE

NQ = carga("nq", range(2019, 2027)); ES = carga("es", range(2021, 2027))
for vent in ("londres", "ny"):
    fn = lambda df, v=vent: toto(df, v, COSTE["nq"], mantener=True)
    o = mina.correr_variante(fn, NQ); r = r_fn(o); s = C.resumen(r); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
    nul = [r_fn(x) for sd in range(6) if len(x := mina.correr_variante(fn, {a: C.paseo_aleatorio(d, 9100 + 13 * sd + a % 100) for a, d in NQ.items()}))]
    sn = C.resumen(np.concatenate(nul)); z = (s["R"] - sn["R"]) / np.sqrt(s["ee"] ** 2 + sn["ee"] ** 2)
    fe = lambda df, v=vent: toto(df, v, COSTE["es"], mantener=True); oe = mina.correr_variante(fe, ES); re_ = r_fn(oe)
    ok = s["p_1cola"] < 0.025 and (py > 0).sum() >= 6 and z > 1.65 and re_.mean() > 0
    print(f"{vent.upper()} (mantener hasta SL/TP): NQ n={s['n']} R={s['R']:+.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} inv {r_fn(o, True).mean():+.4f}")
    print(f"   años NQ {py.round(3).to_dict()}")
    print(f"   paseo R={sn['R']:+.4f} z={z:+.2f} · ES n={len(oe)} R={re_.mean():+.4f} años {pd.Series(re_).groupby(oe._a.to_numpy()).mean().round(3).to_dict()}")
    print(f"   → {'PASA' if ok else 'NO PASA'}")
