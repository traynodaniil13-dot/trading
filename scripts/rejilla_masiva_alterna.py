"""Ejecuta preregistros/2026-10-03_rejilla_masiva_alterna.md."""
import itertools
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy import stats
from src import loader, motor
from src.motores import momento_generico as MG

TS = [h * 100 + m for h in range(9, 16) for m in range(0, 60, 5) if 935 <= h * 100 + m <= 1500]
LS = [5, 10, 15, 30, 60, 120]; KS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
DIS, VAL = (2021, 2023, 2025), (2022, 2024, 2026)
B = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in DIS + VAL}


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
    filas, guard = [], {}
    for (T, L, k), out in res.items():
        for modo, ix in (("mom", 0), ("rev", 1)):
            for dow in (None, 0, 1, 2, 3, 4):
                sel = lambda a: out[a][ix] if dow is None else out[a][ix][out[a][2] == dow]
                rd = {a: sel(a) for a in DIS}; rv = {a: sel(a) for a in VAL}
                nd = sum(len(x) for x in rd.values())
                if nd < 100:
                    continue
                key = (T, L, k, modo, ["todos", "lun", "mar", "mié", "jue", "vie"][0 if dow is None else dow + 1])
                guard[key] = (np.concatenate(list(rd.values())), np.concatenate(list(rv.values())), rv)
                filas.append(dict(T=T, L=L, k=k, modo=modo, dia=key[4], n_dis=nd,
                                  R_dis=np.concatenate(list(rd.values())).mean(),
                                  min_anio_dis=min(x.mean() for x in rd.values()),
                                  R_val=np.concatenate(list(rv.values())).mean(),
                                  min_anio_val=min(x.mean() for x in rv.values())))
    t = pd.DataFrame(filas); t.to_csv("resultados/2026-10-03_rejilla_masiva_alterna.csv", index=False)
    eleg = t[t.min_anio_dis > 0]
    pd.set_option("display.width", 250)
    print(f"reglas: {len(t):,} · positivas los 3 años de diseño: {len(eleg):,} ({len(eleg)/len(t):.1%}; por azar puro ~12,5%)\n")
    fin = eleg.sort_values("min_anio_dis", ascending=False).head(10).copy()
    pv, wr = [], []
    for r in fin.itertuples():
        _, xv, _ = guard[(r.T, r.L, r.k, r.modo, r.dia)]
        pv.append(stats.ttest_1samp(xv, 0, alternative="greater").pvalue); wr.append(np.mean(xv > 0))
    fin["wr_val"] = wr; fin["p_val"] = pv
    fin["PASA"] = (fin.p_val < 0.05 / 7 / 10) & (fin.min_anio_val > 0)
    print("10 FINALISTAS (mayor R mínima en diseño) y su VALIDACIÓN:")
    print(fin.round(3).to_string(index=False))
    top100 = eleg.sort_values("min_anio_dis", ascending=False).head(100)
    print(f"\nTop-100 robustas: diseño R {top100.R_dis.mean():+.3f} (mín. año {top100.min_anio_dis.mean():+.3f}) → validación R {top100.R_val.mean():+.3f}, positivas {np.mean(top100.R_val > 0):.0%}, 3/3 años en validación {np.mean(top100.min_anio_val > 0):.0%}")
    print(f"Todas: corr(R diseño, R validación) {t.R_dis.corr(t.R_val):+.2f} · elegibles: corr {eleg.R_dis.corr(eleg.R_val):+.2f}")
    print("\nPASAN:", ", ".join(f"{r.T} L{r.L} k{r.k} {r.modo} {r.dia}" for r in fin[fin.PASA].itertuples()) or "ninguna")
