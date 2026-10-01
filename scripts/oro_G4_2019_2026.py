"""Ejecuta preregistros/2026-10-01_oro_G4_2019_2026.md. G4 CONGELADA (copia literal de
scripts/oro_lote1.py) sobre oro 2019-2026. No cambiar nada."""
import numpy as np, pandas as pd
from src import controles as C, loader

ANIOS = list(range(2019, 2027))
COSTE = 0.30
UMBRAL = 0.01


def idx_por(b, mask_hh):
    """dict sesion -> primera posición de barra que cumple (sesión Y hora: bug nº6)."""
    pos = np.flatnonzero(mask_hh)
    ses = b.sesion.to_numpy()[pos]
    s = pd.Series(pos, index=ses)
    return s[~s.index.duplicated()]


def g4(b):
    """Literal de scripts/oro_lote1.py + ancho del rango (solo para la medida secundaria)."""
    hh, ses_arr = b.hhmm.to_numpy(), b.sesion.to_numpy()
    o, h, l, c = b.o.to_numpy(), b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
    df = pd.DataFrame({"ses": ses_arr, "hh": hh, "i": np.arange(len(b))})
    fin = idx_por(b, hh == 1159)
    filas = []
    for s, g in df.groupby("ses", sort=True):
        if s not in fin.index: continue
        asia = g.i[(g.hh >= 1900) | (g.hh < 300)].to_numpy()
        post = g.i[(g.hh >= 300) & (g.hh <= 1059)].to_numpy()
        if len(asia) < 300 or len(post) < 10: continue
        assert asia.max() < post.min()
        top, bot = h[asia].max(), l[asia].min()
        fuera = np.flatnonzero((c[post] > top) | (c[post] < bot))
        if fuera.size == 0: continue
        k = post[fuera[0]]; d = 1 if c[k] > top else -1
        e = k + 1
        if ses_arr[e] != s or e > fin[s]: continue
        filas.append((s, d, (c[fin[s]] - o[e]) * d, top - bot))
    return pd.DataFrame(filas, columns=["ses", "dir", "pts", "ancho"])


def del_anio(t, a):
    return t[pd.to_datetime(t.ses).dt.year == a]


barras, T = {}, []
for a in ANIOS:
    b = loader.cargar_oro([a]); barras[a] = b
    T.append(del_anio(g4(b), a))
t = pd.concat(T, ignore_index=True)
t["u"] = t.pts / t.ancho
t["neto"] = t.pts - COSTE

NUL, NUL_U = [], []
for sem in range(6):
    r = pd.concat([del_anio(g4(C.paseo_aleatorio(b, 13000 + 10 * sem + i)), a) for i, (a, b) in enumerate(barras.items())])
    NUL.append(r.pts.mean()); NUL_U.append((r.pts / r.ancho.where(r.ancho > 0)).mean())

ee_nul = lambda x: np.std(x, ddof=1) / np.sqrt(len(x))
print("== ORO · G4 RUPTURA ASIÁTICA CONGELADA · 2019-2026 (2026 hasta 30/09) · umbral p < 0,01 ==")
for col, nul, nom in (("pts", NUL, "PRINCIPAL pts brutos"), ("u", NUL_U, "rangos asiáticos"), ("neto", None, "pts netos (−0,30)")):
    s = C.resumen(t[col])
    anios = t.groupby(pd.to_datetime(t.ses).dt.year)[col].mean().round(3).to_dict()
    pos = sum(v > 0 for v in anios.values())
    L, S = t[t.dir == 1][col].mean(), t[t.dir == -1][col].mean()
    linea = (f"{nom:22s} n={s['n']} media={s['R']:+.4f} p1c={s['p_1cola']:.4f} · años+ {pos}/8 {anios}\n"
             f"{'':22s} largos {L:+.4f} (n={(t.dir == 1).sum()}) cortos {S:+.4f} (n={(t.dir == -1).sum()}) · neutral {(L + S) / 2:+.4f}")
    if nul is not None:
        z = C.z_exceso(s["R"], s["ee"], np.mean(nul), ee_nul(nul))
        linea += f" · nulo {np.mean(nul):+.4f} z={z:+.2f}"
        if col == "pts":
            pasa = s["p_1cola"] < UMBRAL and pos >= 5 and L > 0 and S > 0 and z > 2
            linea += f"  → {'PASA' if pasa else 'NO PASA'}"
    print(linea)
print("\nPor año (pts brutos): n, media, largos, cortos, cambio del año del oro")
for a in ANIOS:
    x = del_anio(t, a); b = barras[a]
    print(f"  {a}: n={len(x):3d} media={x.pts.mean():+.3f} largos {x[x.dir == 1].pts.mean():+.3f} (n={(x.dir == 1).sum()}) "
          f"cortos {x[x.dir == -1].pts.mean():+.3f} (n={(x.dir == -1).sum()}) · oro {b.c.iloc[0]:.0f}→{b.c.iloc[-1]:.0f}")
