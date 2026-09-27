"""Ejecuta preregistros/2026-09-27_rejilla_momento_reversion.md. Fase: diseño + nulo."""
import itertools, json, sys
import numpy as np
import pandas as pd
from src import controles as C
from src import loader, motor
from src.motores import momento_generico as MG

TS = [940, 1000, 1030, 1100, 1300, 1400, 1500]
LS = [10, 30, 60]
KS = [0.10, 0.15, 0.25, 0.40]
RATIOS = [1.0, 1.5, 2.0]


def correr(datos):
    """datos = {año: barras}. Devuelve {celda: array R neta} y {celda: años} para las 504 celdas."""
    out = {}
    for T, L, k in itertools.product(TS, LS, KS):
        ops = []
        for a, b in datos.items():
            o = motor.simular(b, MG.senales(b, T, L, k))
            o = o[o["sesion"].dt.year == a]
            ops.append(o)
        o = pd.concat(ops, ignore_index=True)
        anio = o["sesion"].dt.year.to_numpy()
        for r in RATIOS:
            for modo, inv in (("mom", False), ("rev", True)):
                out[(T, L, k, r, modo)] = (motor.r_neta(o, r, invertida=inv), anio)
    return out


def tabla(res):
    filas = []
    for (T, L, k, r, modo), (x, anio) in res.items():
        s = C.resumen(x)
        py = pd.Series(x).groupby(anio).mean()
        filas.append({"T": T, "L": L, "k": k, "ratio": r, "modo": modo, "n": s["n"], "R": s["R"],
                      "t": s["t"], "p": s["p_1cola"], "wr": (x > 0).mean(), "min_anio": py.min(),
                      **{f"R{y}": v for y, v in py.items()}})
    return pd.DataFrame(filas)


if __name__ == "__main__":
    fase = sys.argv[1]
    if fase == "diseno":
        dis = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in (2021, 2023, 2025)}
        t = tabla(correr(dis))
        maxR, maxT = [], []
        for sem in range(6):
            rw = {a: C.paseo_aleatorio(b, 9000 + 10 * sem + a % 10) for a, b in dis.items()}
            tn = tabla(correr(rw))
            maxR.append(tn.R.max()); maxT.append(tn.t.max())
            print(f"nulo semilla {sem}: máx R {tn.R.max():+.3f}  máx t {tn.t.max():+.2f}  celdas con R≥0,2: {(tn.R >= 0.2).sum()}", flush=True)
        pd.set_option("display.width", 250)
        print(f"\nREAL: máx R {t.R.max():+.3f}  máx t {t.t.max():+.2f}  celdas con R≥0,2: {(t.R >= 0.2).sum()} de {len(t)}")
        print(f"NULO: máx R {np.mean(maxR):+.3f} ± {np.std(maxR, ddof=1):.3f}  máx t {np.mean(maxT):+.2f} ± {np.std(maxT, ddof=1):.2f}")
        print(f"mejor real a {(t.R.max() - np.mean(maxR)) / np.std(maxR, ddof=1):+.2f}σ del máx R del nulo; t a {(t.t.max() - np.mean(maxT)) / np.std(maxT, ddof=1):+.2f}σ")
        cand = t[(t.R >= 0.10) & (t.min_anio > 0)].sort_values("t", ascending=False)
        print(f"\ncandidatas (R≥0,10 y 3 años positivos): {len(cand)}")
        fin = cand.head(10)
        print(fin.round(3).to_string(index=False))
        fin.to_csv("resultados/2026-09-27_rejilla_finalistas.csv", index=False)
        t.to_csv("resultados/2026-09-27_rejilla_diseno_completa.csv", index=False)
    elif fase == "validacion":
        fin = pd.read_csv("resultados/2026-09-27_rejilla_finalistas.csv")
        val = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in (2022, 2024, 2026)}
        for _, f in fin.iterrows():
            ops = []
            for a, b in val.items():
                o = motor.simular(b, MG.senales(b, int(f["T"]), int(f["L"]), float(f["k"])))
                ops.append(o[o["sesion"].dt.year == a])
            o = pd.concat(ops, ignore_index=True)
            inv = f["modo"] == "rev"
            x = motor.r_neta(o, f["ratio"], invertida=inv)
            s = C.resumen(x)
            py = pd.Series(x).groupby(o["sesion"].dt.year.to_numpy()).mean()
            ok = s["p_1cola"] < 0.005 and (py > 0).all()
            print(f"T={int(f['T'])} L={int(f['L'])} k={f['k']} 1:{f['ratio']} {f['modo']} | DISEÑO R={f['R']:+.3f} wr={f['wr']:.1%} "
                  f"| VALID n={s['n']} R={s['R']:+.3f} wr={s['wr']:.1%} p={s['p_1cola']:.3f} años {py.round(3).to_dict()} -> {'PASA' if ok else 'no'}")
