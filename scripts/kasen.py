import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.motores import kasen as K

def datos(a):
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    ix = nq.index.intersection(es.index)
    return nq.loc[ix], es.loc[ix]
D = {a: datos(a) for a in (2021, 2023, 2025)}
for etiqueta, smt in (("CON SMT (Kasen)", True), ("SIN SMT (control)", False)):
    oo = []
    for a, (nq, es) in D.items():
        o = motor.simular(nq, K.senales(nq, es, exigir_smt=smt)); oo.append(o[o.sesion.dt.year == a])
    o = pd.concat(oo, ignore_index=True)
    ndias = sum(len(pd.unique(nq.sesion)) for nq, _ in D.values())
    print(f"\n=== {etiqueta}: {len(o)} ops ({len(o)/ndias:.0%} de los días, ~{len(o)/ndias*5:.1f}/semana) · stop mediano {o.riesgo_pts.median():.0f} pts · objetivo estructural mediano {o.obj_estr.median():.2f}R")
    for rt in (2.0, 1.0, 1.5):
        r = motor.r_neta(o, rt); s = C.resumen(r)
        py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
        tp = (o.rmax >= rt).mean(); sl = (~(o.rmax >= rt) & o.toco_sl).mean()
        inv = motor.r_neta(o, rt, True).mean()
        tag = "PRINCIPAL" if (rt == 2.0 and smt) else "info"
        print(f"  [{tag}] 1:{rt}: wr {s['wr']:.1%} (TP {tp:.0%} · SL {sl:.0%}) R={s['R']:+.3f} p1c={s['p_1cola']:.3f} años {py} invertida {inv:+.3f}")
    # objetivo estructural: extremo opuesto de la vela 4H
    rr = np.where(o.rmax >= o.obj_estr, o.obj_estr, np.where(o.toco_sl, -1.0, np.minimum(o.r_cierre, o.obj_estr))) - 0.87 / o.riesgo_pts
    print(f"  [info] objetivo = extremo opuesto 4H: R={rr.mean():+.3f} wr {np.mean(rr > 0):.1%}")
