#!/usr/bin/env python3
"""Sum the per-session costs loop0015's driver logs and set knobs.json stop=true past the owner's budget."""
import json, re, time, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
LOG, KNOBS, PIDFILE = HERE / "loop.log", HERE / "knobs.json", HERE / "driver.pid"
BUDGET = 4000.0  # owner, 2026-11-05: $4,000 for loop0015 (TASK.md, plan §0.6; the comment said $2,500 until item 11)
driver = int(PIDFILE.read_text()) if PIDFILE.exists() else int(sys.argv[1])
while True:
    # `total_cost_usd` is cumulative within a session (one session_id, re-woken after each
    # background task), so a session's cost is the LAST `# result` line of its log, not the sum.
    total = 0.0
    for f in sorted(HERE.glob("session_*.log")):
        c = re.findall(r"cost \$([0-9.]+)", f.read_text())
        if c:
            total += float(c[-1])
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
