"""Checker run over pass 1's four closures and pass 1b's 96 floors (2026-11-03, after the 18:10 kill of the
session that planned it).  Each certificate goes through `paper1/obstruction_check.py check-minor` as a
subprocess (own replay, hash, C re-run at the search's 20 s cap; rule-free where the minor has <= 80
vertices), eight at a time, nice 19.  Outputs: check_pass1.jsonl (the checker's full JSON per certificate)
and check_pass1.csv (one summary row each).  After the run the pass 1b certificates were moved to
`certificates_1b/` (git-ignored) and the paths in check_pass1.jsonl rewritten; to re-run, point `d` there for pass 1b."""
import json, subprocess, sys, time
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[3]

def run(t):
    which, cid = t
    d = HERE / "certificates" / cid
    t0 = time.monotonic()
    p = subprocess.run(["nice", "-n", "19", sys.executable, str(ROOT / "paper1/obstruction_check.py"), "check-minor",
                        str(d / "instance.txt"), str(d / "minor.json"), "--c-cap", "20", "--json"],
                       capture_output=True, text=True, cwd=ROOT)
    try:
        res = json.loads(p.stdout)
    except json.JSONDecodeError:
        res = {"verdict": "error", "stderr": p.stderr[-2000:], "stdout": p.stdout[-500:]}
    res.update({"id": cid, "pass": which, "wall_seconds": round(time.monotonic() - t0, 1), "returncode": p.returncode})
    return res

def main():
    jobs = [("1", i) for i in pd.read_csv(HERE / "results_pass1.csv")["id"]]
    jobs += [("1b", i) for i in pd.read_csv(HERE / "pass1b.csv")["id"]]
    print(f"{time.strftime('%F %T')} checking {len(jobs)} certificates, 8 workers", flush=True)
    rows = []
    with Pool(8) as pool, open(HERE / "check_pass1.jsonl", "w") as out:
        for k, r in enumerate(pool.imap_unordered(run, jobs, chunksize=1), 1):
            out.write(json.dumps(r) + "\n"); out.flush()
            row = dict(id=r["id"], **{"pass": r["pass"]}, verdict=r.get("verdict"), n=r.get("n"), m=r.get("m"),
                       claim=(r.get("proves") or {}).get("pathwidth_at_least"), floor=r.get("floor_claimed"),
                       c_status=r.get("c_status"), c_width=r.get("c_width"), c_lower=r.get("c_lower"),
                       c_seconds=r.get("c_seconds"), rulefree=r.get("rulefree"), contradiction=r.get("contradiction", False),
                       failed=[c["check"] for c in r.get("checks", []) if not c["ok"]], wall_seconds=r["wall_seconds"])
            rows.append(row)
            print(f"{time.strftime('%T')} {k}/{len(jobs)} {r['id']} pass {r['pass']} {row['verdict']} m={row['m']} floor {row['floor']} "
                  f"C {row['c_status']} w={row['c_width']} lower={row['c_lower']} rulefree={row['rulefree']} {row['wall_seconds']}s", flush=True)
    pd.DataFrame(rows).to_csv(HERE / "check_pass1.csv", index=False)
    v = pd.DataFrame(rows)["verdict"].value_counts().to_dict()
    print(f"{time.strftime('%F %T')} done: {v}", flush=True)

if __name__ == "__main__":
    main()
