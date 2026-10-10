"""6 estrategias en PDF de FX Replay. preregistros/2026-10-10_pdfs_fxreplay.md"""
import sys
import numpy as np, pandas as pd
from scipy import stats
from src import controles as C, loader, mina

IMPARES, PARES = (2019, 2021, 2023, 2025), (2020, 2022, 2024, 2026)
COSTE = {"nq": 0.87, "es": 0.65}


def camino(h, l, c, a, fin, p, d, r, obj, be):
    """R bruta. Barra a = primera tras el relleno: solo adverso en ella (regla 2). be = R que activa el BE (o None)."""
    stop = p - d * r; tp = p + d * obj * r; act = False
    for k in range(a, fin + 1):
        if (d == 1 and l[k] <= stop) or (d == -1 and h[k] >= stop):
            return 0.0 if act else -1.0
        if k > a:
            if (d == 1 and h[k] >= tp) or (d == -1 and l[k] <= tp):
                return obj
            if be is not None and not act and ((d == 1 and h[k] >= p + be * r) or (d == -1 and l[k] <= p - be * r)):
                act = True; stop = p
    return (c[fin] - p) * d / r


def fila(df, j_fill, px, d, r, fin, obj, be, coste, perdida_directa=False):
    h, l, c = (df[x].to_numpy() for x in "hlc")
    r = max(r, 0.0005 * px)
    if perdida_directa:
        rn = ri = -1.0
    else:
        rn = camino(h, l, c, j_fill + 1, fin, px, d, r, obj, be)
        ri = camino(h, l, c, j_fill + 1, fin, px, -d, r, obj, be)
    return dict(i_ent=j_fill + 1, precio=px, dir=d, riesgo=r, i_fin=fin, r=rn - coste / r, r_inv=ri - coste / r)


def velas(df, regla):
    clave = df.index.floor(regla).to_numpy() if isinstance(regla, str) else regla
    corte = np.r_[True, clave[1:] != clave[:-1]]
    kf = np.flatnonzero(corte); kl = np.r_[kf[1:] - 1, len(df) - 1]
    O = df.o.to_numpy()[kf]; C_ = df.c.to_numpy()[kl]
    H = np.maximum.reduceat(df.h.to_numpy(), kf); L = np.minimum.reduceat(df.l.to_numpy(), kf)
    return kf, kl, O, H, L, C_


def dias(df):
    hm, ses = df.hhmm.to_numpy(), df.sesion.to_numpy(); idx = np.arange(len(df))
    for s in pd.unique(ses):
        ii = idx[ses == s]
        yield s, ii, hm[ii]


# ---------------- 1 · Globex
def globex(df, obj, be, coste):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc")
    kf, kl, O, H, L, Cc = velas(df, "5min"); cidx = np.searchsorted(kf, np.arange(len(df)), "right") - 1
    rng = H - L; body = np.abs(Cc - O)
    peq = body <= 0.5 * rng; imp_up = (Cc > O) & (body >= 0.6 * rng) & (rng > 0); imp_dn = (Cc < O) & (body >= 0.6 * rng) & (rng > 0)
    filas = []
    for s, ii, t in dias(df):
        gl = ii[(t >= 1800) | (t <= 929)]; ven = ii[(t >= 930) & (t <= 1500)]; fin = ii[t == 1559]
        if len(gl) < 300 or len(ven) < 60 or not len(fin):
            continue
        GH, GL = h[gl].max(), l[gl].min(); d = 0; js = None
        for j in ven:
            up, dn = h[j] > GH, l[j] < GL
            if up and dn: break
            if up or dn: d = 1 if dn else -1; js = j; break
        if not d: continue
        zona = None; q0 = cidx[js]
        for j in range(js + 1, ven[-1] + 1):
            q = cidx[j - 1]
            if kl[q] == j - 1 and q - 2 >= q0:               # vela de 5m recién cerrada
                imp = imp_up if d == 1 else imp_dn
                if imp[q] and imp[q - 1]:
                    b = q - 2; base = []
                    while b >= q0 and peq[b] and len(base) < 6:
                        base.append(b); b -= 1
                    if 1 <= len(base) <= 5:
                        bb = np.array(base)
                        if d == 1: zona = (L[bb].min(), np.maximum(O[bb], Cc[bb]).max())
                        else: zona = (np.minimum(O[bb], Cc[bb]).min(), H[bb].max())
            if zona is not None:
                zl, zh = zona; alt = zh - zl
                if (d == 1 and l[j] <= zh) or (d == -1 and h[j] >= zl):
                    px = c[j]; sl = zl - 0.33 * alt if d == 1 else zh + 0.33 * alt
                    if j + 1 <= fin[0]:
                        malo = (d == 1 and px <= sl) or (d == -1 and px >= sl)
                        filas.append(fila(df, j, px, d, abs(px - sl), fin[0], obj, be, coste, malo))
                    break
    return df, pd.DataFrame(filas)


