# Fixing the solvers to match the soundness theorems

Ralph loop0007 (`Ralph_Loops/loop0007/`). This loop carries out the owner's
decision of 2026-10-01: both solvers, the MOSP customer search
(`satisfiability/`) and the graph pathwidth solver (`pathwidth_solver/`), apply
the *repaired* definite and better moves proved sound in
`lean/MOSPFormalization/Search/` (`paper2/revised_algorithm.md` §4.6.1). Each
item appends a section below.

**Status of the default.** As of item 01, `repaired_rules` exists in the Python
reference only and is **off by default**. It becomes the default in both
solvers in item 03, once the C (item 02) and the pathwidth solver carry it, and
that change will be recorded here.

**Findings that would stop the loop** (a changed certified value, or a false
refutation under the old rules): **none so far.**

---

## Item 01: the repaired rules in the Python reference (2026-10-01)

### What changed

`satisfiability/customer_search.py`:

- **`decide(..., repaired_rules=False)`.** When set:
  - the **definite move** fires on the first playable `q`, in index order, that
    passes the published test `close(q, S) ≥ open(q, S)` **and** the matching
    test: the customers `d ≠ q` that closing `q` frees (`o(d, S) ⊆ o(q, S)`)
    have a matching of size at least `open(q, S) − 1` into the stacks, each `d`
    matched to a stack of `o(d, S)`. That is `HasDefiniteMatching`, equivalent to
    `IsHereditarilyDefinite` by `isHereditarilyDefinite_iff_hasDefiniteMatching`.
    A candidate that passes the published test and fails the matching is passed
    over, and a later candidate may still fire. So the pick is the least
    hereditarily definite playable candidate, which is what `repairedFullFilter`
    picks. The published test stays in front as a prefilter, which the repair
    implies.
  - the **better move** cites `q` for `r` only if premises 3 and 4 hold **and**
    `q` passes the same matching test at the child `cl(S ∪ {r})`, against
    `O(S ∪ {r})`, over the customers `d ∉ S ∪ {r}`, `d ≠ q`, with
    `∅ ≠ N[d] − O(S ∪ {r}) ⊆ N[q] − O(S ∪ {r})`. That is `IsRepairedBetter`.
  - the subset rule, the free moves, the memo, old move and the order
    `definite → subset → better` are unchanged.
- **The better move in the Python, for the first time.** Before this item,
  Theorem 2 existed only in the C, and `better_move=True` was silently inert
  under `native=False`. Item 02 has to compare the C with the Python node for
  node under both settings, so the C's `better_move_pass` is ported as
  `_better_move_pass`. It runs over the subset survivors in index order, and only
  an earlier survivor among the first `better_move_dominators` may cite. Under the
  old rules it matches the C node for node (table below). `better_move` and
  `better_move_dominators` are now explicit parameters of `decide`. Before, they
  were popped from `**kwargs` in the native branch only, so they were also lost on
  a fallback to the Python.
- **`_has_definite_matching(freed, need)`**: Kuhn's augmenting paths. It stops
  once `need` edges are matched and returns at once when `need ≤ 0` (the
  `open ≤ 1` corollary) or when `len(freed) < need`.
- `repaired_rules=True` **forces the Python path** until the C implements the
  flag (item 02).

The module docstring now states that Theorems 1 and 2 are false as published.

### Tests

`tests/test_repaired_rules.py`, 11 tests, 2.3 s:

- **flag off, nothing changed node for node.** Status and node count of
  `decide(native=False)` on 40 seeded instances, at every `k`, under all 32
  combinations of subset/definite/old move/memo/restrict, are pinned by a SHA-256
  digest. The digest was computed with the code before the change (commit
  `392a2bda2`): 9,312 decisions, 19,438 nodes. Outside the test, the same
  comparison on 150 instances (35,264 decisions) matched byte for byte, witness
  orders included.
- **the Python better move is the C**, in status, nodes and witness, over 60
  instances × every `k` × `L ∈ {0, 1, 4}` × three old-move/memo settings, and it
  prunes somewhere.
- **`DEFINITE_CEX`**: at `S = {2}`, `k = 6`, the published premise holds for 0,
  the matching fails, and 0 leads to no solution. The old filter keeps `[0]` for
  every `L`. The repaired filter keeps `[3]`, which has a solution, and that is
  exactly `k_repaired_filter`. The whole repaired search is right on both
  counterexample graphs at `k − 1` and `k`.
