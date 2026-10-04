import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.motores import kasen as K
src = open("scripts/kasen_pdh.py").read().split("\ndef datos")[0]; ns = {}; exec(src, ns); senales_pdh = ns["senales"]
def datos(a):
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    ix = nq.index.intersection(es.index); return nq.loc[ix], es.loc[ix]
D = {a: datos(a) for a in (2022, 2024, 2026)}
def ops(fn):
    oo = []
    for a, (nq, es) in D.items():
        o = motor.simular(nq, fn(nq, es)); oo.append(o[o.sesion.dt.year == a])
    return pd.concat(oo, ignore_index=True)
for nom, fn_smt, fn_sin, rt_p in (
    ("H2 PDH + 10:00 + SMT", lambda n, e: senales_pdh(n, e, True), lambda n, e: senales_pdh(n, e, False), 1.5),
    ("H3 vela 4H + SMT + IFVG", lambda n, e: K.senales(n, e, True), lambda n, e: K.senales(n, e, False), 2.0)):
    o, o0 = ops(fn_smt), ops(fn_sin)
    print(f"\n=== {nom}: {len(o)} ops (sin SMT: {len(o0)}) ===")
    for rt in (rt_p, 1.0, 1.5, 2.0):
        if rt != rt_p and rt in (rt_p,): continue
        r = motor.r_neta(o, rt); r0 = motor.r_neta(o0, rt); s = C.resumen(r)
        py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
        tag = "PRINCIPAL" if rt == rt_p else "info"
        ok = s["p_1cola"] < 0.0031 and min(py.values()) > 0 and r.mean() > r0.mean()
        print(f"  [{tag}] 1:{rt}: wr {s['wr']:.1%} (TP {(o.rmax>=rt).mean():.0%}) R={s['R']:+.3f} p1c={s['p_1cola']:.3f} años {py} · sin SMT {r0.mean():+.3f}" + (f" -> {'PASA' if ok else 'NO PASA'}" if rt == rt_p else ""))