# ---------------- 2 · JJ Simon
def jj(df, ventana, coste):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc")
    pc = np.r_[c[0], c[:-1]]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    j_ = np.arange(2, len(h) - 2)
    ph = np.zeros(len(h), bool); pl = np.zeros(len(h), bool)
    ph[j_] = (h[j_] > h[j_ - 1]) & (h[j_] > h[j_ - 2]) & (h[j_] > h[j_ + 1]) & (h[j_] > h[j_ + 2])
    pl[j_] = (l[j_] < l[j_ - 1]) & (l[j_] < l[j_ - 2]) & (l[j_] < l[j_ + 1]) & (l[j_] < l[j_ + 2])
    a0, cont_fin, fin_v = (930, 944, 1100) if ventana == "manana" else (1400, 1414, 1500)
    filas = []
    for s, ii, t in dias(df):
        jfv = ii[t == a0]; fin = ii[t == 1559]
        if not len(jfv) or not len(fin): continue
        fv = o[jfv[0]]; ven = ii[(t >= a0 + 3) & (t <= fin_v)]
        ult_h = ult_l = None
        for j in range(jfv[0] - 60, ven[-1] + 1 if len(ven) else jfv[0]):
            assert j - 3 >= 0
            i = j - 3                                     # pivote en i confirmado al cerrar i+2 = j-1
            if ph[i]: ult_h = h[i]
            if pl[i]: ult_l = l[i]
            if j < (ven[0] if len(ven) else 10**12): continue
            tj = t[j - ii[0]]
            dsp_up = c[j] > o[j] and h[j] > o[j] and (h[j] - c[j]) < 0.2 * (h[j] - o[j])
            dsp_dn = c[j] < o[j] and o[j] > l[j] and (c[j] - l[j]) < 0.2 * (o[j] - l[j])
            up = dsp_up and ult_h is not None and c[j] > ult_h and c[j - 1] <= ult_h
            dn = dsp_dn and ult_l is not None and c[j] < ult_l and c[j - 1] >= ult_l
            if not (up or dn): continue
            d = 1 if up else -1
            if tj <= cont_fin: ok = (d == 1 and c[j] > fv) or (d == -1 and c[j] < fv)
            else: ok = (d == 1 and c[j] < fv) or (d == -1 and c[j] > fv)
            if not ok or np.isnan(atr[j]): continue
            sl = 50.0 if atr[j] > 20 else 25.0 if atr[j] >= 7 else 16.5
            if j + 1 <= fin[0]:
                filas.append(fila(df, j, c[j], d, sl, fin[0], 1.5, None, coste))
            break
    return df, pd.DataFrame(filas)


