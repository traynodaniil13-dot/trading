"""Ejecuta preregistros/2026-09-29_pruebas_duras_II_momento_pct.md."""
import numpy as np, pandas as pd
from src import loader, motor
from src.motores import momento_generico as MG

CFD = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in range(2021, 2027)}


def ops(salida=1559, peor=False):
    out = []
    for a, b in CFD.items():
        s = MG.senales(b, 940, 30, 0.40, salida=salida)
        if peor:
            h, l = b["h"].to_numpy(), b["l"].to_numpy()
            s = s.copy()
            s["precio"] = np.where(s["dir"] == 1, h[s["i_ent"]], l[s["i_ent"]])
            s["riesgo"] = s["precio"] * 0.004
            s["i_ent"] = s["i_ent"] + 1
        o = motor.simular(b, s)
        # volatilidad causal: rango RTH medio de las 20 sesiones previas / precio
        rth = b[(b.hhmm >= 930) & (b.hhmm <= 1559)]
        g = rth.groupby("sesion"); vol = ((g.h.max() - g.l.min()) / g.c.last()).shift(1).rolling(20, min_periods=20).mean()
        o["vol20"] = o["sesion"].map(vol)
        out.append(o[o.sesion.dt.year == a])
    return pd.concat(out, ignore_index=True)


o = ops(); r = motor.r_neta(o, 2.0); ano = o.sesion.dt.year.to_numpy(); ok = {}
print(f"BASE n={len(o)} R={r.mean():+.3f}\n")

# U1
res = []
for d, nom in ((1, "largos"), (-1, "cortos")):
    m = o.dir.to_numpy() == d
    fav = (o.rmax.to_numpy() >= 1)[m]; stop = (o.toco_sl.to_numpy() & (o.rmax.to_numpy() < 1))[m]
    fr = fav.sum() / (fav.sum() + stop.sum()); res.append(fr)
    print(f"U1 {nom}: barrera a favor primero {fr:.1%} (n resueltas {fav.sum()+stop.sum()})")
ok["U1"] = all(x > 0.5 for x in res)

# U2
lo = {y: r[ano != y].mean() for y in sorted(set(ano))}
ok["U2"] = all(v > 0 for v in lo.values())
print("U2 quitando cada año:", {k: round(v, 3) for k, v in lo.items()})

# U3
sem = pd.Series(r).groupby([ano, (o.sesion.dt.month.to_numpy() > 6).astype(int) + 1]).mean()
ok["U3"] = (sem > 0).sum() >= 8
print(f"U3 semestres positivos {(sem > 0).sum()}/{len(sem)}:", {f'{y}-S{h}': round(v, 3) for (y, h), v in sem.items()})

# U4
v = o.vol20.to_numpy(); med = np.nanmedian(v); alta = v > med; baja = v <= med
ok["U4"] = r[alta].mean() > 0 and r[baja].mean() > 0
print(f"U4 volatilidad alta n={alta.sum()} R={r[alta].mean():+.3f} · baja n={baja.sum()} R={r[baja].mean():+.3f}")

# U5
dow = pd.Series(r).groupby(o.sesion.dt.dayofweek.to_numpy()).mean()
ok["U5"] = (dow > 0).sum() >= 4
print("U5 día de la semana (0=lun):", dow.round(3).to_dict())

# U6
r12 = motor.r_neta(ops(salida=1159), 2.0).mean(); r14 = motor.r_neta(ops(salida=1359), 2.0).mean()
ok["U6"] = r12 > 0 and r14 > 0
print(f"U6 salida 12:00 R={r12:+.3f} · salida 14:00 R={r14:+.3f}")

# U7
parado = o.toco_sl.to_numpy() & (o.rmax.to_numpy() < 2)
r7 = r - parado * (5.0 / o.riesgo_pts.to_numpy())
ok["U7"] = r7.mean() > 0
print(f"U7 stop 5 pts peor: R={r7.mean():+.3f}")

# U8
r8 = motor.r_neta(ops(peor=True), 2.0).mean()
ok["U8"] = r8 > 0
print(f"U8 entrada en el peor precio de la vela 09:40: R={r8:+.3f}")

# U9
r9 = np.sort(r)[:-10].mean()
ok["U9"] = r9 > 0
print(f"U9 sin los 10 mejores días: R={r9:+.3f}")

print(f"\nPASA {sum(ok.values())}/9 · fallan: {[k for k, v in ok.items() if not v] or 'ninguna'}")
