#!/bin/bash
check() {
  dur=$(yt-dlp --skip-download --print "%(duration)s" "https://www.youtube.com/watch?v=$2" 2>/dev/null)
  printf "%-28s %-12s %ss\n" "$1" "$2" "$dur"
}

check 04_Candles              SuRgJd8ONIc
check 05_Time                 mBHtx-BfWWg
check 06_Liquidity_pt1        7HOAf7vHMqU
check 08_FVGs                 1McPSXSSR48
check 10_News                 j4f8fV13GQM
check 11_Liquidity_pt2        OtYATAfCfRA
check 13_IFVG                 ICOx4rdFSLg
check 15_Key_Levels           J7Dh-aj9-e0
check 19_Equilibrium          56ES-W1d0xw
check 21_Daily_Bias_DOL       MQyNBiw-QVo
check 23_Manipulation_legs    JO1xDEW2Lhg
check 25_Conditions_Sponsor   E3uwP18EYWI
check 26_TP_SL_RR             fTbf2EX6Cng
check 27_Journal              5Nn4woC6xrI
check 28_Sessions             CepE5r6rU00
check 29_Backtest_together    nxlZJ6abOYA
