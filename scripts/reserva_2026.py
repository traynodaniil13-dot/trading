"""Ejecuta preregistros/2026-09-27_reserva_2026.md."""
import numpy as np
import pandas as pd
from scipy import stats

from src import controles as C
from src import loader, motor
from src.motores import momento_0940 as M
from scripts.rtp_filtros import SIN_OBJ, familia

cfd = loader.cargar_cfd()
es26 = lambda o: o[o["sesion"] >= "2026-01-01"].reset_index(drop=True)
fam = {k: es26(o) for k, o in familia(cfd).items()}
R = {k: motor.r_neta(o, SIN_OBJ) for k, o in fam.items()}


def fila(k):
    s = C.resumen(R[k])
    return f"{k:18s} n={s['n']:4d}  R={s['R']:+.3f}  ee={s['ee']:.3f}  p1c={s['p_1cola']:.3f}  inv={motor.r_neta(fam[k], SIN_OBJ, True).mean():+.3f}"


def dif(a, b):
    t, p2 = stats.ttest_ind(R[a], R[b], equal_var=False)
    return R[a].mean() - R[b].mean(), (p2 / 2 if t > 0 else 1 - p2 / 2)


print("== RTP 2026 (CFD) ==")
for k in fam:
    print(fila(k))
print("\n== Hipótesis ciegas (umbral p < 0,025) ==")
for h, (a, b) in {"H1 contra sesgo": ("F6_contra_sesgo", "F5_con_sesgo"),
                  "H2 barrido largo": ("F11_barr_largo", "F10_barr_corto")}.items():
    s = C.resumen(R[a]); d, pd_ = dif(a, b)
    ok = s["R"] > 0 and s["p_1cola"] < 0.025 and d > 0 and pd_ < 0.025
    print(f"{h}: R={s['R']:+.3f} p={s['p_1cola']:.3f} | diferencia {d:+.3f} p={pd_:.3f} -> {'PASA' if ok else 'NO PASA'}")

o = es26(motor.simular(cfd, M.senales(cfd)))
r = motor.r_neta(o, 2)
s = C.resumen(r)
print(f"\n== Momento 09:40 2026 (informativo, no ciego) ==\nn={s['n']} R={s['R']:+.3f} ee={s['ee']:.3f} p1c={s['p_1cola']:.3f} "
      f"inv={motor.r_neta(o, 2, True).mean():+.3f}")
