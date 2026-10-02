"""Ejecuta preregistros/2026-10-02_familia_filtros_momento.md (DISEÑO por defecto; 'validacion' como argumento)."""
import sys
import numpy as np, pandas as pd
from src import loader, motor
from src.motores import momento_generico as MG

FASE = sys.argv[1] if len(sys.argv) > 1 else "diseno"
ANIOS = [2021, 2023, 2025] if FASE == "diseno" else [2022, 2024, 2026]


def rasgos(b):
    o_, h, l, c, v = (b[k].to_numpy() for k in ("o", "h", "l", "c", "v"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    filas = {}
    for s in pd.unique(ses):
        ii = np.flatnonzero(ses == s); hm = hh[ii]
        sel = lambda a, z: ii[(hm >= a) & (hm <= z)] if a <= z else ii[(hm >= a) | (hm <= z)]
        on, ap, tr, rth = sel(1800, 929), sel(930, 939), sel(909, 939), sel(930, 1559)
        b830, b5, pre = sel(830, 830), sel(930, 934), ii[ii <= (sel(939, 939)[0] if len(sel(939, 939)) else -1)]
        if len(on) < 300 or len(ap) != 10 or len(tr) != 31 or hh[tr[0]] != 909 or len(b5) != 5 or len(b830) != 1:
            continue
        c939 = c[ap[-1]]
        vw = (c[pre] * v[pre]).sum() / v[pre].sum() if v[pre].sum() > 0 else np.nan
        H, L = h[tr].max(), l[tr].min()
        filas[s] = dict(on_r=(h[on].max() - l[on].min()) / c939, ap_r=(h[ap].max() - l[ap].min()) / c939,
                        vwap=np.sign(c939 - vw), ap_dir=np.sign(c939 - o_[ap[0]]), c939=c939,
                        b5=np.sign(c[b5[-1]] - o_[b5[0]]), pos=(c939 - L) / (H - L) if H > L else 0.5,
                        r830=(h[b830[0]] - l[b830[0]]) / c939,
                        rth_mid=(h[rth].max() + l[rth].min()) / 2 if len(rth) > 300 else np.nan,
                        cierre=c[rth[-1]] if len(rth) > 300 else np.nan)
    x = pd.DataFrame.from_dict(filas, orient="index").sort_index()
    med = lambda k: x[k].shift(1).rolling(60, min_periods=45).median()
    x["mid_prev"] = x.rth_mid.ffill().shift(1)
    x["ma20"] = x.cierre.shift(1).rolling(20, min_periods=15).mean()  # tolera días de cierre anticipado
    for k in ("on_r", "ap_r", "r830"):
        x[k + "_m"] = med(k)
    return x


def ops(a):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    o = motor.simular(b, MG.senales(b, 940, 30, 0.40))
    o = o.merge(rasgos(b), left_on="sesion", right_index=True, how="left")
    o = o[(o.sesion.dt.year == a)].dropna(subset=["on_r_m", "ap_r_m", "r830_m", "mid_prev", "ma20", "vwap"])
    return o


o = pd.concat([ops(a) for a in ANIOS], ignore_index=True)
d = o.dir.to_numpy()
F = {
    "F7 overnight amplio": o.on_r > o.on_r_m,
    "F8 apertura amplia": o.ap_r > o.ap_r_m,
    "F9 a favor del VWAP": o.vwap == d,
    "F10 a favor de la apertura 09:30": o.ap_dir == d,
    "F11 a favor del medio del día previo": np.sign(o.c939 - o.mid_prev) == d,
    "F12 a favor de la media de 20 días": np.sign(o.c939 - o.ma20) == d,
    "F13 1ª vela 5m a favor": o.b5 == d,
    "F14 cierre 09:39 en el extremo a favor": np.where(d == 1, o.pos >= 0.75, o.pos <= 0.25),
    "F15 barra 08:30 amplia": o.r830 > o.r830_m,
}
r = motor.r_neta(o, 2.0); wr = lambda z: np.mean(z > 0); anio = o.sesion.dt.year.to_numpy()
print(f"[{FASE}] BASE n={len(r)} R={r.mean():+.3f} wr={wr(r):.1%}\n")
filas = []
for nom, m in F.items():
    m = np.asarray(m, bool)
    for lado, mm in (("cumple", m), ("NO cumple", ~m)):
        rf = r[mm]; py = pd.Series(rf).groupby(anio[mm]).mean()
        filas.append(dict(variante=f"{nom} · {lado}", n=mm.sum(), frac=mm.mean(), R=rf.mean(), wr=wr(rf),
                          min_anio=py.min(), mask=mm))
t = pd.DataFrame(filas).sort_values("R", ascending=False)
print(t.drop(columns="mask").to_string(index=False, formatters={"frac": "{:.0%}".format, "R": "{:+.3f}".format,
      "wr": "{:.1%}".format, "min_anio": "{:+.3f}".format}))
# nulo del MÁXIMO de la familia
rng = np.random.default_rng(11); N = len(r); maxs = []
tam = [np.asarray(m, bool).sum() for m in F.values()]
for _ in range(2000):
    best = -9
    for k in tam:
        perm = rng.permutation(N); a_, b_ = r[perm[:k]].mean(), r[perm[k:]].mean()
        best = max(best, a_, b_)
    maxs.append(best)
p95 = np.percentile(maxs, 95); top = t.iloc[0]
p_fam = np.mean(np.array(maxs) >= top.R)
ok = top.R > p95 and top.R > r.mean() and top.wr > wr(r) and top.frac >= 0.35 and top.min_anio > 0
print(f"\nMejor: {top.variante} R={top.R:+.3f} · máximo del nulo: media {np.mean(maxs):+.3f}, p95 {p95:+.3f} · p familia={p_fam:.3f} -> {'PASA a validación' if ok else 'NO PASA'}")
