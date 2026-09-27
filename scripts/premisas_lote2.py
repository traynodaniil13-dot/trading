"""Ejecuta preregistros/2026-09-27_premisas_lote2.md sobre DISEÑO (2021, 2023, 2025)."""
import numpy as np
import pandas as pd

from src import controles as C
from src import loader
from src import premisas as P
from src import premisas_lote2 as Q

DISENO = [2021, 2023, 2025]
UMBRAL = 0.05 / 7
datos = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in DISENO}


def junta(fn, fuente):
    return pd.concat([fn(b).loc[lambda r: r.index.year == a] for a, b in fuente.items()])


filas = {k: P.evaluar(junta(fn, datos)) for k, fn in Q.DIRECCIONALES.items()}
dias = Q.evaluar_dias(junta(Q.q7_dia_semana, datos))
nulos = {k: [] for k in Q.DIRECCIONALES}
for sem in range(6):
    rw = {a: C.paseo_aleatorio(b, 7000 + 10 * sem + a % 10) for a, b in datos.items()}
    for k, fn in Q.DIRECCIONALES.items():
        nulos[k].append(junta(fn, rw)["y"].mean())

print(f"umbral p bilateral: {UMBRAL:.4f} · coste 0,87 pts\n")
for nom, f in filas.items():
    ok = (f["p"] < UMBRAL and len(set(np.sign(list(f["anio"].values())))) == 1
          and f["largos"] and f["cortos"] and np.sign(f["largos"][0]) == np.sign(f["cortos"][0])
          and abs(f["media"]) > 0.87)
    print(f"{nom:22s} n={f['n']:4d} media={f['media']:+7.2f} pts ee={f['ee']:5.2f} p={f['p']:.4f} "
          f"| año {f['anio']} | L {f['largos']} C {f['cortos']} | paseo {np.mean(nulos[nom]):+.2f} -> {'PASA' if ok else 'no'}")
print(f"\nQ7_dia_semana F={dias['F']:.2f} p={dias['p']:.4f} | media por día (0=lun) {dias['media_por_dia']}")
print("   relativo a la media del año:", dias["rel_por_anio"])
