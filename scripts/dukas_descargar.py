"""Descarga velas M1 BID y ASK de datafeed.dukascopy.com y las convierte al formato de
data/oro_YYYY.csv.gz: timestamp (ms UTC, INICIO del minuto), o, h, l, c, spr, n.

Se usan los ficheros diarios de velas (YYYY/MM-1/DD/{BID,ASK}_candles_min_1.bi5), no los
de ticks: el servidor limita a pocas peticiones por segundo y los ticks son 24 ficheros por
día (inviable). Diferencias con el formato hecho desde ticks (oro 2011-2018):
- o/c medios exactos ((bid+ask)/2); h/l = media de los extremos bid y ask (el extremo del
  medio puede ser algo menor: diferencia de orden del spread/2, irrelevante para G4).
- spr = ask_c − bid_c (spread al cierre del minuto), no la mediana de los ticks.
- n = volumen BID+ASK del minuto (unidades Dukascopy), no el nº de ticks.
- Los minutos sin volumen (mercado cerrado: Dukascopy rellena el día entero) se descartan.

Caché de ficheros crudos en CACHE (reanudable). Uso:
  python -m scripts.dukas_descargar XAUUSD 2019 2026 data/oro [escala=1000] [hasta=2026-09-30]
Variables: DUKAS_CACHE (carpeta de crudos), DUKAS_HILOS (12), DUKAS_SOLO_BAJAR=1 (no convierte).
Los sábados no se piden (el oro no cotiza; Dukascopy los da vacíos).
"""
import lzma, os, sys, time, random, collections, datetime as dt
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd

INSTR, A0, A1, PREFIJO = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
ESCALA = float(sys.argv[5]) if len(sys.argv) > 5 else 1000.0
HASTA = dt.date.fromisoformat(sys.argv[6]) if len(sys.argv) > 6 else dt.date(2026, 9, 30)
CACHE = os.environ.get("DUKAS_CACHE", "/tmp/dukas_cache")
URL = "https://datafeed.dukascopy.com/datafeed/{i}/{y:04d}/{m:02d}/{d:02d}/{s}_candles_min_1.bi5"
REC = np.dtype([("t", ">i4"), ("o", ">i4"), ("c", ">i4"), ("l", ">i4"), ("h", ">i4"), ("v", ">f4")])

CODIGOS = collections.Counter()
ESPERA_MAX = float(os.environ.get("DUKAS_ESPERA_MAX", 8))
UA = {"User-Agent": "Mozilla/5.0"}   # con el UA de Python el servidor responde casi siempre 429


def ruta_de(dia, lado):
    return os.path.join(CACHE, INSTR, f"{dia:%Y%m%d}_{lado}.bi5")


def bajar(dia, lado):
    """Devuelve los bytes crudos (b'' si el día no tiene datos). Reintenta 429/503/timeouts."""
    ruta = ruta_de(dia, lado)
    if os.path.exists(ruta):
        return open(ruta, "rb").read()
    url = URL.format(i=INSTR, y=dia.year, m=dia.month - 1, d=dia.day, s=lado)
    espera = 1.0
    for intento in range(1000):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                datos = r.read()
            CODIGOS[200] += 1
            break
        except urllib.error.HTTPError as e:
            CODIGOS[e.code] += 1
            if e.code == 404:
                datos = b""; break
        except Exception as e:
            CODIGOS[type(e).__name__] += 1
        time.sleep(espera * random.uniform(0.5, 1.5)); espera = min(ESPERA_MAX, espera * 1.5)
    else:
        raise RuntimeError(f"no se pudo bajar {url}")
    if datos:
        lzma.decompress(datos)   # comprueba que no llegó truncado
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta + ".tmp", "wb") as f:
        f.write(datos)
    os.replace(ruta + ".tmp", ruta)
    return datos


def dias(y):
    d, fin = dt.date(y, 1, 1), min(dt.date(y, 12, 31), HASTA)
    while d <= fin:
        if d.weekday() != 5:
            yield d
        d += dt.timedelta(days=1)


def bajar_todo():
    pend = [(d, l) for y in range(A0, A1 + 1) for d in dias(y) for l in ("BID", "ASK")
            if not os.path.exists(ruta_de(d, l))]
    print(f"{INSTR}: {len(pend)} ficheros pendientes", flush=True)
    hechos, t0 = 0, time.time()
    with ThreadPoolExecutor(int(os.environ.get("DUKAS_HILOS", 12))) as ex:
        for _ in ex.map(lambda x: bajar(*x), pend):
            hechos += 1
            if hechos % 25 == 0:
                print(f"  {hechos}/{len(pend)} · {hechos / (time.time() - t0) * 60:.1f}/min · {dict(CODIGOS)}", flush=True)


def velas(dia, lado):
    crudo = bajar(dia, lado)
    if not crudo:
        return None
    a = np.frombuffer(lzma.decompress(crudo), dtype=REC)
    base = int(dt.datetime(dia.year, dia.month, dia.day, tzinfo=dt.timezone.utc).timestamp()) * 1000
    df = pd.DataFrame({k: a[k].astype(float) / ESCALA for k in ("o", "h", "l", "c")})
    df["v"] = a["v"].astype(float)
    df.index = base + a["t"].astype(np.int64) * 1000
    return df


def un_anio(y):
    partes = []
    for d in dias(y):
        b, k = velas(d, "BID"), velas(d, "ASK")
        if b is not None and k is not None:
            j = b.join(k, lsuffix="_b", rsuffix="_a", how="inner")
            j = j[(j.v_b > 0) | (j.v_a > 0)]
            if len(j):
                partes.append(pd.DataFrame({
                    "timestamp": j.index.to_numpy(),
                    "o": (j.o_b + j.o_a) / 2, "h": (j.h_b + j.h_a) / 2,
                    "l": (j.l_b + j.l_a) / 2, "c": (j.c_b + j.c_a) / 2,
                    "spr": j.c_a - j.c_b, "n": (j.v_b + j.v_a).round(4)}))
    df = pd.concat(partes, ignore_index=True).sort_values("timestamp")
    assert not df.timestamp.duplicated().any()
    assert (df.h >= df[["o", "c"]].max(axis=1) - 1e-9).all() and (df.l <= df[["o", "c"]].min(axis=1) + 1e-9).all()
    salida = f"{PREFIJO}_{y}.csv.gz"
    df.to_csv(salida, index=False, compression="gzip")
    print(f"{salida}: {len(df):,} velas · {pd.to_datetime(df.timestamp.iloc[0], unit='ms')} -> "
          f"{pd.to_datetime(df.timestamp.iloc[-1], unit='ms')}", flush=True)


if __name__ == "__main__":
    bajar_todo()
    if os.environ.get("DUKAS_SOLO_BAJAR") != "1":
        for y in range(A0, A1 + 1):
            un_anio(y)
