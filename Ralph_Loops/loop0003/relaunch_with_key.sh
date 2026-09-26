#!/bin/bash
# Waits for the running driver (by PID) to exit, clears the stop knob, and
# relaunches the loop with the API key from ~/.config/anthropic/api_key in the
# environment. The key is read here, never placed on a command line.
#
#   relaunch_with_key.sh <driver-pid>
cd /home/al/dev/MOSP || exit 1
L=Ralph_Loops/loop0003
DRIVER=${1:?driver pid required}
while kill -0 "$DRIVER" 2>/dev/null; do sleep 30; done
echo "[$(date '+%F %T')] driver $DRIVER exited; relaunching with API key" >> $L/loop.log
python3 - <<'PY'
import json; p='Ralph_Loops/loop0003/knobs.json'; k=json.load(open(p)); k['stop']=False
json.dump(k,open(p,'w'),indent=2); open(p,'a').write('\n')
PY
export ANTHROPIC_API_KEY="$(tr -d '\n' < ~/.config/anthropic/api_key)"
setsid nohup python Ralph_Loops/loop0003/loop.py >> $L/nohup.out 2>&1 < /dev/null &
NEW=$!
disown
sleep 5
if kill -0 "$NEW" 2>/dev/null; then
  echo "[$(date '+%F %T')] relaunched with API key: driver pid $NEW" >> $L/loop.log
else
  echo "[$(date '+%F %T')] RELAUNCH FAILED; see nohup.out" >> $L/loop.log
fi
