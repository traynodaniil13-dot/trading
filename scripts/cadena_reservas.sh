#!/bin/bash
# Cadena desatendida: reserva ciega Magalá → réplica Magalá 28 pares → reserva ciega Momento 2019-2020.
cd /home/user/trading
S=/tmp/claude-0/-home-user-trading/44b87bee-7c3d-51c4-85bb-d06929b2cabf/scratchpad
subir() {
  git add -A resultados "$@" >/dev/null 2>&1
  git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01PGgAZivskymc8E8XKfF6bZ" && \
  for i in 1 2 3 4; do git push -q -u origin claude/sharp-shannon-8r7cs4 && break; sleep $((2**i)); done
}
until grep -qE "filas|Traceback|RuntimeError" $S/fxciego.log 2>/dev/null; do sleep 60; done
python -m scripts.magala_28_ciego ciego > resultados/2026-10-04_magala_reserva_ciega_2018_2020.txt 2>&1
MSG="Magalá: reserva ciega 2018-2020 con los 28 pares reales (resultado)"; subir
until grep -qE "filas|Traceback|RuntimeError" $S/fx28.log 2>/dev/null; do sleep 60; done
python -m scripts.magala_28_ciego > resultados/2026-10-04_magala_28_pares_replica_y_ciego.txt 2>&1
MSG="Magalá: réplica 2021-2025 con los 28 pares reales (resultado)"; subir data/fx_diario.csv.gz data/fx_diario_2017_2020.csv.gz
python -m scripts.descargar_dukascopy USATECHIDXUSD nq_cfd 2020 2020 > $S/desc2020.log 2>&1
python -m scripts.reserva_2019_2020 > resultados/2026-10-05_reserva_ciega_2019_2020.txt 2>&1
MSG="Reserva ciega 2019-2020: Momento 09:40 y H4 Aleix (resultado)"; subir data/nq_cfd_2020.csv.gz
echo FIN > $S/cadena.fin