- **Bug B node**: the repaired filter equals `k_repaired_filter` and is node-sound.
- **every labelled graph on 1–4 vertices**, at every state, `k`, refuted old-move
  set and `L ∈ {0, 1, 2}`: the production filter equals the Lean transcription
  under both settings and is node-sound against the oracle.
- **whole search to 5 vertices** (all graphs to 4, 150 sampled at 5): the
  repaired and old searches answer `Sol_k(∅)` under 16 flag combinations, and
  every witness simulates to at most `k`.
- the matching test equals `d_hereditary` on the pinned graphs; unit tests of the
  matching (augmenting path, Hall failure); the flag forces the Python.

`tests/test_differential.py`: a comment that called the Python's Theorem 2 inert
is corrected. The assertion is unchanged and passes.

### The full check

`paper2/solver_fix_check.py` compares the production Python with
`paper2/search_check.py`, which shares no code with the solver. At every
free-closed state with the invariant, every `k`, a family of refuted old-move sets
`Q` (where marked), and every limit `L`, it checks the following:

- the production filter with `repaired=True` **equals** `k_repaired_filter`
  (Lean `repairedFullFilter`) and is **node-sound** against the oracle;
- with `repaired=False` it equals `k_code_filter` (Lean `codeFullFilter`);
- the matching test equals `IsHereditarilyDefinite` by enumeration, on every
  candidate passing `close ≥ open`.

It also runs the whole search, `native=False`, under 16 flag combinations at
every `k ≥ 1`, with both settings.

| family | graphs | node checks | with a solution | matching checks | published premise without hereditary | filters differ | old filter lost the node | whole searches (each setting) |
|---|---|---|---|---|---|---|---|---|
| labelled, 1–6 vertices, all `Q` families, `L` 0–2 | 33,867 | 6,149,187 | 4,337,313 | 5,946,920 | 0 | 0 | 0 | 3,232,208 |
| atlas 7, identity + 4 labellings | 5,220 | 1,551,570 | 1,110,315 | 1,782,115 | 780 | 276 | 0 | 584,640 |
| random sparse / C&S-shaped, 8–13, `Q = ∅` | 600 | 2,994,627 | 2,658,327 | 5,895,953 | 6,959 | 1,943 | 0 | 102,224 |
| pinned (both `DEFINITE_CEX`, Bug A, Bug B, `RUN_LOST_CEX`), every `k`, `L` 0–1 | 5 | 26,690 | 23,312 | 109,496 | 1,317 | 974 | 6 | 1,024 |
| gadgets (`better_augment`), 14–17, `k ∈ {opt−1, opt, opt+1}`, `L` 0–1 | 2,000 | 5,522,016 | 2,980,090 | 23,204,742 | 268,128 | 7,597 | 296 | 96,000 |
| **total** | | **16,244,090** | **11,109,357** | **36,939,226** | 277,184 | 10,790 | 302 | **4,016,096** |

**Failures: zero** in every column that can fail. The production filter equals
the Lean filter at all 16,244,090 nodes under both settings. The repaired filter
is node-sound at all 11,109,357 nodes with a solution. The matching agrees with
the hereditary premise on all 36,939,226 candidates. Every whole search, repaired
or old, gave the right answer and a valid witness. The old filter lost the last
solution at 302 nodes (296 on gadgets, 6 on the pinned graphs). The repaired
filter lost none, and the old search still answered correctly on every run, as
loop0006 found. 231 s on 12 workers (final code; an earlier run before a behaviour-neutral refactor gave identical totals).

**Python better move against the C** (old rules; outside the test, seeded
instances at 2–13 customers, sparse): 117,828 runs, under every combination of
subset/definite × three old-move/memo settings × `L ∈ {0, 1, 4}` at every `k`.
**Zero mismatches** in status, nodes or active-customer witness. The better move
pruned on 15,518 of them.

**Size range.** Node and whole-search checks cover graphs of 1 to 17 vertices:
exhaustive to 6, every graph at 7 under five labellings, sampled at 8–17. The
Python–C comparison covers 2–13 customers. Nothing here measures cost; that is
item 04.

### Regenerate

```
python -m pytest tests/test_repaired_rules.py -q
python -m paper2.solver_fix_check --workers 16 --aug 2000   # writes paper2/data/solver_fix_check.json, ~5 min
python -m paper2.solver_fix_check --quick                    # ~10 s
```
