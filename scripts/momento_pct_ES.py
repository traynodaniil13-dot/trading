"""Ejecuta preregistros/2026-09-28_momento_pct_en_ES.md."""
import numpy as np, pandas as pd
from src import controles as C
from src import loader, motor
from src.motores import momento_generico as MG

COSTE_MES = 0.74 / 5 + 0.5   # 0,648 pts
anios = [a for a in range(2021, 2027) if (loader.RAIZ / f"data/es_cfd_{a}.csv.gz").exists()]
print("años disponibles:", anios, "" if len(anios) == 6 else "(PRELIMINAR)")
es = {a: loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=True) for a in anios}


def ops(datos):
    out = []
    for a, b in datos.items():
        o = motor.simular(b, MG.senales(b, 940, 30, 0.40)); out.append(o[o.sesion.dt.year == a])
    return pd.concat(out, ignore_index=True)


o = ops(es); r = motor.r_neta(o, 2.0, coste=COSTE_MES); s = C.resumen(r)
py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).agg(["mean", "count"])
pos = int((py["mean"] > 0).sum())
print(f"\nES Momento 09:40 stop 0,40% 1:2 · n={s['n']} R={s['R']:+.3f} ee={s['ee']:.3f} p1c={s['p_1cola']:.4f} wr={s['wr']:.1%}")
print("por año:", {int(y): (round(m, 3), int(n)) for y, (m, n) in py.iterrows()}, f"-> {pos}/{len(py)} positivos")
print(f"invertida {motor.r_neta(o, 2.0, True, coste=COSTE_MES).mean():+.3f} · largos {r[o.dir.to_numpy()==1].mean():+.3f} · cortos {r[o.dir.to_numpy()==-1].mean():+.3f}")
nul = [motor.r_neta(ops({a: C.paseo_aleatorio(b, 13000 + 10 * k + a % 10) for a, b in es.items()}), 2.0, coste=COSTE_MES).mean() for k in range(6)]
print(f"paseo aleatorio (6 semillas): {np.mean(nul):+.3f} ± {np.std(nul, ddof=1)/np.sqrt(6):.3f}")

nqo = []
for a in anios:
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    x = motor.simular(b, MG.senales(b, 940, 30, 0.40)); nqo.append(x[x.sesion.dt.year == a])
nqo = pd.concat(nqo, ignore_index=True)
j = pd.DataFrame({"ses": o.sesion, "d_es": o.dir, "r_es": r}).merge(
    pd.DataFrame({"ses": nqo.sesion, "d_nq": nqo.dir, "r_nq": motor.r_neta(nqo, 2.0)}), on="ses")
print(f"vs NQ mismos días: misma dirección {(j.d_es == j.d_nq).mean():.0%} · corr R {np.corrcoef(j.r_es, j.r_nq)[0,1]:.2f} · "
      f"R media de la cartera NQ+ES {((j.r_es + j.r_nq) / 2).mean():+.3f}")
ok = s["R"] > 0 and s["p_1cola"] < 0.05 and pos >= 4
print("\nVEREDICTO (pre-registro):", "PASA" if ok else "NO PASA", "" if len(anios) == 6 else "— preliminar, falta 2025")
