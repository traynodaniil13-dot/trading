"""Ejecuta preregistros/2026-10-02_rejilla_londres.md."""
import itertools, sys
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.motores import momento_generico as MG

TS = [210, 230, 310, 330, 400, 500]; LS = [10, 30, 60]; KS = [0.10, 0.15, 0.25, 0.40]; RATIOS = [1.0, 1.5, 2.0]
SALIDA = 829


def correr(datos):
    out = {}
    for T, L, k in itertools.product(TS, LS, KS):
        ops = []
        for a, b in datos.items():
            o = motor.simular(b, MG.senales(b, T, L, k, salida=SALIDA)); ops.append(o[o.sesion.dt.year == a])
        o = pd.concat(ops, ignore_index=True); anio = o.sesion.dt.year.to_numpy()
        for r in RATIOS:
            for modo, inv in (("mom", False), ("rev", True)):
                out[(T, L, k, r, modo)] = (motor.r_neta(o, r, invertida=inv), anio, o.riesgo_pts.median())
    return out


def tabla(res):
    f = []
    for (T, L, k, r, modo), (x, anio, rp) in res.items():
        s = C.resumen(x); py = pd.Series(x).groupby(anio).mean()
        f.append({"T": T, "L": L, "k": k, "ratio": r, "modo": modo, "n": s["n"], "stop_pts": round(rp, 1), "R": s["R"],
                  "t": s["t"], "p": s["p_1cola"], "wr": (x > 0).mean(), "min_anio": py.min(),
                  **{f"R{y}": v for y, v in py.items()}})
    return pd.DataFrame(f)


if __name__ == "__main__":
    fase = sys.argv[1] if len(sys.argv) > 1 else "diseno"
    pd.set_option("display.width", 250)
    if fase == "diseno":
        dis = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in (2021, 2023, 2025)}
        t = tabla(correr(dis)); t.to_csv("resultados/2026-10-02_rejilla_londres_diseno.csv", index=False)
        maxR, maxT = [], []
        for sem in range(6):
            tn = tabla(correr({a: C.paseo_aleatorio(b, 17000 + 10 * sem + a % 10) for a, b in dis.items()}))
            maxR.append(tn.R.max()); maxT.append(tn.t.max())
            print(f"nulo semilla {sem}: máx R {tn.R.max():+.3f} máx t {tn.t.max():+.2f} · R medio {tn.R.mean():+.3f}", flush=True)
        mR, sR = np.mean(maxR), np.std(maxR, ddof=1); mT, sT = np.mean(maxT), np.std(maxT, ddof=1)
        print(f"\nREAL: máx R {t.R.max():+.3f} máx t {t.t.max():+.2f} · R medio de la rejilla {t.R.mean():+.3f}")
        print(f"NULO: máx R {mR:+.3f} ± {sR:.3f} · máx t {mT:+.2f} ± {sT:.2f}")
        print(f"mejor real a {(t.R.max() - mR) / sR:+.2f}σ (R) y {(t.t.max() - mT) / sT:+.2f}σ (t) del máximo del nulo")
        print("\nTop 15 por t:"); print(t.sort_values("t", ascending=False).head(15).round(3).to_string(index=False))
        print("\nR medio por hora y modo (k y ratio juntos):")
        print(t.pivot_table(index="T", columns="modo", values="R", aggfunc="mean").round(3).to_string())
        cand = t[(t.R >= 0.10) & (t.min_anio > 0)].sort_values("t", ascending=False).head(3)
        pasa = t.t.max() > mT + 2 * sT or t.R.max() > mR + 2 * sR
        print(f"\nFINALISTAS ({'la rejilla supera al nulo' if pasa else 'la rejilla NO supera al nulo -> se cierra'}):")
        print(cand.round(3).to_string(index=False) if pasa and len(cand) else "ninguna")
