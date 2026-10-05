"""OPEN_DRIVE m=5 cuerpo>0,8 en años no vistos. preregistros/2026-10-05_open_drive_m5_80_ciego.md"""
import numpy as np, pandas as pd
from src import controles as C, loader, mina, motor
from scripts.mina_nq_tanda2 import n3

FN = n3(5, 0.8)
A = (2019, 2020, 2022, 2024, 2026)
D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in A}
o = mina.correr_variante(FN, D); r = mina.r_obj(o); ri = mina.r_obj(o, True); s = C.resumen(r)
yr = o._a.to_numpy()
print(f"OPEN_DRIVE m=5 cuerpo>0,8 · años no vistos {A}: n={s['n']} ({s['n']/4.75:.0f}/año) · wr {s['wr']:.1%} · "
      f"R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · invertida {ri.mean():+.4f}")
print("  por año: " + " · ".join(f"{y} {m:+.3f} (n={int(n)})" for y, (m, n) in pd.Series(r).groupby(yr).agg(["mean", "size"]).iterrows()))
b1, b2 = r[np.isin(yr, [2019, 2020])], r[np.isin(yr, [2022, 2024, 2026])]
s1, s2 = C.resumen(b1), C.resumen(b2)
print(f"  bloque 2019-2020: n={s1['n']} R={s1['R']:+.4f} p1c={s1['p_1cola']:.3f} · bloque 2022/24/26: n={s2['n']} R={s2['R']:+.4f} p1c={s2['p_1cola']:.3f}")
for rt in (1.0, 1.5, 3.0):
    x = o.copy(); x["obj"] = rt; rr = mina.r_obj(x); print(f"  informativo 1:{rt:g}: wr {(rr>0).mean():.1%} R {rr.mean():+.4f}")
nul = []
for sem in range(12):
    on = mina.correr_variante(FN, {a: C.paseo_aleatorio(df, 41000 + 17 * sem + a % 100) for a, df in D.items()})
    nul.append(mina.r_obj(on))
sn = C.resumen(np.concatenate(nul)); z = C.z_exceso(s["R"], s["ee"], sn["R"], sn["ee"])
print(f"  paseo aleatorio: R={sn['R']:+.4f} (n={sn['n']}) · z={z:+.2f}")
ok = s["R"] > 0 and s["p_1cola"] < 0.05 / 6 and s1["R"] > 0 and s2["R"] > 0 and z > 2 and ri.mean() <= 0
print("  -> PRINCIPAL:", "PASA" if ok else "NO PASA")
nq = loader.cargar(verbose=False)
oq = motor.simular(nq, FN(nq)[1]); oq = oq[oq.sesion.dt.year.isin([2023, 2024, 2025])]
rq = mina.r_obj(oq)
print(f"  informativo NQ futuro real 2023-25: n={len(oq)} R={rq.mean():+.4f} wr {(rq>0).mean():.1%} · por año "
      + str(pd.Series(rq).groupby(oq.sesion.dt.year.to_numpy()).mean().round(3).to_dict()))
