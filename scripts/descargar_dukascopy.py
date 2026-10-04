"""Descarga velas de 1 min BID/ASK de Dukascopy (datafeed público) y escribe
data/<prefijo>_<año>.csv.gz con el mismo formato que los CSV de Colab.
Uso: python -m scripts.descargar_dukascopy USATECHIDXUSD nq_cfd 2019 2020"""
import gzip, io, lzma, struct, sys, time, urllib.request
from datetime import date, datetime, timedelta, timezone
import pandas as pd
from src.loader import RAIZ

SIM, PREF, ANIOS = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3:]]
URL = "https://datafeed.dukascopy.com/datafeed/{s}/{y}/{m:02d}/{d:02d}/{lado}_candles_min_1.bi5"


CACHE = RAIZ / "data" / "cache_dukascopy" / SIM
CACHE.mkdir(parents=True, exist_ok=True)


def bajar(dia, lado):
    url = URL.format(s=SIM, y=dia.year, m=dia.month - 1, d=dia.day, lado=lado)
    f = CACHE / f"{dia.isoformat()}_{lado}.bi5"
    for intento in range(14):
        try:
            if f.exists():
                raw = f.read_bytes()
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    raw = r.read()
                f.write_bytes(raw)
                time.sleep(1.0)
            if not raw:
                return None
            d = lzma.decompress(raw)
            base = int(datetime(dia.year, dia.month, dia.day, tzinfo=timezone.utc).timestamp() * 1000)
            filas = [struct.unpack(">5if", d[i:i + 24]) for i in range(0, len(d), 24)]
            return pd.DataFrame([(base + t * 1000, o / 1000, h / 1000, l / 1000, c / 1000, v) for t, o, c, l, h, v in filas],
                                columns=["timestamp", "open", "high", "low", "close", "volume"])
        except urllib.error.HTTPError as e:
            if e.code == 404:
                f.write_bytes(b"")
                return None
            time.sleep(min(120, 2 ** intento))
        except Exception:
            time.sleep(min(120, 2 ** intento))
    raise RuntimeError(f"no se pudo bajar {url}")


for a in ANIOS:
    import os
    SOLO_BID, SIN_DIC = os.environ.get("SOLO_BID") == "1", os.environ.get("SIN_DIC") == "1"
    dia, fin, partes = (date(a, 1, 1) if SIN_DIC else date(a - 1, 12, 1)), date(a, 12, 31), []
    while dia <= fin:
        if dia.weekday() != 5:  # el sábado no hay mercado
            b = bajar(dia, "BID")
            k = b if SOLO_BID else bajar(dia, "ASK")  # SOLO_BID=1: medio = BID (mitad de peticiones)
            if b is not None and k is not None and len(b) and len(k):
                m = b.merge(k, on="timestamp", suffixes=("_bid", "_ask"))
                m = m[(m.volume_bid > 0) | (m.volume_ask > 0)]
                partes.append(m)
        dia += timedelta(days=1)
        if dia.day == 1:
            print(f"{a}: hasta {dia} · días con datos {len(partes)}", flush=True)
    df = pd.concat(partes, ignore_index=True).sort_values("timestamp").drop_duplicates("timestamp")
    out = RAIZ / "data" / f"{PREF}_{a}.csv.gz"
    df.to_csv(out, index=False, compression="gzip")
    print(f"escrito {out} · {len(df):,} filas", flush=True)
