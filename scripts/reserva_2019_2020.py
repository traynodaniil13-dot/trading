"""Ejecuta preregistros/2026-10-03_reserva_ciega_2019_2020.md (Momento 09:40 0,40% y H4 Aleix).
No cambiar nada después de ver resultados."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.motores import momento_generico as MG
from scripts.aleix_reversion_0930 import correr as aleix, r_obj

D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"]) for a in (2019, 2020)}


def momento(datos):
    out = []
    for a, b in datos.items():
        o = motor.simular(b, MG.senales(b, 940, 30, 0.40)); out.append(o[o.sesion.dt.year == a])
    return pd.concat(out, ignore_index=True)


def informe(nombre, o, r, nulo, umbral):
    s = C.resumen(r); yr = o.sesion.dt.year.to_numpy()
    py = pd.Series(r).groupby(yr).agg(["mean", "size"])
    sn = C.resumen(np.concatenate(nulo)); z = C.z_exceso(s["R"], s["ee"], sn["R"], sn["ee"])
    print(f"\n=== {nombre} (umbral p < {umbral})")
    print(f"  n={s['n']} R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} · R total {s['R_total']:+.1f}")
    print("  por año: " + " · ".join(f"{y} {m:+.3f} (n={int(n)})" for y, (m, n) in py.iterrows()))
    print(f"  paseo aleatorio: {sn['R']:+.4f} (n={sn['n']}) · z exceso {z:+.2f}")
    return s, z


om = momento(D); rm = motor.r_neta(om, 2.0)
oa = aleix(D, liq="on", tp="piv15"); ra = r_obj(oa)
nm, na = [], []
for sem in range(6):
    P = {a: C.paseo_aleatorio(b, 7000 * a + sem) for a, b in D.items()}
    nm.append(motor.r_neta(momento(P), 2.0))
    o = aleix(P, liq="on", tp="piv15")
    if len(o): na.append(r_obj(o))

s, z = informe("PRINCIPAL · Momento 09:40, stop 0,40%, 1:2", om, rm, nm, 0.05)
tp = (om.rmax >= 2).mean(); sl = (~(om.rmax >= 2) & om.toco_sl).mean()
print(f"  TP {tp:.1%} · SL {sl:.1%} · cierre {1-tp-sl:.1%} · invertida {motor.r_neta(om, 2.0, True).mean():+.4f}")
print("  ->", "PASA" if s["R"] > 0 and s["p_1cola"] < 0.05 else "NO PASA")

s, z = informe("H4 · Aleix overnight + TP pivote 15m", oa, ra, na, 0.025)
print(f"  TP a {oa.obj.median():.2f}R de mediana · invertida 1:1 {motor.r_neta(oa, 1.0, True).mean():+.4f}")
print("  ->", "PASA" if s["R"] > 0 and s["p_1cola"] < 0.025 and z > 1.5 else "NO PASA")
