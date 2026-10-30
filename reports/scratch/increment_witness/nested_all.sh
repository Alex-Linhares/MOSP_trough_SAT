#!/bin/bash
cd /home/al/dev/MOSP/reports/scratch/increment_witness
for k in 5 6 7; do nice -n 19 python3 nested.py mycielski $k >> nested.log 2>&1; done
for h in 3 4; do nice -n 19 python3 nested.py ternary $h >> nested.log 2>&1; done
for d in 5 6; do nice -n 19 python3 nested.py hypercube $d >> nested.log 2>&1; done
echo DONE >> nested.log
