#!/bin/bash
cd /home/al/dev/MOSP/reports/scratch/increment_witness
for s in $(seq 10 29); do nice -n 19 python3 search.py mycielski 5 random 0 $s 1 0 120 > /dev/null 2>> seeds_more.err; done
for s in $(seq 10 19); do nice -n 19 python3 search.py mycielski 6 random 0 $s 1 0 120 > /dev/null 2>> seeds_more.err; done
echo DONE >> seeds_more.err
