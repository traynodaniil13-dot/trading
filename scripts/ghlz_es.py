"""Ejecuta preregistros/2026-10-02_ghlz_es.md. No cambiar nada."""
import numpy as np, pandas as pd
from src import controles as C, loader, premisas as P

ANIOS = list(range(2021, 2027))
COSTE = 0.65
T, NUL = [], {s: [] for s in range(6)}
for i, a in enumerate(ANIOS):
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    t = P.p1_momento_ultima_media_hora(es); T.append(t[t.index.year == a])
    for sem in range(6):
        n = P.p1_momento_ultima_media_hora(C.paseo_aleatorio(es, 41000 + 10 * sem + i)); NUL[sem].append(n[n.index.year == a].y)
t = pd.concat(T); nul = np.array([pd.concat(v).mean() for v in NUL.values()])
s = C.resumen(t.y); anios = t.y.groupby(t.index.year).mean().round(2).to_dict()
L, S = t[t.s == 1].y.mean(), t[t.s == -1].y.mean()
z = C.z_exceso(s["R"], s["ee"], nul.mean(), nul.std(ddof=1) / np.sqrt(6))
pos = sum(v > 0 for v in anios.values())
pasa = s["p_1cola"] < 0.05 and pos >= 4 and L > 0 and S > 0 and z > 2
print("== GHLZ (1ª media hora → última media hora) CONGELADO · ES 2021-2026 ==")
print(f"n={s['n']} media={s['R']:+.3f} pts (neta {s['R'] - COSTE:+.3f}) p1c={s['p_1cola']:.4f} · años+ {pos}/6 {anios}")
print(f"s=+1 {L:+.3f} (n={(t.s == 1).sum()}) · s=−1 {S:+.3f} (n={(t.s == -1).sum()}) · nulo {nul.mean():+.3f} z={z:+.2f}  → {'PASA' if pasa else 'NO PASA'}")
