# Pre-registro · VALIDACIÓN 2022/2024/2026 del SMT de Kasen · 04/10/2026

Escrito antes de ejecutar. Reglas congeladas tal cual se probaron en diseño (21/23/25):
- H2 · `scripts/kasen_pdh.py` con smt=True (PDH/PDL + apertura 10:00 + SMT con ES), 1:1,5.
  Diseño: +0,139R, wr 48,3%, n=116.
- H3 · `src/motores/kasen.py` con exigir_smt=True (vela 4H + SMT + IFVG), 1:2.
  Diseño: +0,053R, wr 37%, n=292.
Uso nº8 del protocolo (umbral por idea 0,05/8) con 2 hipótesis → p < 0,0031 (una cola) cada una,
R > 0 en los 3 años de validación, y mejor que la misma regla sin SMT.
Informativo: los otros ratios. Las hipótesis de 2019-2020 siguen en pie aparte.
Expectativa dicha antes: con ~60 (H2) y ~150 (H3) operaciones, solo un efecto grande pasa.
