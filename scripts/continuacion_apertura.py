"""Continuación de la apertura (invertida de Xavi E1). preregistros/2026-10-08_continuacion_apertura.md"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, mina
from scripts.xavi_ruyra import e1, carga, PARES

regla = lambda df: e1(df, 3.0, filtro=True, invertir=True)
D = carga(PARES)
o = mina.correr_variante(regla, D); r = mina.r_obj(o); s = C.resumen(r)
py = pd.Series(r).groupby(o._a.to_numpy()).mean()
nul = []
for sd in range(12):
    on = mina.correr_variante(regla, {a: C.paseo_aleatorio(df, 5000 + 37 * sd + a % 100) for a, df in D.items()})
    if len(on): nul.append(mina.r_obj(on))
rn = np.concatenate(nul); sn = C.resumen(rn)
z = (s["R"] - sn["R"]) / np.sqrt(s["ee"] ** 2 + sn["ee"] ** 2)
print(f"CONTINUACIÓN DE LA APERTURA · años pares {PARES}")
print(f"n={s['n']} ({s['n']/4:.0f}/año) R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} · invertida {mina.r_obj(o, True).mean():+.4f}")
print(f"años {py.round(3).to_dict()} · stop mediano {o.riesgo_pts.median():.1f} pts · largos {(o.dir==1).mean():.0%}")
print(f"paseo aleatorio (12 semillas): R={sn['R']:+.4f} (n={sn['n']}) · exceso z={z:+.2f}")
ok = s["p_1cola"] < 0.05 and (py > 0).sum() >= 3 and z > 1.65
print("PASA" if ok else "NO PASA")
