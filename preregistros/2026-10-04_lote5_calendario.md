# Pre-registro · Lote 5: efectos de calendario y flujos (TP-vs-SL) · 04/10/2026

Escrito antes de ejecutar. Familia NUEVA (calendario / flujos institucionales). DISEÑO CFD
2021/2023/2025. Medida: carrera a barreras simétricas ±k% (k = 0,25 · 0,40) desde la referencia
hasta 15:59; % de resueltas a favor. Todo derivable del propio calendario de sesiones (causal:
"último día del mes" y "víspera de festivo" se conocen de antemano por el calendario oficial).

| # | Evento | Referencia | d | Comparación (regla M) |
|---|---|---|---|---|
| C1 | Cambio de mes: último día hábil y 3 primeros | apertura 09:30 (cierre de 09:30) | largo | largos del resto de días |
| C2 | Víspera de festivo (el siguiente día laborable sin sesión) | 09:30 | largo | largos del resto de días |
| C3 | Vencimiento mensual (3er viernes): reversión de la 1ª hora | 10:30 | −signo(c10:29 − o09:30) | el mismo setup en el resto de viernes |
| C4 | Rebalanceo fin de mes: último día hábil | 15:00 | −signo(c14:59 − cierre del último día del mes anterior) | el mismo setup el resto de días |
(C4 usa barreras de 0,10 · 0,15% porque solo quedan 60 min.)

## Criterio (8 tests → p < 0,05/8 = 0,00625)
Diferencia de % a favor entre evento y comparación, test de proporciones una cola, p < 0,00625,
y el mismo signo en los 3 años. Si pasa, estrategia y validación 22/24/26 aparte.
