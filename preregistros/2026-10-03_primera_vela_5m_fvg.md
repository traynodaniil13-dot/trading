# Pre-registro · "Regla de la primera vela" (rango 5m + FVG 1m + envolvente) · 03/10/2026

Escrito antes de ejecutar. Vídeo traído por Daniil. Versión mecánica (regla F: lectura
fija declarada; el vídeo no define dirección ni tamaño del desplazamiento).
DISEÑO CFD 2021/2023/2025. Familia emparentada con ORB (enterrado) y barrida+IFVG.

## Regla (causal)
- Rango: máximo/mínimo de las barras 09:30-09:34 (conocido a las 09:35).
- Desplazamiento: FVG de 1 min nacido en la barra i (09:37 ≤ i ≤ 11:00) a favor y con
  cierre de i fuera del rango: alcista (l[i] > h[i−2] y c[i] > máx rango) → largo;
  bajista (h[i] < l[i−2] y c[i] < mín rango) → corto. Se usa el PRIMERO del día.
- Retroceso: primera barra posterior que toca la zona del FVG (largo: l ≤ l[i]).
  Si antes una barra cierra al otro lado de la zona, no hay operación.
- Confirmación: desde el toque, primera vela envolvente a favor (largo: c>o, c ≥ o
  previa, o ≤ c previa y la previa bajista) antes de las 12:00 y sin invalidar la zona.
- Entrada al cierre de la envolvente (i_ent = k+1). Stop: extremo desde el toque
  (revalidado). Riesgo mínimo 0,05%. Objetivo 1:2 (el del vídeo). Cierre 15:59.

## Criterio (variante única: 1:2, continuación → p < 0,05 una cola)
R > 0 con p < 0,05, positiva en los 3 años, por encima del paseo aleatorio (6 semillas),
invertida ≤ 0. Informativo: 1:1 y 1:1,5, invertida (la lectura "reversión"), winrate,
y % de TP / SL / cierre a las 15:59 (lo que pide Daniil: que gane por TP, no por cierre).
