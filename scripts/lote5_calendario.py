import numpy as np, pandas as pd
from scipy import stats
from src import loader
from scripts.premisas_lote3 import carrera

def eventos(a):
    b = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    if a < 2026:  # para saber el primer día del año siguiente / festivos de fin de año
        b2 = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a+1}.csv.gz"], verbose=False)
        dias_sig = sorted(pd.unique(b2.sesion))[:5]
    else:
        dias_sig = []
    o, h, l, c = (b[k].to_numpy() for k in ("o", "h", "l", "c")); hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    dias = [s for s in pd.unique(ses) if ((ses == s) & (hh == 1559)).any()]
    todos = [pd.Timestamp(d) for d in dias] + [pd.Timestamp(d) for d in dias_sig]
    filas = []
    for t, s in enumerate(dias):
        S = pd.Timestamp(s)
        if S.year != a or t == 0:
            continue
        ii = np.flatnonzero(ses == s); hm = hh[ii]
        get = lambda x: ii[hm == x][0] if (hm == x).any() else None
        j930, j1029, j1030, j1459, j1500 = get(930), get(1029), get(1030), get(1459), get(1500)
        if j930 is None:
            continue
        sig = todos[t + 1] if t + 1 < len(todos) else None
        ult_mes = sig is not None and sig.month != S.month
        prim3 = sum(1 for d in todos[max(0, t - 3):t] if d.month == S.month) < 3 and todos[t - 1].month != S.month or \
                (len([d for d in todos[:t] if d.month == S.month and d.year == S.year]) < 3)
        cm = ult_mes or prim3
        vispera = sig is not None and np.busday_count(S.date(), sig.date()) > 1
        rest = ii[(hm >= 930) & (hm <= 1559)]
        def race(j, d, ks):
            tr = rest[rest > j]; return {k: carrera(h, l, c, j, tr, d, k) for k in ks}
        filas.append(dict(c="C1", ev=cm, dir=1, **{f"k{k}": v for k, v in race(j930, 1, (0.25, 0.40)).items()}, a=a))
        filas.append(dict(c="C2", ev=vispera, dir=1, **{f"k{k}": v for k, v in race(j930, 1, (0.25, 0.40)).items()}, a=a))
        if S.dayofweek == 4 and j1029 is not None and j1030 is not None:
            d = -int(np.sign(c[j1029] - o[j930]))
            if d != 0:
                opex = 15 <= S.day <= 21
                filas.append(dict(c="C3", ev=opex, dir=d, **{f"k{k}": v for k, v in race(j1030, d, (0.25, 0.40)).items()}, a=a))
        if j1459 is not None and j1500 is not None:
            prev_mes = [x for x in todos[:t] if (x.year, x.month) != (S.year, S.month)]
            if prev_mes:
                pm = prev_mes[-1]; jj = np.flatnonzero((ses == np.datetime64(pm)) & (hh == 1559))
                if len(jj):
                    d = -int(np.sign(c[j1459] - c[jj[0]]))
                    if d != 0:
                        filas.append(dict(c="C4", ev=ult_mes, dir=d, **{f"k{k}": v for k, v in race(j1459, d, (0.10, 0.15)).items()}, a=a))
    return pd.DataFrame(filas)

e = pd.concat([eventos(a) for a in (2021, 2023, 2025)], ignore_index=True)
for cc, ks in (("C1", (0.25, 0.40)), ("C2", (0.25, 0.40)), ("C3", (0.25, 0.40)), ("C4", (0.10, 0.15))):
    x = e[e.c == cc]
    for k in ks:
        col = f"k{k}"; y = x[x[col] != 0]
        ev, ot = y[y.ev], y[~y.ev]
        pe, po = (ev[col] == 1).mean(), (ot[col] == 1).mean()
        n1, n2 = len(ev), len(ot)
        pp = ((ev[col] == 1).sum() + (ot[col] == 1).sum()) / (n1 + n2)
        z = (pe - po) / np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2)) if n1 and n2 else 0
        p = 1 - stats.norm.cdf(z)
        py = {int(a): round((g[col] == 1).mean() - (ot[ot.a == a][col] == 1).mean(), 3) for a, g in ev.groupby("a")}
        ok = p < 0.00625 and all(v > 0 for v in py.values())
        print(f"{cc} ±{k}%: evento {pe:.1%} (n={n1}) vs resto {po:.1%} (n={n2}) · dif {pe-po:+.1%} · p={p:.3f} · por año {py} -> {'PASA' if ok else 'no'}")
