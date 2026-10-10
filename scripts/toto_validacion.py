"""Validación de Toto Londres (uso nº15). preregistros/2026-10-10_pdfs_fxreplay.md (adenda)"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, mina
from scripts.pdfs_fxreplay import familias, carga, r_fn

fn = familias("nq")["toto"]["Londres"]
P = carga("nq", (2020, 2022, 2024, 2026))
o = mina.correr_variante(fn, P); r = r_fn(o); s = C.resumen(r); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
nul = [r_fn(x) for sd in range(12) if len(x := mina.correr_variante(fn, {a: C.paseo_aleatorio(d, 7700 + 41 * sd + a % 100) for a, d in P.items()}))]
rn = np.concatenate(nul); sn = C.resumen(rn); z = (s["R"] - sn["R"]) / np.sqrt(s["ee"] ** 2 + sn["ee"] ** 2)
print(f"NQ pares: n={s['n']} R={s['R']:+.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} inv {r_fn(o, True).mean():+.4f} años {py.round(3).to_dict()}")
print(f"paseo aleatorio: R={sn['R']:+.4f} · z={z:+.2f}")
fe = familias("es")["toto"]["Londres"]; oe = mina.correr_variante(fe, carga("es", (2022, 2024, 2026))); re_ = r_fn(oe)
print(f"ES pares: n={len(oe)} R={re_.mean():+.4f} wr {(re_>0).mean():.1%} años {pd.Series(re_).groupby(oe._a.to_numpy()).mean().round(3).to_dict()}")
ok = s["p_1cola"] < 0.05 and (py > 0).sum() >= 3 and z > 1.65 and re_.mean() > 0
print("PASA" if ok else "NO PASA")
