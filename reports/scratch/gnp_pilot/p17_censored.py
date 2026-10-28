"""Exact treewidth of the pilot graphs pwtw.py left censored, by p17's grtd -m 64 (PACE 2017
exact-track winner, built in tools/p17; see tools/README.md).  Each graph: .gr from its seed,
grtd under a cap, the printed decomposition checked by check_td.py (so the width is a verified
upper bound; the lower half rests on grtd's iterative deepening, cross-checked on 120 graphs
with an independently proved treewidth, 120 agreements).  Resumable by key.
    nohup nice -n 19 python3 p17_censored.py --procs 8 --cap 600 > p17_censored.log 2>&1 &
Output: p17_censored.csv with n, c, sample, seed, pw, tw_lo, tw_hi (from pwtw.csv), grtd_tw, valid, seconds, status.
"""
import argparse, csv, subprocess, sys, time, tempfile, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
GRTD = HERE.parents[2] / "tools/p17/grtd.bin"
OUT = HERE / "p17_censored.csv"
FIELDS = ["n", "c", "sample", "seed", "pw", "tw_lo", "tw_hi", "grtd_tw", "valid", "seconds", "status"]


def one(r, cap):
    key = (r["n"], r["c"], r["sample"])
    gr = subprocess.run([sys.executable, str(HERE / "to_gr.py"), *key], capture_output=True, text=True).stdout
    row = {k: r[k] for k in ("n", "c", "sample", "seed", "pw", "tw_lo", "tw_hi")}
    row.update(grtd_tw="", valid="", seconds="", status="")
    t = time.time()
    try:
        p = subprocess.run(["nice", "-n", "19", str(GRTD), "-m", "64"], input=gr, capture_output=True, text=True, timeout=cap)
    except subprocess.TimeoutExpired:
        row.update(seconds=round(time.time() - t, 1), status="timeout"); return row
    row["seconds"] = round(time.time() - t, 1)
    s = [l for l in p.stdout.splitlines() if l.startswith("s td")]
    if not s:
        row["status"] = "no result"; return row
    row["grtd_tw"] = int(s[0].split()[3]) - 1
    with tempfile.TemporaryDirectory() as d:
        Path(d, "g.gr").write_text(gr); Path(d, "g.td").write_text(p.stdout)
        chk = subprocess.run([sys.executable, str(HERE / "check_td.py"), f"{d}/g.gr", f"{d}/g.td"], capture_output=True, text=True)
    row["valid"] = chk.returncode == 0 and f"width {row['grtd_tw']}," in chk.stdout
    lo, hi = int(r["tw_lo"]), int(r["tw_hi"])
    row["status"] = "ok" if row["valid"] and lo <= row["grtd_tw"] <= hi else "CONFLICT" if row["valid"] else "invalid td"
    return row


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--procs", type=int, default=8); ap.add_argument("--cap", type=float, default=600)
    a = ap.parse_args()
    src = [r for r in csv.DictReader(open(HERE / "pwtw.csv")) if r["exact"] != "True"]
    done = {(r["n"], r["c"], r["sample"]) for r in csv.DictReader(open(OUT))} if OUT.exists() else set()
    jobs = [r for r in src if (r["n"], r["c"], r["sample"]) not in done]
    jobs.sort(key=lambda r: (int(r["n"]), float(r["c"])))
    new = not OUT.exists()
    print(f"{len(jobs)} censored graphs, {a.procs} procs, cap {a.cap}s", flush=True)
    with open(OUT, "a", newline="") as f, ThreadPoolExecutor(a.procs) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new: w.writeheader(); f.flush()
        for k, row in enumerate(ex.map(lambda r: one(r, a.cap), jobs), 1):
            w.writerow(row); f.flush()
            if row["status"] != "ok" or k % 100 == 0:
                print(k, row["n"], row["c"], row["sample"], row["status"], row["grtd_tw"], row["seconds"], flush=True)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