# ---------------- 3 · Toto Capital SBL
def toto(df, ventana, coste, mantener=False):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc")
    kf, kl, O, H, L, Cc = velas(df, "15min")
    e = {n: pd.Series(Cc).ewm(span=n, adjust=False).mean().to_numpy() for n in (50, 100, 200)}
    ult = lambda j: np.searchsorted(kl, j, "right") - 1     # última 15m cerrada en j
    filas = []
    for s, ii, t in dias(df):
        D = pd.Timestamp(s); edt = D.tz_localize("America/New_York").utcoffset() == pd.Timedelta(hours=-4)
        asia = ii[((t >= (2000 if edt else 1900)) & (t <= 2359)) | ((t <= 59) if edt else np.zeros(len(t), bool))]
        lon = ii[(t >= 300) & (t <= 459)]; fin = ii[t == 1559]
        if ventana == "londres": w = ii[(t >= 300) & (t <= 459)]; niveles = [asia]
        else: w = ii[(t >= 800) & (t <= 1029)]; niveles = [asia, lon]
        if len(asia) < 120 or len(w) < 60 or not len(fin) or (ventana == "ny" and len(lon) < 60): continue
        effH, effL = [], []
        for nv in niveles:
            tras = np.arange(nv[-1] + 1, w[0])
            effH.append(max(h[nv].max(), h[tras].max() if len(tras) else -np.inf))
            effL.append(min(l[nv].min(), l[tras].min() if len(tras) else np.inf))
        nh, nl = min(effH), max(effL)
        js = d = None
        for j in w:
            q = ult(j - 1)
            if q < 200: break
            baj = e[50][q] < e[100][q] < e[200][q]; alc = e[50][q] > e[100][q] > e[200][q]
            if baj and h[j] > nh: js, d = j, -1; break
            if alc and l[j] < nl: js, d = j, 1; break
        if js is None: continue
        nivel = None
        for j in range(js + 1, w[-1] + 1):
            q = ult(j - 1)
            if kl[q] == j - 1 and kl[q] >= js:
                if (d == -1 and Cc[q] < O[q]): nivel = L[q]
                if (d == 1 and Cc[q] > O[q]): nivel = H[q]
            if nivel is not None and ((d == -1 and l[j] <= nivel) or (d == 1 and h[j] >= nivel)):
                tramo = np.arange(js, j + 1); sl = h[tramo].max() if d == -1 else l[tramo].min()
                px = c[j]
                f_ = min(j + 5 * 1380, len(df) - 1) if mantener else fin[0]
                if j + 1 <= f_:
                    filas.append(fila(df, j, px, d, abs(sl - px), f_, 2.0, None, coste))
                break
    return df, pd.DataFrame(filas)


# ---------------- 4 · Omar Agag EBP (4H)
def ebp(df, tipo, coste):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc")
    idx = df.index; mins = ((idx.hour * 60 + idx.minute - 1080) % 1440).to_numpy() // 240
    clave = df.sesion.to_numpy().astype("datetime64[m]").astype(np.int64) * 10 + mins
    kf, kl, O, H, L, Cc = velas(df, clave)
    filas = []; libre_desde = 0
    for q in range(1, len(kf) - 1):
        if kl[q] < libre_desde: continue
        rgq = H[q] - L[q]
        if rgq <= 0: continue
        alc = L[q] < L[q - 1] and Cc[q] > max(O[q - 1], Cc[q - 1])
        baj = H[q] > H[q - 1] and Cc[q] < min(O[q - 1], Cc[q - 1])
        if not (alc or baj): continue
        d = 1 if alc else -1
        fuerza = (H[q] - Cc[q]) / rgq if d == 1 else (Cc[q] - L[q]) / rgq
        fuerte = fuerza <= 0.15
        if (tipo == "fuerte") != fuerte: continue
        if tipo == "fuerte":
            lim = H[q] - 0.25 * rgq if d == 1 else L[q] + 0.25 * rgq
            sl = H[q] - 0.75 * rgq if d == 1 else L[q] + 0.75 * rgq
            mercado = False
        else:
            lim = H[q] - 0.5 * rgq if d == 1 else L[q] + 0.5 * rgq
            sl = L[q] if d == 1 else H[q]
            mercado = fuerza > 0.5
        ext = H[q] if d == 1 else L[q]
        a = kl[q] + 1; caduca = kl[min(q + 6, len(kl) - 1)]
        jf = None
        if mercado: jf = kl[q]
        else:
            for m in range(a, caduca + 1):
                if (d == 1 and l[m] <= lim) or (d == -1 and h[m] >= lim): jf = m; break
        if jf is None: continue
        fin = kl[min(q + 30, len(kl) - 1)]
        px = c[jf]; malo = (d == 1 and px <= sl) or (d == -1 and px >= sl)
        r = abs(px - sl)
        # BE cuando supera el extremo de la vela EBP: se aproxima con un "be" en R equivalente
        be_r = max((ext - px) * d / max(r, 1e-9), 0.0) if not malo else None
        filas.append(fila(df, jf, px, d, r, fin, 2.0, be_r if be_r and be_r < 2.0 else None, coste, malo))
        libre_desde = fin
    return df, pd.DataFrame(filas)


