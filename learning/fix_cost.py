"""Which of the `better_move` fix's two changes carries its cost? (plan 3 §1
Q1a, loop0004 item 04)

The 2026-09-26 fix of the C `better_move` (`0eb33915`, `reports/better_move_bug.md`
§7) changed the rule in two places: the close count `close(q, S ∪ {r})` no
longer counts customers `r` finishes on its own, and the subset rule now runs
*before* better move so that no rule cites a candidate another has discarded.
The fixed rule costs +7.3% nodes at n ≤ 40, ×2–3.5 on the 100-customer
half-ratio classes and ≥ 15× on `Random-100-100-2-4_0` (§18). This module
toggles the two changes separately, behind flags that default to today's rule
(`old_close_count`, `old_rule_order` on `satisfiability.customer_search.decide`,
bits of `better_move_variant` on the C's new entry point `cs_decide_variant`),
and measures four variants:

    fixed      today's rule (both corrections)
    old-close  the over-counting close count, today's rule order
    old-order  today's close count, better move before the subset rule
    prefix     both reverted: the rule as it stood before the fix

and one candidate that is not a revert, added once the four had been
measured: `bm-first`, better move first over every candidate, then the
subset rule over its survivors citing nothing better move discarded -- the
pre-fix order with the cycle closed off, `BM_SUBSET_RESTRICTED` in the C.

Two stages, then tables:

- `harness`: every certified instance at n ≤ 40 on which Theorem 2 is
  switched on (`sparse_enough_for_better_move`), the identity, eight
  relabellings and one re-covering (`learning.differential.labellings`),
  `decide(optimum − 1)` and `decide(optimum)` under each variant, `csearch`
  configuration (`better_move_dominators = 0`). A `sat` below the optimum or
  an `unsat` at it is a false answer; the pre-fix variant must reproduce §15's
  56 instances / 88 false answers or the reproduction is wrong.
- `scale`: identity labelling, `decide(optimum − 1)` only, each variant, on
  the campaign at 50–100 (`results_upward.csv`), the corpus at 41–100 where
  Theorem 2 is on, and `Random-100-100-2-4_0` at a 600 s deadline. A censored
  call is a lower bound on nodes, never a missing value.

Nothing here decides `k` for anything: the flags are unsound by construction
and exist to be measured. Nothing is written to `solutions/`.

Run:

    python -m learning.fix_cost --stage harness --workers 14
    python -m learning.fix_cost --stage scale --workers 14 --deadline 60 --corpus-deadline 120
    python -m learning.fix_cost --stage tables

Writes `learning/data/ensemble/fix_cost_harness.csv.gz`,
`learning/data/ensemble/fix_cost_scale.csv` (both appended as jobs finish; a
rerun of `scale` skips pairs already present) and `reports/fix_cost_tables.md`.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

from learning.differential import (
    DEFAULT_INSTANCE_DIR,
    DEFAULT_SOLUTIONS_DIR,
    ENSEMBLE_DIR,
    RELABELLINGS,
    RESULTS_CSV,
    _materialise,
    campaign_targets,
    corpus_targets,
    labellings,
    witness_value,
)
from mosp.instance import MOSPInstance

VARIANTS: dict[str, dict[str, bool]] = {
    "fixed": {},
    "old-close": {"old_close_count": True},
    "old-order": {"old_rule_order": True},
    "prefix": {"old_close_count": True, "old_rule_order": True},
    # Not a revert: the candidate sound composition -- better move first over
    # every candidate, then the subset rule over its survivors citing nothing
    # better move discarded. Measured beside the four; default of nothing.
    "bm-first": {"subset_after_better_move": True},
}
VARIANT_ORDER = tuple(VARIANTS)
REVERTS = ("fixed", "old-close", "old-order", "prefix")

HARNESS_CSV = ENSEMBLE_DIR / "fix_cost_harness.csv.gz"
HARNESS_PARTIAL = Path("learning/data/fix_cost_harness_partial.csv")
SCALE_CSV = ENSEMBLE_DIR / "fix_cost_scale.csv"
UPWARD_CSV = ENSEMBLE_DIR / "results_upward.csv"
TABLES = Path("reports/fix_cost_tables.md")

RIDGE_INSTANCE = "Random-100-100-2-4_0"
RIDGE_DEADLINE = 600.0

SIZE_BANDS = ((0, 10), (11, 20), (21, 30), (31, 40))


# ----------------------------------------------------------------------------
# one decision under one variant
# ----------------------------------------------------------------------------


def decide_variant(instance: MOSPInstance, k: int, variant: str,
                   deadline_seconds: float | None = None,
                   better_move: bool | None = None):
    """`decide` under the `csearch` configuration with one variant's flags.

    `better_move` defaults to the `csearch` switch for the instance; with it
    off the variants are the same search and the call is a control.
    """
    from satisfiability.customer_search import decide, sparse_enough_for_better_move

    if better_move is None:
        better_move = bool(sparse_enough_for_better_move(instance))
    deadline = None if deadline_seconds is None else time.monotonic() + deadline_seconds
    started = time.monotonic()
    # The variants are reverts within the published rules, so those rules are
    # named: the repaired ones are the default since 2026-10-01 (loop0007).
    answer = decide(instance, k, deadline=deadline, better_move=better_move,
                    better_move_dominators=0, repaired_rules=False, **VARIANTS[variant])
    return answer, round(time.monotonic() - started, 4), better_move


def false_answers(row: dict) -> int:
    """How many of a row's two calls contradict the certificate."""
    bad = 0
    if row.get("status_lo") == "sat":
        bad += 1
    if row.get("status_hi") == "unsat" or row.get("witness_ok") is False:
        bad += 1
    return bad


