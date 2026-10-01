"""Ejecuta preregistros/2026-10-01_oro_lote1.md en DISEÑO (2011/2013/2015/2017). No cambiar nada."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor
from src.motores import momento_generico as MG

ANIOS = [2011, 2013, 2015, 2017]
COSTE = 0.30
UMBRAL = 0.01


def idx_por(b, mask_hh):
    """dict sesion -> primera posición de barra que cumple (sesión Y hora: bug nº6)."""
    pos = np.flatnonzero(mask_hh)
    ses = b.sesion.to_numpy()[pos]
    s = pd.Series(pos, index=ses)
    return s[~s.index.duplicated()]


def g1(b):
    lon = b.index.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").tz_convert("Europe/London")
    lhh = np.asarray(lon.hour * 100 + lon.minute)
    o, c = b.o.to_numpy(), b.c.to_numpy()
    a, z = idx_por(b, lhh == 1430), idx_por(b, lhh == 1529)
    ses = a.index.intersection(z.index)
    prem = o[a[ses]] - c[z[ses]]
    # control: media de las ventanas hh:30 -> hh+1:29 (Londres) del mismo día, en corto
    ctrl = []
    for s in ses:
        vals = []
        for h in range(24):
            ia = idx_por_cache(b, lhh, h * 100 + 30).get(s); iz = idx_por_cache(b, lhh, h * 100 + 129 if h < 23 else 29).get(s)
            if ia is not None and iz is not None and iz > ia:
                vals.append(o[ia] - c[iz])
        ctrl.append(np.mean(vals))
    return pd.DataFrame({"ses": ses, "pts": prem, "exceso": prem - np.array(ctrl), "dir": -1})


_cache = {}
def idx_por_cache(b, lhh, hh):
    k = (id(b), hh)
    if k not in _cache:
        _cache[k] = idx_por(b, lhh == hh).to_dict()
    return _cache[k]


def g2(b):
    s = MG.senales(b, 940, 30, 0.40)
    c = b.c.to_numpy(); r909 = idx_por(b, b.hhmm.to_numpy() == 909)
    i_ref = r909.reindex(b.sesion.to_numpy()[s.i_ent.to_numpy()]).to_numpy()
    ok = ~np.isnan(i_ref); s = s[ok]; i_ref = i_ref[ok].astype(int)
    assert (i_ref < s.i_ent.to_numpy()).all()
    dist = (s.precio.to_numpy() - c[i_ref]) * s.dir.to_numpy()
    s = s.assign(riesgo=dist)[(dist > 0) & (dist >= 0.001 * s.precio.to_numpy())]
    return motor.simular(b, s)


def g3(b):
    hh, o, h, l, c = b.hhmm.to_numpy(), b.o.to_numpy(), b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
    i830, i831, i929 = idx_por(b, hh == 830), idx_por(b, hh == 831), idx_por(b, hh == 929)
    filas = []
    for s, k in i830.items():
        if s not in i831.index or s not in i929.index: continue
        pre = np.arange(k - 10, k)
        if (hh[pre] < 820).any() or (b.sesion.to_numpy()[pre] != s).any(): continue
        if (h[k] - l[k]) <= 3 * np.median(h[pre] - l[pre]) or c[k] == o[k]: continue
        d = 1 if c[k] > o[k] else -1
        assert i831[s] == k + 1
        filas.append((s, d, (c[i929[s]] - o[i831[s]]) * d))
    return pd.DataFrame(filas, columns=["ses", "dir", "pts"])


def g4(b):
    hh, ses_arr = b.hhmm.to_numpy(), b.sesion.to_numpy()
    o, h, l, c = b.o.to_numpy(), b.h.to_numpy(), b.l.to_numpy(), b.c.to_numpy()
    df = pd.DataFrame({"ses": ses_arr, "hh": hh, "i": np.arange(len(b))})
    fin = idx_por(b, hh == 1159)
    filas = []
    for s, g in df.groupby("ses", sort=True):
        if s not in fin.index: continue
        asia = g.i[(g.hh >= 1900) | (g.hh < 300)].to_numpy()
        post = g.i[(g.hh >= 300) & (g.hh <= 1059)].to_numpy()
        if len(asia) < 300 or len(post) < 10: continue
        assert asia.max() < post.min()
        top, bot = h[asia].max(), l[asia].min()
        fuera = np.flatnonzero((c[post] > top) | (c[post] < bot))
        if fuera.size == 0: continue
        k = post[fuera[0]]; d = 1 if c[k] > top else -1
        e = k + 1
        if ses_arr[e] != s or e > fin[s]: continue
        filas.append((s, d, (c[fin[s]] - o[e]) * d))
    return pd.DataFrame(filas, columns=["ses", "dir", "pts"])


def g5(b):
    hh, o, c = b.hhmm.to_numpy(), b.o.to_numpy(), b.c.to_numpy()
    a, z = idx_por(b, hh == 820), idx_por(b, hh == 1329)
    df = pd.DataFrame({"ses": b.sesion.to_numpy(), "i": np.arange(len(b))})
    ini, fin = df.groupby("ses").i.min(), df.groupby("ses").i.max()
    ses = a.index.intersection(z.index)
    prem = o[a[ses]] - c[z[ses]]
    deriva = (c[fin[ses]] - o[ini[ses]]) / (fin[ses].to_numpy() - ini[ses].to_numpy() + 1) * (z[ses].to_numpy() - a[ses].to_numpy() + 1)
    return pd.DataFrame({"ses": ses, "pts": prem, "exceso": prem + deriva, "dir": -1})


def del_anio(t, a):
    return t[pd.to_datetime(t.ses).dt.year == a]


def informe(nombre, t, col="pts", nulo=None):
    s = C.resumen(t[col]); anios = t.groupby(pd.to_datetime(t.ses).dt.year)[col].mean().round(2).to_dict()
    signo = np.sign(s["R"]); mismos = sum(np.sign(v) == signo for v in anios.values())
    linea = f"{nombre:28s} n={s['n']:4d} media={s['R']:+.3f} p1c={s['p_1cola']:.4f} años {anios} ({mismos}/4 mismo signo)"
    pasa = s["p_1cola"] < UMBRAL and mismos >= 3
    if "dir" in t and t.dir.nunique() > 1:
        L, S = t[t.dir == 1][col].mean(), t[t.dir == -1][col].mean()
        linea += f" · largos {L:+.3f} cortos {S:+.3f}"; pasa = pasa and L > 0 and S > 0
    if nulo is not None:
        z = C.z_exceso(s["R"], s["ee"], np.mean(nulo), np.std(nulo, ddof=1) / np.sqrt(len(nulo)))
        linea += f" · nulo {np.mean(nulo):+.3f} z={z:+.2f}"; pasa = pasa and z > 2
    print(linea + ("  → PASA" if pasa else "  → no pasa"))


barras = {a: loader.cargar_oro([a]) for a in ANIOS}
T = {k: [] for k in ("G1", "G3", "G4", "G5")}; R2, ses2 = [], []
for a, b in barras.items():
    _cache.clear()
    for k, f in (("G1", g1), ("G3", g3), ("G4", g4), ("G5", g5)):
        T[k].append(del_anio(f(b), a))
    o2 = g2(b); o2 = o2[o2.sesion.dt.year == a]
    R2.append(pd.DataFrame({"ses": o2.sesion, "dir": o2.dir, "pts": motor.r_neta(o2, 2.0, coste=COSTE)}))
T = {k: pd.concat(v, ignore_index=True) for k, v in T.items()}
g2t = pd.concat(R2, ignore_index=True)

nul2, nul4 = [], []
for sem in range(6):
    r2, r4 = [], []
    for i, (a, b) in enumerate(barras.items()):
        rw = C.paseo_aleatorio(b, 7000 + 10 * sem + i)
        o2 = g2(rw); o2 = o2[o2.sesion.dt.year == a]; r2.append(motor.r_neta(o2, 2.0, coste=COSTE))
        r4.append(del_anio(g4(rw), a).pts.to_numpy())
    nul2.append(np.concatenate(r2).mean()); nul4.append(np.concatenate(r4).mean())

print("== ORO · LOTE 1 · DISEÑO 2011/13/15/17 · umbral p < 0,01 ==")
informe("G1 fixing PM (corto, pts)", T["G1"]); informe("G1 exceso sobre otras horas", T["G1"], "exceso")
informe("G2 Momento S1 congelado (R)", g2t, nulo=nul2)
informe("G3 dato 08:30 (pts)", T["G3"])
informe("G4 ruptura asiática (pts)", T["G4"], nulo=nul4)
informe("G5 corto COMEX 08:20-13:29", T["G5"]); informe("G5 exceso sobre la deriva", T["G5"], "exceso")
