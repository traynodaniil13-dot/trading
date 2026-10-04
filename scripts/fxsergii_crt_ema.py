"""CRT H1 + rotura de EMA 20 en 5m (fxsergii). Pre-registro:
preregistros/2026-10-04_fxsergii_crt_ema.md. DISEÑO 2021/2023/2025."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor

COSTE = 0.87


def senales(df, media="ema", ventana=60):
    idx = df.index
    pos = np.arange(len(df))
    o, h, l, c = (df[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    hh, ses = df.hhmm.to_numpy(), df.sesion.to_numpy()
    # fin de sesión: última barra <= 16:09 de cada sesión
    ok = hh <= 1609
    fin_ses = pd.Series(pos[ok]).groupby(ses[ok]).max()

    def agrupa(clave):
        g = pd.DataFrame({"k": clave, "o": o, "h": h, "l": l, "c": c, "p": pos}).groupby("k", sort=True)
        return pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(),
                             "p": g.p.last(), "n": g.p.size()})

    H = agrupa(idx.floor("h"))
    M = agrupa(idx.floor("5min"))
    m5 = (M.c.ewm(span=20, adjust=False).mean() if media == "ema" else M.c.rolling(20).mean()).to_numpy()
    Mk, Mo, Mh, Ml, Mc, Mp = M.index.values, M.o.to_numpy(), M.h.to_numpy(), M.l.to_numpy(), M.c.to_numpy(), M.p.to_numpy()

    Hk, Hh, Hl, Hc, Hn = H.index.values, H.h.to_numpy(), H.l.to_numpy(), H.c.to_numpy(), H.n.to_numpy()
    una_h = np.timedelta64(1, "h")
    filas = []
    for a in range(len(H) - 1):
        b = a + 1
        if Hk[b] - Hk[a] != una_h or Hn[a] < 30 or Hn[b] < 30:
            continue
        barre_baj, barre_alc = Hl[b] < Hl[a], Hh[b] > Hh[a]
        if barre_baj == barre_alc or not (Hl[a] < Hc[b] < Hh[a]):
            continue
        d = 1 if barre_baj else -1
        stop = Hl[b] if d == 1 else Hh[b]
        t0 = Hk[b] + una_h
        k0, k1 = np.searchsorted(Mk, t0), np.searchsorted(Mk, t0 + np.timedelta64(ventana, "m"))
        for k in range(k0, k1):
            # revalidación: el bajo/alto protegido no puede haberse perforado (incluye la vela gatillo)
            if (d == 1 and Ml[k] <= stop) or (d == -1 and Mh[k] >= stop):
                break
            if np.isnan(m5[k]):
                continue
            rompe = (Mo[k] < m5[k] < Mc[k]) if d == 1 else (Mo[k] > m5[k] > Mc[k])
            if not rompe:
                continue
            ie, px = Mp[k] + 1, Mc[k]
            if ie >= len(df) or ses[ie] != ses[Mp[k]] or hh[ie] > 1609:
                break
            if (d == 1 and px >= Hh[a]) or (d == -1 and px <= Hl[a]):
                break
            r = (px - stop) * d
            if r < 0.0003 * px:
                break
            fin = fin_ses.get(ses[ie])
            if fin is None or fin < ie:
                break
            obj = ((Hh[a] - px) if d == 1 else (px - Hl[a])) / r
            filas.append(dict(i_ent=ie, precio=px, dir=d, riesgo=r, i_fin=int(fin), obj=obj))
            break
    return pd.DataFrame(filas)


def r_obj(o):
    return np.where(o.rmax >= o.obj, o.obj, np.where(o.toco_sl, -1.0, np.minimum(o.r_cierre, o.obj))) - COSTE / o.riesgo_pts


def r_var(o, var):
    return r_obj(o) if var == "V2" else motor.r_neta(o, 1.0)


VARS = {"V1": dict(media="ema"), "V2": dict(media="ema"), "V3": dict(media="sma")}


def correr(D, var, adv=True, ventana=60):
    oo = []
    for a, df in D.items():
        s = senales(df, ventana=ventana, **VARS[var])
        if len(s) == 0:
            continue
        o = motor.simular(df, s, adverso_primera=adv)
        oo.append(o[o.sesion.dt.year == a])
    return pd.concat(oo, ignore_index=True)


if __name__ == "__main__":
    AÑOS = (2021, 2023, 2025)
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in AÑOS}
    res = {}
    for var in VARS:
        o = correr(D, var); res[var] = o
        r = r_var(o, var); s = C.resumen(r)
        py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
        inv = (motor.r_neta(o, 1.0, True).mean() if var != "V2" else np.nan)
        dias = o.sesion.nunique()
        print(f"\n=== {var} {VARS[var]} · {len(o)} ops ({len(o)/dias:.1f}/día operado, {dias} días) · "
              f"stop mediano {o.riesgo_pts.median():.1f} pts · largos {(o.dir==1).mean():.0%} · obj mediano {o.obj.median():.2f}R")
        print(f"  PRINCIPAL: R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} · años {py} · invertida 1:1 {inv:+.3f}")
        for rt in (1.0, 1.5, 2.0):
            rr = motor.r_neta(o, rt); tp = (o.rmax >= rt).mean(); sl = (~(o.rmax >= rt) & o.toco_sl).mean()
            bruta = (rr + COSTE / o.riesgo_pts).mean()
            print(f"  1:{rt}: TP {tp:.1%} · SL {sl:.1%} · cierre {1-tp-sl:.1%} · R neta {rr.mean():+.4f} (bruta {bruta:+.4f}) · invertida {motor.r_neta(o, rt, True).mean():+.4f}")
    # paseo aleatorio, 6 semillas por año, mismas 3 variantes
    print("\n=== PASEO ALEATORIO (6 semillas × 3 años)")
    nulo = {v: [] for v in VARS}
    for sem in range(6):
        P = {a: C.paseo_aleatorio(df, 1000 * a + sem) for a, df in D.items()}
        for var in VARS:
            o = correr(P, var); nulo[var].append(r_var(o, var))
    for var in VARS:
        rn = np.concatenate(nulo[var]); sn = C.resumen(rn); s = C.resumen(r_var(res[var], var))
        z = C.z_exceso(s["R"], s["ee"], sn["R"], sn["ee"])
        print(f"  {var}: nulo R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={len(rn)}) · real {s['R']:+.4f} · exceso {s['R']-sn['R']:+.4f} z={z:+.2f}")
    # informativo sobre V1
    o = res["V1"]; r = motor.r_neta(o, 1.0)
    hh = o.t_ent.dt.hour * 100 + o.t_ent.dt.minute
    tramo = np.where(hh >= 1800, "Asia", np.where(hh < 300, "Asia", np.where(hh < 930, "Londres", "NY")))
    print("\n=== V1 informativo")
    for t in ("Asia", "Londres", "NY"):
        m = tramo == t; s = C.resumen(r[m]); print(f"  {t}: n={m.sum()} R={s['R']:+.4f} wr {s['wr']:.1%} p1c={s['p_1cola']:.3f}")
    for d, n in ((1, "largos"), (-1, "cortos")):
        m = (o.dir == d).to_numpy(); s = C.resumen(r[m]); print(f"  {n}: n={m.sum()} R={s['R']:+.4f} wr {s['wr']:.1%}")
    for lo, hi in ((0, 10), (10, 20), (20, 40), (40, 1e9)):
        m = ((o.riesgo_pts >= lo) & (o.riesgo_pts < hi)).to_numpy(); s = C.resumen(r[m])
        print(f"  stop {lo}-{hi} pts: n={m.sum()} R={s['R']:+.4f} wr {s['wr']:.1%} bruta {(r[m] + COSTE/o.riesgo_pts.to_numpy()[m]).mean():+.4f}")
    o2 = correr(D, "V1", adv=False); s = C.resumen(motor.r_neta(o2, 1.0))
    print(f"  otra convención vela de entrada: R={s['R']:+.4f} wr {s['wr']:.1%}")
    o3 = correr(D, "V1", ventana=120); s = C.resumen(motor.r_neta(o3, 1.0))
    print(f"  ventana 120 min: n={len(o3)} R={s['R']:+.4f} wr {s['wr']:.1%} p1c={s['p_1cola']:.3f}")
    print(f"  consistencia V1: {C.consistencia(o, r)}")
