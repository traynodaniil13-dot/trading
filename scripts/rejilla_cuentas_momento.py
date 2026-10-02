"""Ejecuta preregistros/2026-10-02_rejilla_cuentas_momento.md."""
import itertools
from multiprocessing import Pool
import numpy as np, pandas as pd
from src import cuentas as K, loader, motor
from src.motores import momento_generico as MG

KS = (0.30, 0.40, 0.50, 0.60, 0.80); RATIOS = (1.0, 1.5, 2.0, 2.5, 3.0)
PRECIO_HOY = 30_000; NSIM = 1500
CUENTAS = {
    "25K": (50.30, K.Reglas(), (1, 2, 3)),
    "50K": (90.20, K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=20, tope_fund=40,
                            umbral_tope=2_000, pago_min=500, pago_max=2_000, dia_min=200), (1, 2, 3, 4)),
}
MITADES = {"diseno": (2021, 2023, 2025), "control": (2022, 2024, 2026)}


def preparar():
    datos = {}
    barras = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in range(2021, 2027)}
    for k in KS:
        for mitad, anios in MITADES.items():
            oo, mm = [], {rt: [] for rt in RATIOS}
            for a in anios:
                b = barras[a]
                o = motor.simular(b, MG.senales(b, 940, 30, k)); o = o[o.sesion.dt.year == a].reset_index(drop=True)
                oo.append(o)
                for rt in RATIOS:
                    mm[rt].append(K.mae_hasta_salida(b, o, rt))
            o = pd.concat(oo, ignore_index=True)
            datos[(k, mitad)] = dict(rmax=o.rmax.to_numpy(), toco=o.toco_sl.to_numpy(), rc=o.r_cierre.to_numpy(),
                                     coste_R=(0.87 / o.riesgo_pts).to_numpy(),
                                     r={rt: motor.r_neta(o, rt) for rt in RATIOS},
                                     mae={rt: np.concatenate(mm[rt]) for rt in RATIOS})
    return datos


def evaluacion(d, idx, ratio, riesgo, R):
    cost = 0.87 * riesgo / pts_g  # coste en $ por op (riesgo/pts = $ por punto)
    bal, alto, mll, mejor = R.inicial, R.inicial, R.inicial - R.dd, 0.0
    for n, i in enumerate(idx):
        if bal - d["mae"][ratio][i] * riesgo <= mll:
            return False, n + 1
        need = R.inicial + R.objetivo - bal
        rt = float(np.clip((need + cost) / riesgo, 0.5, ratio)) if need < ratio * riesgo else ratio
        bruta = rt if d["rmax"][i] >= rt else (-1.0 if d["toco"][i] else min(d["rc"][i], rt))
        pnl = bruta * riesgo - cost
        bal += pnl; mejor = max(mejor, pnl)
        if bal <= mll:
            return False, n + 1
        alto = max(alto, bal); mll = max(mll, min(alto - R.dd, R.inicial + R.tope_mll))
        ben = bal - R.inicial
        if ben >= R.objetivo and mejor <= R.consistencia * ben:
            return True, n + 1
    return False, len(idx)


def celda(args):
    global pts_g
    cuenta, k, ratio, mic, mitad = args
    precio, R, _ = CUENTAS[cuenta]
    d = DATOS[(k, mitad)]
    pts_g = k / 100 * PRECIO_HOY
    riesgo = mic * pts_g * 2
    N = len(d["rmax"]); rng = np.random.default_rng(hash((cuenta, k, ratio, mic, mitad)) % 2**32)
    pts = np.full(N, pts_g); pasa = cob = cobran = 0
    for s in rng.integers(N, size=NSIM):
        ok, n = evaluacion(d, (s + np.arange(500)) % N, ratio, riesgo, R)
        if ok:
            pasa += 1
            j = (s + n + np.arange(600)) % N
            c, npag, _ = K.fondeada(d["r"][ratio][j], d["mae"][ratio][j], pts[j], riesgo + 0.5, R)
            cob += c; cobran += npag > 0
    return dict(cuenta=cuenta, stop=k, ratio=ratio, micros=mic, mitad=mitad, riesgo=round(riesgo),
                pasan=10 * pasa / NSIM, cobran=10 * cobran / NSIM, EV=cob / NSIM - precio)


DATOS = preparar()
if __name__ == "__main__":
    tareas = [(c, k, rt, m, mi) for c, (_, _, mics) in CUENTAS.items() for k in KS for rt in RATIOS for m in mics
              for mi in MITADES]
    with Pool(4) as p:
        t = pd.DataFrame(p.map(celda, tareas, chunksize=4))
    t.to_csv("resultados/2026-10-02_rejilla_cuentas_momento.csv", index=False)
    w = t.pivot_table(index=["cuenta", "stop", "ratio", "micros", "riesgo"], columns="mitad", values=["EV", "pasan", "cobran"])
    w.columns = [f"{a}_{b}" for a, b in w.columns]; w = w.reset_index()
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    for c in CUENTAS:
        x = w[w.cuenta == c].sort_values("EV_diseno", ascending=False)
        x["puesto_control"] = x.EV_control.rank(ascending=False).astype(int)
        print(f"\n===== {c}: top 15 por EV en DISEÑO =====")
        print(x.head(15).round(1).to_string(index=False))
        act = x[(x.stop == 0.40) & (x.ratio == 2.0) & (x.micros == (1 if c == "25K" else 2))]
        print(f"ACTUAL ({c}):"); print(act.round(1).to_string(index=False))
        mp = x.sort_values("pasan_diseno", ascending=False).head(5)
        print(f"Top 5 por TASA DE PASE en diseño ({c}):"); print(mp.round(1).to_string(index=False))
