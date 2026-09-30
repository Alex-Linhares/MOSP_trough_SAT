# Transfer from `~/dev/pathwidth` (2026-09-30)

`~/dev/pathwidth` was a separate working folder, not under git, created
2026-09-25 to 2026-09-28. It held a port of Chu & Stuckey's customer search
to graph pathwidth, its benchmarks, papers, and a paper plan. Everything in it
was audited and copied into this repository on 2026-09-30. The original folder
is left untouched.

## Where everything went

| In `~/dev/pathwidth` | Now in MOSP | Notes |
|---|---|---|
| `pathwidth/` (the package: `graph.py`, `search.py`, `bounds.py`, `solve.py`, `native.py`, `closing_search.c`, `closing_search_w.c`) | `pathwidth_solver/pathwidth/` | Compiled `.so` files not copied; `native.py` rebuilds them on first use. |
| `src/customer_search.py` | `pathwidth_solver/src/customer_search.py` | The pristine reference copy of MOSP's `satisfiability/customer_search.py`, from commit `add832af5` (2026-09-27), after the `better_move` fix. Not edited. |
| `tests/` (95 tests) | `pathwidth_solver/tests/` | One change: `conftest.py` now finds MOSP in the parent directory, with `PATHWIDTH_MOSP_DIR` still an override. |
| `bench/` scripts (`run.py`, `readers.py`, `summary.py`, `reference.py`) | `pathwidth_solver/bench/` | Unchanged; paths are relative to the file. |
| `bench/results/` (35 files: CSVs and logs) | `pathwidth_solver/bench/results/` | Committed. |
| `bench/instances/` (12,247 files, 90 MB) | `pathwidth_solver/bench/instances/`, **git-ignored** | Duplicates `paper2/benchmarks/raw/`, verified by sha256. Copied so `bench/` runs unchanged. |
| `pyproject.toml` | `pathwidth_solver/pyproject.toml` | |
| `PLAN.md` | `pathwidth_solver/PLAN.md` | The solver plan and its status log, including the benchmark results. |
| `TODO.md` | `pathwidth_solver/TODO.md` | Written 2026-09-28, before loop0005; see *Superseded* below. |
| `CLUSTER_PAPER_PLAN.md` | `pathwidth_solver/CLUSTER_PAPER_PLAN.md` | An earlier paper plan, "Pathwidth is a cluster of problems"; see *Superseded*. |
| `literature/` (50 PDFs and a README) | `literature/` | 11 PDFs were byte-identical to files already there and were not copied. The other 39 were copied under their original names. |
| `literature/README.md` | `literature/pathwidth_solvers_README.md` | Reading notes on the exact pathwidth solvers. |
| `.pytest_cache/`, `__pycache__/` | not copied | |

## The audit

- **Soundness of the search.** `closing_search.c` is byte-identical to MOSP's
  current `satisfiability/customer_search.c`, which includes the 2026-09-26
  `better_move` fix (`0eb33915a`). The Python reference is MOSP's
  `customer_search.py` at `add832af5` (2026-09-27), also after the fix. The
  multiword engine `closing_search_w.c` is new code, and its tests compare it
  node for node with the legacy engine and with the Python.
- **Tests.** All 95 pass, both in the original folder and in the new location
  (6 min each).
- **Instances.** VSPLIB, TreewidthLIB's colouring subset and the Rome graphs
  are byte-identical archives to those in `paper2/benchmarks/raw/`. The
  freetdi named graphs came as a different archive but are identical file by
  file (452 files, 417 distinct contents). No instance data is new.
- **Results checked against known values.**
  - Every proved VSPLIB grid has width equal to its side length, the known
    pathwidth of a square grid: 93 result rows, no mismatches.
  - Every proved VSPLIB tree has the width its name encodes (22 vertices: 3;
    67: 4; 202: 5). These are Ellis, Sudborough & Turner's smallest trees of
    those widths, ⌊5·3^k/6⌋ vertices. All 50 trees are proved.
  - The Rome figure recomputes exactly from the three result files: 11,183 of
    11,534 proved (8,282 by refutation, 2,901 by bound), 97.0%.
- **Two things to fix before the results enter the dataset.**
  - The `proof` column says `budget` for unproved graphs, not empty as in
    MOSP's convention. Only `refutation` and `bound` are certified.
  - The `name` column drops the folder, and VSPLIB's trees come in three
    rotation folders (`1rot`, `2rot`, `3rot`) with the same file names. So 50
    rows carry only 35 distinct names. The rows are distinct files, since
    their node counts differ, but the dataset needs the full path as its key.
- **Papers.** Of the 39 copied, 35 are new papers. Four are other files of
  papers already held:
  - `2010-Yanasse-Senne-...-EJOR.pdf` (MOSP had `yanasse_senne_2010_properties_preprocessing.pdf`);
  - `2014-Coudert-Mazauric-Nisse-...-INRIA-RR-8470.pdf`, the long report
    version of the SEA 2014 chapter MOSP had;
  - `2014-Kobayashi-Komuro-Tamaki-...-SEA.pdf`;
  - `2018-Mallach-...-JDA.pdf`.

## What it contains that MOSP did not have

- **An exact graph pathwidth solver** (`pathwidth_solver/pathwidth/`): the
  customer search run on neighbourhood masks, with a C engine for any number
  of vertices up to 1,024 (`closing_search_w.c`, 2 to 16 64-bit words).
- **The benchmark results** (see `PLAN.md`, §3), at ≤ 600 s per graph:
  - Rome graphs: 11,183 / 11,534 proved (97.0%), against 95.6% for Coudert,
    Mazauric & Nisse (2016).
  - VSPLIB: trees 50 / 50 (they: 30, none of the 202-vertex ones); grids up to
    13 × 13 (they: the same); Harwell-Boeing 39 / 73 (they: 26).
  - TreewidthLIB colouring: 31 / 58, all 14 of Coudert et al.'s Table 4 graphs
    that are held matching their values, and queen11_11 = 87,
    queen12_12 = 103 proved.
  - freetdi named graphs: 125 / 150.
- **35 papers** on exact and approximate pathwidth and treewidth, with the
  reading notes in `literature/pathwidth_solvers_README.md`.

## Superseded, and what to read instead

- `CLUSTER_PAPER_PLAN.md` and `TODO.md` predate loop0005. Their Lean items
  are all done (`paper2/equivalences.md`, `paper2/problem_transformations.md`),
  and their tiering is refined there. For example, their "Tier C" PLA folding
  is now proved false in the simple form and exact as multiple folding, and
  "edge separation" is settled as misattributed. The current plan is
  `paper2/plan.md`. The solver items in `TODO.md` (phase 7: certified-minor
  lower bounds, component push, preprocessing, the open graphs) remain open
  and are not yet in `paper2/plan.md`.