# ---------------- 5 · ORB
def orb(df, modo, coste):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc")
    filas = []
    for s, ii, t in dias(df):
        r15 = ii[(t >= 930) & (t <= 944)]; fin = ii[t == 1559]
        if len(r15) != 15 or not len(fin): continue
        RH, RL = h[r15].max(), l[r15].min(); M = (RH + RL) / 2; R = RH - RL
        cierres = ii[(t >= 949) & (t <= 1159) & (t % 5 == 4)]
        for j in cierres:
            d = 1 if c[j] > RH else -1 if c[j] < RL else 0
            if not d: continue
            tp = RH + R if d == 1 else RL - R; px = c[j]; riesgo = abs(px - M)
            if (tp - px) * d >= riesgo:
                if j + 1 <= fin[0]:
                    filas.append(fila(df, j, px, d, riesgo, fin[0], (tp - px) * d / riesgo, None, coste))
            elif modo == "autor":
                borde = RH if d == 1 else RL
                for m in range(j + 1, fin[0]):
                    if (d == 1 and h[m] >= tp) or (d == -1 and l[m] <= tp): break
                    if (d == 1 and l[m] <= borde) or (d == -1 and h[m] >= borde):
                        px = c[m]; riesgo = abs(px - M); malo = (px - M) * d <= 0
                        obj = (tp - px) * d / max(riesgo, 1e-9)
                        if obj > 0 and m + 1 <= fin[0]:
                            filas.append(fila(df, m, px, d, riesgo, fin[0], obj, None, coste, malo))
                        break
            break
    return df, pd.DataFrame(filas)


# ---------------- 6 · Doyle Exchange
def doyle(df, ventana, coste):
    o, h, l, c = (df[x].to_numpy() for x in "ohlc")
    kf, kl, O, H, L, Cc = velas(df, "5min")
    ema = pd.Series(Cc).ewm(span=200, adjust=False).mean().to_numpy()
    rng = H - L; med = pd.Series(rng).rolling(20).median().shift(1).to_numpy()
    cidx = np.searchsorted(kf, np.arange(len(df)), "right") - 1
    w0, w1 = (930, 1200) if ventana == "ny" else (300, 600)
    filas = []
    for s, ii, t in dias(df):
        w = ii[(t >= w0) & (t <= w1)]; fin = ii[t == 1559]
        if len(w) < 60 or not len(fin): continue
        q_ini, q_fin = cidx[w[0]], cidx[w[-1]]
        zonas = []; hecho = False
        for q in range(max(q_ini - 48, 210), q_fin + 1):
            # zona nacida en q-2 (vela contraria) confirmada al cerrar q
            i = q - 2
            if Cc[i] < O[i] and Cc[q - 1] > O[q - 1] and Cc[q] > O[q] and Cc[q] - H[i] >= rng[i]:
                zonas.append((1, L[i], H[i], q))
            if Cc[i] > O[i] and Cc[q - 1] < O[q - 1] and Cc[q] < O[q] and L[i] - Cc[q] >= rng[i]:
                zonas.append((-1, L[i], H[i], q))
            if q < q_ini: continue
            vivas = []
            for z in zonas:
                d, zl, zh, nace = z
                if q <= nace or q - nace > 48: 
                    if q <= nace: vivas.append(z)
                    continue
                toca = (d == 1 and L[q] <= zh) or (d == -1 and H[q] >= zl)
                if not toca: vivas.append(z); continue
                cierra_dentro = (d == 1 and Cc[q] <= zh) or (d == -1 and Cc[q] >= zl)
                tendencia = (d == 1 and Cc[q] > ema[q]) or (d == -1 and Cc[q] < ema[q])
                pequena = not np.isnan(med[q]) and rng[q] <= 1.5 * med[q]
                if cierra_dentro or not tendencia or not pequena: continue   # zona consumida
                nivel = H[q] if d == 1 else L[q]; sl0 = L[q] if d == 1 else H[q]
                for m in range(kl[q] + 1, min(kl[min(q + 3, len(kl) - 1)], fin[0]) + 1):
                    if (d == 1 and l[m] <= sl0) or (d == -1 and h[m] >= sl0): break
                    if (d == 1 and h[m] >= nivel) or (d == -1 and l[m] <= nivel):
                        if m + 1 <= fin[0]:
                            filas.append(fila(df, m, c[m], d, abs(c[m] - sl0), fin[0], 3.0, 1.0, coste))
                        hecho = True; break
                if hecho: break
            zonas = vivas
            if hecho: break
    return df, pd.DataFrame(filas)


