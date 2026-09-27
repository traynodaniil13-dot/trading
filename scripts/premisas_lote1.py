"""Ejecuta preregistros/2026-09-27_premisas_lote1.md sobre los años de DISEÑO disponibles."""
import sys

import numpy as np
import pandas as pd

from src import controles as C
from src import loader
from src import premisas as P

DISENO = [2021, 2023, 2025]
disp = [a for a in DISENO if (loader.RAIZ / f"data/nq_cfd_{a}.csv.gz").exists()]
print("Años de diseño disponibles:", disp, "" if disp == DISENO else "(PRELIMINAR)")
UMBRAL = 0.05 / 7

res, nulos = {}, {k: [] for k in list(P.DIRECCIONALES) + ["P6_cambio_de_mes"]}
for a in disp:
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    b = b[b["sesion"].dt.year == a]  # el diciembre previo fuera (solo historia)... salvo para c_prev
    res[a] = b

# unir años (cada uno con su propia historia de diciembre para c_prev)
def por_anio(fn):
    trozos = []
    for a in disp:
        b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
        r = fn(b)
        trozos.append(r[r.index.year == a])
    return pd.concat(trozos)

filas = {}
for nom, fn in P.DIRECCIONALES.items():
    filas[nom] = P.evaluar(por_anio(fn))
tom = P.evaluar_tom(por_anio(P.p6_cambio_de_mes))

# paseo aleatorio: 6 semillas sobre la rejilla de cada año
for sem in range(6):
    for a in disp:
        b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
        rw = C.paseo_aleatorio(b, 5000 + 10 * sem + a % 10)
        for nom, fn in P.DIRECCIONALES.items():
            r = fn(rw); nulos[nom].append(r[r.index.year == a]["y"].mean())
        r = P.p6_cambio_de_mes(rw); r = r[r.index.year == a]
        nulos["P6_cambio_de_mes"].append(r.loc[r.tom, "y"].mean() - r.loc[~r.tom, "y"].mean())

print(f"\numbral p bilateral: {UMBRAL:.4f} · coste 0,87 pts\n")
for nom, f in filas.items():
    ok = (f["p"] < UMBRAL and len(set(np.sign(list(f["anio"].values())))) == 1
          and f["largos"] and f["cortos"] and np.sign(f["largos"][0]) == np.sign(f["cortos"][0])
          and abs(f["media"]) > 0.87)
    print(f"{nom:22s} n={f['n']:4d} media={f['media']:+6.2f} pts ee={f['ee']:.2f} t={f['t']:+.2f} p={f['p']:.4f} "
          f"| año {f['anio']} | L {f['largos']} C {f['cortos']} | paseo {np.mean(nulos[nom]):+.2f} -> {'PASA' if ok else 'no'}")
ok = tom["p"] < UMBRAL and len(set(np.sign(list(tom["anio"].values())))) == 1 and abs(tom["media"]) > 0.87
print(f"{'P6_cambio_de_mes':22s} n={tom['n_tom']}/{tom['n_resto']} dif={tom['media']:+6.2f} pts (tom {tom['tom']:+.2f} resto {tom['resto']:+.2f}) "
      f"t={tom['t']:+.2f} p={tom['p']:.4f} | año {tom['anio']} | paseo {np.mean(nulos['P6_cambio_de_mes']):+.2f} -> {'PASA' if ok else 'no'}")
