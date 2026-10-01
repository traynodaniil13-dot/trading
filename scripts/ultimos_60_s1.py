"""Últimas 60 sesiones con señal de Momento S1 (stop en cierre 09:09, 1:2) en CFD 2026, día a día,
y una evaluación 50K simulada encima (riesgo ~$464, micros = 464/(stop·2), MLL intradía)."""
import numpy as np, pandas as pd
from src import loader, motor, cuentas as K
from src.motores import momento_generico as MG

b = loader.cargar_cfd([loader.RAIZ / "data/nq_cfd_2026.csv.gz"], verbose=False)
s = MG.senales(b, 940, 30, 0.40).tail(60).reset_index(drop=True)
c = b.c.to_numpy(); hh = b.hhmm.to_numpy(); sesion = b.sesion.to_numpy()
i909 = {}
for i in np.flatnonzero(hh == 909): i909.setdefault(sesion[i], i)
i939 = {}
for i in np.flatnonzero(hh == 939): i939.setdefault(sesion[i], i)
filas = []
for _, x in s.iterrows():
    se = sesion[int(x.i_ent)]; a, z = i909[se], i939[se]
    assert a < z < x.i_ent and hh[int(x.i_ent)] == 940
    dist = (x.precio - c[a]) * x.dir
    filas.append(dict(fecha=pd.Timestamp(se).date(), c0909=round(c[a], 1), c0939=round(c[z], 1),
                      dir="LARGO" if x.dir == 1 else "CORTO", entrada=round(x.precio, 1), stop_pts=round(dist, 1),
                      opera=bool(dist > 0 and dist >= 0.001 * x.precio), i_ent=x.i_ent, i_fin=x.i_fin, d=x.dir))
t = pd.DataFrame(filas)
op = t[t.opera].copy()
sg = pd.DataFrame({"i_ent": op.i_ent.astype(int), "precio": op.entrada, "dir": op.d.astype(int), "riesgo": op.stop_pts, "i_fin": op.i_fin.astype(int)})
# precio exacto (sin redondeo) para el motor
sg["precio"] = s.loc[op.index, "precio"].to_numpy()
sg["riesgo"] = (sg.precio.to_numpy() - c[[i909[sesion[int(i)]] for i in sg.i_ent]]) * sg["dir"].to_numpy()
o = motor.simular(b, sg).reset_index(drop=True)
assert len(o) == len(op)
r = motor.r_neta(o, 2.0); mae = K.mae_hasta_salida(b, o, 2.0)
salida = np.where(o.rmax >= 2, "TP", np.where(o.toco_sl, "SL", "16h"))
op["salida"], op["R"] = salida, np.round(r, 2)
op["micros"] = np.maximum(1, np.floor(464 / (o.riesgo_pts.to_numpy() * 2))).astype(int)
op["pnl_$"] = np.round(r * op.micros * o.riesgo_pts.to_numpy() * 2).astype(int)
op["mae"] = mae
t = t.join(op[["salida", "R", "micros", "pnl_$", "mae"]])

# evaluación 50K encadenada
R_ = K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000)
n_eval, bal, alto, mll, mejor, estados = 1, 50_000.0, 50_000.0, 48_000.0, 0.0, []
for _, x in t.iterrows():
    if not x.opera:
        estados.append(f"E{n_eval} {bal - 50_000:+.0f}"); continue
    riesgo = x.micros * x.stop_pts * 2
    if bal - x.mae * riesgo <= mll or bal + x["pnl_$"] <= mll:
        estados.append(f"E{n_eval} QUEMADA"); n_eval += 1; bal, alto, mll, mejor = 50_000.0, 50_000.0, 48_000.0, 0.0; continue
    bal += x["pnl_$"]; mejor = max(mejor, x["pnl_$"]); alto = max(alto, bal)
    mll = max(mll, min(alto - 2_000, 50_100)); ben = bal - 50_000
    if ben >= 3_000 and mejor <= 0.5 * ben:
        estados.append(f"E{n_eval} APROBADA {ben:+.0f}"); n_eval += 1; bal, alto, mll, mejor = 50_000.0, 50_000.0, 48_000.0, 0.0
    else:
        estados.append(f"E{n_eval} {ben:+.0f}")
t["evaluacion"] = estados
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 100)
cols = ["fecha", "dir", "c0909", "c0939", "entrada", "stop_pts", "opera", "micros", "salida", "R", "pnl_$", "evaluacion"]
print(t[cols].to_string(index=False))
rr = t.R.dropna()
print(f"\nSesiones: {len(t)} · operadas: {len(rr)} · TP {(t.salida=='TP').sum()} · SL {(t.salida=='SL').sum()} · 16h {(t.salida=='16h').sum()}")
print(f"R total {rr.sum():+.2f} · R/op {rr.mean():+.3f} · winrate {(rr>0).mean():.0%} · $ total {t['pnl_$'].sum():+.0f}")
