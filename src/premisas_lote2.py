"""Lote 2 de premisas. Definiciones: preregistros/2026-09-27_premisas_lote2.md."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .premisas import _fuera, _rejilla


def _diario(b):
    """Por sesión: o 09:30, c 15:59, máx/mín RTH (09:30-15:59)."""
    rth = b[(b["hhmm"] >= 930) & (b["hhmm"] <= 1559)]
    g = rth.groupby("sesion")
    d = pd.DataFrame({"hi": g["h"].max(), "lo": g["l"].min()})
    x = _rejilla(b, [930, 1559])
    d["o"], d["c"] = x["o"][930], x["c"][1559]
    return d.dropna().sort_index()


def q1_vuelta_media(b):
    m = b[(b["hhmm"] >= 930) & (b["hhmm"] <= 1059)]
    g = m.groupby("sesion")
    tipico = ((m["h"] + m["l"] + m["c"]) / 3).groupby(m["sesion"]).mean()
    rango = g["h"].max() - g["l"].min()
    x = _rejilla(b, [1059, 1100, 1259])
    dev = x["c"][1059] - tipico
    s = (-np.sign(dev)).where(dev.abs() > 0.5 * rango)
    return _fuera(s, (x["c"][1259] - x["o"][1100]) * s)


def q2_nr7(b):
    d = _diario(b)
    r = d["hi"] - d["lo"]
    nr7 = r < r.shift(1).rolling(6, min_periods=6).min()
    previa_nr7 = nr7.shift(1).fillna(False).astype(bool)
    x = _rejilla(b, [930, 959, 1000, 1559])
    s = np.sign(x["c"][959] - x["o"][930]).where(previa_nr7.reindex(x["c"].index).fillna(False))
    return _fuera(s, (x["c"][1559] - x["o"][1000]) * s)


def q3_tarde(b):
    x = _rejilla(b, [930, 1259, 1300, 1559])
    s = np.sign(x["c"][1259] - x["o"][930])
    return _fuera(s, (x["c"][1559] - x["o"][1300]) * s)


def q4_cierre_extremo(b):
    d = _diario(b)
    pos = ((d["c"] - d["lo"]) / (d["hi"] - d["lo"])).shift(1)
    s = pd.Series(np.where(pos > 0.8, 1.0, np.where(pos < 0.2, -1.0, np.nan)), index=d.index)
    return _fuera(s, (d["c"] - d["o"]) * s)


def q5_momentum_10d(b):
    d = _diario(b)
    s = np.sign(d["c"].shift(1) - d["c"].shift(11))
    return _fuera(s, (d["c"] - d["o"]) * s)


def q6_reversion_extremo(b):
    d = _diario(b)
    ret = ((d["c"] - d["o"]) / d["o"]).shift(1)
    s = (-np.sign(ret)).where(ret.abs() > 0.015)
    return _fuera(s, (d["c"] - d["o"]) * s)


def q7_dia_semana(b):
    d = _diario(b)
    return pd.DataFrame({"y": d["c"] - d["o"], "dia": d.index.dayofweek})


DIRECCIONALES = {
    "Q1_vuelta_media": q1_vuelta_media,
    "Q2_nr7": q2_nr7,
    "Q3_tarde": q3_tarde,
    "Q4_cierre_extremo": q4_cierre_extremo,
    "Q5_momentum_10d": q5_momentum_10d,
    "Q6_reversion_extremo": q6_reversion_extremo,
}


def evaluar_dias(df):
    grupos = [g["y"].to_numpy() for _, g in df.groupby("dia")]
    f, p = stats.f_oneway(*grupos)
    tabla = df.groupby([df.index.year, "dia"])["y"].mean().unstack()
    rel = tabla.sub(tabla.mean(axis=1), axis=0)
    return {"F": f, "p": p, "media_por_dia": df.groupby("dia")["y"].mean().round(1).to_dict(),
            "rel_por_anio": rel.round(1).to_dict(orient="index")}
