"""Ejecuta preregistros/2026-10-01_oro_ruptura_asia.md. Uso: python -m scripts.oro_ruptura_asia diseno|validacion"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader, motor

FASE = sys.argv[1]
ANIOS = [2011, 2013, 2015, 2017] if FASE == "diseno" else [2012, 2014, 2016, 2018]
COSTE = 0.30


def senales(b, modo):
    hh, ses_arr = b.hhmm.to_numpy(), b.sesion.to_numpy()
    o, h, l, c = b.o.to_numpy(), b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
    df = pd.DataFrame({"ses": ses_arr, "hh": hh, "i": np.arange(len(b))})
    filas, prem = [], []
    for s, g in df.groupby("ses", sort=True):
        fin = g.i[g.hh == 1159].to_numpy()
        if fin.size == 0: continue
        fin = fin[0]
        asia = g.i[(g.hh >= 1900) | (g.hh < 300)].to_numpy()
        post = g.i[(g.hh >= 300) & (g.hh <= 1059)].to_numpy()
        if len(asia) < 300 or len(post) < 10: continue
        assert asia.max() < post.min()
        top, bot = h[asia].max(), l[asia].min()
        fuera = np.flatnonzero((c[post] > top) | (c[post] < bot))
        if fuera.size == 0: continue
        k = post[fuera[0]]; d = 1 if c[k] > top else -1; e = k + 1
        if ses_arr[e] != s or e > fin: continue
        prem.append((s, d, (c[fin] - o[e]) * d))
        stop = (top + bot) / 2 if modo == "E1" else (bot if d == 1 else top)
        dist = (o[e] - stop) * d
        if dist <= 0 or dist < 0.001 * o[e]: continue
        filas.append((e, o[e], d, dist, fin))
    s = pd.DataFrame(filas, columns=["i_ent", "precio", "dir", "riesgo", "i_fin"])
    return s, pd.DataFrame(prem, columns=["ses", "dir", "pts"])


def correr(barras, modo):
    R, Y, INV, P = [], [], [], []
    for a, b in barras.items():
        s, p = senales(b, modo)
        o = motor.simular(b, s); m = o.sesion.dt.year == a
        R.append(motor.r_neta(o[m], 2.0, coste=COSTE)); INV.append(motor.r_neta(o[m], 2.0, invertida=True, coste=COSTE))
        Y.append(np.full(m.sum(), a)); P.append(p[pd.to_datetime(p.ses).dt.year == a])
    return np.concatenate(R), np.concatenate(Y), np.concatenate(INV), pd.concat(P)


barras = {a: loader.cargar_oro([a], verbose=False) for a in ANIOS}
print(f"== ORO · RUPTURA ASIA · {FASE.upper()} {ANIOS} ==")
for modo in ("E1", "E2"):
    r, y, inv, p = correr(barras, modo)
    s = C.resumen(r); anios = pd.Series(r).groupby(y).mean().round(3).to_dict()
    nul = [correr({a: C.paseo_aleatorio(b, 9000 + 10 * sem + i) for i, (a, b) in enumerate(barras.items())}, modo)[0].mean() for sem in range(6)]
    z = C.z_exceso(s["R"], s["ee"], np.mean(nul), np.std(nul, ddof=1) / np.sqrt(6))
    print(f"{modo} n={s['n']} R={s['R']:+.3f} wr={s['wr']:.1%} p1c={s['p_1cola']:.4f} años {anios} · inv {inv.mean():+.3f} · "
          f"nulo {np.mean(nul):+.3f} z={z:+.2f} · stop mediano {np.median(pd.concat([senales(b, modo)[0] for b in barras.values()]).riesgo):.2f} pts")
sp = C.resumen(p.pts)
print(f"premisa G4 desnuda: n={sp['n']} {sp['R']:+.3f} pts p1c={sp['p_1cola']:.4f} · largos {p[p.dir==1].pts.mean():+.3f} cortos {p[p.dir==-1].pts.mean():+.3f}")
