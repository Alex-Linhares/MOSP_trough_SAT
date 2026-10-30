#!/bin/bash
cd /home/al/dev/MOSP/reports/scratch/increment_witness
for a in "hypercube 3" "hypercube 4" "hypercube 5" "mycielski 4" "mycielski 5" "mycielski 6" "mycielski 7" "ternary 2" "ternary 3" "ternary 4"; do
  for prot in 0 1; do
    nice -n 19 python3 search.py $a min-d $prot 0 1 0 120 > /dev/null 2>> small_all.err
  done
done
echo DONE >> small_all.err
