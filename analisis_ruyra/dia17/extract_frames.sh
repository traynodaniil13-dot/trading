#!/bin/bash
cd "$(dirname "$0")"
mkdir -p frames

extract() {
  ffmpeg -ss "$1" -i dia17.webm -frames:v 1 "frames/$2.png" -y 2>&1 | tail -1
}

extract 106  t1_46_smt_alcista1
extract 170  t2_50_reaccion
extract 280  t4_40_smt_bajista
extract 335  t5_35_hora_marcada
extract 384  t6_24_15m_ejemplo2
extract 420  t7_00_smt_doble_bajo
extract 530  t8_50_ejemplo3
extract 668  t11_08_bad_smt_nosentido
extract 753  t12_33_true_manip_buena
extract 1000 t16_40_nwog_ejemplo
extract 1150 t19_10_condicion3_invertido

echo "done"
