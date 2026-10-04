"""Marco de la mina de estrategias (ver mina/README.md).

Una FAMILIA es un conjunto de variantes declaradas en un pre-registro. Cada variante es una
función `fn(datos_de_un_año) -> (barras, ops)`: `barras` es la serie sobre la que se simula
(o, h, l, c, sesion) y `ops` las operaciones (i_ent, precio, dir, riesgo, i_fin[, obj]).
`r_fn(ops, invertida)` da la R neta por operación.

Criterios de la fase de DISEÑO (todos a la vez, fijados aquí y no por familia):
  1. R media > p95 del MÁXIMO de la familia sobre el nulo (paseo aleatorio o barajado,
     las mismas variantes a la vez).
  2. Placebo de dirección a nivel de familia (mismo sorteo por sesión para todas): p < 0,05.
  3. R > 0 en los 3 años de diseño.
  4. Invertida ≤ 0.
Las que pasan van a VALIDACIÓN (2022/24/26), con Bonferroni por nº de supervivientes y
contabilizadas en el protocolo de partición.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import controles as C, motor

DISENO = (2021, 2023, 2025)
VALIDACION = (2022, 2024, 2026)


def correr_variante(fn, D: dict):
    oo = []
    for a, datos in D.items():
        barras, s = fn(datos)
        if s is None or len(s) == 0:
            continue
        o = motor.simular(barras, s)
        o = o[o["sesion"].dt.year == a].copy()
        o["_a"] = a
        oo.append(o)
    return pd.concat(oo, ignore_index=True) if oo else pd.DataFrame()


def r_obj(o: pd.DataFrame, invertida=False, coste=None):
    """R con objetivo por operación en la columna `obj` (o fijo si es número)."""
    s = "_inv" if invertida else ""
    obj = o["obj"].to_numpy()
    rmax, toco, rc = o["rmax" + s].to_numpy(), o["toco_sl" + s].to_numpy(), o["r_cierre" + s].to_numpy()
    coste = o["coste"].to_numpy() if coste is None else coste
    return np.where(rmax >= obj, obj, np.where(toco, -1.0, np.minimum(rc, obj))) - coste / o["riesgo_pts"].to_numpy()


def evaluar(nombre, variantes: dict, r_fn, D: dict, nulo_fn, semillas=12, reps_placebo=200, semilla=0):
    """Evalúa la familia en D (normalmente DISEÑO). Devuelve (tabla, supervivientes, ops)."""
    ops = {v: correr_variante(fn, D) for v, fn in variantes.items()}
    filas = []
    for v, o in ops.items():
        if len(o) == 0:
            filas.append(dict(variante=v, n=0)); continue
        r = r_fn(o); ri = r_fn(o, True); s = C.resumen(r)
        py = pd.Series(r).groupby(o["_a"].to_numpy()).mean()
        filas.append(dict(variante=v, n=s["n"], wr=s["wr"], R=s["R"], ee=s["ee"], p1c=s["p_1cola"],
                          inv=ri.mean(), anios_pos=int((py > 0).sum()), anios=py.round(3).to_dict()))
    tab = pd.DataFrame(filas)
    # nulo: máximo de la familia sobre series sin información
    maxs = []
    for k in range(semillas):
        Dn = {a: nulo_fn(d, semilla * 1000 + 37 * k + a % 100) for a, d in D.items()}
        mejor = -np.inf
        for v, fn in variantes.items():
            o = correr_variante(fn, Dn)
            if len(o) >= 30:
                mejor = max(mejor, r_fn(o).mean())
        maxs.append(mejor)
    maxs = np.array(maxs)
    p95 = np.percentile(maxs, 95)
    # placebo de dirección a nivel de familia
    rng = np.random.default_rng(semilla)
    validos = {v: o for v, o in ops.items() if len(o)}
    ses = np.unique(np.concatenate([o["sesion"].to_numpy() for o in validos.values()]))
    idx = {v: np.searchsorted(ses, o["sesion"].to_numpy()) for v, o in validos.items()}
    rn = {v: r_fn(o) for v, o in validos.items()}; ri = {v: r_fn(o, True) for v, o in validos.items()}
    real_max = max(x.mean() for x in rn.values())
    pmax = np.empty(reps_placebo)
    for k in range(reps_placebo):
        f = rng.random(len(ses)) < 0.5
        pmax[k] = max(np.where(f[idx[v]], ri[v], rn[v]).mean() for v in validos)
    p_placebo = (pmax >= real_max).mean()
    tab["supera_p95_nulo"] = tab["R"] > p95
    tab["pasa"] = tab["supera_p95_nulo"] & (tab["anios_pos"] == len(D)) & (tab["inv"] <= 0) & (p_placebo < 0.05)
    print(f"\n######## FAMILIA {nombre} · {len(variantes)} variantes · años {sorted(D)}")
    print(f"nulo (máximo de la familia, {semillas} semillas): media {maxs.mean():+.4f} · p95 {p95:+.4f} · "
          f"placebo de dirección (máximo real {real_max:+.4f}): p={p_placebo:.3f}")
    cols = ["variante", "n", "wr", "R", "p1c", "inv", "anios_pos", "supera_p95_nulo", "pasa"]
    with pd.option_context("display.width", 200, "display.max_rows", 200, "display.float_format", "{:+.4f}".format):
        print(tab[cols].sort_values("R", ascending=False).to_string(index=False))
    sup = tab[tab["pasa"]]["variante"].tolist()
    print(f"SUPERVIVIENTES a validación: {sup if sup else 'ninguna'}")
    return tab, sup, ops
