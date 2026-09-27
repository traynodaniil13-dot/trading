import numpy as np
import pandas as pd
import pytest

from src import controles as C
from src import loader, motor

pytestmark = pytest.mark.skipif(not loader.CSV_NQ.exists(), reason="falta el CSV")


@pytest.fixture(scope="module")
def real():
    return loader.cargar(verbose=False)


@pytest.fixture(scope="module")
def rw(real):
    return C.paseo_aleatorio(real, 123)


def test_generador_misma_rejilla_y_rango(real, rw):
    assert (rw.index == real.index).all()
    assert abs((rw.h - rw.l).mean() / (real.h - real.l).mean() - 1) < 0.03
    assert set(loader.minutos_mas_volatiles(rw, estad="mean").index) == {"08:30", "09:30", "10:00"}


def test_generador_50_50(rw):
    r = C.chequear_generador(rw, n=5000, x_pts=20)
    assert abs(r["pct_arriba"] - 0.5) < 0.025


def test_motor_sin_sesgo_en_paseo(rw):
    """Entradas y direcciones al azar, coste cero: la R bruta tiene que ser ~0 a
    1:1 y a 1:2 en las DOS direcciones. Sin el puente browniano salía +0,015R."""
    rng = np.random.default_rng(7)
    pos = pd.DataFrame({"ses": rw.sesion.to_numpy(), "hh": rw.hhmm.to_numpy(), "i": np.arange(len(rw))})
    rth = pos[(pos.hh >= 930) & (pos.hh < 1600)]
    fin = rth.groupby("ses").i.max()
    cand = rth[(rth.hh >= 941) & (rth.hh <= 1400)].sample(20_000, random_state=1)
    ops = pd.DataFrame({"i_ent": cand.i.values, "precio": rw.o.values[cand.i.values],
                        "dir": rng.choice([-1, 1], len(cand)), "riesgo": 30.0,
                        "i_fin": fin.reindex(cand.ses).values})
    ops = motor.simular(rw, ops)
    for ratio in (1, 2):
        for inv in (False, True):
            assert abs(motor.r_neta(ops, ratio, inv, coste=0).mean()) < 0.02


def test_motor_vela_entrada_solo_adverso():
    idx = pd.date_range("2024-01-02 09:30", periods=4, freq="min")
    b = pd.DataFrame({"o": [100, 100, 100, 100], "h": [200, 101, 101, 101],
                      "l": [99, 99, 99, 99], "c": [100, 100, 100, 100]}, index=idx)
    ops = motor.simular(b, pd.DataFrame({"i_ent": [0], "precio": [100.0], "dir": [1], "riesgo": [10.0], "i_fin": [3]}))
    assert ops.rmax[0] == pytest.approx(0.1)  # el +100 de la barra de entrada no cuenta
    ops2 = motor.simular(b, pd.DataFrame({"i_ent": [0], "precio": [100.0], "dir": [1], "riesgo": [10.0], "i_fin": [3]}),
                         adverso_primera=False)
    assert ops2.rmax[0] == pytest.approx(10.0)


def test_motor_stop_y_objetivo_misma_barra_gana_stop():
    idx = pd.date_range("2024-01-02 09:30", periods=3, freq="min")
    b = pd.DataFrame({"o": [100, 100, 100], "h": [100, 150, 100], "l": [100, 80, 100], "c": [100, 100, 100]}, index=idx)
    ops = motor.simular(b, pd.DataFrame({"i_ent": [0], "precio": [100.0], "dir": [1], "riesgo": [10.0], "i_fin": [2]}))
    assert ops.toco_sl[0] and ops.rmax[0] == 0
