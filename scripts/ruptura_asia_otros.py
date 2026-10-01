"""Ejecuta preregistros/2026-10-01_ruptura_asia_otros_mercados.md. No cambiar nada.
Uso: python -m scripts.ruptura_asia_otros plata|eurusd"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader

NOMBRE = sys.argv[1]
ANIOS = list(range(2011, 2019))
UMBRAL = 0.025


def g4(b):
    """Idéntica a G4 del oro (scripts/oro_lote1.py) + ancho del rango."""
    hh, ses_arr = b.hhmm.to_numpy(), b.sesion.to_numpy()
    o, h, l, c = b.o.to_numpy(), b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
    df = pd.DataFrame({"ses": ses_arr, "hh": hh, "i": np.arange(len(b))})
    filas = []
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
        pts = (c[fin] - o[e]) * d
        filas.append((s, d, pts, pts / (top - bot)))
    return pd.DataFrame(filas, columns=["ses", "dir", "pts", "u"])


def anio(t, a):
    return t[pd.to_datetime(t.ses).dt.year == a]


T, NUL = [], []
barras = {}
for a in ANIOS:
    b = loader.cargar_dukas(NOMBRE, [a]); barras[a] = b
    T.append(anio(g4(b), a))
t = pd.concat(T, ignore_index=True)
for sem in range(6):
    NUL.append(pd.concat([anio(g4(C.paseo_aleatorio(b, 11000 + 10 * sem + i)), a) for i, (a, b) in enumerate(barras.items())]).u.mean())

s = C.resumen(t.u)
anios = t.groupby(pd.to_datetime(t.ses).dt.year).u.mean().round(3).to_dict()
pos = sum(v > 0 for v in anios.values())
L, S = t[t.dir == 1].u.mean(), t[t.dir == -1].u.mean()
z = C.z_exceso(s["R"], s["ee"], np.mean(NUL), np.std(NUL, ddof=1) / np.sqrt(6))
pasa = s["p_1cola"] < UMBRAL and pos >= 5 and L > 0 and S > 0 and z > 2
print(f"== RUPTURA ASIA CONGELADA · {NOMBRE.upper()} 2011-2018 ==")
print(f"n={s['n']} media={s['R']:+.4f} rangos (bruto {t.pts.mean():+.4f}) p1c={s['p_1cola']:.4f} · años positivos {pos}/8 {anios}")
print(f"largos {L:+.4f} cortos {S:+.4f} · neutral (L+S)/2 {(L+S)/2:+.4f} · nulo {np.mean(NUL):+.4f} z={z:+.2f}  → {'PASA' if pasa else 'no pasa'}")
