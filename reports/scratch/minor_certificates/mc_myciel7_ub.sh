#!/bin/bash
# myciel7: simulated annealing for a width-71 layout (upper bound side).
cd "$(dirname "$0")"
for s in 1 2 3; do
  ./vsanneal myciel7_full_edges.txt $s 900 > myciel7_anneal_s$s.out
  echo "$(date '+%F %T') vsanneal myciel7 seed $s 900s random start: $(head -1 myciel7_anneal_s$s.out)" >> results.log
done
./vsanneal myciel7_full_edges.txt 4 900 myciel7_w72_order.txt > myciel7_anneal_s4.out
echo "$(date '+%F %T') vsanneal myciel7 seed 4 900s from the w72 layout: $(head -1 myciel7_anneal_s4.out)" >> results.log
