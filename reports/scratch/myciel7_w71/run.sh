#!/bin/bash
# Search for a width-71 layout of myciel7 (the A001629 conjecture predicts pw = 71),
# by simulated annealing, forever, at nice 19. Owner's request, 2026-10-18.
# Rounds of 6 h; each restarts from its own best order with a fresh seed.
# Stops as soon as a layout of vertex separation <= 71 is found, and saves it.
#   run.sh SEEDBASE
set -u
D=$(cd "$(dirname "$0")" && pwd)
A=$D/../minor_certificates
E=$A/myciel7_full_edges.txt
base=$1; best=$D/best_$base.txt
[ -s "$best" ] || cp $A/myciel7_w72_order.txt "$best"
r=0
while true; do
  r=$((r + 1)); seed=$((base * 100000 + r))
  out=$D/round_${base}_$r.out
  $A/vsanneal $E $seed 21600 "$best" > $out
  vs=$(grep -o -E "best vs=[0-9]+" $out | grep -o -E "[0-9]+$")
  echo "$(date '+%F %T') chain $base round $r seed $seed: best vs=$vs" >> $D/run.log
  grep "^order:" $out | sed 's/^order: //' > $D/cand_$base.txt
  [ -s $D/cand_$base.txt ] && cp $D/cand_$base.txt "$best"
  if [ -n "$vs" ] && [ "$vs" -le 71 ]; then
    cp "$best" $D/FOUND_w${vs}_$base.txt
    echo "$(date '+%F %T') chain $base: FOUND a layout of width $vs" >> $D/run.log
    exit 0
  fi
done
