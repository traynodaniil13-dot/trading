"""Regla J: moneda al aire (expectancy cero) -> ~2,09 de 10 según CLAUDE.md."""
import numpy as np
from src import cuentas as K
rng = np.random.default_rng(0)
N = 200_000
for nombre, ratio, p in (("1:1 al 50%", 1.0, 0.5), ("1:2 al 33,3%", 2.0, 1 / 3)):
    gana = rng.random(N) < p
    r = np.where(gana, ratio, -1.0)
    for mae_gan, et in ((0.0, "sin MAE en ganadoras"), (None, "MAE uniforme en ganadoras")):
        mae = np.where(gana, rng.random(N) if mae_gan is None else 0.0, 1.0)
        pts = np.full(N, 25.0)  # stop 25 pts -> $500 = 10 micros
        for riesgo in (250, 500, 833):
            m = K.montecarlo(r, mae, pts, riesgo_eval=riesgo, riesgo_fund=riesgo, n=4000)
            print(f"{nombre:12s} {et:26s} riesgo ${riesgo}: pasa {m['pase_de_10']:.2f}/10 · cobra {m['cobran_de_10']:.2f}/10 · "
                  f"cobro medio por evaluación ${m['cobro_medio_por_eval']:.0f}")
