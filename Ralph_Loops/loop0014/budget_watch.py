#!/usr/bin/env python3
"""Sum the per-session costs loop0014's driver logs and set knobs.json stop=true past the owner's budget."""
import json, re, time, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
LOG, KNOBS, PIDFILE = HERE / "loop.log", HERE / "knobs.json", HERE / "driver.pid"
BUDGET = 1500.0
driver = int(PIDFILE.read_text()) if PIDFILE.exists() else int(sys.argv[1])
while True:
    total = sum(float(m) for m in re.findall(r"cost \$([0-9.]+)", LOG.read_text())) if LOG.exists() else 0.0
    (HERE / "budget.txt").write_text(f"{time.strftime('%F %T')} summed cost ${total:.2f} of ${BUDGET:.0f}\n")
    if total > BUDGET:
        k = json.loads(KNOBS.read_text()); k["stop"] = True
        KNOBS.write_text(json.dumps(k, indent=2) + "\n")
        (HERE / "budget.txt").write_text(f"{time.strftime('%F %T')} BUDGET EXCEEDED: ${total:.2f}; stop set\n")
        break
    try:
        os.kill(driver, 0)
    except OSError:
        break
    time.sleep(300)
