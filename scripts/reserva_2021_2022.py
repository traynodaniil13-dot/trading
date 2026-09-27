"""Ejecuta preregistros/2026-09-27_reserva_2021_2022.md. No cambiar nada."""
import numpy as np
import pandas as pd
from scipy import stats

from src import controles as C
from src import loader, motor
from src.motores import momento_0940 as M
from scripts.rtp_filtros import SIN_OBJ, familia

RUTAS = sorted(loader.RAIZ.glob("data/nq_cfd_202[12].csv.gz"))
cfd = loader.cargar_cfd(RUTAS)
dentro = lambda o: o[(o["sesion"] >= "2021-01-04") & (o["sesion"] <= "2022-12-30")].reset_index(drop=True)


def rtp_h1(b):
    fam = familia(b)
    return dentro(fam["F6_contra_sesgo"]), dentro(fam["F5_con_sesgo"]), dentro(fam["BASE"])


def mom(b):
    return dentro(motor.simular(b, M.senales(b)))


def por_anio(o, r):
    s = pd.Series(r).groupby(o["t_ent"].dt.year.to_numpy()).agg(["mean", "count"])
    return " | ".join(f"{y}: {m:+.3f} (n={int(n)})" for y, (m, n) in s.iterrows())


f6, f5, base = rtp_h1(cfd)
r6, r5, rb = (motor.r_neta(x, SIN_OBJ) for x in (f6, f5, base))
o_m = mom(cfd)
rm = motor.r_neta(o_m, 2)

# nulo de paseo aleatorio, 6 semillas
nul6, nulm = [], []
for s in range(6):
    rw = C.paseo_aleatorio(cfd, 3000 + s)
    a, _, _ = rtp_h1(rw)
    nul6.append(motor.r_neta(a, SIN_OBJ).mean())
    nulm.append(motor.r_neta(mom(rw), 2).mean())

print("== H1 · RTP contra el sesgo overnight (umbral p < 0,025) ==")
s6, s5 = C.resumen(r6), C.resumen(r5)
t, p2 = stats.ttest_ind(r6, r5, equal_var=False)
pdif = p2 / 2 if t > 0 else 1 - p2 / 2
print(f"F6 contra sesgo: n={s6['n']} R={s6['R']:+.3f} ee={s6['ee']:.3f} p1c={s6['p_1cola']:.3f} inv={motor.r_neta(f6, SIN_OBJ, True).mean():+.3f}")
print(f"   por año: {por_anio(f6, r6)}")
print(f"F5 a favor:      n={s5['n']} R={s5['R']:+.3f} ee={s5['ee']:.3f}")
print(f"   por año: {por_anio(f5, r5)}")
print(f"Diferencia F6-F5: {r6.mean() - r5.mean():+.3f}  p1c={pdif:.3f}")
nm, ne = np.mean(nul6), np.std(nul6, ddof=1) / np.sqrt(6)
print(f"Paseo aleatorio F6: {nm:+.3f} ± {ne:.3f} -> z exceso {C.z_exceso(s6['R'], s6['ee'], nm, ne):+.2f}")
ok1 = s6["R"] > 0 and s6["p_1cola"] < 0.025 and r6.mean() > r5.mean() and pdif < 0.025
print("H1 ->", "PASA" if ok1 else "NO PASA")
print(f"(RTP base informativa: n={len(rb)} R={rb.mean():+.3f})")

print("\n== H3 · Momento 09:40 (umbral p < 0,025) ==")
sm = C.resumen(rm)
print(f"n={sm['n']} R={sm['R']:+.3f} ee={sm['ee']:.3f} p1c={sm['p_1cola']:.3f} wr={sm['wr']:.3f} inv={motor.r_neta(o_m, 2, True).mean():+.3f}")
print(f"   por año: {por_anio(o_m, rm)}")
nm, ne = np.mean(nulm), np.std(nulm, ddof=1) / np.sqrt(6)
print(f"Paseo aleatorio: {nm:+.3f} ± {ne:.3f} -> z exceso {C.z_exceso(sm['R'], sm['ee'], nm, ne):+.2f}")
print("H3 ->", "PASA" if (sm["R"] > 0 and sm["p_1cola"] < 0.025) else "NO PASA")
print("Consistencia Momento:", C.consistencia(o_m, rm))
