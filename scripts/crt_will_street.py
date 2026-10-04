"""CRT de Will Street. preregistros/2026-10-04_crt_will_street.md"""
import numpy as np, pandas as pd
from src import controles as C, loader, motor

COSTE = 0.87


def senales(b):
    o, h, l, c = (b[k].to_numpy(float) for k in ("o", "h", "l", "c"))
    hh, ses = b.hhmm.to_numpy(), b.sesion.to_numpy()
    idx = np.arange(len(b))
    sesiones = pd.unique(ses)
    velas = []  # (sesion, h, l, c) de sesiones completas
    filas, nset = [], 0
    for s in sesiones:
        ii = idx[ses == s]; hm = hh[ii]
        if len(velas) >= 2:
            _, H1, L1, C1 = velas[-2]; _, H2, L2, C2 = velas[-1]
            baj, alc = L2 < L1, H2 > H1
            if baj != alc and L1 < C2 < H1:
                d = 1 if baj else -1
                nset += 1
                f = trigger(o, h, l, c, ii, hm, d, H1, L1)
                if f is not None:
                    filas.append(f)
        if len(ii) >= 300:
            velas.append((s, h[ii].max(), l[ii].min(), c[ii[-1]]))
    return pd.DataFrame(filas), nset


def trigger(o, h, l, c, ii, hm, d, H1, L1):
    j900 = ii[hm == 900]; fin = ii[hm == 1559]
    if not len(j900) or not len(fin):
        return None
    j900, fin = j900[0], fin[0]
    zona = ii[(hm >= 800) & (hm <= 1030)]
    # velas de 5m desde las 08:00 (índices M1 contiguos por bloque de 5 minutos de reloj)
    bloques = {}
    for j in zona:
        bloques.setdefault((hm[j - ii[0]] // 100) * 60 + (hm[j - ii[0]] % 100) // 5 * 5, []).append(j)
    claves = sorted(bloques)
    V = [(k, bloques[k][0], bloques[k][-1], h[bloques[k]].max(), l[bloques[k]].min()) for k in claves]
    ap = o[j900]
    objetivo = H1 if d == 1 else L1
    extremo = None; breaker = None; armado_desde = None
    for m, (k, a, z, vh, vl) in enumerate(V):
        if k < 9 * 60:
            continue
        # 1) con la orden armada, ¿alguna M1 de esta vela toca el breaker?
        if breaker is not None:
            for j in range(a, z + 1):
                if hm[j - ii[0]] > 1030:
                    return None
                ext_hasta = min(extremo, l[j:j + 1].min()) if d == 1 else max(extremo, h[j:j + 1].max())
                if (d == 1 and l[j] < extremo) or (d == -1 and h[j] > extremo):
                    extremo = ext_hasta  # nuevo extremo dentro de la vela: la orden sigue viva
                if (d == 1 and h[j] >= breaker) or (d == -1 and l[j] <= breaker):
                    px = c[j]
                    if (objetivo - px) * d <= 0:
                        return None
                    tramo = np.arange(j900, j + 1)
                    stop = l[tramo].min() if d == 1 else h[tramo].max()
                    r = (px - stop) * d
                    if r < 0.0005 * px or j + 1 > fin:
                        return None
                    return dict(i_ent=j + 1, precio=px, dir=d, riesgo=r, i_fin=fin, obj_ext=(objetivo - px) * d / r)
        # cancelación: el objetivo ya se alcanzó
        if (d == 1 and vh >= H1) or (d == -1 and vl <= L1):
            return None
        # 2) al cerrar esta vela, actualizar manipulación y breaker
        nuevo = (d == 1 and (extremo is None or vl < extremo)) or (d == -1 and (extremo is None or vh > extremo))
        if nuevo:
            extremo = vl if d == 1 else vh
            if (d == 1 and extremo < ap) or (d == -1 and extremo > ap):
                breaker = None
                for q in range(m - 1, 0, -1):  # pivote en q confirmado por q+1 <= m
                    if d == 1 and V[q][3] > V[q - 1][3] and V[q][3] > V[q + 1][3]:
                        breaker = V[q][3]; break
                    if d == -1 and V[q][4] < V[q - 1][4] and V[q][4] < V[q + 1][4]:
                        breaker = V[q][4]; break
            else:
                breaker = None
    return None


def sim_be(b, ops, obj_col, be=True, coste=COSTE):
    """Simulación con break-even a 1R (activo desde la barra siguiente) y TP a obj R."""
    h, l, c = (b[k].to_numpy(float) for k in ("h", "l", "c"))
    out = np.empty(len(ops))
    for n, (a, p, d, r, f, ob) in enumerate(ops[["i_ent", "precio", "dir", "riesgo", "i_fin", obj_col]].itertuples(index=False)):
        a, f = int(a), int(f); stop = p - d * r; tp = p + d * ob * r; activo = False; res = None
        for k in range(a, f + 1):
            if (d == 1 and l[k] <= stop) or (d == -1 and h[k] >= stop):
                res = 0.0 if activo else -1.0; break
            if k > a:
                if (d == 1 and h[k] >= tp) or (d == -1 and l[k] <= tp):
                    res = ob; break
                if be and not activo and ((d == 1 and h[k] >= p + r) or (d == -1 and l[k] <= p - r)):
                    activo = True; stop_n = p
            if activo:
                stop = p
        if res is None:
            res = (c[f] - p) * d / r
        out[n] = res - coste / r
    return out


VARS = {"V1 autor (mín 3R/extremo + BE)": ("o3", True), "V2 sin BE": ("o3", False), "V3 extremo sin tope + BE": ("ext", True)}


def correr(D):
    oo, ns = [], 0
    for a, df in D.items():
        s, n = senales(df)
        if len(s):
            o = motor.simular(df, s); o = o[o.sesion.dt.year == a].copy()
            o["o3"] = np.minimum(3.0, o.obj_ext); o["ext"] = o.obj_ext; o["_a"] = a
            oo.append(o)
        ns += n
    return (pd.concat(oo, ignore_index=True) if oo else pd.DataFrame()), ns


def r_var(D, o, var):
    col, be = VARS[var]
    return np.concatenate([sim_be(D[a], o[o._a == a], col, be) for a in D if (o._a == a).any()])


def informe(etq, D):
    o, ns = correr(D); o = o.sort_values(["_a", "i_ent"]).reset_index(drop=True)
    dias = sum(df.sesion.nunique() for df in D.values())
    print(f"\n##### {etq}: setups CRT {ns} ({ns/dias:.0%} de los días) · entradas {len(o)} ({len(o)/max(ns,1):.0%} de los setups) · "
          f"stop mediano {o.riesgo_pts.median():.1f} pts · TP al extremo mediano {o.obj_ext.median():.2f}R · largos {(o.dir==1).mean():.0%}")
    res = {}
    for var in VARS:
        r = r_var(D, o, var); s = C.resumen(r); res[var] = (o, r, s)
        py = pd.Series(r).groupby(o._a.to_numpy()).mean().round(3).to_dict()
        print(f"  {var}: R={s['R']:+.4f} ee {s['ee']:.4f} p1c={s['p_1cola']:.4f} wr {s['wr']:.1%} · años {py}")
    for rt in (1.0, 2.0, 3.0):
        rr = motor.r_neta(o, rt)
        print(f"  info 1:{rt} sin BE: wr {(rr>0).mean():.1%} R {rr.mean():+.4f} · invertida {motor.r_neta(o, rt, True).mean():+.4f}")
    r = res[list(VARS)[0]][1]
    for d, n in ((1, "largos"), (-1, "cortos")):
        m = (o.dir == d).to_numpy(); print(f"  V1 {n}: n={m.sum()} R={r[m].mean():+.4f} wr {(r[m]>0).mean():.1%}")
    return res


def nulo(D, res, semillas=6, base=11000):
    print("  -- paseo aleatorio")
    acc = {v: [] for v in VARS}
    for sem in range(semillas):
        P = {a: C.paseo_aleatorio(df, base + 100 * sem + a % 100) for a, df in D.items()}
        o, _ = correr(P)
        if len(o):
            o = o.sort_values(["_a", "i_ent"]).reset_index(drop=True)
            for v in VARS: acc[v].append(r_var(P, o, v))
    for v in VARS:
        rn = np.concatenate(acc[v]); sn = C.resumen(rn); s = res[v][2]
        print(f"  {v}: nulo R={sn['R']:+.4f} wr {sn['wr']:.1%} (n={len(rn)}) · real {s['R']:+.4f} · z={C.z_exceso(s['R'], s['ee'], sn['R'], sn['ee']):+.2f}")


if __name__ == "__main__":
    import sys
    anios = (2021, 2023, 2025) if "seis" not in sys.argv else tuple(range(2021, 2027))
    D = {a: loader.cargar_cfd([loader.RAIZ / f"data/nq_cfd_{a}.csv.gz"], verbose=False) for a in anios}
    res = informe("DISEÑO 2021/23/25" if len(anios) == 3 else "6 AÑOS 2021-2026", D)
    if len(anios) == 6:
        V = {a: D[a] for a in (2022, 2024, 2026)}
        informe("solo 2022/24/26 (uso nº11, umbral 0,0045)", V)
    nulo(D, res)
