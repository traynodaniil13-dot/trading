"""Carga de precios. Punto único de entrada (CLAUDE.md, secciones 2 y 10).

Convenciones del DataFrame devuelto:
- Índice = INICIO de la vela, hora de Nueva York sin tz. El CSV de origen etiqueta
  el FIN de la vela (bug nº10): aquí se resta un minuto, siempre.
- Una vela M1 con índice t se conoce entera en t + 1 min.
- `sesion` = fecha de la sesión de futuros (empieza a las 18:00 del día anterior).
  Cualquier "primera barra de X" tiene que filtrar por `sesion` Y por `hhmm`
  (bug nº6).
- `hhmm` = hora del inicio de la vela como entero (930 = 09:30).

Si algún chequeo falla, la carga lanza excepción. No hay modo "cargar igualmente".
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CSV_NQ = RAIZ / "data" / "nq_1min_2022_2025.csv"

COSTE_PTS = 0.87  # por operación, ida y vuelta (CLAUDE.md sección 2)


class DatosInvalidos(Exception):
    pass


def _leer_csv(ruta: Path, fin_de_vela: bool) -> pd.DataFrame:
    df = pd.read_csv(ruta, parse_dates=["ts"])
    df = df.rename(columns=str.lower)
    faltan = {"ts", "o", "h", "l", "c"} - set(df.columns)
    if faltan:
        raise DatosInvalidos(f"Faltan columnas: {faltan}")
    if fin_de_vela:
        df["ts"] = df["ts"] - pd.Timedelta(minutes=1)
    return df.set_index("ts")


def minutos_mas_volatiles(df: pd.DataFrame, n: int = 3, estad: str = "median") -> pd.Series:
    """Rango (h-l) por minuto del día, ordenado de mayor a menor.

    Mediana por defecto: con la media, los días de IPC de 2023-2024 ponen las
    08:30 por encima de las 09:30 (también en el futuro NQ) y el chequeo da una
    falsa alarma. La mediana sigue detectando el desfase de un minuto."""
    rango = (df["h"] - df["l"]).groupby(df.index.strftime("%H:%M")).agg(estad)
    return rango.sort_values(ascending=False).head(n)


def histograma_por_hora(df: pd.DataFrame) -> pd.Series:
    return df.index.hour.value_counts().sort_index()


def chequear(df: pd.DataFrame) -> dict:
    """Los controles obligatorios de la sección 2. Lanza DatosInvalidos si falla alguno."""
    errores = []

    dup = int(df.index.duplicated().sum())
    if dup:
        errores.append(f"{dup} timestamps duplicados")
    if not df.index.is_monotonic_increasing:
        errores.append("índice no ordenado")
    if df[["o", "h", "l", "c"]].isna().any().any():
        errores.append("hay NaN en OHLC")
    malas = int(((df["h"] < df[["o", "c"]].max(axis=1)) | (df["l"] > df[["o", "c"]].min(axis=1))).sum())
    if malas:
        errores.append(f"{malas} velas con h/l incoherentes")

    # 1. Desfase de un minuto: el 09:30 tiene que estar entre los 3 minutos más
    #    volátiles (mediana) Y ser más volátil que el 09:29 y el 09:31. En NQ es
    #    el primero; en ES el 15:50 (desequilibrio MOC) puede ganarle, y es real.
    top = minutos_mas_volatiles(df)
    todos = minutos_mas_volatiles(df, n=24 * 60)
    pico = all(todos.get("09:30", 0) > todos.get(m, 0) for m in ("09:29", "09:31"))
    if "09:30" not in top.index or not pico:
        errores.append(
            f"09:30 no es el pico de la apertura (top3 {top.round(2).to_dict()}; "
            f"09:29 {todos.get('09:29', 0):.2f} · 09:30 {todos.get('09:30', 0):.2f} · "
            f"09:31 {todos.get('09:31', 0):.2f}). ¿Timestamps de fin de vela?"
        )

    # 2. Histograma por hora: la parada del CME (17:00-18:00 NY) tiene que estar
    #    vacía en verano Y en invierno. Si se desplaza con el cambio de hora, el
    #    fichero está en UTC u otro huso.
    for nombre, meses in (("verano", [6, 7, 8]), ("invierno", [12, 1, 2])):
        sub = df[df.index.month.isin(meses)]
        if len(sub) == 0:
            continue
        h = histograma_por_hora(sub)
        tipico = h.median()
        vacias = [int(x) for x in h.index if h[x] < 0.05 * tipico]
        vacias += [x for x in range(24) if x not in h.index]
        if sorted(set(vacias)) != [17]:
            errores.append(f"{nombre}: horas vacías {sorted(set(vacias))}, se esperaba solo [17]")

    if errores:
        raise DatosInvalidos("; ".join(errores))

    return {
        "filas": len(df),
        "desde": df.index[0],
        "hasta": df.index[-1],
        "top_minutos": top.round(2).to_dict(),
        "duplicados": dup,
    }


def _anadir_columnas(df: pd.DataFrame) -> pd.DataFrame:
    idx = df.index
    # 18:00 + 6h = 00:00 del día siguiente -> la sesión que abre el domingo 18:00 es la del lunes.
    df["sesion"] = (idx + pd.Timedelta(hours=6)).normalize()
    df["hhmm"] = (idx.hour * 100 + idx.minute).astype(np.int16)
    return df


def cargar(ruta: Path | str = CSV_NQ, fin_de_vela: bool = True, verbose: bool = True) -> pd.DataFrame:
    """Carga un CSV M1 con columnas ts,o,h,l,c[,v], corrige y chequea.

    `fin_de_vela=True` porque el CSV de NQ etiqueta el fin de la vela. Para otro
    fichero, si no se sabe, déjalo en True: si está mal, el chequeo del 09:30 salta.
    """
    ruta = Path(ruta)
    cache = ruta.with_suffix(f".{int(fin_de_vela)}.pkl")
    if cache.exists() and cache.stat().st_mtime > ruta.stat().st_mtime:
        df = pd.read_pickle(cache)
    else:
        df = _leer_csv(ruta, fin_de_vela)
        df = _anadir_columnas(df)
        df.to_pickle(cache)

    info = chequear(df)
    if verbose:
        print(
            f"[loader] {ruta.name}: {info['filas']:,} filas, {info['desde']} -> {info['hasta']}. "
            f"Top minutos {info['top_minutos']}. Duplicados {info['duplicados']}. OK"
        )
    return df


CFD_DUKAS = sorted((RAIZ / "data").glob("nq_cfd_*.csv.gz"))


def cargar_cfd(rutas=None, verbose: bool = True) -> pd.DataFrame:
    """CFD USATECHIDXUSD de Dukascopy (índice Nasdaq 100 de contado, no el futuro).

    - timestamp en ms UTC, etiqueta el INICIO de la vela (comprobado: 09:30 es el
      minuto más volátil sin desplazar). Se pasa a hora de Nueva York.
    - Precio = medio entre bid y ask. El diferencial mediano es ~1,2-1,4 pts.
    - Cierra a las 16:15 NY; la hora 17 está vacía como en el futuro.
    - Ojo: nivel distinto al futuro (base) y apertura de contado más brusca.
    """
    rutas = [Path(r) for r in (rutas or CFD_DUKAS)]
    if not rutas:
        raise DatosInvalidos("no hay data/nq_cfd_*.csv.gz")
    raw = pd.concat([pd.read_csv(r) for r in rutas], ignore_index=True)
    ts = (pd.to_datetime(raw["timestamp"], unit="ms", utc=True)
          .dt.tz_convert("America/New_York").dt.tz_localize(None))
    df = pd.DataFrame({k: (raw[f"{n}_bid"] + raw[f"{n}_ask"]).to_numpy() / 2
                       for k, n in (("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"))},
                      index=pd.DatetimeIndex(ts, name="ts"))
    df["h"] = df[["o", "h", "c"]].max(axis=1)
    df["l"] = df[["o", "l", "c"]].min(axis=1)
    df = df.sort_index()
    df = _anadir_columnas(df)
    info = chequear(df)
    if verbose:
        print(f"[loader] CFD Dukascopy {[r.name for r in rutas]}: {info['filas']:,} filas, "
              f"{info['desde']} -> {info['hasta']}. Top minutos {info['top_minutos']}. OK")
    return df


if __name__ == "__main__":
    df = cargar()
    print(histograma_por_hora(df).to_string())


# ---------------------------------------------------------------- oro (XAUUSD Dukascopy)

def chequear_oro(df: pd.DataFrame) -> dict:
    """Controles de la sección 2 adaptados al oro. Los minutos de evento del oro son
    08:20 (apertura COMEX), 08:30 (macro EE. UU.), 09:30 (apertura de acciones) y
    10:00 (macro / fixing PM); en plata además 08:25 y 13:24 (apertura y cierre
    del corro de la plata en COMEX). Según el año gana uno u otro (2011: 08:20), así que
    se exige: el minuto nº1 por media es uno de esos 4, y los dos minutos macro
    (08:30 y 10:00) son más volátiles que su minuto anterior y su siguiente (la
    09:30 no se exige: en 2018 la apertura de acciones apenas mueve el oro). Si
    los picos salen un minuto después (08:31, 10:01), los timestamps son de fin
    de vela."""
    errores = []
    if df.index.duplicated().any():
        errores.append(f"{int(df.index.duplicated().sum())} timestamps duplicados")
    if df[["o", "h", "l", "c"]].isna().any().any():
        errores.append("hay NaN en OHLC")
    eventos = {"08:20": ("08:19", "08:21"), "08:25": ("08:24", "08:26"), "13:24": ("13:23", "13:25"),
               "08:30": ("08:29", "08:31"),
               "09:30": ("09:29", "09:31"), "10:00": ("09:59", "10:01")}
    top = minutos_mas_volatiles(df, n=3, estad="mean")
    todos = minutos_mas_volatiles(df, n=24 * 60, estad="mean")
    if top.index[0] not in eventos:
        errores.append(f"el minuto más volátil no es de evento: {top.round(3).to_dict()}")
    for m, (a, z) in ((k, eventos[k]) for k in ("08:30", "10:00")):
        if not (todos[m] > todos.get(a, 0) and todos[m] > todos.get(z, 0)):
            errores.append(f"{m} no es pico local ({a} {todos.get(a, 0):.3f} · {m} {todos[m]:.3f} · {z} {todos.get(z, 0):.3f})")
    if errores:
        raise DatosInvalidos("; ".join(errores))
    return {"filas": len(df), "desde": df.index[0], "hasta": df.index[-1], "top_minutos": top.round(3).to_dict()}


def cargar_oro(anios, verbose: bool = True) -> pd.DataFrame:
    """XAUUSD de Dukascopy (oro de contado), medio bid/ask, ms UTC, etiqueta el INICIO
    del minuto. Se pasa a hora de Nueva York. Ficheros data/oro_YYYY.csv.gz."""
    raw = pd.concat([pd.read_csv(RAIZ / f"data/oro_{a}.csv.gz") for a in anios], ignore_index=True)
    ts = (pd.to_datetime(raw["timestamp"], unit="ms", utc=True)
          .dt.tz_convert("America/New_York").dt.tz_localize(None))
    df = pd.DataFrame({k: raw[k].to_numpy() for k in ("o", "h", "l", "c", "spr")}, index=pd.DatetimeIndex(ts, name="ts"))
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]  # el cambio de hora no duplica en UTC; por si acaso
    df = _anadir_columnas(df)
    info = chequear_oro(df)
    if verbose:
        print(f"[loader] oro {list(anios)}: {info['filas']:,} filas, {info['desde']} -> {info['hasta']}. Top {info['top_minutos']}. OK")
    return df


def cargar_dukas(nombre: str, anios, verbose: bool = True) -> pd.DataFrame:
    """Cualquier instrumento convertido con scripts/oro_ticks_a_m1.py (data/<nombre>_YYYY.csv.gz):
    plata, eurusd... Mismo formato y mismos controles que el oro (picos de 08:30 y 10:00)."""
    raw = pd.concat([pd.read_csv(RAIZ / f"data/{nombre}_{a}.csv.gz") for a in anios], ignore_index=True)
    ts = (pd.to_datetime(raw["timestamp"], unit="ms", utc=True)
          .dt.tz_convert("America/New_York").dt.tz_localize(None))
    df = pd.DataFrame({k: raw[k].to_numpy() for k in ("o", "h", "l", "c", "spr")}, index=pd.DatetimeIndex(ts, name="ts"))
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = _anadir_columnas(df)
    info = chequear_oro(df)
    if verbose:
        print(f"[loader] {nombre} {list(anios)}: {info['filas']:,} filas, {info['desde']} -> {info['hasta']}. Top {info['top_minutos']}. OK")
    return df
