"""Parte 'gestión' del pre-registro 2026-10-02_aleix_dol_fvg_ifvg: 50K arriesgando $1.000 vs $500/$250 a 1:1,5."""
import numpy as np, pandas as pd
from src import cuentas as K, loader, motor
from src.motores import dol_ifvg as S
ops, mae = [], []
for a in (2021, 2023, 2025):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(b, S.senales(b)); o = o[o.sesion.dt.year == a].reset_index(drop=True)
    mae.append(K.mae_hasta_salida(b, o, 1.5)); ops.append(o)
o = pd.concat(ops, ignore_index=True); mae = np.concatenate(mae)
pts = o.riesgo_pts.to_numpy(); r0 = motor.r_neta(o, 1.5)
R50 = K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=20, tope_fund=40,
               umbral_tope=2_000, pago_min=1_000, pago_max=2_000, dia_min=200)
filas = []
for esc, obj in (("cero", 0.0), ("+0,10R", 0.10)):
    r = r0 - (r0.mean() - obj)
    for rie in (1000, 500, 250):
        m = K.montecarlo(r, mae, pts, riesgo_eval=rie, riesgo_fund=500, n=4000, largo=500, R=R50)
        pp, _ = K.tandas_de_10(m["_cob"], 90.20)
        filas.append({"ventaja": esc, "riesgo eval $": rie, "pasan/10": round(m["pase_de_10"], 1),
                      "cobran/10": round(m["cobran_de_10"], 1), "EV/cuenta $": round(m["cobro_medio_por_eval"] - 90.20),
                      "tandas de 10 en pérdidas": f"{pp:.0%}"})
print(pd.DataFrame(filas).to_string(index=False))
