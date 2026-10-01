"""Cuándo pedir el retiro en la 50K (2 micros) y la 25K (1 micro), MLL intradía (confirmado por el bot 01/10).
Política: solo se solicita cuando el importe (50% del beneficio, con tope) llega a X. X=500 es la regla mínima de Lucid."""
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
base = {"25K 1 micro": (50.30, 1, dict(tope_fund_ini=20), (500, 750, 1000)),
        "50K 2 micros": (90.20, 2, dict(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=40, tope_fund=40,
                                        pago_max=2_000, dia_min=200), (500, 1000, 1500, 2000))}
filas = []
for nombre, (precio, mic, kw, umbrales) in base.items():
    for esc, obj in (("+0,05R", 0.05), ("cero", 0.0)):
        r = r0 - (r0.mean() - obj)
        for x in umbrales:
            R = K.Reglas(pago_min=x, **kw)
            m = K.montecarlo(r, mae, pts, riesgo_eval=mic * 232 + 1, riesgo_fund=mic * 232 + 1, n=4000, largo=500, R=R)
            pp, _ = K.tandas_de_10(m["_cob"], precio)
            filas.append({"cuenta": nombre, "ventaja": esc, "pedir retiro desde $": x, "pasan/10": round(m["pase_de_10"], 1),
                          "cobran/10": round(m["cobran_de_10"], 1), "cobro si cobra $": round(m["cobro_medio_si_cobra"]),
                          "EV/cuenta $": round(m["cobro_medio_por_eval"] - precio), "tandas10 en pérdidas": f"{pp:.0%}"})
pd.set_option("display.width", 200)
print(pd.DataFrame(filas).to_string(index=False))
