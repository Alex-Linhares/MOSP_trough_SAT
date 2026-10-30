#!/bin/bash
cd /home/al/dev/MOSP/reports/scratch/increment_witness
nice -n 19 python3 search.py mycielski 7 min-d 0 0 1 1 120 > /dev/null 2>> myc_variants.err
nice -n 19 python3 search.py mycielski 7 least-c 0 0 1 1 120 > /dev/null 2>> myc_variants.err
for s in 1 2; do nice -n 19 python3 search.py mycielski 7 random 0 $s 1 1 120 > /dev/null 2>> myc_variants.err; done
echo DONE_B >> myc_variants.err
