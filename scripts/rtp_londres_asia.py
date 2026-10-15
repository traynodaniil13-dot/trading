"""RTP en las velas de 3h de Londres y Asia. preregistros/2026-10-15_rtp_londres_asia.md

Uso: python -m scripts.rtp_londres_asia
"""
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina
from src.motores import rtp
from scripts.mina_nq_tanda4 import COSTE, IMPARES, PARES


def variante(caja, desde, hasta):
    def fn(df):
        s = rtp.senales(df, caja=caja, desde=desde, hasta=hasta)
        if len(s) == 0:
            return df, s
        bot = s["mid"] - 0.5 * s["caja"]; top = s["mid"] + 0.5 * s["caja"]
        opuesto = np.where(s["dir"] == 1, top, bot)
        s["obj"] = (opuesto - s["precio"]) * s["dir"] / s["riesgo"]
        s = s[s["obj"] > 0].copy()   # relleno ya más allá del extremo opuesto: no hay recorrido
        s["coste"] = COSTE
        return df, s.reset_index(drop=True)
    return fn


FAMILIA = {
    "L Londres 03:00": variante((0, 259), 300, 559),
    "A Asia 21:00": variante((1800, 2059), 2100, 2359),
}
INFO_NY = variante((600, 859), 900, 1159)


def informe(o, etiqueta):
    r = mina.r_obj(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
    p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
    tp = (o["rmax"] >= o["obj"]).mean(); sl = (o["toco_sl"] & (o["rmax"] < o["obj"])).mean()
    print(f"  {etiqueta}: n={len(o)} R={r.mean():+.4f} p1c={p:.4f} wr {(r > 0).mean():.1%} · TP {tp:.1%} SL {sl:.1%} · "
          f"ratio mediano {o['obj'].median():.2f} · riesgo mediano {o['riesgo_pts'].median():.1f} pts · "
          f"inv {mina.r_obj(o, True).mean():+.4f} · años {py.round(3).to_dict()}")
    return r, py, p


if __name__ == "__main__":
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in IMPARES}
    tab, sup, ops = mina.evaluar("RTP Londres/Asia", FAMILIA, mina.r_obj, D,
                                 lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    print("\nDetalle diseño:")
    for v, o in ops.items():
        informe(o, v)
    print("\nInformativo (no decide): RTP NY 09:00 con TP en el extremo opuesto, mismos años:")
    informe(mina.correr_variante(INFO_NY, D), "NY 09:00")
    if sup:
        umbral = 0.05 / len(sup)
        print(f"\nVALIDACIÓN pares para {sup} (p < {umbral:.4f} y ≥3/4 años):")
        P = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in PARES}
        for v in sup:
            r, py, p = informe(mina.correr_variante(FAMILIA[v], P), v)
            print(f"    → {'PASA' if p < umbral and (py > 0).sum() >= 3 else 'NO PASA'}")
