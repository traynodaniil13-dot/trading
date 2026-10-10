"""Auditoría del Venom: horas de entrada y gráficos de operaciones recientes (hora de España = NY + 6 h)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scripts.ict_venom import senales, carga
from scripts import forward_open_drive as F
from src import loader

d25 = carga([2025])[2025]
_, s = senales(d25, "G12")
hm = d25.hhmm.to_numpy()[s.i_ent - 1]
print("hora NY de la barra de entrada (2025): min", hm.min(), "· max", hm.max(), "· mediana", int(np.median(hm)))
print(pd.Series(hm // 100 * 100 + (hm % 100) // 30 * 30).value_counts().sort_index().to_string())
# minuto más volátil (control obligatorio del loader)
rg = (d25.h - d25.l).groupby(d25.hhmm).median().sort_values(ascending=False)
print("minutos más volátiles (mediana del rango):", rg.head(3).round(1).to_dict())

sal = loader.RAIZ / "resultados/graficos_venom"; sal.mkdir(exist_ok=True)
fw = F.datos()
for nom, df in (("2026", carga([2026])[2026]), ("fw", fw)):
    _, s = senales(df, "G12"); idx = df.index
    if not len(s): continue
    s["t"] = idx[s.i_ent - 1]; s = s[s.t >= "2026-09-20"]
    for r in s.itertuples():
        dia = r.t.normalize(); sub = df[(idx >= dia + pd.Timedelta(hours=7, minutes=30)) & (idx <= dia + pd.Timedelta(hours=12))]
        rgo = df[(idx >= dia + pd.Timedelta(hours=8)) & (idx < dia + pd.Timedelta(hours=9, minutes=30))]
        fig, ax = plt.subplots(figsize=(13, 6)); w = pd.Timedelta(seconds=40)
        for t, row in zip(sub.index + pd.Timedelta(hours=6), sub.itertuples()):
            col = "#2e7d32" if row.c >= row.o else "#c62828"
            ax.vlines(t, row.l, row.h, color=col, lw=0.6); ax.add_patch(plt.Rectangle((t - w / 2, min(row.o, row.c)), w, abs(row.c - row.o) or 0.2, color=col))
        ax.axhline(rgo.h.max(), color="purple", ls="--", lw=1, label=f"máx. 08:00-09:29 NY (14:00-15:29 España) {rgo.h.max():.1f}")
        ax.axhline(rgo.l.min(), color="purple", ls=":", lw=1, label=f"mín. 08:00-09:29 NY {rgo.l.min():.1f}")
        ax.axvline(dia + pd.Timedelta(hours=15, minutes=30), color="gray", lw=0.8, label="09:30 NY = 15:30 España")
        sl = r.precio - r.dir * r.riesgo; tp = r.precio + r.dir * 2 * r.riesgo; te = r.t + pd.Timedelta(hours=6)
        ax.axhline(sl, color="red", lw=1, label=f"stop {sl:.1f}"); ax.axhline(tp, color="green", lw=1, label=f"TP 2R {tp:.1f}")
        ax.scatter([te], [r.precio], marker="^" if r.dir == 1 else "v", s=150, color="black", zorder=5, label=f"entrada {r.precio:.1f} ({te:%H:%M} España)")
        ax.set_title(f"Venom · {te:%d/%m/%Y} · {'LARGO' if r.dir == 1 else 'CORTO'} · NAS100 CFD 1m · hora de España"); ax.legend(fontsize=8); ax.grid(alpha=.2)
        f = sal / f"{te:%Y-%m-%d}.png"; fig.savefig(f, dpi=100, bbox_inches="tight"); plt.close(fig); print(f.name)
