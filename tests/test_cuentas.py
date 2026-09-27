import numpy as np

from src import cuentas as K


def test_evaluacion_quema_con_dos_stops_de_500():
    r = np.array([-1.0, -1.0, 1.0]); mae = np.array([1.0, 1.0, 0.0]); pts = np.full(3, 25.0)
    ok, n = K.evaluacion(r, mae, pts, 500, K.Reglas())
    assert not ok and n == 2


def test_consistencia_impide_pasar_con_un_solo_dia():
    r = np.array([3.0, 0.1, 0.1]); mae = np.zeros(3); pts = np.full(3, 25.0)
    ok, _ = K.evaluacion(r, mae, pts, 500, K.Reglas())  # +1.500 en un día: > 50% del beneficio
    assert not ok


def test_moneda_al_aire_con_coste_no_cobra_mas_que_con_ventaja():
    rng = np.random.default_rng(0); N = 50_000; g = rng.random(N) < 0.5
    base = np.where(g, 1.0, -1.0) - 0.035; mae = np.where(g, 0.0, 1.0); pts = np.full(N, 25.0)
    cero = K.montecarlo(base, mae, pts, n=1500)["cobro_medio_por_eval"]
    ventaja = K.montecarlo(base + 0.2, mae, pts, n=1500)["cobro_medio_por_eval"]
    assert ventaja > cero
