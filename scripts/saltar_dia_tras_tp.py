import numpy as np, pandas as pd
from src import loader, motor
from src.motores import momento_generico as MG
def ops(anios):
    oo = []
    for a in anios:
        b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
        o = motor.simular(b, MG.senales(b, 940, 30, 0.40)); oo.append(o[o.sesion.dt.year == a])
    return pd.concat(oo, ignore_index=True).sort_values("sesion").reset_index(drop=True)
rng = np.random.default_rng(3)
for nom, anios in (("DISEÑO 21/23/25", (2021, 2023, 2025)), ("6 años (informativo)", range(2021, 2027))):
    o = ops(anios); r = motor.r_neta(o, 2.0); tp = (o.rmax >= 2).to_numpy()
    ayer_tp = np.r_[False, tp[:-1]] & np.r_[False, o.sesion.dt.year.to_numpy()[1:] == o.sesion.dt.year.to_numpy()[:-1]]
    keep = ~ayer_tp
    p95 = np.percentile([r[rng.choice(len(r), keep.sum(), replace=False)].mean() for _ in range(2000)], 95)
    py = pd.DataFrame({"a": o.sesion.dt.year, "r": r, "s": ayer_tp}).groupby(["a", "s"]).r.mean().unstack().round(3)
    print(f"== {nom} ==  n={len(r)}")
    print(f"  P(TP | ayer TP) = {tp[ayer_tp].mean():.1%} (n={ayer_tp.sum()})  ·  P(TP | ayer no TP) = {tp[~ayer_tp].mean():.1%}")
    print(f"  BASE R={r.mean():+.3f} · operando solo tras no-TP: R={r[keep].mean():+.3f} (n={keep.sum()}) · días saltados R={r[ayer_tp].mean():+.3f} · p95 azar {p95:+.3f}")
    print("  R por año (False = se opera, True = se salta):"); print(py.to_string())
    if nom.startswith("DISEÑO"):
        ok = r[keep].mean() > r.mean() and r[keep].mean() > p95 and (py[True] < 0).all()
        print("  VEREDICTO:", "PASA" if ok else "NO PASA")
