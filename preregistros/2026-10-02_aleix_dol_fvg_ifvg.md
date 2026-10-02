# Pre-registro · Aleix Andreu: DOL + FVG 15m + IFVG 1m · 02/10/2026

Escrito antes de ejecutar. DISEÑO: CFD 2021/2023/2025. Versión mecánica del vídeo
(el autor decide el DOL a ojo; esta es una lectura fija y declarada, regla F).

## Regla (todo causal; vela de 15 min conocida al terminar su último minuto)
- Velas de 15 min agrupando las de 1 min de la sesión (desde las 18:00).
- FVG de 15 min alcista en la vela k: L[k] > H[k−2] (zona [H[k−2], L[k]]);
  bajista: H[k] < L[k−2] (zona [H[k], L[k−2]]). Invalidado cuando una vela de
  15 min posterior CIERRA al otro lado de la zona.
- **DOL / sesgo a las 09:30**: el FVG de 15 min más reciente que siga válido.
  Su dirección es el sesgo; su zona es la zona de reacción.
- **Retroceso**: primera vela de 1 min entre 09:30 y 11:00 que toca la zona
  (l ≤ techo de zona si alcista; h ≥ suelo si bajista). Si antes una vela de
  15 min invalida la zona, no hay operación.
- **IFVG 1 min**: tras el toque, un FVG de 1 min en contra del sesgo nacido
  después del toque, invertido por un cierre de 1 min a favor del sesgo.
  Entrada al cierre de esa vela (≤ 11:00). Stop: extremo desde el toque
  (revalidado). Riesgo mínimo 0,05% del precio.
- Objetivo 1,5R (el del vídeo) y, informativo, 1R y 2R. Cierre 11:59.

## Criterio (a 1,5R; los otros dos ratios cuentan para Bonferroni: p < 0,0167)
R > 0 con p < 0,0167 (una cola), positiva en los 3 años, por encima del paseo
aleatorio (6 semillas), invertida no positiva.

## Aparte: la gestión del vídeo (no es una variante de estrategia)
Cuenta 50K (MLL $2.000, objetivo $3.000) arriesgando $1.000 a 1:1,5 frente a
$500 a 1:1,5, con ventaja cero y con +0,10R, en el simulador de cuentas.
