"""Ejecuta preregistros/2026-09-27_pruebas_duras_momento_pct.md."""
import numpy as np, pandas as pd
from src import controles as C
from src import loader, motor, premisas as P
from src.motores import momento_generico as MG

T0, L0, K0, RAT0 = 940, 30, 0.40, 2.0
CFD = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in range(2021, 2027)}
ok = {}


def ops_de(datos, T=T0, L=L0, k=K0, adv=True, retraso=0, anios=None):
    out = []
    for a, b in datos.items():
        s = MG.senales(b, T, L, k)
        if retraso:
            s = s.copy(); s["i_ent"] += retraso
            s["precio"] = b["o"].to_numpy()[s["i_ent"]]; s["riesgo"] = s["precio"] * k / 100
        o = motor.simular(b, s, adverso_primera=adv)
        out.append(o[o["sesion"].dt.year == a] if anios is None else o[o["sesion"].dt.year.isin(anios)])
    return pd.concat(out, ignore_index=True)


base = ops_de(CFD); rb = motor.r_neta(base, RAT0)
print(f"BASE CFD 2021-26: n={len(base)} R={rb.mean():+.3f}\n")

# T1
nq = loader.cargar(verbose=False)
onq = motor.simular(nq, MG.senales(nq, T0, L0, K0)); onq = onq[onq.sesion.dt.year.isin([2023, 2024, 2025])].reset_index(drop=True)
rnq = motor.r_neta(onq, RAT0)
j = pd.DataFrame({"ses": onq.sesion, "r_nq": rnq}).merge(pd.DataFrame({"ses": base.sesion, "r_cfd": rb}), on="ses")
corr = np.corrcoef(j.r_nq, j.r_cfd)[0, 1]
ok["T1"] = rnq.mean() > 0 and corr >= 0.8
print(f"T1 NQ futuro 2023-25: n={len(onq)} R={rnq.mean():+.3f} (CFD mismos días {j.r_cfd.mean():+.3f}) corr={corr:.2f} "
      f"| por año {pd.Series(rnq).groupby(onq.sesion.dt.year.to_numpy()).mean().round(3).to_dict()} -> {'OK' if ok['T1'] else 'FALLA'}")

# T2
vec = []
for nombre, kw, rat in [("stop 0,30%", dict(k=0.30), RAT0), ("stop 0,35%", dict(k=0.35), RAT0), ("stop 0,45%", dict(k=0.45), RAT0),
                        ("stop 0,50%", dict(k=0.50), RAT0), ("L=20", dict(L=20), RAT0), ("L=40", dict(L=40), RAT0),
                        ("T=09:35", dict(T=935), RAT0), ("T=09:45", dict(T=945), RAT0), ("ratio 1,75", {}, 1.75), ("ratio 2,25", {}, 2.25)]:
    o = base if not kw else ops_de(CFD, **kw)
    x = motor.r_neta(o, rat).mean(); vec.append(x)
    print(f"   T2 vecino {nombre:11s} R={x:+.3f}")
ok["T2"] = sum(v > 0 for v in vec) >= 8
print(f"T2 vecinos positivos: {sum(v > 0 for v in vec)}/10 -> {'OK' if ok['T2'] else 'FALLA'}")

# T3
rng = np.random.default_rng(0)
pl = np.array([motor.r_mezcla(base, RAT0, rng.random(len(base)) < 0.5).mean() for _ in range(1000)])
sig = (rb.mean() - pl.mean()) / pl.std(ddof=1)
ok["T3"] = sig >= 2.5
print(f"T3 placebo dirección: media {pl.mean():+.3f} ± {pl.std(ddof=1):.3f} -> real a {sig:+.2f}σ (p={(pl >= rb.mean()).mean():.3f}) -> {'OK' if ok['T3'] else 'FALLA'}")

