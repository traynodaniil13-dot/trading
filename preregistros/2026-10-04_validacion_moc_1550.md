# Pre-registro · Validación de F4 (desequilibrio de cierre 15:50) · 04/10/2026

Escrito ANTES de ejecutar. Regla congelada tal cual en `scripts/lote6_fomc_datos.py`:
signo(c 15:52 − c 15:49) → dirección; carrera ±0,10% desde c 15:52 hasta 15:59.

- **Datos:** CFD 2022/2024/2026 (2026 hasta el 23/09), nunca usados para esta idea.
  **Uso nº10 de la validación → p < 0,05/10 = 0,005**, binomial de una cola (continuación,
  la dirección quedó fijada en diseño).
- **Para pasar:** p < 0,005, > 50% en los 3 años, y largos y cortos > 50%.
- **Informativo:**
  - Como estrategia: entrada en c 15:52, stop y TP a ±0,10%, cierre a las 15:59, coste 0,87
    pts → R neta. Con coste ×2 también, por el diferencial al cierre.
  - El mismo test en el futuro NQ real 2023-25 (Kaggle), para ver si aparece en el
    instrumento que se opera.
Expectativa dicha antes: la caída de 2025 en diseño (48,5%) apunta a que no pasará.
