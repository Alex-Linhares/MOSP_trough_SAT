#!/bin/bash
# myciel7 (refute 71) and W4 (refute 26) in the C program, a 4-way portfolio each,
# nice 19, no time limit, started 2026-10-18 at the owner's request after the
# Python runs were stopped. Each starts from the stored layout and the proved floor.
#   A large minor budget (the owner's large config of 2026-10-12)
#   B minor-heavy (W4 run B's config): sizes 50-97% in 2% steps, unlimited budget
#   C default minor config: reaches the full refutation soonest
#   D large minors: sizes 85-99% in 1% steps, 5e9 nodes
P=/home/al/dev/MOSP/pathwidth_solver/cli/pathwidth
declare -A CFG=(
  [A]="-m first_nodes=1000000 -m total_nodes=500000000"
  [B]="-m first_nodes=1000000 -m total_nodes=1000000000000000 -m share=1.0 -m max_fraction=0.97 -m step_fraction=0.02"
  [C]=""
  [D]="-m first_nodes=1000000 -m total_nodes=5000000000 -m start_fraction=0.85 -m max_fraction=0.99 -m step_fraction=0.01"
)
cd "$(dirname "$0")"
for g in myciel7:71 w4:26; do
  name=${g%%:*}; low=${g##*:}
  for c in A B C D; do
    out=${name}_${c}
    echo "$(date '+%F %T') start $out: refute $low, ${CFG[$c]:-default minor config}" >> run.log
    nohup nice -n 19 bash -c "$P -t 0 -l -v -u ${name}_seed.txt -L $low ${CFG[$c]} < ${name}.g6 > $out.out 2> $out.err; echo \"\$(date '+%F %T') done $out: \$(head -1 $out.out)\" >> run.log" > /dev/null 2>&1 &
    echo "$! $out" >> pids.txt
  done
done
