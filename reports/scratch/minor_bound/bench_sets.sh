#!/bin/bash
# The benchmark sets with the minor step on and off, 60 s per graph.
# usage: bench_sets.sh on|off PROCS SET...
cd /home/al/dev/MOSP/pathwidth_solver
mode=$1; procs=$2; shift 2
for set in "$@"; do
  extra=""
  [ "$set" = "vsplib-grids" ] && extra="--limit 12"
  if [ "$set" = "rome-sample" ]; then
    python3 bench/run.py rome --names ../reports/scratch/minor_bound/rome_sample.txt --time 60 --procs $procs \
      --minor $mode --out ../reports/scratch/minor_bound/bench_rome-sample_$mode.csv
  else
    python3 bench/run.py $set --time 60 --procs $procs --minor $mode $extra \
      --out ../reports/scratch/minor_bound/bench_${set}_$mode.csv
  fi
done
