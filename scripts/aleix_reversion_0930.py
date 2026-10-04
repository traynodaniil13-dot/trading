"""Aleix, modelo de reversión de las 09:30. Pre-registro
preregistros/2026-10-04_aleix_reversion_0930.md. DISEÑO 2021/2023/2025."""
import numpy as np, pandas as pd
from src import controles as C, loader, motor

COSTE = 0.87


def fvg_h1(df):
    """FVG H1 por instante de conocimiento. Devuelve velas H1 y lista de FVG
    (dir, abajo, arriba, i_nace = índice H1 de la 3ª vela)."""
    pos = np.arange(len(df))
    g = pd.DataFrame({"k": df.index.floor("h"), "h": df.h.to_numpy(), "l": df.l.to_numpy(),
                      "c": df.c.to_numpy(), "p": pos}).groupby("k", sort=True)
    H = pd.DataFrame({"h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "n": g.p.size()})
    hh, ll = H.h.to_numpy(), H.l.to_numpy()
    f = []
    for i in range(2, len(H)):
        if ll[i] > hh[i - 2]:
            f.append((1, hh[i - 2], ll[i], i))
        elif hh[i] < ll[i - 2]:
            f.append((-1, hh[i], ll[i - 2], i))
    return H, f


def zonas_vigentes(H, f, t930):
    """FVG nacidos en velas H1 que CIERRAN antes de las 09:30 (vela de inicio <= 08:00) y
    respetados por los cierres H1 hasta la vela de las 08:00 incluida."""
    k = H.index.values
    ult = np.searchsorted(k, t930 - np.timedelta64(90, "m"), side="right") - 1  # vela de las 08:00
    if ult < 0:
        return []
    c = H.c.to_numpy()
    out = []
    for d, ab, ar, i in f:
        if i > ult or i < ult - 120:
            continue
        cc = c[i + 1:ult + 1]
        if (d == 1 and (cc < ab).any()) or (d == -1 and (cc > ar).any()):
            continue
        out.append((d, ab, ar))
    return out


def dol_h1(H, ix, h, l, j930, apertura):
    """Pivote H1 sin barrer más cercano por encima/debajo de la apertura de 09:30."""
    k = H.index.values; hh, ll = H.h.to_numpy(), H.l.to_numpy()
    t930 = np.datetime64(ix[j930])
    ult = np.searchsorted(k, t930 - np.timedelta64(90, "m"), side="right") - 1  # vela 08:00
    if ult < 125:
        return None, None
    j900 = j930 - 30
    m_l = l[max(j900, 0):j930].min(); m_h = h[max(j900, 0):j930].max()
    NL = NH = None
    for i in range(ult - 2, ult - 120, -1):  # pivote i confirmado al cerrar i+2 <= ult
        assert i - 2 >= 0
        if NL is None and ll[i] < ll[i - 1] and ll[i] < ll[i - 2] and ll[i] < ll[i + 1] and ll[i] < ll[i + 2]:
            if ll[i] < apertura and min(ll[i + 1:ult + 1].min(), m_l) > ll[i]:
                NL = ll[i]
        if NH is None and hh[i] > hh[i - 1] and hh[i] > hh[i - 2] and hh[i] > hh[i + 1] and hh[i] > hh[i + 2]:
            if hh[i] > apertura and max(hh[i + 1:ult + 1].max(), m_h) < hh[i]:
                NH = hh[i]
    if NL is None or NH is None:
        return None, None
    return NH, NL


def niveles15(b):
    pos = np.arange(len(b))
    g = pd.DataFrame({"k": b.index.floor("15min"), "h": b.h.to_numpy(), "l": b.l.to_numpy(), "p": pos}).groupby("k", sort=True)
    return g.h.max().to_numpy(), g.l.min().to_numpy(), g.p.last().to_numpy()


def objetivo_estructural(Q, h, l, j, px, d, modo, atras=500):
    """Nivel conocido al cierre de la barra M1 j. Solo velas de 15m cerradas (última M1 <= j)."""
    Qh, Ql, Qp = Q
    n = np.searchsorted(Qp, j, side="right")  # velas 15m completas: índices < n
    lo = max(2, n - atras)
    mejor = None
    for i in range(n - 1, lo - 1, -1):
        if modo == "fvg15":
            if d == 1 and Qh[i] < Ql[i - 2]:
                nivel, nace = Qh[i], i
            elif d == -1 and Ql[i] > Qh[i - 2]:
                nivel, nace = Ql[i], i
            else:
                continue
        else:  # piv15: pivote en i confirmado al cerrar i+2 (< n)
            if i + 2 >= n:
                continue
            if d == 1 and Qh[i] > max(Qh[i - 1], Qh[i - 2], Qh[i + 1], Qh[i + 2]):
                nivel, nace = Qh[i], i
            elif d == -1 and Ql[i] < min(Ql[i - 1], Ql[i - 2], Ql[i + 1], Ql[i + 2]):
                nivel, nace = Ql[i], i
            else:
                continue
        if (nivel - px) * d <= 0:
            continue
        a, z = Qp[nace] + 1, j + 1  # M1 posteriores al nacimiento hasta la entrada
        if a < z and ((d == 1 and h[a:z].max() >= nivel) or (d == -1 and l[a:z].min() <= nivel)):
            continue
        if mejor is None or (nivel - px) * d < (mejor - px) * d:
            mejor = nivel
    return mejor


def senales(b, liq="on", usar_fvg=True, tp="alto", min_riesgo_pct=0.0005):
    o, h, l, c = (b[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    idx = np.arange(len(b))
    H, f = fvg_h1(b)
    Q = niveles15(b) if tp in ("fvg15", "piv15") else None
    filas, prev_rth = [], None
    for s in pd.unique(ses):
        ii = idx[ses == s]; hm = hh[ii]
        on = ii[(hm >= 1800) | (hm <= 929)]
        rth = ii[(hm >= 930) & (hm <= 1559)]
        ven = ii[(hm >= 930) & (hm <= 1030)]
        fin = ii[hm == 1559]
        ref = prev_rth
        prev_rth = (h[rth].max(), l[rth].min()) if len(rth) >= 300 else None
        if len(on) < 300 or len(ven) < 50 or len(fin) == 0 or hh[ven[0]] != 930:
            continue
        if liq == "on":
            NH, NL = h[on].max(), l[on].min()
        elif liq == "h1":
            NH, NL = dol_h1(H, b.index, h, l, ven[0], o[ven[0]])
            if NH is None:
                continue
        else:
            if ref is None:
                continue
            NH, NL = ref
        sw_ven = ven[hh[ven] <= 1000]
        arriba, abajo = h[sw_ven] > NH, l[sw_ven] < NL
        k = np.flatnonzero(arriba | abajo)
        if k.size == 0 or (arriba[k[0]] and abajo[k[0]]):
            continue
        j_sw = sw_ven[k[0]]; d = -1 if arriba[k[0]] else 1
        zonas = [z for z in zonas_vigentes(H, f, np.datetime64(b.index[ven[0]])) if z[0] == d] if usar_fvg else None
        i0 = ven[0]
        for j in ven[ven > j_sw]:
            # FVG de 1m en contra (bajistas para largo) nacidos en barras i0+2..j-1
            tops = []
            for i in range(i0 + 2, j):
                if d == 1 and h[i] < l[i - 2]:
                    tops.append(l[i - 2])
                if d == -1 and l[i] > h[i - 2]:
                    tops.append(h[i - 2])
            if not tops:
                continue
            if not ((d == 1 and c[j] > max(tops)) or (d == -1 and c[j] < min(tops))):
                continue
            tramo = np.arange(i0, j + 1)
            ext = l[tramo].min() if d == 1 else h[tramo].max()
            if usar_fvg and not any(ab <= ext <= ar for _, ab, ar in zonas):
                break
            riesgo = (c[j] - ext) * d
            if riesgo < min_riesgo_pct * c[j] or j + 1 > fin[0]:
                break
            alto = h[tramo].max() if d == 1 else l[tramo].min()
            obj = (alto - c[j]) * d / riesgo
            if tp == "alto" and obj <= 0:
                break
            if Q is not None:
                nv = objetivo_estructural(Q, h, l, j, c[j], d, tp)
                if nv is None:
                    break
                obj = (nv - c[j]) * d / riesgo
            filas.append(dict(i_ent=j + 1, precio=c[j], dir=d, riesgo=riesgo, i_fin=fin[0], obj=obj))
            break
    return pd.DataFrame(filas)


def r_obj(o):
    return np.where(o.rmax >= o.obj, o.obj, np.where(o.toco_sl, -1.0, np.minimum(o.r_cierre, o.obj))) - COSTE / o.riesgo_pts


VARS = {"V1": dict(liq="on", tp="alto"), "V2": dict(liq="on", tp="r15"), "V3": dict(liq="rth", tp="alto"),
        "V4": dict(liq="h1", tp="alto"), "V5": dict(liq="h1", tp="r15"), "V6": dict(liq="h1", tp="r3")}


def rv(o, var):
    tp = VARS[var]["tp"]
    return motor.r_neta(o, 1.5) if tp == "r15" else motor.r_neta(o, 3.0) if tp == "r3" else r_obj(o)


def correr(D, usar_fvg=True, **kw):
    oo = []
    for a, df in D.items():
        s = senales(df, usar_fvg=usar_fvg, **kw)
        if len(s):
            o = motor.simular(df, s); oo.append(o[o.sesion.dt.year == a])
    return pd.concat(oo, ignore_index=True) if oo else pd.DataFrame()


if __name__ == "__main__":
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in (2021, 2023, 2025)}
    res = {}
    for var, kw in VARS.items():
        o = correr(D, **kw); res[var] = o
        r = rv(o, var); s = C.resumen(r)
        py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
        inv = motor.r_neta(o, 1.5, True).mean()
        print(f"\n=== {var} {kw}: {len(o)} ops ({len(o)/3:.0f}/año) · stop mediano {o.riesgo_pts.median():.1f} pts · obj mediano {o.obj.median():.2f}R · largos {(o.dir==1).mean():.0%}")
        print(f"  PRINCIPAL: R={s['R']:+.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} · años {py} · invertida 1:1,5 {inv:+.3f}")
        for rt in (1.0, 1.5, 2.0, 3.0):
            rr = motor.r_neta(o, rt); tp = (o.rmax >= rt).mean(); sl = (~(o.rmax >= rt) & o.toco_sl).mean()
            print(f"  1:{rt}: TP {tp:.1%} · SL {sl:.1%} · R {rr.mean():+.4f} · invertida {motor.r_neta(o, rt, True).mean():+.4f}")
    print("\n=== Sin filtro FVG H1 (informativo, liquidez overnight)")
    o = correr(D, usar_fvg=False, liq="on", tp="alto")
    for rt in (1.0, 1.5, 2.0):
        rr = motor.r_neta(o, rt); print(f"  n={len(o)} 1:{rt}: wr {(rr>0).mean():.1%} R {rr.mean():+.4f}")
    print(f"  TP alto: R {r_obj(o).mean():+.4f} wr {(r_obj(o)>0).mean():.1%}")
    print("\n=== PASEO ALEATORIO (6 semillas × 3 años)")
    nulo = {v: [] for v in VARS}
    for sem in range(6):
        P = {a: C.paseo_aleatorio(df, 2000 * a + sem) for a, df in D.items()}
        for var, kw in VARS.items():
            o = correr(P, **kw)
            if len(o): nulo[var].append(rv(o, var))
    for var in VARS:
        rn = np.concatenate(nulo[var]); sn = C.resumen(rn); s = C.resumen(rv(res[var], var))
        print(f"  {var}: nulo R={sn['R']:+.4f} (n={len(rn)}) · real {s['R']:+.4f} · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")
    o = res["V1"]; r = r_obj(o)
    for d, n in ((1, "largos"), (-1, "cortos")):
        m = (o.dir == d).to_numpy(); print(f"  V1 {n}: n={m.sum()} R={r[m].mean():+.4f} wr {(r[m]>0).mean():.1%}")
