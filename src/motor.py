"""Simulador común de operaciones. Las estrategias (src/motores/) solo generan
señales; la ejecución y la medición pasan todas por aquí.

Una operación se define con:
- i_ent   posición de la PRIMERA barra cuyo recorrido es posterior al relleno.
          · A mercado en la apertura de la barra k      -> i_ent = k,   precio = o[k]
          · Pendiente rellenada al cierre de la barra k -> i_ent = k+1, precio = c[k]
            (regla 3: la barra k no se evalúa para nada)
- precio  relleno REAL (regla 4: la R se mide desde aquí, no desde el nivel pedido)
- dir     +1 largo, -1 corto
- riesgo  distancia del stop en puntos, medida desde `precio`
- i_fin   última barra (incluida) en la que la operación sigue viva; se cierra a
          su cierre si no ha tocado nada.

Convenciones pesimistas:
- En la barra i_ent solo cuenta el recorrido adverso (regla 2). `adverso_primera=False`
  da la otra cota (regla A).
- En la barra donde se toca el stop no cuenta el recorrido favorable: si stop y
  objetivo caen en la misma barra, gana el stop.
- El stop se llena en el nivel (sin deslizamiento extra; va dentro del coste).

Por operación se guarda rmax, toco_sl, r_cierre y riesgo_pts (regla 6), en las
DOS direcciones. La invertida y el placebo de dirección salen de ahí gratis.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .loader import COSTE_PTS


def _una_direccion(o, h, l, c, i_ent, precio, d, riesgo, i_fin, adverso_primera):
    n = len(i_ent)
    rmax = np.zeros(n)
    toco = np.zeros(n, dtype=bool)
    rcierre = np.zeros(n)
    ini = 1 if adverso_primera else 0
    for k in range(n):
        a, b = int(i_ent[k]), int(i_fin[k])
        assert 0 <= a <= b < len(c), (k, a, b)
        p, r, dk = precio[k], riesgo[k], d[k]
        assert r > 0
        if dk == 1:
            hit = np.flatnonzero(l[a:b + 1] <= p - r)
        else:
            hit = np.flatnonzero(h[a:b + 1] >= p + r)
        fin = hit[0] if hit.size else b - a + 1  # barras anteriores a la del stop (relativo)
        if fin > ini:
            fav = h[a + ini:a + fin].max() - p if dk == 1 else p - l[a + ini:a + fin].min()
            rmax[k] = max(0.0, fav / r)
        toco[k] = hit.size > 0
        rcierre[k] = -1.0 if toco[k] else (c[b] - p) * dk / r
    return rmax, toco, rcierre


def simular(barras: pd.DataFrame, ops: pd.DataFrame, adverso_primera: bool = True) -> pd.DataFrame:
    """Añade a `ops` rmax/toco_sl/r_cierre (dirección pedida) y sus versiones _inv.

    Deduplica por barra de entrada (regla 7) y avisa de cuántas quita.
    """
    for col in ("i_ent", "precio", "dir", "riesgo", "i_fin"):
        assert col in ops.columns, col
    n0 = len(ops)
    ops = ops.drop_duplicates("i_ent").reset_index(drop=True).copy()
    if len(ops) < n0:
        print(f"[motor] dedup por barra de entrada: {n0 - len(ops)} de {n0} fuera")

    o, h, l, c = (barras[x].to_numpy(float) for x in ("o", "h", "l", "c"))
    args = (ops["i_ent"].to_numpy(), ops["precio"].to_numpy(float))
    d = ops["dir"].to_numpy(int)
    assert set(np.unique(d)) <= {-1, 1}
    rie, fin = ops["riesgo"].to_numpy(float), ops["i_fin"].to_numpy()

    ops["rmax"], ops["toco_sl"], ops["r_cierre"] = _una_direccion(o, h, l, c, *args, d, rie, fin, adverso_primera)
    ops["rmax_inv"], ops["toco_sl_inv"], ops["r_cierre_inv"] = _una_direccion(o, h, l, c, *args, -d, rie, fin, adverso_primera)
    ops["riesgo_pts"] = rie
    ops["t_ent"] = barras.index[ops["i_ent"].to_numpy()]
    if "sesion" in barras.columns:
        ops["sesion"] = barras["sesion"].to_numpy()[ops["i_ent"].to_numpy()]
    return ops


def r_neta(ops: pd.DataFrame, ratio: float, invertida: bool = False, coste: float = COSTE_PTS) -> np.ndarray:
    """R neta por operación con objetivo a `ratio` R y cierre a i_fin."""
    s = "_inv" if invertida else ""
    rmax, toco, rc = ops["rmax" + s].to_numpy(), ops["toco_sl" + s].to_numpy(), ops["r_cierre" + s].to_numpy()
    bruta = np.where(rmax >= ratio, ratio, np.where(toco, -1.0, np.minimum(rc, ratio)))
    return bruta - coste / ops["riesgo_pts"].to_numpy()


def r_mezcla(ops: pd.DataFrame, ratio: float, voltear: np.ndarray, coste: float = COSTE_PTS) -> np.ndarray:
    """R neta con la dirección volteada donde `voltear` es True (placebo de dirección)."""
    return np.where(voltear, r_neta(ops, ratio, True, coste), r_neta(ops, ratio, False, coste))
