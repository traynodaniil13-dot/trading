"""Ejecuta preregistros/2026-09-28_filtros_momento_pct.md. Uso: python -m scripts.filtros_momento_pct diseno|validacion"""
import sys
import numpy as np, pandas as pd
from src import controles as C
from src import loader, motor, premisas as P
from src.motores import momento_generico as MG

fase = sys.argv[1]
ANIOS = [2021, 2023, 2025] if fase == "diseno" else [2022, 2024, 2026]


def por_anio(a):
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(nq, MG.senales(nq, 940, 30, 0.40))
    g = P._rejilla(nq, [909, 930, 939, 1559]); e = P._rejilla(es, [909, 939])
    d = pd.DataFrame(index=g["c"].index)
    d["es"] = np.sign(e["c"][939] - e["c"][909]).reindex(d.index)
    d["gap"] = np.sign(g["o"][930] - g["c"][1559].shift(1))
    d["prev"] = np.sign((g["c"][1559] - g["o"][930]).shift(1))
    imp = ((g["c"][939] - g["c"][909]).abs() / g["c"][939])
    d["fuerte"] = imp > imp.shift(1).rolling(60, min_periods=60).median()
    d["fuerte_ok"] = imp.shift(1).rolling(60, min_periods=60).median().notna()
    o = o.merge(d, left_on="sesion", right_index=True, how="left")
    return o[o.sesion.dt.year == a]


o = pd.concat([por_anio(a) for a in ANIOS], ignore_index=True)
r = motor.r_neta(o, 2.0); dirs = o["dir"].to_numpy()
mask = {"F1_ES_de_acuerdo": (o["es"].to_numpy() == dirs), "F2_a_favor_gap": (o["gap"].to_numpy() == dirs),
        "F3_a_favor_dia_previo": (o["prev"].to_numpy() == dirs), "F4_impulso_fuerte": o["fuerte"].fillna(False).to_numpy().astype(bool)}
base = C.resumen(r)
print(f"FASE {fase} {ANIOS} · BASE n={base['n']} R={base['R']:+.3f} wr={base['wr']:.1%}\n")
rng = np.random.default_rng(0)
filas = {}
for k, m in mask.items():
    x = r[m]; s = C.resumen(x)
    azar = np.array([r[rng.choice(len(r), size=m.sum(), replace=False)].mean() for _ in range(1000)])
    p95 = np.percentile(azar, 95)
    py = pd.Series(x).groupby(o.sesion.dt.year.to_numpy()[m]).mean().round(3).to_dict()
    filas[k] = (s, p95)
    if fase == "diseno":
        ok = s["R"] > base["R"] and s["wr"] > base["wr"] and s["n"] >= 0.35 * base["n"] and s["R"] > p95
    else:
        ok = s["R"] > 0 and s["p_1cola"] < 0.0125 and s["R"] > base["R"] and s["wr"] > base["wr"] and s["R"] > p95
    print(f"{k:22s} n={s['n']:4d} ({s['n']/base['n']:.0%}) R={s['R']:+.3f} wr={s['wr']:.1%} p1c={s['p_1cola']:.3f} "
          f"| azar p95 {p95:+.3f} | años {py} | resto R={r[~m].mean():+.3f} -> {'CUMPLE' if ok else 'no'}")
