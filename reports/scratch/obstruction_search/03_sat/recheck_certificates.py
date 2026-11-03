"""Item 03: every certificate the run left under `certificates/<instance>/`
through `paper1/obstruction_check.py::check_expansion` (the checker that
shares nothing with the search but the contract), one row each in
`checker_verdicts.csv`: instance, certificate path, (t, b), the bound it
proves, the checker's verdict and seconds. Run as
`nice -n 19 python3 reports/scratch/obstruction_search/03_sat/recheck_certificates.py --workers 8`.
"""
from __future__ import annotations

import argparse
import importlib.util
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
CHECKER = ROOT / "paper1" / "obstruction_check.py"


def _checker():
    spec = importlib.util.spec_from_file_location("obstruction_check", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _one(cert: Path) -> dict:
    oc = _checker()
    t0 = time.monotonic()
    res = oc.check_expansion(cert.parent / "instance.mosp", cert, timeout=1800.0)
    failed = [c["check"] for c in res["checks"] if not c["ok"]]
    return {"instance_name": res.get("instance_name"), "n": res.get("n"), "t": res.get("t"), "b": res.get("b"),
            "certificate": str(cert.relative_to(ROOT)), "verdict": res["verdict"],
            "drat_trim": res.get("drat_trim", ""), "check_seconds": res.get("check_seconds", 0.0),
            "wall_seconds": round(time.monotonic() - t0, 3),
            "mosp_at_least": res.get("proves", {}).get("mosp_at_least"),
            "failed_checks": ";".join(failed)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    certs = sorted(HERE.glob("certificates/*/t*_b*.json"))
    print(f"{len(certs)} certificates")
    t0 = time.monotonic()
    with Pool(args.workers) as pool:
        rows = list(pool.imap_unordered(_one, certs, chunksize=1))
    out = pd.DataFrame(rows).sort_values(["instance_name", "t", "b"])
    out.to_csv(HERE / "checker_verdicts.csv", index=False)
    print(out["verdict"].value_counts().to_string())
    print(f"{time.monotonic() - t0:.0f} s wall; check seconds total {out['check_seconds'].sum():.0f}")


if __name__ == "__main__":
    main()
