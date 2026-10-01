"""Negocio de 12 meses con copiador: todas las cuentas operan la MISMA secuencia diaria.
50K, 2 micros, MLL intradía, retiro desde $1.000. Máx. 5 fondeadas y 10 cuentas en total.
Política: mantener K evaluaciones vivas; al quemarse o pasar una, se compra otra al día siguiente
(si hay hueco: fondeadas < 5 y total < 10)."""
import numpy as np, pandas as pd
from src import cuentas as K, loader, motor
from src.motores import momento_generico as MG

ops, mae = [], []
for a in range(2021, 2027):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(b, MG.senales(b, 940, 30, 0.40)); o = o[o.sesion.dt.year == a].reset_index(drop=True)
    mae.append(K.mae_hasta_salida(b, o, 2.0)); ops.append(o)
o = pd.concat(ops, ignore_index=True); MAE = np.concatenate(mae); r0 = motor.r_neta(o, 2.0)
R = K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=40, tope_fund=40,
             pago_min=1_000, pago_max=2_000, dia_min=200)
PRECIO, RIESGO, DIAS = 90.20, 2 * 116 * 2.0, 250

def eval_paso(st, r, m):
    """Un día de evaluación. Devuelve 'vivo' | 'quemada' | 'pasa'."""
    riesgo = RIESGO
    if st["bal"] - m * riesgo <= st["mll"]: return "quemada"
    pnl = r * riesgo; st["bal"] += pnl
    if st["bal"] <= st["mll"]: return "quemada"
    st["mejor"] = max(st["mejor"], pnl); st["alto"] = max(st["alto"], st["bal"])
    st["mll"] = max(st["mll"], min(st["alto"] - R.dd, R.inicial + R.tope_mll))
    ben = st["bal"] - R.inicial
    return "pasa" if ben >= R.objetivo and st["mejor"] <= R.consistencia * ben else "vivo"

def fund_paso(st, r, m):
    """Un día de fondeada. Devuelve (estado, cobrado_hoy)."""
    riesgo = RIESGO
    if st["bal"] - m * riesgo <= st["mll"]: return "quemada", 0.0
    pnl = r * riesgo; st["bal"] += pnl
    if st["bal"] <= st["mll"]: return "quemada", 0.0
    st["alto"] = max(st["alto"], st["bal"]); st["mll"] = max(st["mll"], min(st["alto"] - R.dd, R.inicial + R.tope_mll))
    st["ciclo"] += pnl; st["dias"] += pnl >= R.dia_min
    ben = st["bal"] - R.inicial
    if st["dias"] >= R.dias_ciclo and st["ciclo"] > 0:
        imp = min(R.pago_max, R.pago_frac * ben)
        if imp >= R.pago_min:
            st["bal"] -= imp; st["pagos"] += 1; st["mll"] = max(st["mll"], R.inicial + R.tope_mll)
            st["dias"], st["ciclo"] = 0, 0.0
            return ("live" if st["pagos"] >= R.max_pagos else "vivo"), imp * R.reparto
    return "vivo", 0.0

nueva = lambda: dict(bal=R.inicial, alto=R.inicial, mll=R.inicial - R.dd, mejor=0.0, ciclo=0.0, dias=0, pagos=0)

def un_anio(r, m, k_eval, rng):
    i0 = rng.integers(len(r)); idx = (i0 + np.arange(DIAS)) % len(r)
    evals, funds = [], []; caja, gastado, cobrado, peor = 0.0, 0.0, 0.0, 0.0
    compradas = pasadas = 0
    for d in idx:
        while len(evals) < k_eval and len(funds) < 5 and len(evals) + len(funds) < 10:
            evals.append(nueva()); caja -= PRECIO; gastado += PRECIO; compradas += 1
        sig = []
        for st in evals:
            e = eval_paso(st, r[d], m[d])
            if e == "vivo": sig.append(st)
            elif e == "pasa": funds.append(nueva()); pasadas += 1
        evals = sig; sig = []
        for st in funds:
            e, c = fund_paso(st, r[d], m[d]); caja += c; cobrado += c
            if e == "vivo": sig.append(st)
        funds = sig; peor = min(peor, caja)
    return caja, gastado, cobrado, peor, compradas, pasadas

filas = []
for esc, obj in (("+0,05R", 0.05), ("cero", 0.0)):
    r = r0 - (r0.mean() - obj)
    for k in (1, 2, 3, 5):
        rng = np.random.default_rng(7)
        res = np.array([un_anio(r, MAE, k, rng) for _ in range(2000)])
        neto, gast, cob, peor, comp, pas = res.T
        filas.append({"ventaja": esc, "evals a la vez": k, "evals compradas/año": round(comp.mean(), 1),
                      "pasadas/año": round(pas.mean(), 1), "gastado $": round(gast.mean()), "cobrado $": round(cob.mean()),
                      "neto medio $": round(neto.mean()), "neto mediana $": round(np.median(neto)),
                      "P(año en pérdidas)": f"{(neto < 0).mean():.0%}", "peor hueco caja (mediana) $": round(np.median(peor)),
                      "peor hueco caja (p90) $": round(np.percentile(peor, 10))})
pd.set_option("display.width", 250)
print(pd.DataFrame(filas).to_string(index=False))
