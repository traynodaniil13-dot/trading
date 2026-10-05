"""Mina NQ tanda 2: N1 apertura de Asia, N2 días de tendencia, N3 OPEN_DRIVE.
preregistros/2026-10-05_mina_nq_tanda2.md"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader, mina

COSTE = 0.87


def apertura_ny(sesion, zona, hh, mm):
    """Apertura de contado de `zona` del día `sesion` (fecha local) en hora NY (naive)."""
    t = pd.Timestamp(sesion.year, sesion.month, sesion.day, hh, mm, tz=zona)
    return t.tz_convert("America/New_York").tz_localize(None)


def n1(mercado, L, k):
    zona, hh, mm = ("Asia/Tokyo", 9, 0) if mercado == "Tokio" else ("Asia/Hong_Kong", 9, 30)

    def fn(df):
        o, c = df.o.to_numpy(), df.c.to_numpy(); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
        ix = df.index; filas = []
        for s in pd.unique(ses):
            ap = apertura_ny(pd.Timestamp(s), zona, hh, mm)
            T = ap + pd.Timedelta(minutes=10)
            pos = ix.get_indexer([T - pd.Timedelta(minutes=1 + L), T - pd.Timedelta(minutes=1), T])
            if (pos < 0).any():
                continue
            a, j, e = pos
            if ses[e] != s or ses[a] != s:
                continue
            fin = np.flatnonzero((ses == s) & (hm == 259))
            if not len(fin) or fin[0] <= e:
                continue
            d = np.sign(c[j] - c[a])
            if d == 0:
                continue
            p = o[e]
            filas.append(dict(i_ent=e, precio=p, dir=int(d), riesgo=p * k / 100, i_fin=fin[0], obj=2.0, coste=COSTE))
        return df, pd.DataFrame(filas)
    return fn


def n2(modo, q, k):
    def fn(df):
        o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
        idx = np.arange(len(df)); filas = []; hist = []
        for s in pd.unique(ses):
            ii = idx[ses == s]; t = hm[ii]
            h1 = ii[(t >= 930) & (t <= 1029)]; e = ii[t == 1030]; f = ii[t == 1559]
            if len(h1) < 55 or not len(e) or not len(f):
                continue
            rango = h[h1].max() - l[h1].min()
            if len(hist) >= 20:
                med = np.median(hist[-20:])
                if med > 0 and rango / med >= q:
                    d = np.sign(c[h1[-1]] - o[h1[0]])
                    if d != 0:
                        d = int(d if modo == "CONT" else -d); p = o[e[0]]
                        filas.append(dict(i_ent=e[0], precio=p, dir=d, riesgo=p * k / 100, i_fin=f[0], obj=2.0, coste=COSTE))
            hist.append(rango)
        return df, pd.DataFrame(filas)
    return fn


def n3(m, u):
    def fn(df):
        o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
        idx = np.arange(len(df)); filas = []
        for s in pd.unique(ses):
            ii = idx[ses == s]; t = hm[ii]
            v = ii[(t >= 930) & (t <= 930 + m - 1)]; f = ii[t == 1559]
            if len(v) != m or not len(f) or hm[v[0]] != 930:
                continue
            rg = h[v].max() - l[v].min(); cu = c[v[-1]] - o[v[0]]
            if rg <= 0 or abs(cu) / rg <= u:
                continue
            px = c[v[-1]]; r = max(rg, 0.0005 * px)
            filas.append(dict(i_ent=v[-1] + 1, precio=px, dir=int(np.sign(cu)), riesgo=r, i_fin=f[0], obj=2.0, coste=COSTE))
        return df, pd.DataFrame(filas)
    return fn


FAMILIAS = {
    "N1 apertura de Asia": {f"{mk} L{L} k={k}%": n1(mk, L, k) for mk in ("Tokio", "HongKong") for L in (15, 30) for k in (0.15, 0.25)},
    "N2 días de tendencia": {f"{md} q={q} k={k}%": n2(md, q, k) for md in ("CONT", "REV") for q in (1.5, 2.0) for k in (0.30, 0.50)},
    "N3 OPEN_DRIVE": {f"m={m} cuerpo>{u}": n3(m, u) for m in (2, 3, 5) for u in (0.6, 0.8)},
}

if __name__ == "__main__":
    anios = mina.VALIDACION if "validacion" in sys.argv else mina.DISENO
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in anios}
    for nom, V in FAMILIAS.items():
        if len(sys.argv) > 1 and not any(x in nom for x in sys.argv[1:] if x != "validacion"):
            continue
        mina.evaluar(nom, V, mina.r_obj, D, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
