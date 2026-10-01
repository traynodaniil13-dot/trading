# Pre-registro · Oro · Ruptura del rango asiático como estrategia · 01/10/2026

Escrito tras ver que la premisa G4 pasa en DISEÑO (`2026-10-01_oro_lote1.md`,
+1,04 pts, p=0,0011, 4/4 años, z=2,85; neutral a la deriva +0,99) y ANTES de
calcular ninguna estrategia. Auditoría hecha: cruce a mano de 1 día idéntico al
script. Señal: la de G4, sin tocar. Ojo declarado: la continuación es mucho más
fuerte del lado de la tendencia del año (cortos en 2011/13/15, nada en 2017).

## Variantes (2), para la regla B (riesgo fijo, objetivo 2R)
- **E1 · stop en el punto medio del rango asiático.** Objetivo 2R, cierre 11:59 NY.
- **E2 · stop en el lado opuesto del rango asiático.** Objetivo 2R, cierre 11:59.
Ambas: se salta el día si la distancia < 0,10% del precio o si la entrada ya
está al otro lado del stop (regla 5). Coste 0,30 pts. Motor común (`src/motor.py`).

## DISEÑO 2011/2013/2015/2017 — pasa a validación la mejor que cumpla todo
R > 0 con p < 0,025 (0,05/2), ≥ 3 de 4 años positivos, z de exceso sobre paseo
aleatorio (6 semillas) > 2, invertida ≤ 0.

## VALIDACIÓN 2012/2014/2016/2018-S1 — una sola ejecución
Idea nº7 del protocolo → p < 0,05/7 = 0,0071. Además: ≥ 3 de 4 periodos
positivos, y la premisa G4 desnuda con el mismo signo en validación (paso 6).
Si falla, el oro queda como "premisa viva sin estrategia" y no se retoca nada.

## Resultado DISEÑO (01/10): ninguna pasa
E1 −0,050R p=0,87 · E2 +0,044R p=0,10, 2017 −0,056, z=+3,09 sobre su nulo (−0,076).

## Añadido POST HOC (01/10, escrito tras ver E1/E2) — variante E3
El objetivo 2R recorta la premisa (que es "aguanta hasta las 11:59"). Se declara
**E3 · stop en el lado opuesto del rango, SIN objetivo, cierre 11:59.** Variante
nº3 de la familia → umbral de diseño p < 0,05/3 = 0,0167, mismas demás
condiciones. Es post hoc: si pasa, la validación lo descuenta igual (p < 0,0071).

## Resultado E3 (01/10): NO PASA por poco
+0,087R p=0,0195 (umbral 0,0167), 2017 −0,046, z=+3,79, invertida −0,121.
Validación SIN gastar. Estado: premisa viva sin estrategia aprobada.
