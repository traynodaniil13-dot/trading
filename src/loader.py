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


def minutos_mas_volatiles(df: pd.DataFrame, n: int = 3) -> pd.Series:
    """Rango medio (h-l) por minuto del día, ordenado de mayor a menor."""
    rango = (df["h"] - df["l"]).groupby(df.index.strftime("%H:%M")).mean()
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

    # 1. El minuto más volátil tiene que ser el 09:30 clavado.
    top = minutos_mas_volatiles(df)
    if top.index[0] != "09:30":
        errores.append(
            f"minuto más volátil = {top.index[0]}, no 09:30 "
            f"(top3 {top.round(2).to_dict()}). ¿Timestamps de fin de vela?"
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


if __name__ == "__main__":
    df = cargar()
    print(histograma_por_hora(df).to_string())
