"""TRADING VOLIUM setup 1 en NQ. preregistros/2026-10-04_volium_setup1.md"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader, motor

COSTE = 0.87


def h1(b):
    pos = np.arange(len(b))
    g = pd.DataFrame({"k": b.index.floor("h"), "h": b.h.to_numpy(), "l": b.l.to_numpy(), "p": pos}).groupby("k", sort=True)
    return g.h.max().to_numpy(), g.l.min().to_numpy(), g.p.last().to_numpy()


def senales(b):
    o, h, l, c = (b[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy(); idx = np.arange(len(b))
    HH, HL, HP = h1(b)
    # pivotes H1: (nivel, índice M1 desde el que se conoce)
    piv_h = [(HH[k], HP[k + 2], HP[k]) for k in range(2, len(HH) - 2) if HH[k] > max(HH[k - 1], HH[k - 2], HH[k + 1], HH[k + 2])]
    piv_l = [(HL[k], HP[k + 2], HP[k]) for k in range(2, len(HL) - 2) if HL[k] < min(HL[k - 1], HL[k - 2], HL[k + 1], HL[k + 2])]
    ph_t = np.array([p[1] for p in piv_h]); pl_t = np.array([p[1] for p in piv_l])
    cierres = []; filas = []
    for s in pd.unique(ses):
        ii = idx[ses == s]; hm = hh[ii]
        if len(ii) < 300:
            continue
        if len(cierres) >= 25:
            ema = pd.Series(cierres).ewm(span=20, adjust=False).mean().to_numpy()
            if cierres[-1] > ema[-1] and ema[-1] > ema[-6]:
                d = 1
            elif cierres[-1] < ema[-1] and ema[-1] < ema[-6]:
                d = -1
            else:
                d = 0
            if d:
                f = dia(o, h, l, c, ii, hm, d, piv_h, piv_l, ph_t, pl_t)
                if f: filas.append(f)
        cierres.append(c[ii[-1]])
    return pd.DataFrame(filas)


def dia(o, h, l, c, ii, hm, d, piv_h, piv_l, ph_t, pl_t):
    win = ii[(hm >= 800) & (hm <= 1130)]; fin = ii[hm == 1559]
    if not len(win) or not len(fin):
        return None
    j0 = win[0]
    # liquidez a barrer: pivote más reciente conocido en j0, sin barrar hasta j0
    piv, tiempos = (piv_l, pl_t) if d == 1 else (piv_h, ph_t)
    n = np.searchsorted(tiempos, j0, side="right") - 1
    nivel = None
    for q in range(n, max(n - 50, -1), -1):
        lv, t_conf, t_piv = piv[q]
        seg = (l[t_piv + 1:j0] if d == 1 else h[t_piv + 1:j0])
        if not seg.size or (d == 1 and seg.min() > lv) or (d == -1 and seg.max() < lv):
            nivel = lv; break
    if nivel is None:
        return None
    sw = np.flatnonzero(l[win] < nivel) if d == 1 else np.flatnonzero(h[win] > nivel)
    if not sw.size:
        return None
    js = win[sw[0]]
    # TP: pivote opuesto más reciente conocido en el momento de la barrida
    piv2, t2 = (piv_h, ph_t) if d == 1 else (piv_l, pl_t)
    m = np.searchsorted(t2, js, side="right") - 1
    if m < 0:
        return None
    tp, _, t_tp = piv2[m]
    if (tp - c[js]) * d <= 0:
        return None
    # velas de 5m desde las 08:00 hasta las 12:00
    blo = {}
    for j in ii[(hm >= 800) & (hm <= 1159)]:
        t = hm[j - ii[0]]; blo.setdefault(((t // 100) * 60 + t % 100) // 5, []).append(j)
    V = [(v[0], v[-1], o[v[0]], h[v].max(), l[v].min(), c[v[-1]]) for _, v in sorted(blo.items())]
    for n5, (a, z, vo, vh, vl, vc) in enumerate(V):
        if z <= js:
            continue
        ext = (l[js:z + 1].min() if d == 1 else h[js:z + 1].max())
        tramo = abs(tp_origen(h, l, t_tp, js, d) - ext)
        # FVG en contra nacidos desde el máximo del retroceso (por velas de 5m completas)
        tops = []
        for q in range(2, n5):
            if V[q][1] < t_tp:
                continue
            if d == 1 and V[q][3] < V[q - 2][4]:
                tops.append(V[q - 2][4])
            if d == -1 and V[q][4] > V[q - 2][3]:
                tops.append(V[q - 2][3])
        if not tops:
            continue
        ifvg = (vc > min(tops)) if d == 1 else (vc < max(tops))
        recup = (vc - ext) * d >= 0.3 * tramo
        if ifvg and recup:
            px = vc; r = (px - ext) * d; rr = (tp - px) * d / r if r > 0 else 0
            if r < 0.0005 * px or rr < 2 or z + 1 > fin[0]:
                return None
            return dict(i_ent=z + 1, precio=px, dir=d, riesgo_nat=r, riesgo=(tp - px) * d / 2, i_fin=fin[0], rr_nat=rr)
    return None


def tp_origen(h, l, t_tp, js, d):
    """Extremo del retroceso: máximo (largos) desde el pivote TP hasta la barrida."""
    return h[t_tp:js + 1].max() if d == 1 else l[t_tp:js + 1].min()


def correr(D):
    oo = []
    for a, df in D.items():
        s = senales(df)
        if len(s):
            o1 = motor.simular(df, s)  # V1: riesgo ensanchado, TP = 2R
            s2 = s.copy(); s2["riesgo"] = s2.riesgo_nat
            o2 = motor.simular(df, s2); o2["obj"] = o2.rr_nat  # V2: SL natural, TP estructural
            keep = o1.sesion.dt.year == a
            oo.append((o1[keep], o2[o2.sesion.dt.year == a]))
    return pd.concat([x[0] for x in oo], ignore_index=True), pd.concat([x[1] for x in oo], ignore_index=True)


def r_v2(o):
    return np.where(o.rmax >= o.obj, o.obj, np.where(o.toco_sl, -1.0, np.minimum(o.r_cierre, o.obj))) - COSTE / o.riesgo_pts


def informe(etq, D, nulo=True):
    o1, o2 = correr(D)
    dias = sum(df.sesion.nunique() for df in D.values())
    print(f"\n##### {etq}: {len(o1)} operaciones ({len(o1)/dias:.0%} de los días) · R:R natural mediano {o1.rr_nat.median():.2f} · stop ensanchado mediano {o1.riesgo_pts.median():.1f} pts (natural {o2.riesgo_pts.median():.1f}) · largos {(o1.dir==1).mean():.0%}")
    res = {}
    for nom, r in (("V1 autor (SL ensanchado, 1:2)", motor.r_neta(o1, 2.0)), ("V2 SL natural, TP estructural", r_v2(o2))):
        s = C.resumen(r); res[nom] = s; o = o1 if nom.startswith("V1") else o2
        py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
        print(f"  {nom}: wr {s['wr']:.1%} R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · años {py}")
    print(f"  V1 invertida {motor.r_neta(o1, 2.0, True).mean():+.4f} · V1 a 1:1 {motor.r_neta(o1, 1.0).mean():+.4f}")
    r = motor.r_neta(o1, 2.0)
    print("  V1 largos/cortos: " + " · ".join(f"{n} n={m.sum()} R={r[m].mean():+.3f}" for d, n in ((1, "largos"), (-1, "cortos")) for m in [(o1.dir == d).to_numpy()]))
    if nulo:
        a1, a2 = [], []
        for sem in range(6):
            P = {a: C.paseo_aleatorio(df, 29000 + 100 * sem + a % 100) for a, df in D.items()}
            n1, n2 = correr(P); a1.append(motor.r_neta(n1, 2.0)); a2.append(r_v2(n2))
        for nom, acc in (("V1 autor (SL ensanchado, 1:2)", a1), ("V2 SL natural, TP estructural", a2)):
            sn = C.resumen(np.concatenate(acc)); s = res[nom]
            print(f"  paseo {nom[:2]}: R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={sn['n']}) · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")


if __name__ == "__main__":
    seis = "seis" in sys.argv
    A = tuple(range(2021, 2027)) if seis else (2021, 2023, 2025)
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in A}
    informe("6 AÑOS 2021-2026" if seis else "DISEÑO 2021/23/25", D)
    if seis:
        informe("solo 2022/24/26 (uso nº14, umbral 0,0036)", {a: D[a] for a in (2022, 2024, 2026)}, nulo=False)