# ----------------------------------------------------------------------------
# stage harness: soundness and cost at n <= 40
# ----------------------------------------------------------------------------


def harness_targets(max_customers: int = 40, limit: int | None = None,
                    source: str = "all") -> list[dict]:
    jobs: list[dict] = []
    if source in ("all", "campaign"):
        jobs += campaign_targets(RESULTS_CSV, limit, max_customers)
    if source in ("all", "corpus"):
        jobs += corpus_targets(DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, max_customers, limit)
    return jobs


def harness_rows(instance: MOSPInstance, optimum: int, relabellings: int = RELABELLINGS,
                 deadline_seconds: float | None = 60.0,
                 variants: tuple[str, ...] = VARIANT_ORDER) -> list[dict]:
    """Both calls under every variant on every labelling; empty if Theorem 2
    is off for the instance (the variants would be one search)."""
    from satisfiability.customer_search import sparse_enough_for_better_move

    if not sparse_enough_for_better_move(instance):
        return []
    rows = []
    for label, inst in labellings(instance, relabellings, recovering=True):
        for variant in variants:
            row = {"base_name": instance.name, "labelling": label, "n": inst.n_customers,
                   "m": inst.n_patterns, "optimum": optimum, "variant": variant}
            if optimum <= 1:
                row.update(status_lo="trivial", nodes_lo=0, seconds_lo=0.0)
            else:
                lo, secs, bm = decide_variant(inst, optimum - 1, variant, deadline_seconds)
                row.update(status_lo=lo.status, nodes_lo=int(lo.nodes), seconds_lo=secs,
                           better_move=bm)
            hi, secs, bm = decide_variant(inst, optimum, variant, deadline_seconds)
            value = witness_value(inst, hi.order) if hi.status == "sat" else None
            row.update(status_hi=hi.status, nodes_hi=int(hi.nodes), seconds_hi=secs,
                       better_move=bm, witness_value=value,
                       witness_ok=(value is not None and value <= optimum) if hi.status == "sat" else None)
            row["false"] = false_answers(row)
            rows.append(row)
    return rows


def _harness_job(args) -> list[dict]:
    job, relabellings, deadline, variants = args
    instance = _materialise(job)
    rows = harness_rows(instance, int(job["optimum"]), relabellings, deadline, variants)
    for row in rows:
        row.update(source=job["source"], cell=job.get("cell", ""))
    return rows


