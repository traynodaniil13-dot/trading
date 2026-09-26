"""Batería de controles (CLAUDE.md sección 4).

- paseo_aleatorio      control 0: misma rejilla temporal, vol por minuto del día real,
                       máx/mín intravela de 12 subpasos.
- chequear_generador   carrera a barreras simétricas desde puntos al azar -> 50/50.
- resumen              R media, ee, t, p, winrate.
- placebo_direccion    control 1 + regla B: mismo sorteo por sesión para toda la
                       familia, máximo real contra distribución del máximo del nulo.
- invertida            control 2 + regla C.
- consistencia         control 3.
- z_exceso             regla O.
- bonferroni           control 5.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import motor

TICK = 0.25


# ---------------------------------------------------------------- control 0

def paseo_aleatorio(real: pd.DataFrame, semilla: int, subpasos: int = 12) -> pd.DataFrame:
    """Serie sin ninguna información, con el mismo índice, sesiones y perfil de
    volatilidad por minuto del día que `real`. Devuelve o,h,l,c,sesion,hhmm."""
    rng = np.random.default_rng(semilla)
    c_real = real["c"].to_numpy(float)
    hhmm = real["hhmm"].to_numpy()
    dt = np.diff(real.index.values).astype("timedelta64[m]").astype(int)
    ret = np.diff(c_real)
    contiguo = dt == 1
    # sigma por minuto del día a partir del RANGO medio real (E[rango] = raíz(8/pi)·sigma
    # en un browniano). La sd de los retornos se infla con los picos de noticias.
    rango = pd.Series((real["h"] - real["l"]).to_numpy()).groupby(hhmm).mean()
    sig_min = rango / np.sqrt(8 / np.pi)
    sigma = sig_min.reindex(hhmm).fillna(sig_min.median()).to_numpy()
    sd_hueco = ret[dt >= 60].std()

    n = len(real)
    hueco = np.zeros(n)
    salto = np.r_[1, dt]
    grande = salto >= 60
    hueco[grande] = rng.standard_normal(grande.sum()) * sd_hueco
    peq = (salto > 1) & ~grande
    hueco[peq] = rng.standard_normal(peq.sum()) * sigma[peq] * np.sqrt(salto[peq] - 1)
    hueco[0] = 0.0

    o = np.empty(n); h = np.empty(n); l = np.empty(n); c = np.empty(n)
    nivel = c_real[0]
    trozo = 200_000
    for s in range(0, n, trozo):
        e = min(n, s + trozo)
        var_sub = (sigma[s:e, None] ** 2) / subpasos
        z = rng.standard_normal((e - s, subpasos)) * np.sqrt(var_sub)
        cam = np.cumsum(z, axis=1)
        ini = np.hstack([np.zeros((e - s, 1)), cam[:, :-1]])
        # Máx/mín EXACTOS de un puente browniano entre cada par de subpasos. Con
        # solo los puntos, el motor (que llena el stop en el nivel, camino continuo)
        # se regala el salto del camino discreto: +0,015R a 1:2 en las dos direcciones.
        sep2 = (cam - ini) ** 2
        u1 = rng.random((e - s, subpasos))
        u2 = rng.random((e - s, subpasos))
        maxi = (ini + cam + np.sqrt(sep2 - 2 * var_sub * np.log(u1))) / 2
        mini = (ini + cam - np.sqrt(sep2 - 2 * var_sub * np.log(u2))) / 2
        mov = hueco[s:e] + cam[:, -1]
        cierre = nivel + np.cumsum(mov)
        apertura = cierre - cam[:, -1]
        o[s:e] = apertura
        c[s:e] = cierre
        h[s:e] = apertura + maxi.max(axis=1)
        l[s:e] = apertura + mini.min(axis=1)
        nivel = cierre[-1]

    r = lambda x: np.round(x / TICK) * TICK
    o, c = r(o), r(c)
    h = np.maximum(r(h), np.maximum(o, c))
    l = np.minimum(r(l), np.minimum(o, c))
    return pd.DataFrame({"o": o, "h": h, "l": l, "c": c, "sesion": real["sesion"].to_numpy(),
                         "hhmm": hhmm}, index=real.index)


def carrera_barreras(barras: pd.DataFrame, i0: np.ndarray, x_pts: float, horizonte: int = 390):
    """Desde el cierre de la barra i0, ¿toca antes +x o -x? Empieza en i0+1.
    Devuelve array con +1 (arriba), -1 (abajo), 0 (misma barra o sin resolver)."""
    h, l, c = (barras[k].to_numpy(float) for k in ("h", "l", "c"))
    out = np.zeros(len(i0), dtype=int)
    for k, i in enumerate(i0):
        ref = c[i]
        hh, ll = h[i + 1:i + 1 + horizonte], l[i + 1:i + 1 + horizonte]
        up = np.flatnonzero(hh >= ref + x_pts)
        dn = np.flatnonzero(ll <= ref - x_pts)
        a = up[0] if up.size else 10 ** 9
        b = dn[0] if dn.size else 10 ** 9
        if a < b:
            out[k] = 1
        elif b < a:
            out[k] = -1
    return out


def chequear_generador(barras: pd.DataFrame, n: int = 20_000, x_pts: float = 20.0, semilla: int = 0) -> dict:
    rng = np.random.default_rng(semilla)
    i0 = rng.integers(0, len(barras) - 400, n)
    res = carrera_barreras(barras, i0, x_pts)
    ok = res != 0
    arriba = (res[ok] == 1).mean()
    p = stats.binomtest(int((res[ok] == 1).sum()), int(ok.sum()), 0.5).pvalue
    return {"n_resueltas": int(ok.sum()), "pct_arriba": arriba, "p": p}


# ---------------------------------------------------------------- estadística

def resumen(r: np.ndarray) -> dict:
    r = np.asarray(r, float)
    n = len(r)
    m = r.mean()
    ee = r.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
    t = m / ee if ee > 0 else np.nan
    return {"n": n, "R": m, "ee": ee, "t": t, "p_1cola": stats.t.sf(t, n - 1) if n > 1 else np.nan,
            "wr": (r > 0).mean(), "R_total": r.sum()}


def z_exceso(m_real, ee_real, m_nulo, ee_nulo):
    """Regla O: el exceso se divide por los dos errores."""
    return (m_real - m_nulo) / np.sqrt(ee_real ** 2 + ee_nulo ** 2)


def bonferroni(p: float, n_variantes: int) -> float:
    return min(1.0, p * n_variantes)


# ---------------------------------------------------------------- controles 1 y 2

def invertida(ops: pd.DataFrame, ratio: float) -> dict:
    """Control 2 + regla C."""
    nor = motor.r_neta(ops, ratio).mean()
    inv = motor.r_neta(ops, ratio, invertida=True).mean()
    return {"normal": nor, "invertida": inv, "suma": nor + inv,
            "comun": (nor + inv) / 2, "direccional": (nor - inv) / 2}


def placebo_direccion(familia: dict[str, pd.DataFrame], ratio: float, reps: int = 200, semilla: int = 0) -> dict:
    """Regla B. `familia` = {nombre_config: ops simuladas}. Un mismo sorteo por
    SESIÓN para todas las configuraciones. Compara el máximo real contra la
    distribución del máximo del nulo."""
    rng = np.random.default_rng(semilla)
    sesiones = np.unique(np.concatenate([f["sesion"].to_numpy() for f in familia.values()]))
    idx = {nombre: np.searchsorted(sesiones, f["sesion"].to_numpy()) for nombre, f in familia.items()}
    real = {nombre: motor.r_neta(f, ratio).mean() for nombre, f in familia.items()}
    maxs = np.empty(reps)
    for k in range(reps):
        volt = rng.random(len(sesiones)) < 0.5
        maxs[k] = max(motor.r_mezcla(f, ratio, volt[idx[nom]]).mean() for nom, f in familia.items())
    mejor = max(real, key=real.get)
    return {"mejor": mejor, "R_mejor": real[mejor], "max_nulo_media": maxs.mean(), "max_nulo_sd": maxs.std(ddof=1),
            "sigmas": (real[mejor] - maxs.mean()) / maxs.std(ddof=1), "p": (maxs >= real[mejor]).mean(),
            "real": real}


# ---------------------------------------------------------------- control 3

def consistencia(ops: pd.DataFrame, r: np.ndarray) -> dict:
    s = pd.Series(np.asarray(r, float), index=pd.DatetimeIndex(ops["t_ent"]))
    mes = s.groupby(s.index.to_period("M")).sum()
    eq = s.cumsum().to_numpy()
    dd = (np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq]).max()
    racha = mx = 0
    for x in s.to_numpy():
        racha = racha + 1 if x < 0 else 0
        mx = max(mx, racha)
    anio = s.groupby(s.index.year).agg(["mean", "count"])
    return {"pct_meses_pos": (mes > 0).mean(), "R_total": s.sum(),
            "R_sin_3_mejores_meses": s.sum() - mes.nlargest(3).sum(),
            "racha_perdedoras": mx, "max_dd_R": dd,
            "por_anio": {int(y): (round(m, 3), int(n)) for y, (m, n) in anio.iterrows()}}
