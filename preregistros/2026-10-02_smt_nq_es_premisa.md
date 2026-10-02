# Pre-registro · Premisa SMT NQ-ES (carrera a barreras, sin salida por tiempo) · 02/10/2026

Escrito antes de ejecutar. Familia NUEVA (CLAUDE.md §9: "relaciones entre índices").
Petición de Daniil: ventaja que venga de tocar TP antes que SL, no de cierres por hora.
Regla Q: se mide la premisa desnuda. DISEÑO: CFD 2021/2023/2025 (NQ y ES Dukascopy).

## Evento (todo causal, barras de 1 min conocidas al cerrar)
- Niveles: máximo y mínimo overnight (18:00-09:29) de NQ y de ES, por separado.
- Ventana 09:30-11:00. Primera barra en la que NQ rompe su mínimo overnight (l < mín ON)
  o su máximo (h > máx ON). Si rompe los dos en la misma barra, fuera.
- **SMT**: en esa misma barra ES NO ha roto su nivel equivalente (ni en esa barra ni
  antes en la ventana). **Sin SMT**: ES sí lo ha roto.
- Dirección: reversión (rotura de mínimo → largo; de máximo → corto).

## Medida (premisa desnuda, regla Q y nº12)
Desde el cierre de la barra del evento, carrera a barreras SIMÉTRICAS ±k% del precio,
hasta las 15:59. Se cuenta: % que toca primero la barrera a favor, % en contra, % sin
resolver (se reporta, no cuenta). En la barra que toca las dos, gana la contraria.
k ∈ {0,20 · 0,30 · 0,40}%. Separado por dirección (regla M).

## Criterio (3 variantes → p < 0,0167, una cola, binomial sobre resueltas)
SMT pasa si, en algún k: % a favor > 50% con p < 0,0167, > 50% en largos Y en cortos,
y mayor que el grupo "sin SMT" (control: misma rotura, sin divergencia).
Si pasa, se diseña la estrategia (pre-registro aparte). Si no, la familia SMT se cierra.
