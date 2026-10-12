"""Refute pw(H) <= w with the independent CNF (mc_sat.encode), standalone
CaDiCaL 2.1.2 with binary DRAT proof, checked by tools/drat-trim.

  python mc_refute.py CLAIM K [--no-check] [--lrat]
CLAIM is a certificate stem (CLAIM_edges.json). Work files go to
$MC_WORK (default the session scratchpad); the result line is appended to
results.log here; proofs are compressed with xz into proofs/ when < 50 MB.
"""
import hashlib, json, os, subprocess, sys, time
from pathlib import Path
from mc_sat import encode

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAD = "/home/al/.elan/toolchains/leanprover--lean4---v4.29.0/bin/cadical"
DRAT = ROOT / "tools/drat-trim/drat-trim"
WORK = Path(os.environ.get("MC_WORK", "/tmp/claude-1000/-home-al-dev-MOSP/9d06bf97-8c6f-4e88-9a63-b522dee867f8/scratchpad/work"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def log(line):
    with open(HERE / "results.log", "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + line + "\n")
    print(line, flush=True)


def main():
    claim, k = sys.argv[1], int(sys.argv[2])
    check = "--no-check" not in sys.argv
    lrat = "--lrat" in sys.argv
    WORK.mkdir(parents=True, exist_ok=True)
    E = [tuple(e) for e in json.load(open(HERE / f"{claim}_edges.json"))]
    n = 1 + max(max(e) for e in E)
    F, _ = encode(n, E, k)
    stem = f"{claim}_k{k}"
    cnf = WORK / f"{stem}.cnf"
    F.dimacs(cnf, comment=f"{claim}: vertex separation <= {k}? m={n} edges={len(E)} (mc_sat.py)")
    ch = sha(cnf)
    proof = WORK / f"{stem}.{'lrat' if lrat else 'drat'}"
    log(f"start {stem}: {F.nv} vars {len(F.cl)} clauses cnf_sha256={ch}")
    t0 = time.time()
    args = [CAD, "-q", str(cnf), str(proof)] + (["--lrat=true"] if lrat else [])
    r = subprocess.run(args, capture_output=True, text=True)
    secs = time.time() - t0
    verdict = {10: "SAT", 20: "UNSAT"}.get(r.returncode, f"rc{r.returncode}")
    psize = proof.stat().st_size if proof.exists() else 0
    log(f"solved {stem}: {verdict} in {secs:.1f}s, proof {psize/1e6:.1f} MB")
    if verdict != "UNSAT":
        if proof.exists():
            proof.unlink()
        return
    if check:
        t1 = time.time()
        if lrat:
            chk = [str(HERE / "lrat-check"), str(cnf), str(proof)]
        else:
            chk = [str(DRAT), str(cnf), str(proof), "-t", "200000"]
        c = subprocess.run(chk, capture_output=True, text=True)
        out = (c.stdout + c.stderr).strip().splitlines()
        ok = any(l.strip() in ("s VERIFIED", "c VERIFIED") or "VERIFIED" in l and "NOT" not in l for l in out)
        log(f"checked {stem}: {'VERIFIED' if ok else 'NOT VERIFIED'} by {'lrat-check' if lrat else 'drat-trim'} "
            f"in {time.time()-t1:.1f}s; last: {' | '.join(out[-2:])}")
    xz = HERE / "proofs" / f"{stem}.{'lrat' if lrat else 'drat'}.xz"
    xz.parent.mkdir(exist_ok=True)
    ps = sha(proof)
    subprocess.run(["xz", "-T1", "-6", "-k", "-f", str(proof)], check=True)
    zs = Path(str(proof) + ".xz").stat().st_size
    if zs < 50e6:
        os.replace(str(proof) + ".xz", xz)
        log(f"kept {stem}: proof sha256={ps} raw {psize/1e6:.1f} MB, xz {zs/1e6:.1f} MB -> {xz.relative_to(ROOT)}")
    else:
        log(f"not kept {stem}: proof sha256={ps} raw {psize/1e6:.1f} MB, xz {zs/1e6:.1f} MB (over 50 MB)")
    proof.unlink()


if __name__ == "__main__":
    main()
