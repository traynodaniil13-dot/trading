"""Convierte ticks Dukascopy de XAUUSD (repo FX-Data/FX-Data-XAUUSD-DS, una rama por año)
a velas M1 del precio medio bid/ask. Etiqueta = INICIO del minuto, en UTC (como el CFD del NQ).
Precio en el fichero = oro/100 → se multiplica por 100.
Uso: python -m scripts.oro_ticks_a_m1 <carpeta_XAUUSD_del_año> <salida.csv.gz>"""
import sys, glob, os
import numpy as np, pandas as pd
from concurrent.futures import ProcessPoolExecutor


def un_fichero(ruta):
    try:
        df = pd.read_csv(ruta, header=None, names=["t", "p1", "p2", "v1", "v2"])
    except pd.errors.EmptyDataError:
        return None
    if df.empty:
        return None
    ts = pd.to_datetime(df.t, format="%Y.%m.%d %H:%M:%S.%f")
    mid = (df.p1 + df.p2).to_numpy() * 50.0           # (a+b)/2 * 100
    spr = (df.p2 - df.p1).abs().to_numpy() * 100.0
    s = pd.DataFrame({"mid": mid, "spr": spr}, index=ts)
    g = s.mid.resample("1min", label="left", closed="left")   # agrupa por minuto natural: el label es el inicio, y se usa como tal
    out = pd.DataFrame({"o": g.first(), "h": g.max(), "l": g.min(), "c": g.last(),
                        "spr": s.spr.resample("1min", label="left", closed="left").median(),
                        "n": g.count()}).dropna()
    return out


if __name__ == "__main__":
    carpeta, salida = sys.argv[1], sys.argv[2]
    rutas = sorted(glob.glob(os.path.join(carpeta, "**", "*_ticks.csv"), recursive=True))
    with ProcessPoolExecutor() as ex:
        partes = [p for p in ex.map(un_fichero, rutas, chunksize=32) if p is not None]
    df = pd.concat(partes).sort_index()
    assert not df.index.duplicated().any(), "minutos duplicados entre ficheros horarios"
    df.insert(0, "timestamp", df.index.astype("datetime64[ns]").asi8 // 10**6)
    df.to_csv(salida, index=False, compression="gzip")
    print(f"{salida}: {len(df):,} velas {df.index[0]} -> {df.index[-1]} · ficheros {len(rutas)}")