def familias(ins="nq"):
    k = COSTE[ins]
    return {
        "globex": {"TP 2R + BE 1R": lambda df: globex(df, 2.0, 1.0, k), "TP 4R + BE 2R": lambda df: globex(df, 4.0, 2.0, k)},
        "jj": {"mañana": lambda df: jj(df, "manana", k), "tarde": lambda df: jj(df, "tarde", k)},
        "toto": {"Londres": lambda df: toto(df, "londres", k), "NY": lambda df: toto(df, "ny", k)},
        "ebp": {"EBP fuerte": lambda df: ebp(df, "fuerte", k), "EBP indeciso": lambda df: ebp(df, "indeciso", k)},
        "orb": {"autor (mercado o retest)": lambda df: orb(df, "autor", k), "solo mercado": lambda df: orb(df, "mercado", k)},
        "doyle": {"NY": lambda df: doyle(df, "ny", k), "Londres": lambda df: doyle(df, "londres", k)},
    }


r_fn = lambda o, invertida=False: o["r_inv" if invertida else "r"].to_numpy()
carga = lambda pref, anios: {a: loader.cargar_cfd([loader.RAIZ / f"data/{pref}_cfd_{a}.csv.gz"], verbose=False) for a in anios}

if __name__ == "__main__":
    fam = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "calibrar":
        df = carga("nq", [2021])[2021]
        for v, fn in familias()[fam].items():
            a, rr, nn = [], [], []
            for sd in range(8):
                o = mina.correr_variante(fn, {2021: C.paseo_aleatorio(df, 2100 + sd)})
                if len(o): a.append(((o.r - o.r_inv) / 2).mean()); rr.append(o.r.mean()); nn.append(len(o))
            a = np.array(a)
            print(f"{fam} · {v}: n/año {np.mean(nn):.0f} · paseo R {np.mean(rr):+.4f} · asimetría {a.mean():+.4f} ± {a.std(ddof=1)/np.sqrt(len(a)):.4f}")
        sys.exit()
    V = familias("nq")[fam]
    tab, sup, ops = mina.evaluar(f"{fam} (NQ)", V, r_fn, carga("nq", IMPARES), lambda df, sd: C.paseo_aleatorio(df, sd), semillas=12)
    for v, o in ops.items():
        r = r_fn(o); print(f"  {v}: n={len(o)} ({len(o)/4:.0f}/año) wr {(r>0).mean():.1%} stop mediano {o.riesgo_pts.median():.1f} · años {tab.set_index('variante').loc[v, 'anios']}")
    if fam in ("globex", "toto", "orb", "jj", "doyle"):
        E = carga("es", (2021, 2023, 2025))
        for v, fn in familias("es")[fam].items():
            o = mina.correr_variante(fn, E); r = r_fn(o)
            if len(o): print(f"  Informativo ES {v}: n={len(o)} R={r.mean():+.4f} wr {(r>0).mean():.1%} años {pd.Series(r).groupby(o._a.to_numpy()).mean().round(3).to_dict()}")
    if sup:
        print(f"\nVALIDACIÓN pares para {sup} (p < {0.05/len(sup):.4f} y ≥3/4 años):")
        P = carga("nq", PARES)
        for v in sup:
            o = mina.correr_variante(V[v], P); r = r_fn(o); py = pd.Series(r).groupby(o._a.to_numpy()).mean()
            p = stats.ttest_1samp(r, 0, alternative="greater").pvalue
            print(f"  {v}: n={len(o)} R={r.mean():+.4f} p1c={p:.4f} inv {r_fn(o, True).mean():+.4f} años {py.round(3).to_dict()} → {'PASA' if p < 0.05/len(sup) and (py > 0).sum() >= 3 else 'NO PASA'}")
