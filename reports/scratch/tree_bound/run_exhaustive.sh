#!/bin/bash
# exhaustive pw of all trees on N vertices, N=17..24, printing trees with pw >= 3
cd /home/al/dev/MOSP/reports/scratch/tree_bound
for n in 17 18 19 20 21 22 23 24; do
  s=$(date +%s)
  nauty-gentreeg -p -q $n | nice -n 19 ./treepw -p 3 > exh_$n.txt
  echo "N=$n done in $(( $(date +%s) - s )) s: $(grep hist exh_$n.txt | tr '\n' ';') pw>=3 trees: $(grep -c '^pw' exh_$n.txt)"
done
