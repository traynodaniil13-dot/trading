"""Ejecuta preregistros/2026-10-02_oro_lote2.md en DISEÑO (2019/2021/2023/2025). No cambiar nada.
Uso: python -m scripts.oro_lote2 [diseno|validacion]"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader

FASE = sys.argv[1] if len(sys.argv) > 1 else "diseno"
ANIOS = [2019, 2021, 2023, 2025] if FASE == "diseno" else [2020, 2022, 2024, 2026]
UMBRAL = 0.0125
COSTE_BPS = 1.0


def rejilla(b, minutos):
    """sesion x hhmm, primera barra de cada (sesión, minuto): las dos cotas (bug nº6)."""
    sub = b[b.hhmm.isin(minutos)]
    return {k: sub.pivot_table(index="sesion", columns="hhmm", values=k, aggfunc="first") for k in ("o", "c")}


def extremos_sesion(b):
    g = pd.DataFrame({"ses": b.sesion.to_numpy(), "o": b.o.to_numpy(), "c": b.c.to_numpy(), "hh": b.hhmm.to_numpy()})
    g = g[g.hh != 1700]   # por si acaso: la sesión acaba a las 16:59
    return g.groupby("ses").o.first(), g.groupby("ses").c.last(), g.groupby("ses").hh.first()


def senal(s, ent, sal):
    df = pd.DataFrame({"s": s, "y": (sal - ent) / ent * 1e4 * s}).dropna()
    return df[df.s != 0]


def premisas(b):
    g = rejilla(b, [300, 759, 800, 820, 919, 920, 1159, 1259, 1800, 259])
    o, c = g["o"], g["c"]
    ab, ci, hh0 = extremos_sesion(b)
    out = {}
    out["O1"] = senal(np.sign(c[759] - o[300]), o[800], c[1159])
    out["O2"] = senal(np.sign(c[919] - o[820]), o[920], c[1259])
    ok = hh0.reindex(o.index) == 1800   # la sesión empieza en su barra de 18:00
    ex = ((c[259] - o[1800]) / o[1800] - (ci.reindex(o.index) - o[1800]) / o[1800] * 540 / 1380) * 1e4
    out["O3"] = pd.DataFrame({"s": 0, "y": ex[ok]}).dropna()
    prev = ((ci - ab) / ab).shift(1).reindex(o.index)
    s4 = (-np.sign(prev)).where(prev.abs() > 0.02)
    out["O4"] = senal(s4, o[300], c[1159])
    return out


def anio(t, a):
    return t[t.index.year == a]


barras = {a: loader.cargar_oro([a]) for a in ANIOS}
real = {k: [] for k in ("O1", "O2", "O3", "O4")}
for a, b in barras.items():
    for k, t in premisas(b).items():
        real[k].append(anio(t, a))
real = {k: pd.concat(v) for k, v in real.items()}
nul = {k: [] for k in real}
for sem in range(6):
    acc = {k: [] for k in real}
    for i, (a, b) in enumerate(barras.items()):
        for k, t in premisas(C.paseo_aleatorio(b, 51000 + 10 * sem + i)).items():
            acc[k].append(anio(t, a).y)
    for k in real:
        nul[k].append(pd.concat(acc[k]).mean())

print(f"== ORO · LOTE 2 · {FASE.upper()} {ANIOS} · bps · umbral p bilateral < {UMBRAL} ==")
for k, t in real.items():
    s = C.resumen(t.y); p2 = 2 * min(s["p_1cola"], 1 - s["p_1cola"])
    anios = t.y.groupby(t.index.year).mean().round(2).to_dict()
    sg = np.sign(s["R"]); mismos = sum(np.sign(v) == sg for v in anios.values())
    nm = np.array(nul[k]); z = C.z_exceso(s["R"], s["ee"], nm.mean(), nm.std(ddof=1) / np.sqrt(len(nm)))
    pasa = p2 < UMBRAL and mismos >= 3 and abs(s["R"]) > COSTE_BPS and abs(z) > 2 and np.sign(z) == sg
    linea = f"{k} n={s['n']:4d} media={s['R']:+.2f} bps (neta {abs(s['R']) - COSTE_BPS:+.2f}) p2c={p2:.4f} años {anios} ({mismos}/4)"
    if t.s.nunique() > 1:
        L, S = t[t.s == 1].y.mean(), t[t.s == -1].y.mean()
        linea += f" · s+ {L:+.2f} (n={(t.s == 1).sum()}) s− {S:+.2f} (n={(t.s == -1).sum()})"
        pasa = pasa and np.sign(L) == np.sign(S) == sg
    print(linea + f" · nulo {nm.mean():+.2f} z={z:+.2f}  → {'PASA' if pasa else 'no'}")
