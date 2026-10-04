"""Estructura + oferta/demanda + R:R >= 2,5. preregistros/2026-10-04_estructura_oferta_demanda.md"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader, motor

COSTE = 0.87


def velas_tf(b, regla):
    pos = np.arange(len(b))
    g = pd.DataFrame({"k": b.index.floor(regla), "o": b.o.to_numpy(), "h": b.h.to_numpy(), "l": b.l.to_numpy(),
                      "c": b.c.to_numpy(), "p": pos}).groupby("k", sort=True)
    return g.o.first().to_numpy(), g.h.max().to_numpy(), g.l.min().to_numpy(), g.c.last().to_numpy(), g.p.last().to_numpy()


def zonas(O, H, L, Cc, P):
    """Eventos (t, dir, z_lo, z_hi, i_ext): zona nacida al cierre de la vela t."""
    ev = []
    SH = SL = None  # (precio, índice, roto)
    tend, valido = 0, None  # valido = (precio, índice) del mínimo/máximo válido
    for t in range(4, len(Cc)):
        # pivote en t-2 confirmado al cierre de t
        k = t - 2
        assert k - 2 >= 0
        if H[k] > max(H[k - 1], H[k - 2], H[k + 1], H[k + 2]):
            SH = [H[k], k, False]
        if L[k] < min(L[k - 1], L[k - 2], L[k + 1], L[k + 2]):
            SL = [L[k], k, False]
        nuevo = None
        if tend >= 0 and SH is not None and not SH[2] and Cc[t] > SH[0]:
            SH[2] = True
            seg = np.arange(SH[1], t + 1); i_v = seg[np.argmin(L[seg])]
            tend, valido = 1, (L[i_v], i_v); nuevo = (1, i_v)
        elif tend <= 0 and SL is not None and not SL[2] and Cc[t] < SL[0]:
            SL[2] = True
            seg = np.arange(SL[1], t + 1); i_v = seg[np.argmax(H[seg])]
            tend, valido = -1, (H[i_v], i_v); nuevo = (-1, i_v)
        elif tend == 1 and Cc[t] < valido[0]:
            seg = np.arange(valido[1], t + 1); i_v = seg[np.argmax(H[seg])]
            tend, valido = -1, (H[i_v], i_v); nuevo = (-1, i_v)
            if SL is not None: SL[2] = True
        elif tend == -1 and Cc[t] > valido[0]:
            seg = np.arange(valido[1], t + 1); i_v = seg[np.argmin(L[seg])]
            tend, valido = 1, (L[i_v], i_v); nuevo = (1, i_v)
            if SH is not None: SH[2] = True
        if nuevo:
            d, i_v = nuevo
            cand = [j for j in range(max(0, i_v - 5), i_v + 1) if (Cc[j] < O[j] if d == 1 else Cc[j] > O[j])]
            j = cand[-1] if cand else i_v
            ev.append((t, d, L[j], H[j], i_v))
    return ev


def senales(b, regla):
    O, H, L, Cc, P = velas_tf(b, regla)
    ev = zonas(O, H, L, Cc, P)
    h, l, c = (b[k].to_numpy(float) for k in ("h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    ok_h = hh <= 1530
    fin_ses = pd.Series(np.flatnonzero(hh <= 1559)).groupby(ses[hh <= 1559]).max()
    filas, toques = [], 0
    for n, (t, d, zlo, zhi, i_v) in enumerate(ev):
        a = P[t] + 1
        z = P[ev[n + 1][0]] if n + 1 < len(ev) else len(b) - 1  # hasta la siguiente zona/giro
        if a > z:
            continue
        borde, sl = (zhi, zlo) if d == 1 else (zlo, zhi)
        seg = np.flatnonzero(l[a:z + 1] <= borde) if d == 1 else np.flatnonzero(h[a:z + 1] >= borde)
        if not seg.size:
            continue
        j = a + seg[0]; toques += 1
        px = c[j]
        if (px - sl) * d <= 0 or not ok_h[j]:
            continue
        ext_tf = H[i_v:t + 1].max() if d == 1 else L[i_v:t + 1].min()
        ext_m1 = (h[a:j].max() if j > a else -np.inf) if d == 1 else (l[a:j].min() if j > a else np.inf)
        tp = max(ext_tf, ext_m1) if d == 1 else min(ext_tf, ext_m1)
        r = (px - sl) * d
        obj = (tp - px) * d / r
        if r < 0.0005 * px or obj < 2.5:
            continue
        f = fin_ses.get(ses[j])
        if f is None or f <= j:
            continue
        filas.append(dict(i_ent=j + 1, precio=px, dir=d, riesgo=r, i_fin=int(f), obj=obj))
    return pd.DataFrame(filas), toques


def r_obj(o):
    return np.where(o.rmax >= o.obj, o.obj, np.where(o.toco_sl, -1.0, np.minimum(o.r_cierre, o.obj))) - COSTE / o.riesgo_pts


VARS = {"5m": "5min", "15m": "15min", "1h": "h"}


def correr(D, regla):
    oo, tq = [], 0
    for a, df in D.items():
        s, t = senales(df, regla); tq += t
        if len(s):
            o = motor.simular(df, s); oo.append(o[o.sesion.dt.year == a])
    return (pd.concat(oo, ignore_index=True) if oo else pd.DataFrame()), tq


def informe(etq, D, con_nulo=True):
    print(f"\n##### {etq}")
    for nom, regla in VARS.items():
        o, tq = correr(D, regla)
        r = r_obj(o); s = C.resumen(r)
        py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
        tp = (o.rmax >= o.obj).mean()
        print(f"\n=== {nom}: toques {tq} → operaciones {len(o)} ({len(o)/max(tq,1):.0%} pasan el filtro) · TP mediano {o.obj.median():.2f}R · stop mediano {o.riesgo_pts.median():.1f} pts · largos {(o.dir==1).mean():.0%}")
        print(f"  PRINCIPAL (TP estructural): wr {s['wr']:.1%} (TP {tp:.1%}) R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · años {py}")
        r25 = motor.r_neta(o, 2.5)
        print(f"  1:2,5 fijo: wr {(r25>0).mean():.1%} R={r25.mean():+.4f} · invertida {motor.r_neta(o, 2.5, True).mean():+.4f} · 1:1 R={motor.r_neta(o, 1.0).mean():+.4f}")
        print("  largos/cortos: " + " · ".join(f"{n} n={m.sum()} R={r[m].mean():+.3f}" for d, n in ((1, "largos"), (-1, "cortos")) for m in [(o.dir == d).to_numpy()]))
        if con_nulo:
            acc = []
            for sem in range(6):
                P = {a: C.paseo_aleatorio(df, 23000 + 100 * sem + a % 100) for a, df in D.items()}
                on, _ = correr(P, regla)
                if len(on): acc.append(r_obj(on))
            rn = np.concatenate(acc); sn = C.resumen(rn)
            print(f"  paseo aleatorio: R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={len(rn)}) · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")


if __name__ == "__main__":
    seis = "seis" in sys.argv
    A = tuple(range(2021, 2027)) if seis else (2021, 2023, 2025)
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in A}
    informe("6 AÑOS 2021-2026" if seis else "DISEÑO 2021/23/25", D)
    if seis:
        informe("solo 2022/24/26 (uso nº13, umbral 0,0038)", {a: D[a] for a in (2022, 2024, 2026)}, con_nulo=False)
