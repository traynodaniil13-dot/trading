"""Riesgo dinámico en evaluación/fondeada 50K con Momento S1. Ver pre-registro 2026-10-01_cuentas_reglas_bot.md (añadido 4)."""
import numpy as np, pandas as pd
from src import cuentas as K
from scripts.cuentas_rtp_vs_momento import junta

R = K.Reglas(inicial=50_000, dd=2_000, objetivo=3_000, tope_eval=40, tope_fund_ini=40, tope_fund=40,
             pago_min=1_000, pago_max=2_000, dia_min=200)
PRECIO = 90.20
POL = {"fijo 464": lambda m: 464, "fijo 500": lambda m: 500, "fijo 750": lambda m: 750,
       "A (750, 500 si margen<1250)": lambda m: 750 if m >= 1250 else 500,
       "B (min 750, margen)": lambda m: min(750, m)}


def micros(riesgo, pts, tope):
    return int(min(tope, max(1, np.floor(riesgo / (pts * 2)))))


def evaluacion(r, mae, pts, pol):
    bal = alto = R.inicial; mll = R.inicial - R.dd; mejor = 0.0
    for i in range(len(r)):
        riesgo = micros(pol(bal - mll), pts[i], R.tope_eval) * pts[i] * 2
        if bal - mae[i] * riesgo <= mll: return False, i + 1
        pnl = r[i] * riesgo; bal += pnl
        if bal <= mll: return False, i + 1
        mejor = max(mejor, pnl); alto = max(alto, bal); mll = max(mll, min(alto - R.dd, R.inicial + R.tope_mll))
        ben = bal - R.inicial
        if ben >= R.objetivo and mejor <= R.consistencia * ben: return True, i + 1
    return False, len(r)


def fondeada(r, mae, pts, pol):
    bal = alto = R.inicial; mll = R.inicial - R.dd; cob, pagos, dias, ciclo = 0.0, 0, 0, 0.0
    for i in range(len(r)):
        riesgo = micros(pol(bal - mll), pts[i], R.tope_fund) * pts[i] * 2
        if bal - mae[i] * riesgo <= mll: return cob, pagos
        pnl = r[i] * riesgo; bal += pnl
        if bal <= mll: return cob, pagos
        alto = max(alto, bal); mll = max(mll, min(alto - R.dd, R.inicial + R.tope_mll))
        ciclo += pnl; dias += pnl >= R.dia_min; ben = bal - R.inicial
        if dias >= R.dias_ciclo and ciclo > 0:
            imp = min(R.pago_max, R.pago_frac * ben)
            if imp >= R.pago_min:
                bal -= imp; cob += imp * R.reparto; pagos += 1; mll = max(mll, R.inicial + R.tope_mll); dias, ciclo = 0, 0.0
                if pagos >= R.max_pagos: return cob, pagos
    return cob, pagos


o, mae, r0 = junta("Momento S1")
pts = o.riesgo_pts.to_numpy() * 29_000 / o.precio.to_numpy()
filas = []
for esc, r in (("histórica S1", r0), ("cero", r0 - r0.mean())):
    for nombre, pol in POL.items():
        for fase in ("solo eval", "eval+fondeada"):
            pf = POL["fijo 464"] if fase == "solo eval" else pol
            if fase == "eval+fondeada" and nombre == "fijo 464": continue
            rng = np.random.default_rng(0); N = len(r); n = 4000
            pasa = np.zeros(n, bool); cob = np.zeros(n); npag = np.zeros(n, int); dur = np.zeros(n)
            for k in range(n):
                idx = (rng.integers(N) + np.arange(1000)) % N
                ok, ne = evaluacion(r[idx[:500]], mae[idx[:500]], pts[idx[:500]], pol); pasa[k], dur[k] = ok, ne
                if ok:
                    j = idx[ne:ne + 500]; cob[k], npag[k] = fondeada(r[j], mae[j], pts[j], pf)
            pp, _ = K.tandas_de_10(cob, PRECIO)
            filas.append({"ventaja": esc, "riesgo": nombre, "aplica a": fase, "pasan/10": round(10 * pasa.mean(), 1),
                          "ops hasta pasar": np.median(dur[pasa]), "cobran/10": round(10 * (npag > 0).mean(), 1),
                          "EV/cuenta $": round(cob.mean() - PRECIO), "tandas10 en pérdidas": f"{pp:.0%}"})
pd.set_option("display.width", 220)
print(pd.DataFrame(filas).to_string(index=False))
