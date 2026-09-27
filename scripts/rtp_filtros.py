"""Ejecuta preregistros/2026-09-27_rtp_filtros.md. No cambiar umbrales."""
import numpy as np
import pandas as pd

from src import controles as C
from src import loader, motor
from src.motores import rtp

SIN_OBJ = 1e9


def por_sesion(b):
    """Datos diarios causales: caja, cierre 15:59, cierre 08:59, momento, proxy macro."""
    hh, ses = b["hhmm"].to_numpy(), b["sesion"].to_numpy()
    d = pd.DataFrame({"ses": ses, "hh": hh, "h": b.h.values, "l": b.l.values, "c": b.c.values})
    caja = d[(d.hh >= 600) & (d.hh <= 859)].groupby("ses").agg(top=("h", "max"), bot=("l", "min"))
    out = pd.DataFrame({"caja": caja.top - caja.bot})
    pick = lambda t: d[d.hh == t].groupby("ses").c.first()
    out["c859"], out["c1559"], out["c940"], out["c910"] = pick(859), pick(1559), pick(940), pick(910)
    rng = (d.h - d.l)
    r830 = rng[d.hh == 830].groupby(d.ses[d.hh == 830]).first()
    pre = d[(d.hh >= 820) & (d.hh <= 829)]
    base = (pre.h - pre.l).groupby(pre.ses).median()
    r830, base = r830.align(base, join="inner")
    out["macro"] = (r830 > 3 * base).reindex(out.index)
    out = out.sort_index()
    out["caja_med20"] = out["caja"].shift(1).rolling(20, min_periods=20).median()
    out["c1559_prev"] = out["c1559"].shift(1)
    return out


def filtros(b, ops):
    s = por_sesion(b).reindex(ops["sesion"].to_numpy())
    hh = b["hhmm"].to_numpy()
    h_barr = hh[ops["i_barrido"].to_numpy()]
    h_rell = hh[ops["i_ent"].to_numpy() - 1]
    d = ops["dir"].to_numpy()
    sesgo = np.sign(s["c859"].to_numpy() - s["c1559_prev"].to_numpy())
    mom = np.sign(s["c940"].to_numpy() - s["c910"].to_numpy())
    med = s["caja_med20"].to_numpy()
    macro = s["macro"].to_numpy(dtype=float)
    ratio = ops["riesgo_pts"].to_numpy() / ops["caja"].to_numpy()
    valid_med = ~np.isnan(med)
    return {
        "BASE": np.ones(len(ops), bool),
        "F1_caja_peq": valid_med & (ops["caja"].to_numpy() < np.nan_to_num(med, nan=-1)),
        "F2_caja_grande": valid_med & (ops["caja"].to_numpy() >= np.nan_to_num(med, nan=1e9)),
        "F3_barr_pre930": h_barr < 930,
        "F4_barr_post930": h_barr >= 930,
        "F5_con_sesgo": d == sesgo,
        "F6_contra_sesgo": d == -sesgo,
        "F7_fusion_momento": (h_rell >= 940) & (d == mom),
        "F8_macro": macro == 1,
        "F9_no_macro": macro == 0,
        "F10_barr_corto": ratio < 0.70,
        "F11_barr_largo": ratio >= 0.70,
    }


def familia(b):
    ops = motor.simular(b, rtp.senales(b))
    return {k: ops[m].reset_index(drop=True) for k, m in filtros(b, ops).items()}


if __name__ == "__main__":
    real = loader.cargar()
    fam = familia(real)
    filas = {}
    for k, o in fam.items():
        r = motor.r_neta(o, SIN_OBJ)
        res = C.resumen(r)
        anio = pd.Series(r).groupby(o["t_ent"].dt.year.to_numpy()).mean()
        filas[k] = {"n": res["n"], "R": res["R"], "ee": res["ee"], "p": res["p_1cola"],
                    "inv": motor.r_neta(o, SIN_OBJ, True).mean(),
                    "2023": anio.get(2023, np.nan), "2024": anio.get(2024, np.nan), "2025": anio.get(2025, np.nan)}
    # nulo de paseo aleatorio, 6 semillas, misma celda
    nulos = {k: [] for k in fam}
    for sem in range(6):
        for k, o in familia(C.paseo_aleatorio(real, 1000 + sem)).items():
            nulos[k].append(motor.r_neta(o, SIN_OBJ).mean())
    for k in fam:
        v = np.array(nulos[k])
        filas[k]["R_paseo"] = v.mean()
        filas[k]["z_exc_paseo"] = C.z_exceso(filas[k]["R"], filas[k]["ee"], v.mean(), v.std(ddof=1) / np.sqrt(len(v)))
    tabla = pd.DataFrame(filas).T
    pl = C.placebo_direccion(fam, SIN_OBJ, reps=1000, semilla=1)
    pd.set_option("display.width", 200)
    print(tabla.astype(float).round(3).to_string())
    print(f"\nPlacebo de dirección (1000 reps, sorteo compartido): mejor={pl['mejor']} R={pl['R_mejor']:.3f} | "
          f"máx nulo {pl['max_nulo_media']:.3f} ± {pl['max_nulo_sd']:.3f} | {pl['sigmas']:.2f}σ | p={pl['p']:.3f}")
    print(f"Bonferroni: p umbral = {0.05/12:.4f}")
