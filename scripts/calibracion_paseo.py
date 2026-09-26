"""Control 0: un motor sobre N semillas de paseo aleatorio. Normal e invertida
tienen que salir ~ -coste/R. Uso: python -m scripts.calibracion_paseo [semillas]"""
import sys

import numpy as np
import pandas as pd

from src import controles as C
from src import loader, motor
from src.motores import momento_0940 as M

semillas = int(sys.argv[1]) if len(sys.argv) > 1 else 24
real = loader.cargar()
print("generador:", C.chequear_generador(C.paseo_aleatorio(real, 0)))
filas = []
for s in range(semillas):
    rw = C.paseo_aleatorio(real, s)
    inv = C.invertida(motor.simular(rw, M.senales(rw)), 2)
    filas.append((s, inv["normal"], inv["invertida"], inv["suma"]))
df = pd.DataFrame(filas, columns=["semilla", "normal", "invertida", "suma"]).set_index("semilla")
print(df.round(4).to_string())
print("media", df.mean().round(4).to_dict(), "ee", (df.std(ddof=1) / np.sqrt(len(df))).round(4).to_dict(),
      "coste/R", round(-loader.COSTE_PTS / 30, 4))
