"""EV por cuenta Lucid Flex 25K/50K con las reglas del bot (01/10).
Pre-registro: preregistros/2026-10-01_cuentas_reglas_bot.md"""
import numpy as np, pandas as pd
from src import cuentas as K, loader, motor
from src.motores import momento_generico as MG

ops, mae = [], []
for a in range(2021, 2027):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(b, MG.senales(b, 940, 30, 0.40)); o = o[o.sesion.dt.year == a].reset_index(drop=True)
    mae.append(K.mae_hasta_salida(b, o, 2.0)); ops.append(o)
o = pd.concat(ops, ignore_index=True); mae = np.concatenate(mae)
pts = np.full(len(o), 116.0); r0 = motor.r_neta(o, 2.0)

CUENTAS = {
    "25K": (50.30, K.Reglas(tope_fund_ini=20)),
    "50K": (90.20, K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=40, tope_fund=40,
                            pago_min=500, pago_max=2_000, dia_min=200)),
}
filas = []
for nombre, (precio, R) in CUENTAS.items():
    for mll, m_ in (("intradia", mae), ("solo cierre", np.zeros_like(mae))):
        for esc, obj in (("+0,05R", 0.05), ("cero", 0.0), ("moneda+coste", -0.0075)):
            r = r0 - (r0.mean() - obj)
            for micros in range(1, 7):
                riesgo = micros * 116 * 2 + 1
                m = K.montecarlo(r, m_, pts, riesgo_eval=riesgo, riesgo_fund=riesgo, n=3000, largo=500, R=R)
                pp, med = K.tandas_de_10(m["_cob"], precio)
                filas.append({"cuenta": nombre, "MLL": mll, "ventaja": esc, "micros": micros,
                              "pasan/10": round(m["pase_de_10"], 1), "cobran/10": round(m["cobran_de_10"], 1),
                              "cobro si cobra $": round(m["cobro_medio_si_cobra"]),
                              "EV/cuenta $": round(m["cobro_medio_por_eval"] - precio),
                              "tandas10 en pérdidas": f"{pp:.0%}", "ops hasta pasar": m["ops_hasta_pasar_mediana"]})
t = pd.DataFrame(filas); pd.set_option("display.width", 220); pd.set_option("display.max_rows", 500)
for (c, ml, v), g in t.groupby(["cuenta", "MLL", "ventaja"], sort=False):
    print(f"\n=== {c} · MLL {ml} · ventaja {v} ===")
    print(g.drop(columns=["cuenta", "MLL", "ventaja"]).to_string(index=False))
t.to_csv("resultados/2026-10-01_cuentas_reglas_bot.csv", index=False)
