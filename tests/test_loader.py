import pandas as pd
import pytest

from src import loader

pytestmark = pytest.mark.skipif(not loader.CSV_NQ.exists(), reason="falta data/nq_1min_2022_2025.csv")


@pytest.fixture(scope="module")
def df():
    return loader.cargar(verbose=False)


def test_minuto_mas_volatil_0930(df):
    assert loader.minutos_mas_volatiles(df).index[0] == "09:30"


def test_sin_corregir_falla():
    with pytest.raises(loader.DatosInvalidos, match="09:30 no es el pico"):
        loader.cargar(fin_de_vela=False, verbose=False)


def test_primera_barra_es_1800(df):
    # El CSV empieza en 18:01 (fin de vela); corregido tiene que ser 18:00.
    assert df.index[0] == pd.Timestamp("2022-12-26 18:00")


def test_sesion_empieza_a_las_18(df):
    viernes = df[df.index.dayofweek == 4]
    assert (viernes["sesion"] == viernes.index.normalize()).all()
    domingo = df[df.index.dayofweek == 6]
    assert (domingo["sesion"] == domingo.index.normalize() + pd.Timedelta(days=1)).all()
    # Bug nº6: "primera barra con hhmm >= 930" de la sesión devuelve las 18:00.
    # Hace falta la segunda cota.
    s = df[df["sesion"] == pd.Timestamp("2024-03-05")]
    assert s[s["hhmm"] >= 930].index[0] == pd.Timestamp("2024-03-04 18:00")
    assert s[(s["hhmm"] >= 930) & (s["hhmm"] < 1700)].index[0] == pd.Timestamp("2024-03-05 09:30")
    assert s.index[0] == pd.Timestamp("2024-03-04 18:00")
