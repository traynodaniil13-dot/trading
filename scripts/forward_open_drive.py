"""Forward test de OPEN_DRIVE (regla congelada: vela 09:30-09:34 con cuerpo > 80%, entrada al cierre de 09:34,
stop = rango (mín. 0,05%), TP 2R, cierre 15:59, coste 0,87). Días posteriores al último dato del backtest
(23/09/2026), que ninguna prueba ha visto. Se ejecuta de nuevo cada semana: reutiliza la caché.
Salida: resultados/forward_open_drive.csv (una fila por día con señal)."""
import lzma, struct, time, urllib.request
from datetime import date, datetime, timedelta, timezone
import numpy as np, pandas as pd
from src import loader

SIM = "USATECHIDXUSD"; CACHE = loader.RAIZ / "data/cache_dukascopy" / SIM
URL = "https://datafeed.dukascopy.com/datafeed/{s}/{y}/{m:02d}/{d:02d}/{lado}_candles_min_1.bi5"
DESDE = date(2026, 9, 24)


def bajar(dia, lado):
    f = CACHE / f"{dia.isoformat()}_{lado}.bi5"
    if f.exists():
        raw = f.read_bytes()
    else:
        raw = None
        for i in range(30):
            try:
                with urllib.request.urlopen(URL.format(s=SIM, y=dia.year, m=dia.month - 1, d=dia.day, lado=lado), timeout=30) as r:
                    raw = r.read()
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raw = b""; break
                time.sleep(10)
            except Exception:
                time.sleep(10)
        if raw is None:
            raise RuntimeError(f"no se pudo bajar {dia} {lado}")
        CACHE.mkdir(parents=True, exist_ok=True); f.write_bytes(raw); time.sleep(1)
    if not raw:
        return None
    d = lzma.decompress(raw); base = int(datetime(dia.year, dia.month, dia.day, tzinfo=timezone.utc).timestamp() * 1000)
    filas = [struct.unpack(">5if", d[i:i + 24]) for i in range(0, len(d), 24)]
    return pd.DataFrame([(base + t * 1000, o / 1000, h / 1000, l / 1000, c / 1000, v) for t, o, c, l, h, v in filas],
                        columns=["ts", "o", "h", "l", "c", "v"])


def datos():
    partes, dia, hoy = [], DESDE - timedelta(days=1), date.today()
    while dia < hoy:
        if dia.weekday() != 5:
            b, a = bajar(dia, "BID"), bajar(dia, "ASK")
            if b is not None and a is not None and len(b):
                m = b.merge(a, on="ts", suffixes=("_b", "_a")); m = m[(m.v_b > 0) | (m.v_a > 0)]
                partes.append(m)
        dia += timedelta(days=1)
    raw = pd.concat(partes)
    ts = pd.to_datetime(raw.ts, unit="ms", utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    df = pd.DataFrame({k: ((raw[f"{k}_b"] + raw[f"{k}_a"]) / 2).to_numpy() for k in "ohlc"}, index=pd.DatetimeIndex(ts))
    df["h"] = df[["o", "h", "c"]].max(axis=1); df["l"] = df[["o", "l", "c"]].min(axis=1)
    return loader._anadir_columnas(df.sort_index()[~df.index.duplicated()])


def main():
    df = datos(); o, h, l, c = (df[x].to_numpy() for x in "ohlc"); hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    idx = np.arange(len(df)); filas = []
    for s in pd.unique(ses):
        if pd.Timestamp(s).date() < DESDE:
            continue
        ii = idx[ses == s]; t = hm[ii]; v = ii[(t >= 930) & (t <= 934)]; f = ii[t == 1559]
        if len(v) != 5 or not len(f):
            continue
        rg = h[v].max() - l[v].min(); cu = c[v[-1]] - o[v[0]]
        cuerpo = abs(cu) / rg if rg > 0 else 0
        fila = dict(fecha=pd.Timestamp(s).date(), cuerpo=round(cuerpo, 3), senal=cuerpo > 0.8)
        if cuerpo > 0.8:
            d = int(np.sign(cu)); px = c[v[-1]]; r = max(rg, 0.0005 * px); sl, tp = px - d * r, px + 2 * d * r
            res = None
            for k in range(v[-1] + 1, f[0] + 1):
                if (d == 1 and l[k] <= sl) or (d == -1 and h[k] >= sl):
                    res = -1.0; break
                if k > v[-1] + 1 and ((d == 1 and h[k] >= tp) or (d == -1 and l[k] <= tp)):
                    res = 2.0; break
            if res is None:
                res = (c[f[0]] - px) * d / r
            fila.update(dir="LARGO" if d == 1 else "CORTO", entrada=round(px, 1), riesgo_pts=round(r, 1), R=round(res - 0.87 / r, 3))
        filas.append(fila)
    t = pd.DataFrame(filas); t.to_csv(loader.RAIZ / "resultados/forward_open_drive.csv", index=False)
    s = t[t.senal]
    print(f"Forward OPEN_DRIVE desde {DESDE}: {len(t)} sesiones, {len(s)} señales · R total {s.R.sum() if len(s) else 0:+.2f} · R medio {s.R.mean() if len(s) else float('nan'):+.3f}")
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()
