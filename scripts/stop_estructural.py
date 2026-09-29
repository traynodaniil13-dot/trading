import sys
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.motores import momento_generico as MG

fase = sys.argv[1]; ANIOS = [2021, 2023, 2025] if fase == "diseno" else [2022, 2024, 2026]


def ops(a, modo):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    s = MG.senales(b, 940, 30, 0.40)
    if modo != "base":
        h, l, c = b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
        idx = pd.Series(np.arange(len(b)), index=b.index)
        m909 = b.hhmm.to_numpy() == 909
        ref = pd.Series(np.flatnonzero(m909), index=b.sesion.to_numpy()[m909])
        ref = ref[~ref.index.duplicated()]
        ses = b.sesion.to_numpy()[s.i_ent.to_numpy()]
        i_ref = ref.reindex(ses).to_numpy()
        assert not np.isnan(i_ref).any()
        i_ref = i_ref.astype(int)
        assert (b.hhmm.to_numpy()[i_ref] == 909).all() and (i_ref < s.i_ent.to_numpy()).all()
        if modo == "S1":
            stop = c[i_ref]
        else:
            stop = np.array([l[i:e].min() if d == 1 else h[i:e].max()
                             for i, e, d in zip(i_ref, s.i_ent.to_numpy(), s.dir.to_numpy())])
        dist = (s.precio.to_numpy() - stop) * s.dir.to_numpy()
        s = s.assign(riesgo=dist)
        s = s[(dist > 0) & (dist >= 0.001 * s.precio.to_numpy())]
    o = motor.simular(b, s); return o[o.sesion.dt.year == a]


base_n = None
for modo in ("base", "S1", "S2"):
    o = pd.concat([ops(a, modo) for a in ANIOS], ignore_index=True)
    r = motor.r_neta(o, 2.0); s = C.resumen(r)
    py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
    base_n = base_n or s["n"]
    print(f"{fase} {modo:4s} n={s['n']:4d} ({s['n']/base_n:.0%}) R={s['R']:+.3f} wr={s['wr']:.1%} p1c={s['p_1cola']:.3f} "
          f"stop mediano {np.median(o.riesgo_pts):.0f} pts | años {py}")
