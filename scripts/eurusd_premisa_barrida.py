"""Ejecuta preregistros/2026-10-02_eurusd_premisa_barrida.md en DISEÑO. No cambiar nada.
Uso: python -m scripts.eurusd_premisa_barrida [diseno|validacion]"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader

FASE = sys.argv[1] if len(sys.argv) > 1 else "diseno"
ANIOS = [2011, 2013, 2015, 2017] if FASE == "diseno" else [2012, 2014, 2016, 2018]
BARRERAS = (5, 10, 20)
Z_UMBRAL = 2.64


def eventos(b):
    """Lista de (nivel, def, ses, lado, k, fin): lado +1 = barrida arriba (reversión = baja)."""
    hh, ses_arr = b.hhmm.to_numpy(), b.sesion.to_numpy()
    h, l, c = b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
    df = pd.DataFrame({"ses": ses_arr, "hh": hh, "i": np.arange(len(b))})
    grupos = {s: g for s, g in df.groupby("ses", sort=True)}
    sesiones = list(grupos)
    out = []
    for j, s in enumerate(sesiones):
        g = grupos[s]
        fin = g.i.max()
        asia = g.i[(g.hh >= 1900) | (g.hh < 300)].to_numpy()
        ven = g.i[(g.hh >= 300) & (g.hh <= 1059)].to_numpy()
        if len(ven) < 60: continue
        niveles = {}
        if len(asia) >= 300:
            assert asia.max() < ven.min()
            niveles["ASIA"] = (h[asia].max(), l[asia].min())
        if j > 0 and len(grupos[sesiones[j - 1]]) >= 1000:
            p = grupos[sesiones[j - 1]].i.to_numpy()
            assert p.max() < ven.min()
            pre = g.i[(g.hh >= 1800) | (g.hh < 300)].to_numpy()
            top, bot = h[p].max(), l[p].min()
            niveles["PD"] = (top if not (pre.size and h[pre].max() > top) else np.nan,
                             bot if not (pre.size and l[pre].min() < bot) else np.nan)
        for nv, (top, bot) in niveles.items():
            for dfn in ("R", "C"):
                arriba = h[ven] > top if dfn == "R" else (h[ven] > top) & (c[ven] <= top)
                abajo = l[ven] < bot if dfn == "R" else (l[ven] < bot) & (c[ven] >= bot)
                for lado, m in ((1, arriba), (-1, abajo)):
                    w = np.flatnonzero(m)
                    if w.size and ven[w[0]] < fin:
                        out.append((nv, dfn, s, lado, ven[w[0]], fin))
    return out


def carrera(b, ev, X):
    """1 = reversión, 0 = continuación, nan = descartado (ambas en la misma barra o sin toque)."""
    h, l, c = b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
    res = np.full(len(ev), np.nan)
    for n, (_, _, _, lado, k, fin) in enumerate(ev):
        ref = c[k]; hs, ls = h[k + 1:fin + 1], l[k + 1:fin + 1]   # desde la barra SIGUIENTE (bug nº5/nº9)
        up = np.flatnonzero(hs >= ref + X); dn = np.flatnonzero(ls <= ref - X)
        a = up[0] if up.size else np.inf; z = dn[0] if dn.size else np.inf
        if a == z: continue                     # misma barra (o ninguna): descarte
        sube_primero = a < z
        res[n] = float(sube_primero) if lado == -1 else float(not sube_primero)
    return res


def tabla(b, anio):
    ev = eventos(b)
    filas = []
    base = pd.DataFrame(ev, columns=["nivel", "def", "ses", "lado", "k", "fin"])
    for X in BARRERAS:
        t = base.copy(); t["X"] = X; t["rev"] = carrera(b, ev, X); filas.append(t)
    t = pd.concat(filas, ignore_index=True)
    return t[pd.to_datetime(t.ses).dt.year == anio]


barras = {a: loader.cargar_dukas("eurusd", [a]) for a in ANIOS}
real = pd.concat([tabla(b, a) for a, b in barras.items()], ignore_index=True)
nulos = []
for sem in range(6):
    t = pd.concat([tabla(C.paseo_aleatorio(b, 21000 + 10 * sem + i), a) for i, (a, b) in enumerate(barras.items())])
    nulos.append(t.groupby(["nivel", "def", "X"]).rev.mean().rename(sem))
    nulos.append(t.groupby(["nivel", "def", "X", "lado"]).rev.mean().rename(f"{sem}L"))
nul = pd.concat([x for x in nulos if not str(x.name).endswith("L")], axis=1)
nul_l = pd.concat([x for x in nulos if str(x.name).endswith("L")], axis=1)

print(f"== EUR/USD · PREMISA BARRIDA · {FASE.upper()} {ANIOS} · umbral z > {Z_UMBRAL} ==")
print("celda           n   desc  rev%   nulo%   z     arriba (nulo)   abajo (nulo)   años>50%")
for (nv, dfn, X), g in real.groupby(["nivel", "def", "X"]):
    v = g.rev.dropna(); n = len(v); p = v.mean()
    pn = nul.loc[(nv, dfn, X)]; z = C.z_exceso(p, np.sqrt(p * (1 - p) / n), pn.mean(), pn.std(ddof=1) / np.sqrt(len(pn)))
    lados = {ld: (g[g.lado == ld].rev.mean(), nul_l.loc[(nv, dfn, X, ld)].mean()) for ld in (1, -1)}
    anios = g.groupby(pd.to_datetime(g.ses).dt.year).rev.mean()
    pasa = z > Z_UMBRAL and all(r > nn for r, nn in lados.values()) and (anios > 0.5).sum() >= 3
    print(f"{nv:4s} {dfn} ±{X:2d}  {n:5d} {g.rev.isna().sum():5d}  {p:5.1%}  {pn.mean():5.1%}  {z:+5.2f}   "
          f"{lados[1][0]:5.1%} ({lados[1][1]:5.1%})  {lados[-1][0]:5.1%} ({lados[-1][1]:5.1%})   "
          f"{(anios > 0.5).sum()}/4 {anios.round(3).to_dict()}  → {'PASA' if pasa else 'no'}")