def run_harness(jobs: list[dict], workers: int = 14, relabellings: int = RELABELLINGS,
                deadline: float | None = 60.0, partial: Path = HARNESS_PARTIAL,
                out: Path = HARNESS_CSV, progress_every: int = 2000,
                variants: tuple[str, ...] = VARIANT_ORDER) -> pd.DataFrame:
    """Runs every job; rows for variants already in `out` are kept and the new
    variants' rows appended, so a later variant can be added to the study."""
    args = [(job, relabellings, deadline, variants) for job in jobs]
    partial.parent.mkdir(parents=True, exist_ok=True)
    if partial.exists():
        partial.unlink()
    buffer: list[dict] = []
    done = kept = 0
    header = [False]
    started = time.time()

    def _flush() -> None:
        if buffer:
            pd.DataFrame(buffer).to_csv(partial, mode="a", header=not header[0], index=False)
            header[0] = True
            buffer.clear()

    def _consume(rows: list[dict]) -> None:
        nonlocal done, kept
        done += 1
        if rows:
            kept += 1
            buffer.extend(rows)
        if done % progress_every == 0:
            _flush()
            print(f"  {done}/{len(jobs)} instances, {kept} with Theorem 2 on, "
                  f"{time.time() - started:.0f} s", flush=True)

    if workers <= 1:
        for a in args:
            _consume(_harness_job(a))
    else:
        with mp.Pool(workers) as pool:
            for rows in pool.imap_unordered(_harness_job, args, chunksize=4):
                _consume(rows)
    _flush()
    frame = pd.read_csv(partial) if partial.exists() else pd.DataFrame()
    if out.exists():
        prev = pd.read_csv(out, low_memory=False)
        prev = prev[~prev.variant.isin(variants)]
        frame = pd.concat([prev, frame], ignore_index=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False, compression="gzip")
    partial.unlink(missing_ok=True)
    print(f"harness: {done} instances, {kept} with Theorem 2 on, {len(frame)} rows, "
          f"{time.time() - started:.0f} s -> {out}")
    return frame


# ----------------------------------------------------------------------------
# stage scale: refutation cost at 50-100
# ----------------------------------------------------------------------------


def scale_targets(upward_csv: Path = UPWARD_CSV, min_customers: int = 41,
                  max_customers: int = 100, deadline: float = 60.0,
                  corpus_deadline: float = 120.0, limit: int | None = None,
                  source: str = "all") -> list[dict]:
    """Campaign 50–100 (every certified refutation), corpus 41–100 with Theorem
    2 on, and the ridge instance at its own deadline, first in the list."""
    from satisfiability.customer_search import sparse_enough_for_better_move

    jobs: list[dict] = []
    for job in corpus_targets(DEFAULT_INSTANCE_DIR, DEFAULT_SOLUTIONS_DIR, max_customers) \
            if source in ("all", "corpus") else []:
        n = len(job["matrix"])
        if n < min_customers:
            continue
        inst = _materialise(job)
        if not sparse_enough_for_better_move(inst):
            continue
        job = dict(job, n=n, m=len(job["matrix"][0]),
                   deadline=RIDGE_DEADLINE if job["instance_name"] == RIDGE_INSTANCE else corpus_deadline)
        jobs.append(job)
    jobs.sort(key=lambda j: j["instance_name"] != RIDGE_INSTANCE)
    if upward_csv.exists() and source in ("all", "campaign"):
        frame = pd.read_csv(upward_csv, low_memory=False)
        frame = frame[frame.certified.astype(bool) & (frame.n >= min_customers)
                      & (frame.n <= max_customers) & (frame.optimum > 1)]
        cols = ["instance_name", "cell", "generator", "n", "m", "param", "index", "optimum",
                "matrix_digest", "nodes_csearch", "status_csearch"]
        for row in frame[cols].to_dict("records"):
            jobs.append({"source": "campaign", "deadline": deadline, **row})
    if limit is not None:
        jobs = jobs[:limit]
    return jobs


