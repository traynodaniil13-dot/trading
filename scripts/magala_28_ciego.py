"""Magalá: réplica 2021-25 con 28 pares reales + reserva ciega 2018-2020. preregistros/2026-10-04_magala_28_pares_y_ciego.md"""
import numpy as np, pandas as pd
from src import controles as C
from scripts.magala_fuerza import cargar, fuerza, indicadores, senales, simular
from scripts.descargar_fx_diario import PARES

W = cargar(); ind = indicadores(W)
print(f"datos: {W['c'].shape[1]} pares · {W['c'].index[0].date()} → {W['c'].index[-1].date()}")


def prueba(nom, N, desde, hasta, decide=False, reps=200):
    rng = np.random.default_rng(N)
    sen = senales(fuerza(W, N), desde, hasta); o = simular(W, ind, sen)
    s = C.resumen(o.r.to_numpy()); inv = simular(W, ind, sen, invertir=True)
    py = o.groupby(o.fecha.dt.year).r.agg(["mean", "size"])
    azar = np.array([simular(W, ind, [(t, PARES[rng.integers(len(PARES))], int(rng.choice([-1, 1]))) for t, _, _ in sen]).r.mean()
                     for _ in range(reps)])
    print(f"\n=== {nom} N={N} ({desde[:4]}-{hasta[:4]}): n={s['n']} · wr {s['wr']:.1%} · R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · "
          f"invertida {inv.r.mean():+.4f} · duración mediana {o.dias.median():.0f} días")
    print("  por año: " + " · ".join(f"{y} {m:+.3f} (n={int(n)})" for y, (m, n) in py.iterrows()))
    print(f"  azar: media {azar.mean():+.4f} · p95 {np.percentile(azar, 95):+.4f} · p azar {(azar >= s['R']).mean():.3f}")
    if decide:
        ok = s["R"] > 0 and s["p_1cola"] < 0.05 and s["R"] > np.percentile(azar, 95) and inv.r.mean() <= 0 and (py["mean"] > 0).sum() >= 2
        print("  -> RESERVA CIEGA:", "PASA" if ok else "NO PASA")


prueba("Réplica (informativa)", 14, "2021-01-01", "2025-12-31")
prueba("Réplica (informativa)", 20, "2021-01-01", "2025-12-31")
prueba("RESERVA CIEGA (decide)", 14, "2018-01-01", "2020-12-31", decide=True)
prueba("Reserva ciega (informativa)", 20, "2018-01-01", "2020-12-31")
