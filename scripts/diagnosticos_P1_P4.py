import numpy as np, pandas as pd
from scipy import stats
from src import loader, premisas as P

def cfd_anio(a):
    return loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False)

def por_anio(fn, anios=(2021, 2025)):
    return pd.concat([fn(cfd_anio(a)).loc[lambda r: r.index.year == a] for a in anios])

def linea(nombre, y):
    y = np.asarray(y, float); t, p = stats.ttest_1samp(y, 0)
    return f"{nombre:28s} n={len(y):4d} media={y.mean():+6.2f} ee={y.std(ddof=1)/np.sqrt(len(y)):5.2f} p={p:.3f}"

# D1
def p1_con_tamano(b):
    g = P._rejilla(b, [959, 1530, 1559]); cp = g["c"][1559].shift(1)
    mov = (g["c"][959] - cp) / cp; s = np.sign(mov)
    df = pd.DataFrame({"s": s, "y": (g["c"][1559] - g["o"][1530]) * s, "tam": mov.abs()}).dropna()
    return df[df.s != 0]
d = por_anio(p1_con_tamano)
d["tercil"] = pd.qcut(d.tam, 3, labels=["pequeño", "medio", "grande"])
print("== D1 · P1 por tamaño del movimiento 10:00 ==")
for k, g in d.groupby("tercil", observed=True):
    print(linea(f"tercil {k} (|mov| {g.tam.min()*100:.2f}-{g.tam.max()*100:.2f}%)", g.y))

# D2 y D4: NQ vs CFD 2025
nq = loader.cargar(verbose=False)
nq25 = nq[nq.sesion.dt.year == 2025]; nq25 = nq[(nq.sesion >= "2024-12-01") & (nq.sesion <= "2025-12-11")]
c25 = cfd_anio(2025); c25 = c25[c25.sesion <= "2025-12-11"]
for nom, fn in (("P1", P.p1_momento_ultima_media_hora), ("P4", P.p4_primera_m5)):
    a = fn(nq25).loc[lambda r: r.index.year == 2025]; b = fn(c25).loc[lambda r: r.index.year == 2025]
    j = a.join(b, lsuffix="_nq", rsuffix="_cfd", how="inner")
    print(f"\n== {'D2' if nom=='P1' else 'D4'} · {nom} NQ vs CFD 2025 (hasta 11/12) ==")
    print(linea(f"{nom} NQ futuro", a.y)); print(linea(f"{nom} CFD", b.y))
    print(f"días en ambos {len(j)}, misma señal {(j.s_nq == j.s_cfd).mean():.0%}, corr y {np.corrcoef(j.y_nq, j.y_cfd)[0,1]:.2f}")

# D3
print("\n== D3 · P4 barrido de umbral de cuerpo (2021+2025, CFD) ==")
def p4_umbral(u):
    def f(b):
        g = P._rejilla(b, [930, 931, 932, 933, 934, 935, 1059]); cols = [930, 931, 932, 933, 934]
        cu = g["c"][934] - g["o"][930]; ra = g["h"][cols].max(axis=1) - g["l"][cols].min(axis=1)
        s = np.sign(cu).where(cu.abs() > u * ra)
        return P._fuera(s, (g["c"][1059] - g["o"][935]) * s)
    return f
for u in (0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
    r = por_anio(p4_umbral(u))
    print(linea(f"cuerpo > {u:.1f}", r.y), "| por año", r.groupby(r.index.year).y.mean().round(1).to_dict())

# D5
print("\n== D5 · signo por semestre ==")
for nom, fn in (("P1", P.p1_momento_ultima_media_hora), ("P4", P.p4_primera_m5)):
    r = por_anio(fn); sem = r.groupby([r.index.year, (r.index.month > 6).astype(int) + 1]).y.agg(["mean", "count"])
    print(nom, {f"{y}-S{h}": (round(m, 1), int(n)) for (y, h), (m, n) in sem.iterrows()})