def _scale_job(args) -> dict:
    job, variant = args
    instance = _materialise(job)
    k = int(job["optimum"]) - 1
    answer, seconds, bm = decide_variant(instance, k, variant, float(job["deadline"]))
    return {"instance_name": job["instance_name"], "source": job["source"],
            "cell": job.get("cell", ""), "n": instance.n_customers, "m": instance.n_patterns,
            "optimum": int(job["optimum"]), "k": k, "variant": variant, "better_move": bm,
            "status": answer.status, "nodes": int(answer.nodes), "seconds": seconds,
            "deadline": float(job["deadline"]),
            "recorded_csearch_nodes": job.get("nodes_csearch", np.nan),
            "recorded_csearch_status": job.get("status_csearch", "")}


def run_scale(jobs: list[dict], workers: int = 14, out: Path = SCALE_CSV,
              variants: tuple[str, ...] = VARIANT_ORDER, wall: float | None = None,
              progress_every: int = 200) -> pd.DataFrame:
    """One job per (instance, variant); appends to `out` and skips pairs done."""
    done_pairs: set[tuple[str, str]] = set()
    if out.exists():
        prev = pd.read_csv(out)
        done_pairs = set(zip(prev.instance_name, prev.variant))
    args = [(job, v) for job in jobs for v in variants
            if (job["instance_name"], v) not in done_pairs]
    print(f"scale: {len(jobs)} instances × {len(variants)} variants, "
          f"{len(args)} calls to run ({len(done_pairs)} already recorded)", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    buffer: list[dict] = []
    finished = 0

    def _flush() -> None:
        if buffer:
            pd.DataFrame(buffer).to_csv(out, mode="a", header=not out.exists(), index=False)
            buffer.clear()

    with mp.Pool(workers) as pool:
        it = pool.imap_unordered(_scale_job, args, chunksize=1)
        for row in it:
            buffer.append(row)
            finished += 1
            if finished % progress_every == 0:
                _flush()
                print(f"  {finished}/{len(args)} calls, {time.time() - started:.0f} s", flush=True)
            if wall is not None and time.time() - started > wall:
                print(f"  wall {wall:.0f} s reached after {finished} calls; in-flight calls dropped",
                      flush=True)
                pool.terminate()
                break
    _flush()
    frame = pd.read_csv(out)
    print(f"scale: {finished} calls in {time.time() - started:.0f} s; {len(frame)} rows -> {out}")
    return frame


# ----------------------------------------------------------------------------
# tables
# ----------------------------------------------------------------------------


def _band(n: int) -> str:
    for lo, hi in SIZE_BANDS:
        if lo <= n <= hi:
            return f"{lo}–{hi}"
    return f"> {SIZE_BANDS[-1][1]}"


def _md(frame: pd.DataFrame, floatfmt: str = ".3g") -> str:
    from learning.graph_story import _md as md

    return md(frame, floatfmt)


def soundness_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Per variant: instances with a false answer, false calls on each side,
    witness failures, unknowns. Over every labelling."""
    out = []
    for variant in VARIANT_ORDER:
        d = rows[rows.variant == variant]
        if not len(d):
            continue
        bad_lo = (d.status_lo == "sat")
        bad_hi = (d.status_hi == "unsat") | (d.witness_ok == False)  # noqa: E712
        flagged = d[bad_lo | bad_hi]
        out.append({
            "variant": variant, "instances": int(d.base_name.nunique()), "calls": int(2 * len(d)),
            "instances with a false answer": int(flagged.base_name.nunique()),
            "false unsat at optimum": int(bad_hi.sum()),
            "false sat below": int(bad_lo.sum()),
            "witness failures": int((d.witness_ok == False).sum()),  # noqa: E712
            "unknown (censored)": int((d.status_lo == "unknown").sum() + (d.status_hi == "unknown").sum()),
            "sound at n ≤ 40": "yes" if len(flagged) == 0 else "**no**",
        })
    return pd.DataFrame(out)


def _paired(rows: pd.DataFrame, value: str = "nodes_lo", status: str = "status_lo",
            key: tuple[str, ...] = ("base_name", "labelling")) -> pd.DataFrame:
    """Wide table of `value` per variant on the calls every variant settled
    `unsat` (the refutations all four agree on)."""
    d = rows[rows[status].isin(("unsat",))]
    wide = d.pivot_table(index=list(key), columns="variant", values=value, aggfunc="first")
    present = [v for v in VARIANT_ORDER if v in wide.columns]
    wide = wide[present].dropna(subset=present)
    meta = rows.drop_duplicates(list(key)).set_index(list(key))[["n", "m", "optimum"]]
    return wide.join(meta, how="left")


def ratio_summary(wide: pd.DataFrame, num: str, den: str) -> dict:
    r = (wide[num] + 1) / (wide[den] + 1)
    return {"pairs": int(len(r)), "total ratio": float(wide[num].sum() / max(wide[den].sum(), 1)),
            "median": float(r.median()), "p90": float(r.quantile(0.9)),
            "p99": float(r.quantile(0.99)), "max": float(r.max()), "min": float(r.min()),
            "more": int((r > 1).sum()), "fewer": int((r < 1).sum()), "equal": int((r == 1).sum())}


ATTRIBUTION = (
    # (label, numerator, denominator)
    ("the whole fix: fixed / prefix", "fixed", "prefix"),
    ("close count alone, from pre-fix: old-order / prefix", "old-order", "prefix"),
    ("rule order alone, from pre-fix: old-close / prefix", "old-close", "prefix"),
    ("close count, given the new order: fixed / old-close", "fixed", "old-close"),
    ("rule order, given the new count: fixed / old-order", "fixed", "old-order"),
    ("the candidate: bm-first / fixed", "bm-first", "fixed"),
    ("the candidate against pre-fix: bm-first / prefix", "bm-first", "prefix"),
)


def attribution_table(wide: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([{"comparison": label, **ratio_summary(wide, a, b)}
                         for label, a, b in ATTRIBUTION if a in wide and b in wide])


def attribution_by_group(wide: pd.DataFrame, group: pd.Series) -> pd.DataFrame:
    out = []
    for g, part in wide.groupby(group):
        row = {"group": g, "pairs": len(part)}
        for label, a, b in ATTRIBUTION:
            if a not in part or b not in part:
                continue
            s = ratio_summary(part, a, b)
            short = label.split(":")[1].strip()
            row[f"{short} total"] = s["total ratio"]
            row[f"{short} median"] = s["median"]
            row[f"{short} p90"] = s["p90"]
        out.append(row)
    return pd.DataFrame(out)


def totals_table(wide: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([{"variant": v, "total nodes": int(wide[v].sum()),
                          "vs fixed (total)": float(wide[v].sum() / max(wide["fixed"].sum(), 1)),
                          "vs prefix (total)": float(wide[v].sum() / max(wide["prefix"].sum(), 1))}
                         for v in VARIANT_ORDER if v in wide])


def scale_status_table(scale: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (src, band), d in scale.groupby([scale.source, scale.n.map(lambda n: f"{n}")]):
        row = {"source": src, "n": band, "instances": int(d.instance_name.nunique())}
        for v in VARIANT_ORDER:
            dv = d[d.variant == v]
            if not len(dv):
                continue
            row[f"{v} unsat"] = int((dv.status == "unsat").sum())
            row[f"{v} censored"] = int((dv.status == "unknown").sum())
            row[f"{v} sat!"] = int((dv.status == "sat").sum())
        out.append(row)
    return pd.DataFrame(out)


def scale_censored_bounds(scale: pd.DataFrame) -> pd.DataFrame:
    """Where the fixed rule was censored and a reverted variant settled, the
    lower bound on the ratio; and the reverse."""
    wide = scale.pivot_table(index="instance_name", columns="variant", values="nodes", aggfunc="first")
    st = scale.pivot_table(index="instance_name", columns="variant", values="status", aggfunc="first")
    meta = scale.drop_duplicates("instance_name").set_index("instance_name")[["source", "n", "m", "k", "deadline"]]
    rows = []
    for name in wide.index:
        if (st.loc[name] == "unknown").any() and (st.loc[name] == "unsat").any():
            row = {"instance": name, **meta.loc[name].to_dict()}
            for v in VARIANT_ORDER:
                if v not in st.columns or pd.isna(st.loc[name, v]):
                    continue
                row[v] = f"{'≥ ' if st.loc[name, v] == 'unknown' else ''}{int(wide.loc[name, v]):,}"
            rows.append(row)
    return pd.DataFrame(rows)


def reproduction_table(scale: pd.DataFrame) -> pd.DataFrame:
    """Does the pre-fix variant reproduce `results_upward.csv`'s `nodes_csearch`?"""
    d = scale[(scale.source == "campaign") & (scale.recorded_csearch_status == "unsat")
              & (scale.status == "unsat")].copy()
    out = []
    for v in VARIANT_ORDER:
        dv = d[d.variant == v]
        if not len(dv):
            continue
        out.append({"variant": v, "settled campaign refutations": int(len(dv)),
                    "equal to recorded nodes_csearch": int((dv.nodes == dv.recorded_csearch_nodes).sum())})
    return pd.DataFrame(out)


def write_tables(harness_csv: Path = HARNESS_CSV, scale_csv: Path = SCALE_CSV,
                 out: Path = TABLES) -> str:
    text = "# Which change of the `better_move` fix carries its cost? — tables\n\n"
    text += ("Generated by `python -m learning.fix_cost --stage tables` from "
             f"`{harness_csv}` and `{scale_csv}`. Variants: " +
             "; ".join(f"`{k}` = {v or 'today'}" for k, v in VARIANTS.items()) + ".\n\n")
    if harness_csv.exists():
        rows = pd.read_csv(harness_csv, low_memory=False)
        rows = rows[rows.better_move.astype(bool)]
        text += "## Soundness at n ≤ 40 (every labelling, both calls)\n\n"
        text += _md(soundness_table(rows))
        flagged = rows[rows["false"] > 0]
        if len(flagged):
            per = flagged.groupby("variant").agg(
                instances=("base_name", "nunique"), false_calls=("false", "sum"),
                labellings=("labelling", "nunique")).reset_index()
            text += "\n### False answers by variant\n\n" + _md(per)
            by_lab = flagged.groupby(["variant", "labelling"]).size().unstack(fill_value=0)
            text += "\n### False answers by labelling (rows, not calls)\n\n" + _md(by_lab.reset_index())
            worst = (flagged.groupby(["variant", "base_name", "n", "m", "optimum"]).size()
                     .reset_index(name="rows").sort_values(["variant", "rows"], ascending=[True, False]))
            text += "\n### The flagged instances (first 40)\n\n" + _md(worst.head(40))
        ident = rows[rows.labelling == "identity"]
        wide = _paired(ident)
        text += f"\n## Refutation cost at n ≤ 40 (identity labelling, `decide(optimum − 1)`, {len(wide):,} refutations all four variants settled)\n\n"
        text += _md(totals_table(wide))
        text += "\n### Paired ratios, (a + 1) / (b + 1)\n\n" + _md(attribution_table(wide))
        text += "\n### By size band\n\n" + _md(attribution_by_group(wide, wide.n.map(_band)))
        text += "\n### By source\n\n"
        src = rows.drop_duplicates(["base_name", "labelling"]).set_index(["base_name", "labelling"]).source
        text += _md(attribution_by_group(wide, src.reindex(wide.index)))
        # the satisfiable side
        sat_rows = ident[ident.status_hi == "sat"]
        wide_sat = sat_rows.pivot_table(index=["base_name", "labelling"], columns="variant",
                                        values="nodes_hi", aggfunc="first").dropna()
        if len(wide_sat):
            text += f"\n### The witness side, `decide(optimum)`, {len(wide_sat):,} calls all four settled `sat`\n\n"
            text += _md(attribution_table(wide_sat))
        # all labellings
        wide_all = _paired(rows)
        text += f"\n### All labellings, {len(wide_all):,} refutations\n\n" + _md(attribution_table(wide_all))
    if scale_csv.exists():
        scale = pd.read_csv(scale_csv, low_memory=False)
        scale = scale[scale.better_move.astype(bool)]
        text += "\n## Refutation cost at 41–100 (identity labelling, `decide(optimum − 1)`)\n\n"
        text += "### Settled and censored calls per variant\n\n" + _md(scale_status_table(scale))
        settled = scale[scale.status == "unsat"]
        wide = settled.pivot_table(index="instance_name", columns="variant", values="nodes",
                                   aggfunc="first").dropna(subset=list(REVERTS))
        meta = scale.drop_duplicates("instance_name").set_index("instance_name")[["source", "n", "m", "cell"]]
        wide = wide.join(meta)
        text += f"\n### Paired ratios where all four settled ({len(wide):,} instances)\n\n"
        text += _md(totals_table(wide))
        text += "\n" + _md(attribution_table(wide))
        text += "\n### By source and size\n\n"
        text += _md(attribution_by_group(wide, wide.source + " n=" + wide.n.astype(str)))
        camp = wide[wide.source == "campaign"]
        if len(camp):
            text += "\n### Campaign cells at 50–100 (product ratio and density)\n\n"
            text += _md(attribution_by_group(camp, camp.cell))
        corp = wide[wide.source == "corpus"]
        if len(corp):
            text += "\n### Corpus instances at 41–100, each\n\n"
            show = corp.reset_index()[["instance_name", "n", "m"] + [v for v in VARIANT_ORDER if v in corp]].copy()
            for a, b, col in (("fixed", "prefix", "fix / prefix"), ("old-order", "prefix", "close / prefix"),
                              ("old-close", "prefix", "order / prefix")):
                show[col] = ((show[a] + 1) / (show[b] + 1)).round(3)
            text += _md(show.sort_values("fix / prefix", ascending=False))
        cens = scale_censored_bounds(scale)
        if len(cens):
            text += "\n### Censored on some variant, settled on another (lower bounds marked ≥)\n\n" + _md(cens)
        ridge = scale[scale.instance_name == RIDGE_INSTANCE]
        if len(ridge):
            text += f"\n### `{RIDGE_INSTANCE}` at k = {int(ridge.k.iloc[0])}, {RIDGE_DEADLINE:.0f} s deadline\n\n"
            text += _md(ridge[["variant", "status", "nodes", "seconds"]].sort_values("variant"))
        text += "\n### Reproduction: the pre-fix variant against `results_upward.csv`'s recorded `nodes_csearch`\n\n"
        text += _md(reproduction_table(scale))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"tables -> {out}")
    return text


