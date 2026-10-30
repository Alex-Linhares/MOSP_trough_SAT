#!/bin/bash
# N=25..27 exhaustive, 4-way gentreeg res/mod split, trees with pw >= 4 printed (none expected: K(N)=3 to N=66)
cd /home/al/dev/MOSP/reports/scratch/tree_bound
for n in 28; do
  s=$(date +%s)
  for r in 0 1 2 3; do nauty-gentreeg -p -q $n $r/4 | nice -n 19 ./treepw -p 4 > exh_${n}_$r.txt & done; wait
  cat exh_${n}_*.txt | awk '/^hist/{split($2,a,"=");split($3,b,"=");split($4,c,"=");h[b[2]]+=c[2]} /^pw/{print} END{for(k in h) printf "hist n='$n' pw=%s count=%d\n",k,h[k]}' | sort > exh_$n.txt
  echo "N=$n done in $(( $(date +%s) - s )) s: $(grep hist exh_$n.txt | tr '\n' ';') pw>=4 trees: $(grep -c '^pw' exh_$n.txt)"
  rm exh_${n}_*.txt
done
