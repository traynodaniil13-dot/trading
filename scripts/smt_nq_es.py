"""Ejecuta preregistros/2026-10-02_smt_nq_es.md. No cambiar nada.
Uso: python -m scripts.smt_nq_es [diseno|validacion]"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader

FASE = sys.argv[1] if len(sys.argv) > 1 else "diseno"
ANIOS = [2021, 2023, 2025] if FASE == "diseno" else [2022, 2024, 2026]
BARRERAS = (0.15, 0.30)
Z_UMBRAL = 2.24


def unir(nq, es):
    j = nq[["o", "h", "l", "c", "sesion", "hhmm"]].join(es[["h", "l"]], rsuffix="_es", how="inner")
    return j


def eventos(j):
    """(nivel, ses, pred, tipo, k, fin): pred +1 alcista (rotura de mínimos), −1 bajista."""
    hh, ses = j.hhmm.to_numpy(), j.sesion.to_numpy()
    H = {"nq": j.h.to_numpy(), "es": j.h_es.to_numpy()}; L = {"nq": j.l.to_numpy(), "es": j.l_es.to_numpy()}
    df = pd.DataFrame({"ses": ses, "hh": hh, "i": np.arange(len(j))})
    grupos = {s: g for s, g in df.groupby("ses", sort=True)}
    sesiones = list(grupos); out = []
    for n_, s in enumerate(sesiones):
        g = grupos[s]
        on = g.i[(g.hh >= 1800) | (g.hh < 930)].to_numpy()
        ven = g.i[(g.hh >= 930) & (g.hh <= 1059)].to_numpy()
        rth = g.i[(g.hh >= 930) & (g.hh <= 1559)].to_numpy()
        if len(on) < 300 or len(ven) < 60 or not rth.size: continue
        fin = rth.max()
        assert on.max() < ven.min()
        niveles = {"ON": {k: (H[k][on].max(), L[k][on].min()) for k in H}}
        if n_ > 0:
            gp = grupos[sesiones[n_ - 1]]
            p = gp.i[(gp.hh >= 930) & (gp.hh <= 1559)].to_numpy()
            if len(p) >= 300:
                assert p.max() < ven.min()
                niveles["PD"] = {k: (H[k][p].max(), L[k][p].min()) for k in H}
        for nv, lv in niveles.items():
            for pred in (1, -1):                       # +1: mínimos (alcista) · −1: máximos (bajista)
                if pred == 1:
                    rompe = {k: L[k] < lv[k][1] for k in H}
                else:
                    rompe = {k: H[k] > lv[k][0] for k in H}
                if nv == "PD" and any(rompe[k][on].any() for k in H):
                    continue                           # nivel ya roto antes de las 09:30
                a, b = rompe["nq"][ven], rompe["es"][ven]
                pa = np.flatnonzero(a); pb = np.flatnonzero(b)
                ka = pa[0] if pa.size else np.inf; kb = pb[0] if pb.size else np.inf
                if ka == kb: continue                  # los dos a la vez, o ninguno
                tipo = "A" if ka < kb else "B"         # A: rompió NQ y ES aún no
                k = ven[int(min(ka, kb))]
                if k >= fin: continue
                out.append((nv, s, pred, tipo, k, fin))
    return out


def carrera(j, ev, pct):
    h, l, c = j.h.to_numpy(), j.l.to_numpy(), j.c.to_numpy()
    res = np.full(len(ev), np.nan)
    for n, (_, _, pred, _, k, fin) in enumerate(ev):
        ref = c[k]; X = ref * pct / 100
        up = np.flatnonzero(h[k + 1:fin + 1] >= ref + X); dn = np.flatnonzero(l[k + 1:fin + 1] <= ref - X)
        a = up[0] if up.size else np.inf; z = dn[0] if dn.size else np.inf
        if a == z: continue
        res[n] = float((a < z) == (pred == 1))
    return res


def tabla(j, anio):
    ev = eventos(j); base = pd.DataFrame(ev, columns=["nivel", "ses", "pred", "tipo", "k", "fin"])
    t = pd.concat([base.assign(X=x, ok=carrera(j, ev, x)) for x in BARRERAS], ignore_index=True)
    return t[pd.to_datetime(t.ses).dt.year == anio]


datos = {}
for a in ANIOS:
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    datos[a] = (nq, es)
real = pd.concat([tabla(unir(nq, es), a) for a, (nq, es) in datos.items()], ignore_index=True)

claves, claves_p = ["nivel", "X"], ["nivel", "X", "pred"]
nul, nul_p = [], []
for sem in range(6):
    t = pd.concat([tabla(unir(C.paseo_aleatorio(nq, 31000 + 10 * sem + i), C.paseo_aleatorio(es, 32000 + 10 * sem + i)), a)
                   for i, (a, (nq, es)) in enumerate(datos.items())])
    nul.append(t.groupby(claves).ok.mean()); nul_p.append(t.groupby(claves_p).ok.mean())
nul = pd.concat(nul, axis=1); nul_p = pd.concat(nul_p, axis=1)

print(f"== SMT NQ-ES · PREMISA · {FASE.upper()} {ANIOS} · umbral z > {Z_UMBRAL} ==")
for (nv, X), g in real.groupby(claves):
    v = g.ok.dropna(); n = len(v); p = v.mean(); pn = nul.loc[(nv, X)]
    z = C.z_exceso(p, np.sqrt(p * (1 - p) / n), pn.mean(), pn.std(ddof=1) / np.sqrt(len(pn)))
    lados = {d: (g[g.pred == d].ok.mean(), nul_p.loc[(nv, X, d)].mean(), g[g.pred == d].ok.notna().sum()) for d in (1, -1)}
    tipos = {t_: (g[g.tipo == t_].ok.mean(), g[g.tipo == t_].ok.notna().sum()) for t_ in ("A", "B")}
    anios = g.groupby(pd.to_datetime(g.ses).dt.year).ok.mean()
    pasa = z > Z_UMBRAL and all(r > nn for r, nn, _ in lados.values()) and (anios > 0.5).sum() >= 2
    print(f"{nv} ±{X:.2f}%  n={n} (desc {g.ok.isna().sum()}) acierto {p:.1%} nulo {pn.mean():.1%} z={z:+.2f}"
          f" | alcista {lados[1][0]:.1%} ({lados[1][1]:.1%}, n={lados[1][2]}) bajista {lados[-1][0]:.1%} ({lados[-1][1]:.1%}, n={lados[-1][2]})"
          f" | tipo A {tipos['A'][0]:.1%} (n={tipos['A'][1]}) B {tipos['B'][0]:.1%} (n={tipos['B'][1]})"
          f" | años {anios.round(3).to_dict()} → {'PASA' if pasa else 'no'}")
