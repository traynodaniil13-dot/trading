#!/bin/bash
# Reserva ciega 2019-2020 de Momento 09:40 (y H4): termina de bajar NQ 2020 y ejecuta el script congelado.
cd /home/user/trading
S=/tmp/claude-0/-home-user-trading/44b87bee-7c3d-51c4-85bb-d06929b2cabf/scratchpad
python -m scripts.descargar_dukascopy USATECHIDXUSD nq_cfd 2020 2020 > $S/desc2020.log 2>&1
if [ -f data/nq_cfd_2020.csv.gz ]; then
  python -m scripts.reserva_2019_2020 > resultados/2026-10-05_reserva_ciega_2019_2020.txt 2>&1
  git add resultados/2026-10-05_reserva_ciega_2019_2020.txt data/nq_cfd_2020.csv.gz
  git commit -qm "Reserva ciega 2019-2020: Momento 09:40 y H4 Aleix (resultado)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01PGgAZivskymc8E8XKfF6bZ"
  for i in 1 2 3 4; do git push -q -u origin claude/sharp-shannon-8r7cs4 && break; sleep $((2**i)); done
fi
echo FIN > $S/cadena.fin
