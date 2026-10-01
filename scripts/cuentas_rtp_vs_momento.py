"""Misma cuenta (50K, 2 micros equiv. ~$464/op, MLL intradía, retiro desde $1.000) para
Momento 0,40% · Momento S1 (stop en cierre 09:09) · RTP base. R histórica 2021-2026 CFD."""
import numpy as np, pandas as pd
from src import cuentas as K, loader, motor
from src.motores import momento_generico as MG, rtp
from scripts.rtp_filtros import SIN_OBJ

R = K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=40, tope_fund=40,
             pago_min=1_000, pago_max=2_000, dia_min=200)
PRECIO, RIESGO, NQ_HOY = 90.20, 465, 29_000


def s1(b, s):
    c = b.c.to_numpy(); m909 = b.hhmm.to_numpy() == 909
    ref = pd.Series(np.flatnonzero(m909), index=b.sesion.to_numpy()[m909]); ref = ref[~ref.index.duplicated()]
    i_ref = ref.reindex(b.sesion.to_numpy()[s.i_ent.to_numpy()]).to_numpy().astype(int)
    assert (b.hhmm.to_numpy()[i_ref] == 909).all() and (i_ref < s.i_ent.to_numpy()).all()
    dist = (s.precio.to_numpy() - c[i_ref]) * s.dir.to_numpy()
    s = s.assign(riesgo=dist)
    return s[(dist > 0) & (dist >= 0.001 * s.precio.to_numpy())]


def junta(nombre):
    o_all, mae_all, ratio = [], [], (SIN_OBJ if nombre == "RTP" else 2.0)
    for a in range(2021, 2027):
        b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
        if nombre == "RTP":
            s = rtp.senales(b)
        else:
            s = MG.senales(b, 940, 30, 0.40)
            if nombre == "Momento S1": s = s1(b, s)
        o = motor.simular(b, s); o = o[o.sesion.dt.year == a].reset_index(drop=True)
        mae_all.append(K.mae_hasta_salida(b, o, ratio)); o_all.append(o)
    o = pd.concat(o_all, ignore_index=True)
    return o, np.concatenate(mae_all), motor.r_neta(o, ratio)


filas = []
for nombre in ("Momento 0,40%", "Momento S1", "RTP"):
    o, mae, r = junta(nombre)
    pts = o.riesgo_pts.to_numpy() * NQ_HOY / o.precio.to_numpy()
    m = K.montecarlo(r, mae, pts, riesgo_eval=RIESGO, riesgo_fund=RIESGO, n=4000, largo=500, R=R)
    pp, _ = K.tandas_de_10(m["_cob"], PRECIO)
    filas.append({"estrategia": nombre, "ops": len(r), "R/op": round(r.mean(), 3), "winrate": f"{(r > 0).mean():.0%}",
                  "stop mediano hoy (pts)": round(np.median(pts)), "pasan/10": round(m["pase_de_10"], 1),
                  "cobran/10": round(m["cobran_de_10"], 1), "EV/cuenta $": round(m["cobro_medio_por_eval"] - PRECIO),
                  "tandas10 en pérdidas": f"{pp:.0%}"})
pd.set_option("display.width", 200)
print(pd.DataFrame(filas).to_string(index=False))
