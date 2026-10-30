#!/bin/bash
cd /home/al/dev/MOSP/reports/scratch/increment_witness
for k in 5 6; do
  nice -n 19 python3 search.py mycielski $k min-d 0 0 1 1 120 > /dev/null 2>> myc_variants.err
  nice -n 19 python3 search.py mycielski $k least-c 0 0 1 1 120 > /dev/null 2>> myc_variants.err
  for s in 1 2 3 4; do nice -n 19 python3 search.py mycielski $k random 0 $s 1 1 120 > /dev/null 2>> myc_variants.err; done
done
nice -n 19 python3 search.py mycielski 4 min-d 0 0 1 1 120 > /dev/null 2>> myc_variants.err
echo DONE_A >> myc_variants.err
