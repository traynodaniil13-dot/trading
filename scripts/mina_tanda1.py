"""Mina, tanda 1: M1 valor relativo NQ-ES y M2 MOC en ES.
preregistros/2026-10-04_mina_tanda1_relativo_y_moc_es.md"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader, mina

ESCALA = 10000.0  # d en puntos básicos
BASE = 100000.0   # desplazamiento para que la serie sea positiva


def datos_par(a):
    nq = loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)
    es = loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False)
    ix = nq.index.intersection(es.index)
    return nq.loc[ix], es.loc[ix]


def serie_diferencial(par):
    """Barras del diferencial (en pb) y metadatos por sesión, todo causal."""
    nq, es = par
    cN, cE = nq.c.to_numpy(), es.c.to_numpy()
    hh, ses = nq.hhmm.to_numpy(), nq.sesion.to_numpy()
    idx = np.arange(len(nq))
    d = np.full(len(nq), np.nan); meta = {}
    hist = []  # (retNQ, retES, d_cierre) de sesiones previas
    for s in pd.unique(ses):
        ii = idx[ses == s]; hm = hh[ii]
        j929, j1559 = ii[hm == 929], ii[hm == 1559]
        rth = ii[(hm >= 930) & (hm <= 1559)]
        if not len(j929) or not len(j1559) or len(rth) < 300:
            continue
        j0, jf = j929[0], j1559[0]
        if len(hist) >= 20:
            h = np.array(hist[-20:])
            beta = np.polyfit(h[:, 1], h[:, 0], 1)[0]
            sig = h[:, 2].std(ddof=1)
            seg = np.arange(j0, jf + 1)
            d[seg] = np.log(cN[seg] / cN[j0]) - beta * np.log(cE[seg] / cE[j0])
            meta[s] = (beta, sig, j0, jf, cN[j0], cE[j0])
        rN = np.log(cN[jf] / cN[j0]); rE = np.log(cE[jf] / cE[j0])
        bh = np.polyfit(np.array(hist[-20:])[:, 1], np.array(hist[-20:])[:, 0], 1)[0] if len(hist) >= 20 else 1.0
        hist.append((rN, rE, rN - bh * rE))
    S = BASE + ESCALA * np.nan_to_num(d)
    barras = pd.DataFrame({"o": S, "h": S, "l": S, "c": S, "sesion": ses, "hhmm": hh}, index=nq.index)
    return barras, d, meta


def variante_m1(modo, k, inicio):
    def fn(par):
        barras, d, meta = serie_diferencial(par)
        hh = barras.hhmm.to_numpy(); filas = []
        for s, (beta, sig, j0, jf, pN, pE) in meta.items():
            if not np.isfinite(sig) or sig <= 0:
                continue
            ventana = np.arange(j0, jf + 1); ventana = ventana[(hh[ventana] >= inicio) & (hh[ventana] <= 1500)]
            hit = ventana[np.abs(d[ventana]) >= k * sig]
            if not len(hit):
                continue
            j = hit[0]; sg = np.sign(d[j])
            direc = int(-sg if modo == "REV" else sg)
            riesgo = 0.5 * k * sig * ESCALA
            coste = (0.87 / pN + abs(beta) * 0.65 / pE) * ESCALA
            filas.append(dict(i_ent=j + 1, precio=barras.c.iat[j], dir=direc, riesgo=riesgo, i_fin=jf, obj=2.0, coste=coste))
        return barras, pd.DataFrame(filas)
    return fn


def nulo_par(par, semilla):
    """Barajado conjunto de los pares de retornos de 1 min dentro de cada sesión (RTH)."""
    nq, es = par; rng = np.random.default_rng(semilla)
    cN, cE = nq.c.to_numpy().copy(), es.c.to_numpy().copy()
    hh, ses = nq.hhmm.to_numpy(), nq.sesion.to_numpy(); idx = np.arange(len(nq))
    for s in pd.unique(ses):
        ii = idx[ses == s]; hm = hh[ii]
        seg = ii[(hm >= 929) & (hm <= 1559)]
        if len(seg) < 300:
            continue
        rN, rE = np.diff(np.log(cN[seg])), np.diff(np.log(cE[seg]))
        p = rng.permutation(len(rN))
        cN[seg[1:]] = cN[seg[0]] * np.exp(np.cumsum(rN[p])); cE[seg[1:]] = cE[seg[0]] * np.exp(np.cumsum(rE[p]))
    n2, e2 = nq.copy(), es.copy()
    for df, c in ((n2, cN), (e2, cE)):
        df["o"] = df["h"] = df["l"] = df["c"] = c
    return n2, e2


def variante_m2(lb, k):
    def fn(es):
        o, h, l, c = (es[x].to_numpy(float) for x in "ohlc")
        hh, ses = es.hhmm.to_numpy(), es.sesion.to_numpy(); idx = np.arange(len(es)); filas = []
        t0, t1 = (1549, 1552) if lb == 3 else (1550, 1551)
        for s in pd.unique(ses):
            ii = idx[ses == s]; hm = hh[ii]
            a, j, f = ii[hm == t0], ii[hm == t1], ii[hm == 1559]
            if not (len(a) and len(j) and len(f)):
                continue
            j = j[0]; dd = np.sign(c[j] - c[a[0]])
            if dd == 0 or j + 1 > f[0]:
                continue
            filas.append(dict(i_ent=j + 1, precio=c[j], dir=int(dd), riesgo=c[j] * k / 100, i_fin=f[0], obj=1.0, coste=0.65))
        return es, pd.DataFrame(filas)
    return fn


if __name__ == "__main__":
    anios = mina.DISENO if "validacion" not in sys.argv else mina.VALIDACION
    if "m1" in sys.argv or len(sys.argv) == 1:
        D = {a: datos_par(a) for a in anios}
        V = {f"{m} k={k} desde {i}": variante_m1(m, k, i) for m in ("REV", "CONT") for k in (1.5, 2.0, 2.5) for i in (1000, 1200)}
        mina.evaluar("M1 valor relativo NQ-ES", V, mina.r_obj, D, nulo_par, semillas=12)
    if "m2" in sys.argv or len(sys.argv) == 1:
        E = {a: loader.cargar_cfd([loader.RAIZ / f"data/es_cfd_{a}.csv.gz"], verbose=False) for a in anios}
        V2 = {f"L{lb} k={k}%": variante_m2(lb, k) for lb in (3, 1) for k in (0.05, 0.10)}
        mina.evaluar("M2 MOC 15:50 en ES", V2, mina.r_obj, E, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
