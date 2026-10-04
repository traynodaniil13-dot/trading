# Pre-registro · Piramidaje vs entrada única vs promedio a la baja (INVESTCOIN) · 04/10/2026

Escrito ANTES de ejecutar. Fuente: youtube khhRndi88zI (resumen pasado por Daniil). Es gestión de
posición para cripto al contado a medio plazo. No hay datos de cripto: se prueba en velas
diarias de NQ y ES (CFD, dic-2020 a sep-2026) y de los 28 pares de divisas (2020-2025, cruces
sintéticos), **solo largos** como en spot. No es operable en Lucid (mantiene días o semanas):
se mide la afirmación del autor.

## Mecánica común (diario)
- ATR14 = media simple del rango verdadero. Resistencia = máximo de las 20 sesiones previas (sin
  la actual).
- **Ruptura:** cierre del día t > resistencia R. **Primera compra en el retesteo:** orden límite
  en R, viva los días t+1 a t+5. Se llena si el mínimo ≤ R, a min(apertura, R). SL = R − 0,5·ATR(t).
- **Trailing (las tres variantes):** cada ruptura nueva con nivel R' > el último nivel sube el stop
  de toda la posición a R' − 0,5·ATR, si queda por encima del stop actual.
- **Salida:** si el mínimo ≤ stop, sale todo a min(apertura, stop). El día del relleno solo
  cuenta el stop (pesimista).
- **Resultado** en unidades de R0 = (entrada − SL) de la primera compra. Unidades del mismo
  tamaño.

## Variantes
- **A. Entrada única:** 1 unidad con el trailing.
- **B. Piramidaje (el autor):** en cada ruptura nueva con la posición abierta, se añade 1 unidad
  en el retesteo del nuevo nivel (orden límite 5 días), hasta 3 unidades. El stop de todas sube
  al nuevo soporte. Así, al añadir la 2ª, la 1ª queda en beneficio.
- **C. Promedio a la baja:** misma primera compra. Se añaden unidades con órdenes límite a
  entrada − 1·ATR y entrada − 2·ATR, hasta 3. Stop de todo a entrada − 3·ATR (el trailing por
  rupturas lo puede subir).

## Hipótesis (2 contrastes → p < 0,025)
- **H1:** B > A, emparejado por setup (t de una cola sobre la diferencia).
- **H2:** B tiene ventaja de seguimiento de tendencia: resultado medio por setup mayor que en
  las series barajadas (días reordenados al azar, lo que conserva la volatilidad y destruye la
  tendencia; 50 barajados) con z > 2.
- **Informativo:** C frente a A y B (media, peor operación y drawdown máximo de la suma por
  fecha), por mercado (índices / divisas) y por año.