# T4
r4 = motor.r_neta(ops_de(CFD, adv=False), RAT0).mean()
ok["T4"] = r4 > 0
print(f"T4 vela de entrada completa (otra cota): R={r4:+.3f} -> {'OK' if ok['T4'] else 'FALLA'}")

# T5
c2 = motor.r_neta(base, RAT0, coste=1.74).mean(); c3 = motor.r_neta(base, RAT0, coste=2.61).mean()
d1 = motor.r_neta(ops_de(CFD, retraso=1), RAT0).mean()
ok["T5"] = c2 > 0 and c3 > 0 and d1 > 0
print(f"T5 coste×2 R={c2:+.3f} · coste×3 R={c3:+.3f} · entrada 09:41 R={d1:+.3f} -> {'OK' if ok['T5'] else 'FALLA'}")

# T6
s = pd.Series(rb, index=pd.DatetimeIndex(base.t_ent)); m_sum = s.resample("ME").sum(); m_n = s.resample("ME").count()
roll = (m_sum.rolling(12).sum() / m_n.rolling(12).sum()).dropna()
ok["T6"] = (roll > 0).mean() >= 0.7
print(f"T6 ventanas de 12 meses positivas: {(roll > 0).mean():.0%} de {len(roll)} (peor {roll.min():+.3f}) -> {'OK' if ok['T6'] else 'FALLA'}")

# T7
L_ = rb[base.dir.to_numpy() == 1]; S_ = rb[base.dir.to_numpy() == -1]
ok["T7"] = L_.mean() > 0 and S_.mean() > 0
print(f"T7 largos n={len(L_)} R={L_.mean():+.3f} · cortos n={len(S_)} R={S_.mean():+.3f} -> {'OK' if ok['T7'] else 'FALLA'}")

# T8
iguales = total = 0
for a, b in CFD.items():
    b2 = b[~((b.hhmm >= 940) & (b.hhmm < 1700))]
    g = P._rejilla(b2, [909, 939]); sen = np.sign(g["c"][939] - g["c"][909]).dropna()
    oo = base[base.sesion.dt.year == a].set_index("sesion")["dir"]
    comun = oo.index.intersection(sen.index)
    iguales += int((oo.loc[comun] == sen.loc[comun]).sum()); total += len(oo)
ok["T8"] = iguales == total
print(f"T8 señales idénticas con los datos truncados en 09:40: {iguales}/{total} -> {'OK' if ok['T8'] else 'FALLA'}")

# T9
mes = pd.PeriodIndex(base.t_ent, freq="M"); grupos = [rb[mes == p] for p in mes.unique()]
bs = np.array([np.concatenate([grupos[i] for i in rng.integers(len(grupos), size=len(grupos))]).mean() for _ in range(10000)])
lo, hi = np.percentile(bs, [2.5, 97.5])
ok["T9"] = lo > 0
print(f"T9 bootstrap mensual IC95% de R: [{lo:+.3f}, {hi:+.3f}] -> {'OK' if ok['T9'] else 'FALLA'}")

print(f"\nPASA {sum(ok.values())}/9: {[k for k, v in ok.items() if not v] or 'todas'}")

print("\n10 operaciones al azar para cruzar a mano (NQ futuro, precios del CSV de Kaggle):")
m = onq.sample(10, random_state=3).sort_values("t_ent")
for _, x in m.iterrows():
    d = "LARGO" if x.dir == 1 else "CORTO"; st = x.precio - x.dir * x.riesgo_pts; ob = x.precio + x.dir * 2 * x.riesgo_pts
    res = "OBJETIVO" if x.rmax >= 2 else ("STOP" if x.toco_sl else f"CIERRE 16:00 ({x.r_cierre:+.2f}R)")
    print(f"  {x.t_ent:%Y-%m-%d} 09:40 {d:5s} entrada {x.precio:.2f} stop {st:.2f} objetivo {ob:.2f} ({x.riesgo_pts:.1f} pts) -> {res}")
