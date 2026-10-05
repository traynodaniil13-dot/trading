"""Gráficos de operaciones concretas de Gerard García (auditoría visual). Hora de España = NY + 6 h."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scripts.gerard_garcia_fvg import V, COSTE, RATIO_TP, velas
from scripts import forward_open_drive as F
from src import loader

df = F.datos()
_, s = V["Londres SL 0.5% sin promediar"](df)
idx = df.index
for r in s.itertuples():
    dia = idx[r.i_ent - 1].normalize()
    ven = (idx >= dia + pd.Timedelta(hours=0)) & (idx <= dia + pd.Timedelta(hours=8, minutes=29))
    sub = df[ven]
    g = sub.groupby(sub.index.floor("5min")).agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"))
    kl, _, _, c15 = velas(df, 15); ema15 = pd.Series(c15, index=idx[kl]).ewm(span=20, adjust=False).mean()
    ema15 = ema15[(ema15.index >= sub.index[0]) & (ema15.index <= sub.index[-1])]
    fig, ax = plt.subplots(figsize=(13, 6.5))
    x = (g.index + pd.Timedelta(hours=6))
    w = pd.Timedelta(minutes=3.5)
    for t, row in zip(x, g.itertuples()):
        col = "#2e7d32" if row.c >= row.o else "#c62828"
        ax.vlines(t, row.l, row.h, color=col, lw=0.8)
        ax.add_patch(plt.Rectangle((t - w / 2, min(row.o, row.c)), w, abs(row.c - row.o) or 0.5, color=col))
    ax.step(ema15.index + pd.Timedelta(minutes=15 + 360), ema15.values, where="post", color="orange", lw=1.5, label="EMA 20 de M15 (vela cerrada)")
    tb = idx[r.k_barrida] + pd.Timedelta(hours=6); tf = idx[r.i_ent - 1] + pd.Timedelta(hours=6)
    ax.axhline(r.nivel, color="purple", ls="--", lw=1, label=f"swing M5 barrido {r.nivel:.1f}")
    ax.axvline(tb, color="purple", lw=0.8, alpha=.6)
    ax.axhspan(min(r.fvg_a, r.fvg_b), max(r.fvg_a, r.fvg_b), xmin=0, xmax=1, color="royalblue", alpha=.15, label=f"FVG M5 {min(r.fvg_a, r.fvg_b):.1f}-{max(r.fvg_a, r.fvg_b):.1f}")
    sl = r.precio - r.dir * r.riesgo; tp = r.precio + r.dir * RATIO_TP * r.riesgo
    ax.axhline(sl, color="red", lw=1, label=f"stop {sl:.1f}"); ax.axhline(tp, color="green", lw=1, label=f"TP {tp:.1f}")
    ax.scatter([tf], [r.precio], marker="^" if r.dir == 1 else "v", s=160, color="black", zorder=5, label=f"entrada {r.precio:.1f} ({tf:%H:%M} España)")
    ax.set_title(f"{tf:%d/%m/%Y} · {'LARGO' if r.dir == 1 else 'CORTO'} · resultado {r.r:+.2f}R · NAS100 CFD, velas de 5 min, hora de España")
    ax.legend(loc="best", fontsize=8); ax.grid(alpha=.2)
    f = loader.RAIZ / f"resultados/graficos_gerard/{tf:%Y-%m-%d}.png"
    fig.savefig(f, dpi=110, bbox_inches="tight"); plt.close(fig); print(f)