# ----------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=("harness", "scale", "tables"), default="tables")
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--source", choices=("all", "campaign", "corpus"), default="all")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-customers", type=int, default=40)
    ap.add_argument("--relabellings", type=int, default=RELABELLINGS)
    ap.add_argument("--deadline", type=float, default=60.0, help="seconds per call")
    ap.add_argument("--corpus-deadline", type=float, default=120.0,
                    help="seconds per corpus call in the scale stage")
    ap.add_argument("--min-customers", type=int, default=41, help="scale stage lower size")
    ap.add_argument("--scale-max", type=int, default=100)
    ap.add_argument("--wall", type=float, default=None, help="stop dispatching after this many seconds")
    ap.add_argument("--harness-csv", type=Path, default=HARNESS_CSV)
    ap.add_argument("--scale-csv", type=Path, default=SCALE_CSV)
    ap.add_argument("--variants", nargs="*", default=list(VARIANT_ORDER),
                    help="which variants to run (harness and scale stages)")
    ap.add_argument("--out", type=Path, default=TABLES)
    args = ap.parse_args()
    variants = tuple(args.variants)

    if args.stage == "harness":
        jobs = harness_targets(args.max_customers, args.limit, args.source)
        print(f"harness: {len(jobs)} certified instances at n ≤ {args.max_customers}, "
              f"{args.relabellings} relabellings + re-covering, {len(VARIANTS)} variants, "
              f"{args.workers} workers", flush=True)
        run_harness(jobs, args.workers, args.relabellings, args.deadline, out=args.harness_csv,
                    variants=variants)
    elif args.stage == "scale":
        jobs = scale_targets(UPWARD_CSV, args.min_customers, args.scale_max, args.deadline,
                             args.corpus_deadline, args.limit, args.source)
        run_scale(jobs, args.workers, args.scale_csv, variants=variants, wall=args.wall)
    write_tables(args.harness_csv, args.scale_csv, args.out)


if __name__ == "__main__":
    main()
