import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.motores import primera_vela as S
ANIOS = [2021, 2023, 2025]
datos = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in ANIOS}
def ops(dd):
    out = []
    for a, b in dd.items():
        o = motor.simular(b, S.senales(b)); out.append(o[o.sesion.dt.year == a])
    return pd.concat(out, ignore_index=True)
o = ops(datos)
print(f"operaciones {len(o)} ({len(o)/sum(len(pd.unique(b.sesion)) for b in datos.values()):.0%} de los días) · riesgo mediano {o.riesgo_pts.median():.1f} pts · cortos {(o.dir==-1).mean():.0%}")
nul = {rt: [] for rt in (1.0, 1.5, 2.0)}
for sem in range(6):
    orw = ops({a: C.paseo_aleatorio(b, 21000 + 10 * sem + a % 10) for a, b in datos.items()})
    for rt in nul: nul[rt].append(motor.r_neta(orw, rt).mean())
for rt in (2.0, 1.0, 1.5):
    r = motor.r_neta(o, rt); s = C.resumen(r)
    py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
    inv = motor.r_neta(o, rt, True).mean()
    tp = (o.rmax >= rt).mean(); sl = (~(o.rmax >= rt) & o.toco_sl).mean()
    ok = s["R"] > 0 and s["p_1cola"] < 0.05 and min(py.values()) > 0 and s["R"] > np.mean(nul[rt]) and inv <= 0
    tag = "PRINCIPAL" if rt == 2.0 else "info"
    print(f"[{tag}] 1:{rt}  n={s['n']} wr={s['wr']:.1%} (TP {tp:.0%} · SL {sl:.0%} · cierre {1-tp-sl:.0%}) R={s['R']:+.3f} p1c={s['p_1cola']:.3f} | años {py} | invertida {inv:+.3f} | paseo {np.mean(nul[rt]):+.3f}" + (f" -> {'PASA' if ok else 'NO PASA'}" if rt == 2.0 else ""))
