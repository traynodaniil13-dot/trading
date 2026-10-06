"""Gráficos de operaciones recientes del CRT H1 (auditoría visual). Hora de España = NY + 6 h."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scripts.crt_h1_will_street import senales, carga
from scripts import forward_open_drive as F
from src import loader

d26 = carga([2026])[2026]; fw = F.datos()
sal = loader.RAIZ / "resultados/graficos_crt_h1"; sal.mkdir(exist_ok=True)
for lectura in ("A", "B"):
    for nom, df in (("2026", d26), ("fw", fw)):
        _, s = senales(df, lectura, "3R")
        if not len(s):
            continue
        idx = df.index; s["t"] = idx[s.i_ent - 1]; s = s[s.t >= "2026-09-15"]
        for r in s.itertuples():
            dia = r.t.normalize()
            sub = df[(idx >= dia + pd.Timedelta(hours=7)) & (idx <= dia + pd.Timedelta(hours=13))]
            g = sub.groupby(sub.index.floor("5min")).agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"))
            fig, ax = plt.subplots(figsize=(13, 6.5)); w = pd.Timedelta(minutes=3.5)
            for t, row in zip(g.index + pd.Timedelta(hours=6), g.itertuples()):
                col = "#2e7d32" if row.c >= row.o else "#c62828"
                ax.vlines(t, row.l, row.h, color=col, lw=0.8)
                ax.add_patch(plt.Rectangle((t - w / 2, min(row.o, row.c)), w, abs(row.c - row.o) or 0.5, color=col))
            # velas H1 de rango
            for H in (8, 9, 10):
                hb = sub[(sub.index >= dia + pd.Timedelta(hours=H)) & (sub.index < dia + pd.Timedelta(hours=H + 1))]
                if len(hb):
                    x0 = dia + pd.Timedelta(hours=H + 6); ax.add_patch(plt.Rectangle((x0, hb.l.min()), pd.Timedelta(hours=1), hb.h.max() - hb.l.min(), fill=False, ec="gray", ls=":", lw=1))
            ini = dia + pd.Timedelta(hours=r.ini // 100 + 6, minutes=r.ini % 100)
            ax.axvline(ini, color="purple", lw=0.8, alpha=.6, label=f"inicio vela operativa {ini:%H:%M}")
            ax.axhline(r.objetivo, color="green", ls="--", lw=1, label=f"objetivo extremo opuesto {r.objetivo:.1f}")
            if r.barrido == r.barrido and r.barrido is not None:
                ax.axhline(r.barrido, color="purple", ls="--", lw=1, label=f"extremo barrido {r.barrido:.1f}")
            ax.axhline(r.breaker, color="blue", ls="-.", lw=1, label=f"breaker {r.breaker:.1f}")
            sl = r.precio - r.dir * r.riesgo; tp = r.precio + r.dir * 3 * r.riesgo
            ax.axhline(sl, color="red", lw=1, label=f"stop {sl:.1f}"); ax.axhline(tp, color="darkgreen", lw=1, label=f"TP 3R {tp:.1f}")
            te = r.t + pd.Timedelta(hours=6)
            ax.scatter([te], [r.precio], marker="^" if r.dir == 1 else "v", s=160, color="black", zorder=5, label=f"entrada {r.precio:.1f} ({te:%H:%M})")
            ax.set_title(f"CRT H1 lectura {lectura} · {te:%d/%m/%Y} · {'LARGO' if r.dir == 1 else 'CORTO'} · NAS100 CFD 5m · hora de España (cajas grises = velas H1)")
            ax.legend(fontsize=8, loc="best"); ax.grid(alpha=.2)
            f = sal / f"{lectura}_{te:%Y-%m-%d}.png"; fig.savefig(f, dpi=105, bbox_inches="tight"); plt.close(fig); print(f.name, round(r.precio, 1), r.dir)
