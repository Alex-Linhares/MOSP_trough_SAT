#!/bin/bash
# myciel7: rule-free probes of pw <= 71 on larger minors (a refutation would give pw >= 72).
cd "$(dirname "$0")"
for c in myciel7_m120_min-d myciel7_m130_min-d myciel7_m130_least-c myciel7_m140_min-d; do
  s=$( { /usr/bin/time -f "%e s %M KB" ./vsmemo ${c}_edges.txt 71 -o -t 3600 -m 250000000 ; } 2>&1 | cut -c1-160 | tr '\n' ' ')
  echo "$(date '+%F %T') vsmemo $c w=71: $s" >> results.log
done
