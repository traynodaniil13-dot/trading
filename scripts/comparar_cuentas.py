"""Compara Lucid Flex 25K / 50K / 100K con Momento 09:40 stop 0,40%.
Eval verificadas en el panel (28/09). Fondeada de 50K/100K ESCALADA desde la 25K (supuesto)."""
import numpy as np, pandas as pd
from src import cuentas as K, loader, motor
from src.motores import momento_generico as MG

ops, mae = [], []
for a in range(2021, 2027):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(b, MG.senales(b, 940, 30, 0.40)); o = o[o.sesion.dt.year == a].reset_index(drop=True)
    mae.append(K.mae_hasta_salida(b, o, 2.0)); ops.append(o)
o = pd.concat(ops, ignore_index=True); mae = np.concatenate(mae)
# escalar el stop al nivel actual del NQ (~29.000): 0,40% ≈ 116 pts, para que el sizing sea el de hoy
pts = np.full(len(o), 116.0); r0 = motor.r_neta(o, 2.0)

CUENTAS = {
    "25K  ($50,30)": (50.30, K.Reglas()),
    "50K  ($90,20)": (90.20, K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=20, tope_fund=40,
                                      umbral_tope=2_000, pago_min=500, pago_max=2_000, dia_min=200)),
    "100K ($170,60)": (170.60, K.Reglas(inicial=100_000, dd=3_000, objetivo=6_000, tope_eval=60, tope_fund_ini=30, tope_fund=60,
                                        umbral_tope=3_000, pago_min=1_500, pago_max=3_000, dia_min=300)),
}
filas = []
for nombre, (precio, R) in CUENTAS.items():
    for esc, obj in (("realista +0,05R", 0.05), ("cero", 0.0)):
        r = r0 - (r0.mean() - obj)
        for micros in (1, 2, 3, 4):
            riesgo = micros * 116 * 2 + 1
            m = K.montecarlo(r, mae, pts, riesgo_eval=riesgo, riesgo_fund=riesgo, n=3000, largo=500, R=R)
            pp, _ = K.tandas_de_10(m["_cob"], precio)
            filas.append({"cuenta": nombre, "ventaja": esc, "micros": micros, "pasan/10": round(m["pase_de_10"], 1),
                          "cobran/10": round(m["cobran_de_10"], 1), "EV/cuenta $": round(m["cobro_medio_por_eval"] - precio),
                          "EV por $ invertido": round((m["cobro_medio_por_eval"] - precio) / precio, 2),
                          "tandas de 10 en pérdidas": f"{pp:.0%}"})
t = pd.DataFrame(filas); pd.set_option("display.width", 200)
print(t[t.ventaja == "realista +0,05R"].drop(columns="ventaja").to_string(index=False))
print("\n--- mismo con ventaja CERO (referencia) ---")
print(t[t.ventaja == "cero"].drop(columns="ventaja").to_string(index=False))
t.to_csv("resultados/2026-10-02_comparar_cuentas.csv", index=False)
