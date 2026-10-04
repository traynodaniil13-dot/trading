"""Mina M3: Momento de apertura en el oro. preregistros/2026-10-04_mina_tanda3_momento_oro.md"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader, mina

COSTE_ORO = 0.25  # $/oz por operación (MGC: comisión + 2 ticks)


def cargar_oro(a):
    raw = pd.read_csv(loader.RAIZ / f"data/xau_cfd_{a}.csv.gz")
    ts = pd.to_datetime(raw["timestamp"], unit="ms", utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    df = pd.DataFrame({k: (raw[f"{n}_bid"] + raw[f"{n}_ask"]).to_numpy() / 2
                       for k, n in (("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"))}, index=pd.DatetimeIndex(ts, name="ts"))
    df["h"] = df[["o", "h", "c"]].max(axis=1); df["l"] = df[["o", "l", "c"]].min(axis=1)
    df = loader._anadir_columnas(df.sort_index())
    # chequeos (sección 2 adaptada al oro)
    assert not df.index.duplicated().any(), "duplicados"
    todos = loader.minutos_mas_volatiles(df, n=24 * 60)
    assert todos["08:30"] > todos["08:29"] and todos["08:30"] > todos["08:31"], f"08:30 no es pico: {todos[['08:29','08:30','08:31']].to_dict()}"
    for meses in ([6, 7, 8], [12, 1, 2]):
        h = loader.histograma_por_hora(df[df.index.month.isin(meses)])
        vacias = sorted({int(x) for x in h.index if h[x] < 0.05 * h.median()} | {x for x in range(24) if x not in h.index})
        assert vacias == [17], f"horas vacías {vacias}"
    print(f"[oro {a}] {len(df):,} filas · top minutos {loader.minutos_mas_volatiles(df).round(3).to_dict()} · OK")
    return df


def variante(L, k, t=820, fin=1329):
    tm = (t // 100) * 60 + t % 100
    t_ref = (tm - 1 - L) // 60 * 100 + (tm - 1 - L) % 60
    t_sen = (tm - 1) // 60 * 100 + (tm - 1) % 60

    def fn(df):
        o, c = df.o.to_numpy(), df.c.to_numpy(); hh, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
        idx = np.arange(len(df)); filas = []
        for s in pd.unique(ses):
            ii = idx[ses == s]; hm = hh[ii]
            a, j, e, f = ii[hm == t_ref], ii[hm == t_sen], ii[hm == t], ii[hm == fin]
            if not (len(a) and len(j) and len(e) and len(f)):
                continue
            d = np.sign(c[j[0]] - c[a[0]])
            if d == 0:
                continue
            p = o[e[0]]
            filas.append(dict(i_ent=e[0], precio=p, dir=int(d), riesgo=p * k / 100, i_fin=f[0], obj=2.0, coste=COSTE_ORO))
        return df, pd.DataFrame(filas)
    return fn


if __name__ == "__main__":
    anios = mina.DISENO if "validacion" not in sys.argv else mina.VALIDACION
    D = {a: cargar_oro(a) for a in anios}
    V = {f"L{L} k={k}%": variante(L, k) for L in (15, 30, 60) for k in (0.20, 0.30, 0.40)}
    mina.evaluar("M3 Momento de apertura en el oro (08:20)", V, mina.r_obj, D, lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    print("\nInformativo (no decide): misma regla a las 09:30 y 09:40 NY, L30 k=0,30%")
    for t in (930, 940):
        o = mina.correr_variante(variante(30, 0.30, t=t, fin=1559), D)
        r = mina.r_obj(o); print(f"  {t}: n={len(o)} R={r.mean():+.4f} wr {(r>0).mean():.1%}")
