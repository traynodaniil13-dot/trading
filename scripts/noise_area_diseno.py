"""Ejecuta preregistros/2026-10-01_noise_area.md en DISEÑO (2021/2023/2025). No cambiar nada."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.loader import COSTE_PTS
from src.motores import noise_area as NA

ANIOS = [2021, 2023, 2025]


def medir(b, a):
    t = NA.tabla(b)
    t = t[pd.to_datetime(t.ses).dt.year == a].reset_index(drop=True)
    o, c = b["o"].to_numpy(float), b["c"].to_numpy(float)
    prem = (c[t.i_fin] - t.precio) * t.dir                          # premisa: pts brutos a 15:59
    sal = np.where(t.sal_open, o[t.i_sal], c[t.i_sal])
    autor = (sal - t.precio) * t.dir - COSTE_PTS                    # NA-autor, pts netos
    dist = (t.precio - t.base) * t.dir
    ok = (dist > 0) & (dist >= 0.001 * t.precio)
    s = pd.DataFrame({"i_ent": t.i_ent[ok], "precio": t.precio[ok], "dir": t.dir[ok], "riesgo": dist[ok], "i_fin": t.i_fin[ok]})
    ops = motor.simular(b, s) if len(s) else s
    r12 = motor.r_neta(ops, 2.0) if len(s) else np.array([])
    return t.assign(prem=prem.to_numpy(), autor=autor.to_numpy(), anio=a), r12, ops


def correr(barras_por_anio):
    T, R12, Y12 = [], [], []
    for a, b in barras_por_anio.items():
        t, r, ops = medir(b, a); T.append(t); R12.append(r); Y12.append(np.full(len(r), a))
    return pd.concat(T, ignore_index=True), np.concatenate(R12), np.concatenate(Y12)


real = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in ANIOS}
t, r12, y12 = correr(real)
print(f"Días con señal: {len(t)} · controles usados: {t.control.value_counts().sort_index().to_dict()}")
print("\n== PREMISA (pts brutos de la entrada a 15:59, con signo) ==")
s = C.resumen(t.prem); print(f"todos   n={s['n']} media={s['R']:+.2f} pts p1c={s['p_1cola']:.4f}")
for d, nom in ((1, "largos"), (-1, "cortos")):
    s = C.resumen(t.prem[t.dir == d]); print(f"{nom:7s} n={s['n']} media={s['R']:+.2f} pts p1c={s['p_1cola']:.4f}")
print("por año:", t.groupby("anio").prem.mean().round(2).to_dict())

print("\n== ESTRATEGIAS (se miran igual; solo cuentan si la premisa pasa) ==")
s = C.resumen(t.autor); print(f"NA-autor  n={s['n']} {s['R']:+.2f} pts netos p1c={s['p_1cola']:.4f} años {t.groupby('anio').autor.mean().round(2).to_dict()}")
s12 = C.resumen(r12); print(f"NA-1:2    n={s12['n']} R={s12['R']:+.3f} wr={s12['wr']:.1%} p1c={s12['p_1cola']:.4f} años {pd.Series(r12).groupby(y12).mean().round(3).to_dict()}")

print("\n== PASEO ALEATORIO (6 semillas) ==")
na, nb, nc = [], [], []
for sem in range(6):
    rw = {a: C.paseo_aleatorio(b, 5000 + 10 * sem + i) for i, (a, b) in enumerate(real.items())}
    tt, rr, _ = correr(rw); na.append(tt.prem.mean()); nb.append(tt.autor.mean()); nc.append(rr.mean())
for nom, real_v, ee_v, nul in (("premisa", t.prem.mean(), C.resumen(t.prem)["ee"], na),
                               ("NA-autor", t.autor.mean(), C.resumen(t.autor)["ee"], nb),
                               ("NA-1:2", r12.mean(), s12["ee"], nc)):
    nul = np.array(nul)
    print(f"{nom:9s} real {real_v:+.3f} · nulo {nul.mean():+.3f} ± {nul.std(ddof=1)/np.sqrt(6):.3f} · z exceso {C.z_exceso(real_v, ee_v, nul.mean(), nul.std(ddof=1)/np.sqrt(6)):+.2f}")
