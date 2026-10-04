"""Ruptura PDH/PDL (15m) + retesteo con patrón de vela (5m). preregistros/2026-10-04_pdh_pdl_ruptura_retest.md"""
import sys
import numpy as np, pandas as pd
from src import controles as C, loader, motor


def velas(ii, hm, o, h, l, c, minutos, desde=930, hasta=1559):
    """Velas de `minutos` alineadas desde las 09:30 con los índices M1 de la sesión."""
    out = {}
    for j in ii[(hm >= desde) & (hm <= hasta)]:
        t = hm[j - ii[0]]; m = (t // 100) * 60 + t % 100 - 570
        out.setdefault(m // minutos, []).append(j)
    return [(k, v[0], v[-1], o[v[0]], h[v].max(), l[v].min(), c[v[-1]]) for k, v in sorted(out.items())]


def senales(b, nivel="ses"):
    o, h, l, c = (b[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy(); idx = np.arange(len(b))
    filas, prev, cont = [], None, dict(dias=0, ruptura=0, patron=0)
    for s in pd.unique(ses):
        ii = idx[ses == s]; hm = hh[ii]
        rth = ii[(hm >= 930) & (hm <= 1559)]
        if prev is not None and len(rth) >= 300:
            cont["dias"] += 1
            f = dia(o, h, l, c, ii, hm, prev, cont)
            if f: filas.append(f)
        if len(ii) >= 300 and len(rth) >= 300:
            prev = (h[ii].max(), l[ii].min()) if nivel == "ses" else (h[rth].max(), l[rth].min())
    return pd.DataFrame(filas), cont


def dia(o, h, l, c, ii, hm, prev, cont):
    PDH, PDL = prev
    j929 = ii[hm == 929]; fin = ii[hm == 1559]
    if not len(j929) or not len(fin):
        return None
    q = velas(ii, hm, o, h, l, c, 15, 930, 1159)
    ant = c[j929[0]]; rup = None
    for k, a, z, vo, vh, vl, vc in q:
        if k * 15 > 135:  # última vela de ruptura: la de las 11:45
            break
        if vc > PDH >= ant:
            rup = (1, z); break
        if vc < PDL <= ant:
            rup = (-1, z); break
        ant = vc
    if rup is None:
        return None
    cont["ruptura"] += 1
    d, zr = rup; L = PDH if d == 1 else PDL
    v5 = [x for x in velas(ii, hm, o, h, l, c, 5, 930, 1159) if x[1] > zr]
    for n, (k, a, z, vo, vh, vl, vc) in enumerate(v5):
        rg = vh - vl
        if rg <= 0:
            continue
        lo_w, up_w = min(vo, vc) - vl, vh - max(vo, vc)
        toca = (vl <= L) if d == 1 else (vh >= L)
        entrada = None
        if d == 1 and toca and lo_w >= 0.6 * rg and up_w <= 0.3 * rg:
            entrada, sl, tipo = vh, vl, "martillo"
        elif d == -1 and toca and up_w >= 0.6 * rg and lo_w <= 0.3 * rg:
            entrada, sl, tipo = vl, vh, "estrella"
        elif n > 0:
            _, pa, pz, po, ph, pl, pc = v5[n - 1]
            toca2 = toca or ((pl <= L) if d == 1 else (ph >= L))
            if d == 1 and toca2 and pc < po and vc > vo and vo <= pc and vc >= po:
                entrada, sl, tipo = ph, vl, "envolvente"
            elif d == -1 and toca2 and pc > po and vc < vo and vo >= pc and vc <= po:
                entrada, sl, tipo = pl, vh, "envolvente"
        if entrada is None:
            continue
        cont["patron"] += 1
        # orden stop viva hasta las 12:30; se cancela si toca el SL antes
        for j in ii[(ii > z) & (hm <= 1230)]:
            if (d == 1 and l[j] <= sl) or (d == -1 and h[j] >= sl):
                return None
            if (d == 1 and h[j] >= entrada) or (d == -1 and l[j] <= entrada):
                px = c[j]; r = (px - sl) * d
                if r < 0.0005 * px or j + 1 > fin[0]:
                    return None
                return dict(i_ent=j + 1, precio=px, dir=d, riesgo=r, i_fin=fin[0], tipo=tipo)
        return None
    return None


VARS = [("V-SES", "ses"), ("V-RTH", "rth")]


def correr(D, nivel):
    oo, ct = [], dict(dias=0, ruptura=0, patron=0)
    for a, df in D.items():
        s, cnt = senales(df, nivel)
        for k in ct: ct[k] += cnt[k]
        if len(s):
            o = motor.simular(df, s); oo.append(o[o.sesion.dt.year == a])
    return pd.concat(oo, ignore_index=True), ct


def informe(etq, D, con_nulo=True):
    print(f"\n##### {etq}")
    for nom, nivel in VARS:
        o, ct = correr(D, nivel)
        print(f"\n=== {nom}: días {ct['dias']} · con ruptura {ct['ruptura']/ct['dias']:.0%} · con patrón {ct['patron']/ct['dias']:.0%} · "
              f"operaciones {len(o)} ({len(o)/ct['dias']:.0%} de los días) · stop mediano {o.riesgo_pts.median():.1f} pts · largos {(o.dir==1).mean():.0%}")
        for rt in (2.0, 3.0, 1.0):
            r = motor.r_neta(o, rt); s = C.resumen(r)
            py = pd.Series(r).groupby(o.sesion.dt.year.to_numpy()).mean().round(3).to_dict()
            tag = "PRINCIPAL" if rt > 1 else "info"
            print(f"  {tag} 1:{rt:g}: wr {s['wr']:.1%} R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} · años {py} · invertida {motor.r_neta(o, rt, True).mean():+.4f}")
        r = motor.r_neta(o, 2.0)
        print("  por patrón (1:2): " + " · ".join(f"{t} n={m.sum()} R={r[m].mean():+.3f}" for t in o.tipo.unique() for m in [(o.tipo == t).to_numpy()]))
        print("  largos/cortos (1:2): " + " · ".join(f"{n} n={m.sum()} R={r[m].mean():+.3f}" for d, n in ((1, "largos"), (-1, "cortos")) for m in [(o.dir == d).to_numpy()]))
        if con_nulo:
            nul = {2.0: [], 3.0: []}
            for sem in range(6):
                P = {a: C.paseo_aleatorio(df, 19000 + 100 * sem + a % 100) for a, df in D.items()}
                on, _ = correr(P, nivel)
                for rt in nul: nul[rt].append(motor.r_neta(on, rt))
            for rt in nul:
                rn = np.concatenate(nul[rt]); sn = C.resumen(rn); s = C.resumen(motor.r_neta(o, rt))
                print(f"  paseo 1:{rt:g}: R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={len(rn)}) · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")


if __name__ == "__main__":
    seis = "seis" in sys.argv
    A = tuple(range(2021, 2027)) if seis else (2021, 2023, 2025)
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in A}
    informe("6 AÑOS 2021-2026" if seis else "DISEÑO 2021/23/25", D)
    if seis:
        informe("solo 2022/24/26 (uso nº12, umbral 0,0042)", {a: D[a] for a in (2022, 2024, 2026)}, con_nulo=False)
