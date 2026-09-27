"""Premisas desnudas (regla Q). Cada función devuelve un DataFrame por sesión con
`s` (señal ±1, conocida antes de la entrada) e `y` (puntos a favor de la señal,
brutos). Definiciones: preregistros/2026-09-27_premisas_lote1.md.

Todas las horas usadas están entre 02:00 y 16:00, así que la `sesion` coincide
con la fecha natural y no hay ambigüedad con la tarde anterior (bug nº6).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _rejilla(b: pd.DataFrame, minutos) -> dict[str, pd.DataFrame]:
    """{campo: DataFrame sesion x hhmm} solo para los minutos pedidos (< 17:00)."""
    minutos = sorted(set(minutos))
    assert all(0 <= m < 1700 for m in minutos)
    sub = b[b["hhmm"].isin(minutos)]
    return {k: sub.pivot_table(index="sesion", columns="hhmm", values=k, aggfunc="first")
            for k in ("o", "h", "l", "c")}


def _rango(g, desde, hasta):
    cols = [m for m in g["h"].columns if desde <= m <= hasta]
    return g["h"][cols] - g["l"][cols]


def _fuera(s, y):
    df = pd.DataFrame({"s": s, "y": y}).dropna()
    df = df[df["s"] != 0]
    df["s"] = df["s"].astype(int)
    return df


def p1_momento_ultima_media_hora(b):
    g = _rejilla(b, [959, 1530, 1559])
    c_prev = g["c"][1559].shift(1)
    s = np.sign(g["c"][959] - c_prev)
    return _fuera(s, (g["c"][1559] - g["o"][1530]) * s)


def _macro(b, t, desde, hasta, salida):
    ent = t + 1
    g = _rejilla(b, list(range(desde, hasta + 1)) + [t, ent, salida])
    base = _rango(g, desde, hasta).median(axis=1)
    rt = g["h"][t] - g["l"][t]
    s = np.sign(g["c"][t] - g["o"][t]).where(rt > 3 * base)
    return _fuera(s, (g["c"][salida] - g["o"][ent]) * s)


def p2_macro_0830(b):
    return _macro(b, 830, 820, 829, 859)


def p3_macro_1000(b):
    return _macro(b, 1000, 950, 959, 1029)


def p4_primera_m5(b):
    g = _rejilla(b, [930, 931, 932, 933, 934, 935, 1059])
    cols = [930, 931, 932, 933, 934]
    cuerpo = g["c"][934] - g["o"][930]
    rango = g["h"][cols].max(axis=1) - g["l"][cols].min(axis=1)
    s = np.sign(cuerpo).where(cuerpo.abs() > 0.6 * rango)
    return _fuera(s, (g["c"][1059] - g["o"][935]) * s)


def p5_gap(b):
    g = _rejilla(b, [930, 931, 1559])
    c_prev = g["c"][1559].shift(1)
    gap = g["o"][930] - c_prev
    s = np.sign(gap).where(gap.abs() >= 0.001 * c_prev)
    return _fuera(s, (g["c"][1559] - g["o"][931]) * s)


def p6_cambio_de_mes(b):
    """Devuelve y = retorno largo del día y `tom` (bool). No es direccional."""
    g = _rejilla(b, [930, 1559])
    y = (g["c"][1559] - g["o"][930]).dropna()
    ses = pd.Series(y.index, index=y.index)
    mes = ses.dt.to_period("M")
    orden = ses.groupby(mes).rank(method="first")
    ultimo = ses.groupby(mes).transform("max") == ses
    tom = (orden <= 3) | ultimo
    return pd.DataFrame({"y": y, "tom": tom})


def p7_momento_londres(b):
    g = _rejilla(b, [200, 459, 500, 759])
    s = np.sign(g["c"][459] - g["o"][200])
    return _fuera(s, (g["c"][759] - g["o"][500]) * s)


DIRECCIONALES = {
    "P1_ultima_media_hora": p1_momento_ultima_media_hora,
    "P2_macro_0830": p2_macro_0830,
    "P3_macro_1000": p3_macro_1000,
    "P4_primera_m5": p4_primera_m5,
    "P5_gap": p5_gap,
    "P7_londres": p7_momento_londres,
}


def evaluar(df: pd.DataFrame) -> dict:
    """Media de y, t, p bilateral, por año y por dirección (regla M)."""
    y = df["y"].to_numpy(float)
    t, p = stats.ttest_1samp(y, 0.0)
    anio = df.groupby(df.index.year)["y"].mean()
    dirs = df.groupby("s")["y"].agg(["mean", "count"])
    return {"n": len(y), "media": y.mean(), "ee": y.std(ddof=1) / np.sqrt(len(y)), "t": t, "p": p,
            "anio": anio.round(2).to_dict(),
            "largos": (round(dirs.loc[1, "mean"], 2), int(dirs.loc[1, "count"])) if 1 in dirs.index else None,
            "cortos": (round(dirs.loc[-1, "mean"], 2), int(dirs.loc[-1, "count"])) if -1 in dirs.index else None}


def evaluar_tom(df: pd.DataFrame) -> dict:
    a, b = df.loc[df["tom"], "y"], df.loc[~df["tom"], "y"]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    anio = df.groupby([df.index.year, "tom"])["y"].mean().unstack()
    return {"n_tom": len(a), "n_resto": len(b), "media": a.mean() - b.mean(), "tom": a.mean(), "resto": b.mean(),
            "t": t, "p": p, "anio": (anio[True] - anio[False]).round(2).to_dict()}
