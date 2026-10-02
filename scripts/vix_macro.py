"""Ejecuta preregistros/2026-10-02_vix_macro.md. No cambiar nada.
Uso: python -m scripts.vix_macro [diseno|validacion]"""
import re, sys
import numpy as np, pandas as pd
from src import controles as C, loader, motor, premisas as P
from src.motores import momento_generico as MG

FASE = sys.argv[1] if len(sys.argv) > 1 else "diseno"
ANIOS = [2021, 2023, 2025] if FASE == "diseno" else [2022, 2024, 2026]
UMBRAL = 0.0125
PRIORIDAD = ["Core CPI m/m", "CPI m/m", "Non-Farm Employment Change", "Core PCE Price Index m/m",
             "Core Retail Sales m/m", "Core PPI m/m"]


def num(x):
    if not isinstance(x, str): return np.nan
    m = re.search(r"-?\d+(\.\d+)?", x.replace(",", ""))
    if not m: return np.nan
    v = float(m.group()); u = x.strip()[-1].upper()
    return v * {"K": 1e3, "M": 1e6, "B": 1e9}.get(u, 1)


# ---- VIX: cierre de AYER y de anteayer para cada fecha de sesión (solo días anteriores)
vix = pd.read_csv(loader.RAIZ / "data/vix_diario.csv.gz", parse_dates=["DATE"]).set_index("DATE").CLOSE.sort_index()
med60 = vix.rolling(60, min_periods=60).median().shift(1)          # mediana de los 60 cierres ANTERIORES a ese día


def vix_ayer(fechas):
    idx = vix.index.searchsorted(fechas, side="left") - 1             # último cierre estrictamente anterior
    ok = idx >= 1
    ay = np.where(ok, vix.to_numpy()[np.clip(idx, 0, None)], np.nan)
    an = np.where(ok, vix.to_numpy()[np.clip(idx - 1, 0, None)], np.nan)
    md = np.where(ok, med60.to_numpy()[np.clip(idx, 0, None)], np.nan)
    return ay, an, md


# ---- Macro: un evento de las 08:30 por día, con sorpresa y sorpresa normalizada causal
mac = pd.read_csv(loader.RAIZ / "data/macro_usd.csv.gz", parse_dates=["ts"])
mac = mac[mac.event.isin(PRIORIDAD) & (mac.ts.dt.strftime("%H:%M") == "08:30")].copy()
mac["sor"] = mac.actual.map(num) - mac.forecast.map(num)
mac = mac.dropna(subset=["sor"]).sort_values("ts")
mac["sd_prev"] = mac.groupby("event").sor.transform(lambda s: s.expanding(min_periods=6).std().shift(1))
mac["norm"] = mac.sor.abs() / mac.sd_prev
mac["prio"] = mac.event.map({e: i for i, e in enumerate(PRIORIDAD)})
mac["fecha"] = mac.ts.dt.normalize()
mac = mac.sort_values(["fecha", "prio"]).drop_duplicates("fecha").set_index("fecha")


def bps(ent, sal, s):
    return (sal - ent) / ent * 1e4 * s


def premisas(nq):
    g = P._rejilla(nq, [830, 831, 929, 930, 1559]); o, c = g["o"], g["c"]
    fechas = pd.DatetimeIndex(o.index)
    out = {}
    ay, an, _ = vix_ayer(fechas)
    dv = ay / an - 1
    s2 = pd.Series(np.where(np.abs(dv) > 0.10, np.sign(dv), np.nan), index=o.index)
    out["V2"] = pd.DataFrame({"s": s2, "y": bps(o[930], c[1559], s2)}).dropna()
    m = mac.reindex(fechas); m.index = o.index
    s1 = np.sign(m.sor).replace(0, np.nan)
    out["M1"] = pd.DataFrame({"s": s1, "y": bps(o[831], c[1559], s1)}).dropna()
    reac = np.sign(c[830] - o[830]).replace(0, np.nan)
    s3 = reac.where(m.norm > 1)
    out["M2"] = pd.DataFrame({"s": s3, "y": bps(o[831], c[929], s3)}).dropna()
    return out


def anio(t, a):
    return t[pd.DatetimeIndex(t.index).year == a]


barras = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in ANIOS}

# ---- V1: filtro sobre la candidata
ops = []
for a, b in barras.items():
    o_ = motor.simular(b, MG.senales(b, 940, 30, 0.40)); ops.append(o_[o_.sesion.dt.year == a])
ops = pd.concat(ops, ignore_index=True)
r = motor.r_neta(ops, 2.0)
ay, _, md = vix_ayer(pd.DatetimeIndex(ops.sesion))
base = C.resumen(r); rng = np.random.default_rng(0)
print(f"== VIX + MACRO · {FASE.upper()} {ANIOS} ==")
print(f"V1 base Momento n={base['n']} R={base['R']:+.3f} wr={base['wr']:.1%} · sin VIX/mediana: {np.isnan(md).sum()}")
for nom, m in (("VIX alto", ay > md), ("VIX bajo", ay <= md)):
    m = np.asarray(m, bool); s = C.resumen(r[m])
    azar = np.array([r[rng.choice(len(r), m.sum(), replace=False)].mean() for _ in range(1000)]); p95 = np.percentile(azar, 95)
    py = pd.Series(r[m]).groupby(ops.sesion.dt.year.to_numpy()[m]).mean().round(3).to_dict()
    ok = s["R"] > base["R"] and s["wr"] > base["wr"] and s["n"] >= 0.2 * base["n"] and s["R"] > p95
    print(f"   {nom}: n={s['n']} ({s['n']/base['n']:.0%}) R={s['R']:+.3f} wr={s['wr']:.1%} p95 azar {p95:+.3f} años {py} → {'PASA' if ok else 'no'}")

# ---- V2, M1, M2
real = {k: pd.concat([anio(premisas(b)[k], a) for a, b in barras.items()]) for k in ("V2", "M1", "M2")}
nul = {k: [] for k in real}
for sem in range(6):
    acc = {k: [] for k in real}
    for i, (a, b) in enumerate(barras.items()):
        pr = premisas(C.paseo_aleatorio(b, 61000 + 10 * sem + i))
        for k in real: acc[k].append(anio(pr[k], a).y)
    for k in real: nul[k].append(pd.concat(acc[k]).mean())
for k, t in real.items():
    s = C.resumen(t.y); p2 = 2 * min(s["p_1cola"], 1 - s["p_1cola"]); sg = np.sign(s["R"])
    anios = t.y.groupby(pd.DatetimeIndex(t.index).year).mean().round(1).to_dict()
    mismos = sum(np.sign(v) == sg for v in anios.values())
    L, S = t[t.s == 1].y.mean(), t[t.s == -1].y.mean()
    nm = np.array(nul[k]); z = C.z_exceso(s["R"], s["ee"], nm.mean(), nm.std(ddof=1) / np.sqrt(6))
    pasa = p2 < UMBRAL and mismos >= 2 and np.sign(L) == np.sign(S) == sg and abs(z) > 2 and np.sign(z) == sg and abs(s["R"]) > 0.5
    print(f"{k} n={s['n']} media={s['R']:+.1f} bps p2c={p2:.4f} años {anios} ({mismos}/3) · s+ {L:+.1f} (n={(t.s == 1).sum()}) "
          f"s− {S:+.1f} (n={(t.s == -1).sum()}) · nulo {nm.mean():+.1f} z={z:+.2f} → {'PASA' if pasa else 'no'}")
