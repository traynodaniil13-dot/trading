"""Simulador de Lucid Flex 25K (CLAUDE.md sección 8).

Interpretación de las reglas (explícita; si alguna es falsa, se cambia aquí):
- MLL trailing de $1.000 sobre el MÁXIMO del balance al cierre del día (EOD).
  Deja de subir cuando llega a inicial + $100 (balance EOD de $26.100).
- Breach intradía: si en algún momento del día equity ≤ MLL, cuenta perdida.
  El peor momento de cada operación se toma de su recorrido adverso real (MAE)
  hasta la salida, calculado sobre las barras.
- Evaluación: objetivo +$1.250 con consistencia 50% (el mejor día ≤ 50% del
  beneficio total en el momento de pasar). Tope 20 micros. Sin límite de tiempo.
- Fondeada: cuenta nueva a $25.000 con el mismo MLL. Tope 10 micros hasta
  +$1.000 de beneficio, luego 20. Retiro cuando hay ≥5 días con ≥$100 netos en
  el ciclo y el ciclo es positivo: importe = min($1.000, 50% del beneficio), si
  ≥ $500. Al solicitarlo, el MLL pasa a inicial + $100. Reparto 90%. Máx. 5.
- Una operación por día. MNQ = $2 por punto. Micros = floor(riesgo$ / (stop·2)),
  mínimo 1. El coste (0,87 pts) ya va dentro de la R neta.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

USD_PT = 2.0


@dataclass
class Reglas:
    inicial: float = 25_000
    dd: float = 1_000
    tope_mll: float = 100          # el MLL se congela en inicial + esto
    objetivo: float = 1_250
    consistencia: float = 0.5
    tope_eval: int = 20
    tope_fund_ini: int = 10
    tope_fund: int = 20
    umbral_tope: float = 1_000
    pago_min: float = 500
    pago_max: float = 1_000
    pago_frac: float = 0.5
    dias_ciclo: int = 5
    dia_min: float = 100
    reparto: float = 0.9
    max_pagos: int = 5


def mae_hasta_salida(barras: pd.DataFrame, ops: pd.DataFrame, ratio: float, invertida: bool = False) -> np.ndarray:
    """Recorrido adverso máximo (en R, ≤ 1) desde la entrada hasta la salida real
    (objetivo, stop o cierre). Misma convención que el motor: en la barra de
    entrada solo cuenta lo adverso; el objetivo se toca desde la siguiente."""
    h, l = barras["h"].to_numpy(float), barras["l"].to_numpy(float)
    out = np.zeros(len(ops))
    for k, (a, b, p, r, d) in enumerate(ops[["i_ent", "i_fin", "precio", "riesgo_pts", "dir"]].itertuples(index=False)):
        d = -d if invertida else d
        a, b = int(a), int(b)
        fav = (h[a:b + 1] - p) * d / r if d == 1 else (p - l[a:b + 1]) / r
        adv = (p - l[a:b + 1]) / r if d == 1 else (h[a:b + 1] - p) / r
        fav = fav.copy(); fav[0] = -np.inf
        stop = np.flatnonzero(adv >= 1)
        obj = np.flatnonzero(fav >= ratio)
        fin = min(stop[0] if stop.size else b - a, obj[0] if obj.size else b - a)
        if stop.size and stop[0] <= fin:
            out[k] = 1.0
        else:
            out[k] = float(np.clip(adv[:fin + 1].max(), 0, 1))
    return out


def _micros(riesgo_usd, stop_pts, tope):
    return int(min(tope, max(1, np.floor(riesgo_usd / (stop_pts * USD_PT)))))


def evaluacion(r, mae, pts, riesgo_usd, R: Reglas):
    """Recorre la secuencia hasta pasar o quemar. Devuelve (pasa, n_ops)."""
    bal, alto = R.inicial, R.inicial
    mll = R.inicial - R.dd
    mejor_dia = 0.0
    for i in range(len(r)):
        m = _micros(riesgo_usd, pts[i], R.tope_eval)
        riesgo = m * pts[i] * USD_PT
        if bal - mae[i] * riesgo <= mll:
            return False, i + 1
        pnl = r[i] * riesgo
        bal += pnl
        if bal <= mll:
            return False, i + 1
        mejor_dia = max(mejor_dia, pnl)
        alto = max(alto, bal)
        mll = max(mll, min(alto - R.dd, R.inicial + R.tope_mll))
        ben = bal - R.inicial
        if ben >= R.objetivo and mejor_dia <= R.consistencia * ben:
            return True, i + 1
    return False, len(r)


def fondeada(r, mae, pts, riesgo_usd, R: Reglas):
    """Devuelve (cobrado_neto_trader, n_pagos, n_ops)."""
    bal, alto = R.inicial, R.inicial
    mll = R.inicial - R.dd
    cobrado, pagos, dias_ok, ciclo = 0.0, 0, 0, 0.0
    for i in range(len(r)):
        ben = bal - R.inicial
        tope = R.tope_fund if ben >= R.umbral_tope else R.tope_fund_ini
        m = _micros(riesgo_usd, pts[i], tope)
        riesgo = m * pts[i] * USD_PT
        if bal - mae[i] * riesgo <= mll:
            return cobrado, pagos, i + 1
        pnl = r[i] * riesgo
        bal += pnl
        if bal <= mll:
            return cobrado, pagos, i + 1
        alto = max(alto, bal)
        mll = max(mll, min(alto - R.dd, R.inicial + R.tope_mll))
        ciclo += pnl
        dias_ok += pnl >= R.dia_min
        ben = bal - R.inicial
        if dias_ok >= R.dias_ciclo and ciclo > 0:
            importe = min(R.pago_max, R.pago_frac * ben)
            if importe >= R.pago_min:
                bal -= importe
                cobrado += importe * R.reparto
                pagos += 1
                mll = max(mll, R.inicial + R.tope_mll)
                dias_ok, ciclo = 0, 0.0
                if pagos >= R.max_pagos:
                    return cobrado, pagos, i + 1
    return cobrado, pagos, len(r)


def montecarlo(r, mae, pts, riesgo_eval=500, riesgo_fund=500, n=4000, largo=400, semilla=0, R: Reglas = Reglas(),
               r_fund=None, mae_fund=None):
    """Secuencias por bloques: arranque al azar en la historia real y operaciones
    consecutivas (conserva rachas y regímenes). Devuelve métricas por cuenta."""
    rng = np.random.default_rng(semilla)
    N = len(r)
    r, mae, pts = (np.asarray(x, float) for x in (r, mae, pts))
    r_f = r if r_fund is None else np.asarray(r_fund, float)
    mae_f = mae if mae_fund is None else np.asarray(mae_fund, float)
    pasa = np.zeros(n, bool); cob = np.zeros(n); npag = np.zeros(n, int); ops_eval = np.zeros(n, int)
    for k in range(n):
        i0 = rng.integers(N)
        idx = (i0 + np.arange(2 * largo)) % N
        ok, ne = evaluacion(r[idx[:largo]], mae[idx[:largo]], pts[idx[:largo]], riesgo_eval, R)
        pasa[k], ops_eval[k] = ok, ne
        if ok:
            j = idx[ne:ne + largo]
            cob[k], npag[k], _ = fondeada(r_f[j], mae_f[j], pts[j], riesgo_fund, R)
    return {"pase_de_10": 10 * pasa.mean(), "cobran_de_10": 10 * (npag > 0).mean(),
            "cobro_medio_por_eval": cob.mean(), "cobro_medio_si_cobra": cob[npag > 0].mean() if (npag > 0).any() else 0.0,
            "ops_hasta_pasar_mediana": float(np.median(ops_eval[pasa])) if pasa.any() else np.nan,
            "pagos_medios_si_pasa": npag[pasa].mean() if pasa.any() else 0.0, "_cob": cob}


def tandas_de_10(cob, coste_eval, n_tandas=20_000, semilla=1):
    """% de tandas de 10 cuentas que pierden dinero con un coste por evaluación dado."""
    rng = np.random.default_rng(semilla)
    t = rng.choice(cob, size=(n_tandas, 10)).sum(axis=1) - 10 * coste_eval
    return (t < 0).mean(), np.median(t)
