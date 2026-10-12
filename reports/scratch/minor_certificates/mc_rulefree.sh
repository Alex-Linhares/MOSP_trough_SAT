#!/bin/bash
# Rule-free refutation (vsmemo -o), its closure certificate, and the independent check (checkF).
# usage: bash mc_rulefree.sh CLAIM W     (keeps the certificate xz-compressed if under 50 MB)
set -e
cd "$(dirname "$0")"
C=$1; W=$2; WORK=${MC_WORK:-/tmp/claude-1000/-home-al-dev-MOSP/9d06bf97-8c6f-4e88-9a63-b522dee867f8/scratchpad/work}
mkdir -p "$WORK" proofs
F=$WORK/${C}_w${W}.F
s=$( { /usr/bin/time -f "%e s %M KB" ./vsmemo ${C}_edges.txt $W -o -w $F -t 7200 -m 600000000 ; } 2>&1 | tr '\n' ' ')
echo "$(date '+%F %T') vsmemo $C w=$W: $s" >> results.log
c=$( { /usr/bin/time -f "%e s %M KB" ./checkF ${C}_edges.txt $W $F ; } 2>&1 | tr '\n' ' ')
h=$(sha256sum $F | cut -c1-64); raw=$(stat -c %s $F)
echo "$(date '+%F %T') checkF $C w=$W: $c certificate sha256=$h raw=$raw bytes" >> results.log
xz -T1 -9 -k -f $F; z=$(stat -c %s $F.xz)
if [ $z -lt 50000000 ]; then mv $F.xz proofs/${C}_w${W}.F.xz; echo "$(date '+%F %T') kept $C w=$W: xz $z bytes -> proofs/${C}_w${W}.F.xz" >> results.log
else echo "$(date '+%F %T') not kept $C w=$W: xz $z bytes" >> results.log; rm $F.xz; fi
rm -f $F
