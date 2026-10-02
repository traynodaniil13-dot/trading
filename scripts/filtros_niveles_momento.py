"""Ejecuta preregistros/2026-10-02_filtros_niveles_momento.md.
Uso: python -m scripts.filtros_niveles_momento diseno|validacion"""
import sys
import numpy as np, pandas as pd
from src import controles as C
from src import loader, motor
from src.motores import momento_generico as MG

fase = sys.argv[1]
ANIOS = [2021, 2023, 2025] if fase == "diseno" else [2022, 2024, 2026]
MIN_FRAC = 0.20
P_VAL = 0.01


def niveles(b):
    """Por sesión: PDH/PDL (RTH previa), ONH/ONL (18:00-09:29), c 09:39, y extremos 18:00-09:39."""
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    df = pd.DataFrame({"ses": ses, "hh": hh, "h": b.h.to_numpy(), "l": b.l.to_numpy(), "c": b.c.to_numpy()})
    noct = (hh >= 1800) | (hh < 930)          # 18:00-09:29 (la sesión empieza a las 18:00: bug nº6)
    pre = noct | ((hh >= 930) & (hh <= 939))   # 18:00-09:39
    rth = (hh >= 930) & (hh <= 1559)
    g = pd.DataFrame(index=pd.Index(np.unique(ses), name="ses"))
    g["ONH"] = df[noct].groupby("ses").h.max(); g["ONL"] = df[noct].groupby("ses").l.min()
    g["preH"] = df[pre].groupby("ses").h.max(); g["preL"] = df[pre].groupby("ses").l.min()
    g["RTHH"] = df[rth].groupby("ses").h.max(); g["RTHL"] = df[rth].groupby("ses").l.min()
    g["c939"] = df[hh == 939].groupby("ses").c.first()
    g["PDH"] = g.RTHH.shift(1); g["PDL"] = g.RTHL.shift(1)   # sesión ANTERIOR del fichero
    return g.drop(columns=["RTHH", "RTHL"])


def por_anio(a):
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    s = MG.senales(nq, 940, 30, 0.40)
    o = motor.simular(nq, s)
    g = niveles(nq)
    o = o.merge(g, left_on="sesion", right_index=True, how="left")
    # comprobación de causalidad: la barra de entrada es la de 09:40 de la misma sesión
    assert (nq.hhmm.to_numpy()[s.i_ent.to_numpy()] == 940).all()
    return o[o.sesion.dt.year == a]


o = pd.concat([por_anio(a) for a in ANIOS], ignore_index=True)
r = motor.r_neta(o, 2.0)
d = o["dir"].to_numpy(); ent = o["precio"].to_numpy(); obj = ent + d * 2 * o["riesgo_pts"].to_numpy()
lo, hi = np.minimum(ent, obj), np.maximum(ent, obj)
lv = o[["PDH", "PDL", "ONH", "ONL"]].to_numpy()
en_medio = ((lv > lo[:, None]) & (lv < hi[:, None])).any(axis=1)
c939 = o.c939.to_numpy(); PDH, PDL = o.PDH.to_numpy(), o.PDL.to_numpy()
pos = (c939 - o.ONL.to_numpy()) / (o.ONH.to_numpy() - o.ONL.to_numpy())
ok_niv = ~np.isnan(lv).any(axis=1)
mask = {
    "N1_camino_libre": ok_niv & ~en_medio,
    "N2_rango_previo_roto": np.where(d == 1, c939 > PDH, c939 < PDL),
    "N3_tercio_overnight": np.where(d == 1, pos > 2 / 3, pos < 1 / 3),
    "N4_barrida_en_contra": np.where(d == 1, (o.preL.to_numpy() < PDL) & (c939 > PDL),
                                     (o.preH.to_numpy() > PDH) & (c939 < PDH)),
}
base = C.resumen(r)
print(f"FASE {fase} {ANIOS} · BASE n={base['n']} R={base['R']:+.3f} wr={base['wr']:.1%} · sin niveles: {(~ok_niv).sum()} ops\n")
rng = np.random.default_rng(0)
anio = o.sesion.dt.year.to_numpy()
for k, m in mask.items():
    m = np.asarray(m, bool); x = r[m]; s_ = C.resumen(x)
    azar = np.array([r[rng.choice(len(r), size=m.sum(), replace=False)].mean() for _ in range(1000)])
    p95 = np.percentile(azar, 95)
    py = pd.Series(x).groupby(anio[m]).mean().round(3).to_dict()
    L, S = x[d[m] == 1].mean(), x[d[m] == -1].mean()
    if fase == "diseno":
        ok = s_["R"] > base["R"] and s_["wr"] > base["wr"] and s_["n"] >= MIN_FRAC * base["n"] and s_["R"] > p95
    else:
        ok = s_["R"] > 0 and s_["p_1cola"] < P_VAL and s_["R"] > base["R"] and s_["wr"] > base["wr"] and s_["R"] > p95
    print(f"{k:22s} n={s_['n']:4d} ({s_['n']/base['n']:.0%}) R={s_['R']:+.3f} wr={s_['wr']:.1%} p1c={s_['p_1cola']:.3f} "
          f"| azar p95 {p95:+.3f} | años {py} | L {L:+.3f} S {S:+.3f} | resto R={r[~m].mean():+.3f} -> {'CUMPLE' if ok else 'no'}")
