#!/bin/bash
cd "$(dirname "$0")"
for cw in myciel6_m58:37 myciel6_m60:37 Random-125-125-2-3_0_m70:19 myciel7_m110:70 SP4_m96:51 Random-125-125-6-1_0_m120:79 Random-125-125-2-1_0_m87:22; do
  bash mc_rulefree.sh ${cw%:*} ${cw#*:}
done
