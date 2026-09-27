"""Candidata MOMENTO 09:40 stop 0,40% en Lucid Flex 25K. Secuencia histórica real 2021-2026 (CFD)."""
import numpy as np, pandas as pd
from src import cuentas as K
from src import loader, motor
from src.motores import momento_generico as MG

ops, maes = [], {1.0: [], 2.0: []}
for a in (2021, 2022, 2023, 2024, 2025, 2026):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(b, MG.senales(b, 940, 30, 0.40)); o = o[o.sesion.dt.year == a].reset_index(drop=True)
    for rt in maes: maes[rt].append(K.mae_hasta_salida(b, o, rt))
    ops.append(o)
o = pd.concat(ops, ignore_index=True)
mae = {rt: np.concatenate(v) for rt, v in maes.items()}
# escalar el stop al NQ actual: el riesgo en pts cambia con el precio, el sizing lo absorbe (micros enteros)
pts = o["riesgo_pts"].to_numpy()
r = {rt: motor.r_neta(o, rt) for rt in (1.0, 2.0)}
print("R histórica neta: 1:1 %+.3f · 1:2 %+.3f | stop mediano %.0f pts" % (r[1.0].mean(), r[2.0].mean(), np.median(pts)))

filas = []
for esc, objetivo in (("histórica", None), ("realista +0,05R", 0.05), ("cero", 0.0)):
    for gest in ("1:2 todo", "eval 1:1 → fondeada 1:2"):
        re = r[1.0] if gest.startswith("eval") else r[2.0]
        me = mae[1.0] if gest.startswith("eval") else mae[2.0]
        rf, mf = r[2.0], mae[2.0]
        if objetivo is not None:  # desplazar la media a la ventaja del escenario
            re = re - (re.mean() - objetivo * (0.5 if gest.startswith("eval") else 1.0))
            rf = rf - (rf.mean() - objetivo)
        for riesgo in (250, 500):
            m = K.montecarlo(re, me, pts, riesgo_eval=riesgo, riesgo_fund=riesgo, r_fund=rf, mae_fund=mf, n=4000)
            filas.append({"ventaja": esc, "gestión": gest, "riesgo/op": riesgo, "pasan/10": round(m["pase_de_10"], 2),
                          "cobran/10": round(m["cobran_de_10"], 2), "$ cobrado por eval": round(m["cobro_medio_por_eval"]),
                          "$ si cobra": round(m["cobro_medio_si_cobra"]), "ops hasta pasar": m["ops_hasta_pasar_mediana"],
                          "_cob": m["_cob"]})
t = pd.DataFrame(filas)
pd.set_option("display.width", 220)
print(t.drop(columns="_cob").to_string(index=False))
t.drop(columns="_cob").to_csv("resultados/2026-09-27_cuentas_momento_pct.csv", index=False)
print("\n% de tandas de 10 cuentas en pérdidas, según coste de la evaluación (mejor gestión de cada escenario):")
for esc in ("histórica", "realista +0,05R", "cero"):
    sub = t[t.ventaja == esc]; best = sub.loc[sub["$ cobrado por eval"].idxmax()]
    lin = [f"{best['gestión']}, ${best['riesgo/op']}/op:"]
    for coste in (50, 100, 150):
        pp, med = K.tandas_de_10(best["_cob"], coste)
        lin.append(f"coste ${coste}: {pp:.0%} pierden (mediana {med:+.0f}$)")
    print(f"  {esc:16s}", " | ".join(lin))
