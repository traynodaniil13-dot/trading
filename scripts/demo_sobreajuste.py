"""Ejecuta preregistros/2026-10-03_demo_sobreajuste.md."""
import itertools
from multiprocessing import Pool
import numpy as np, pandas as pd
from src import loader, motor
from src.motores import momento_generico as MG

TS = [h * 100 + m for h in range(9, 16) for m in range(0, 60, 5) if 935 <= h * 100 + m <= 1500]
LS = [5, 10, 15, 30, 60, 120]; KS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
B = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in (2021, 2023, 2025)}


def celda(args):
    T, L, k = args
    out = {}
    for a, b in B.items():
        o = motor.simular(b, MG.senales(b, T, L, k)); o = o[o.sesion.dt.year == a]
        out[a] = (motor.r_neta(o, 2.0), motor.r_neta(o, 2.0, True), o.sesion.dt.dayofweek.to_numpy())
    return (T, L, k), out


if __name__ == "__main__":
    with Pool(4) as p:
        res = dict(p.map(celda, list(itertools.product(TS, LS, KS)), chunksize=8))
    filas = []
    for (T, L, k), out in res.items():
        for modo, ix in (("mom", 0), ("rev", 1)):
            for dow in (None, 0, 1, 2, 3, 4):
                def sel(a):
                    r, dw = out[a][ix], out[a][2]
                    return r if dow is None else r[dw == dow]
                rb = np.concatenate([sel(2021), sel(2023)]); rt = sel(2025)
                if len(rb) < 100:
                    continue
                filas.append(dict(T=T, L=L, k=k, modo=modo, dia=["todos", "lun", "mar", "mié", "jue", "vie"][0 if dow is None else dow + 1],
                                  n_busq=len(rb), wr_busq=np.mean(rb > 0), R_busq=rb.mean(),
                                  n_2025=len(rt), wr_2025=np.mean(rt > 0) if len(rt) else np.nan, R_2025=rt.mean() if len(rt) else np.nan))
    t = pd.DataFrame(filas); t.to_csv("resultados/2026-10-03_demo_sobreajuste.csv", index=False)
    pd.set_option("display.width", 250)
    print(f"reglas probadas: {len(t):,}\n")
    print("TOP 10 por WINRATE en la búsqueda (2021+2023) y lo que dan en 2025:")
    print(t.sort_values("wr_busq", ascending=False).head(10).round(3).to_string(index=False))
    print("\nTOP 10 por R en la búsqueda y lo que dan en 2025:")
    print(t.sort_values("R_busq", ascending=False).head(10).round(3).to_string(index=False))
    top = t.sort_values("R_busq", ascending=False).head(100)
    print(f"\nLas 100 mejores por R: media en búsqueda {top.R_busq.mean():+.3f} · media en 2025 {top.R_2025.mean():+.3f} · positivas en 2025 {np.mean(top.R_2025 > 0):.0%}")
    print(f"Todas las reglas: R medio búsqueda {t.R_busq.mean():+.3f} · 2025 {t.R_2025.mean():+.3f} · corr(búsqueda, 2025) {t.R_busq.corr(t.R_2025):+.2f}")
