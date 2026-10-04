"""Velas diarias BID de Dukascopy para los 28 pares de las 8 divisas mayores, 2020-2026.
Uso: python -m scripts.descargar_fx_diario. Salida: data/fx_diario.csv.gz"""
import lzma, random, struct, sys, time, urllib.request
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "data/cache_dukascopy/fx_diario"
DIV = ["EUR", "GBP", "AUD", "NZD", "USD", "CAD", "CHF", "JPY"]  # orden de cotización estándar
PARES = [a + b for i, a in enumerate(DIV) for b in DIV[i + 1:]]


def bajar(par, anio):
    f = CACHE / f"{par}_{anio}.bi5"
    if f.exists():
        return f.read_bytes()
    url = f"https://datafeed.dukascopy.com/datafeed/{par}/{anio}/BID_candles_day_1.bi5"
    for intento in range(400):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                d = r.read()
            CACHE.mkdir(parents=True, exist_ok=True); f.write_bytes(d); time.sleep(1.5); return d
        except Exception as e:
            if getattr(e, "code", None) == 404:
                CACHE.mkdir(parents=True, exist_ok=True); f.write_bytes(b""); return b""
            time.sleep(15 + 15 * random.random())
    raise RuntimeError(f"no se pudo bajar {par} {anio}")


def bajar_horas(par, anio, mes):
    """Velas de 1 h de un mes (mes 0-11). El fichero diario del año en curso no existe todavía."""
    f = CACHE / f"{par}_{anio}_{mes:02d}_h.bi5"
    if f.exists():
        return f.read_bytes()
    url = f"https://datafeed.dukascopy.com/datafeed/{par}/{anio}/{mes:02d}/BID_candles_hour_1.bi5"
    for intento in range(400):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                d = r.read()
            CACHE.mkdir(parents=True, exist_ok=True); f.write_bytes(d); time.sleep(1.5); return d
        except Exception as e:
            if getattr(e, "code", None) == 404:
                CACHE.mkdir(parents=True, exist_ok=True); f.write_bytes(b""); return b""
            time.sleep(15 + 15 * random.random())
    raise RuntimeError(f"no se pudo bajar {par} {anio}-{mes}")


def diario_desde_horas(par, anio, esc):
    filas = []
    for mes in range(12):
        d = bajar_horas(par, anio, mes)
        if not d:
            continue
        d = lzma.decompress(d)
        ini = pd.Timestamp(anio, mes + 1, 1)
        for k in range(len(d) // 24):
            t, o, c, l, h, v = struct.unpack(">5if", d[24 * k:24 * k + 24])
            if v > 0:
                filas.append((ini + pd.Timedelta(seconds=t), o / esc, h / esc, l / esc, c / esc))
    if not filas:
        return []
    x = pd.DataFrame(filas, columns=["t", "o", "h", "l", "c"]).set_index("t")
    g = x.groupby(x.index.normalize())
    dd = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()})
    return [(par, f, r.o, r.h, r.l, r.c) for f, r in dd.iterrows()]


USD7 = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]


def main(pares=PARES, salida="fx_diario.csv.gz", anios=range(2020, 2027)):
    filas = []
    for par in pares:
        esc = 1000 if par.endswith("JPY") else 100000
        for anio in anios:
            d = bajar(par, anio)
            if not d:
                if anio == 2026 and "sin2026" not in sys.argv:
                    filas += diario_desde_horas(par, anio, esc)
                continue
            d = lzma.decompress(d)
            for k in range(len(d) // 24):
                t, o, c, l, h, v = struct.unpack(">5if", d[24 * k:24 * k + 24])
                if v <= 0:
                    continue  # días sin mercado (fines de semana / festivos)
                filas.append((par, pd.Timestamp(anio, 1, 1) + pd.Timedelta(seconds=t), o / esc, h / esc, l / esc, c / esc))
        print(par, "ok", flush=True)
    df = pd.DataFrame(filas, columns=["par", "fecha", "o", "h", "l", "c"])
    df.to_csv(RAIZ / f"data/{salida}", index=False)
    print("filas", len(df))


if __name__ == "__main__":
    import sys
    if "ciego" in sys.argv:  # primero lo que necesita la reserva ciega: 2017-2020 de los 28
        main(PARES, "fx_diario_2017_2020.csv.gz", range(2017, 2021))
    elif "reales" in sys.argv:  # los 28 pares reales, 2017-2025 (2017 de calentamiento)
        main(PARES, "fx_diario.csv.gz", range(2017, 2026))
    elif "usd" in sys.argv:  # plan B: solo los 7 pares contra el dólar, cruces sintéticos
        main(USD7, "fx_diario_usd.csv.gz")
    else:
        main()
