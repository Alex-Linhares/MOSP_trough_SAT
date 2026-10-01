# Fixing the solvers to match the soundness theorems

Ralph loop0007 (`Ralph_Loops/loop0007/`). This loop carries out the owner's
decision of 2026-10-01: both solvers, the MOSP customer search
(`satisfiability/`) and the graph pathwidth solver (`pathwidth_solver/`), apply
the *repaired* definite and better moves proved sound in
`lean/MOSPFormalization/Search/` (`paper2/revised_algorithm.md` §4.6.1). Each
item appends a section below.

**Status of the default: `repaired_rules=True` is the default in both solvers
since 2026-10-01 (item 03).** That covers `satisfiability.customer_search.decide`,
`satisfiability.native.decide_native`, `pathwidth.search.decide` and
`pathwidth.native.decide_native`. Every caller that does not name the flag, which
includes `solve_mosp_exact`, `benchmarks.csearch`, `benchmarks.recertify`, the
heuristics' DFS and `pathwidth.compute_pathwidth`, now runs the repaired definite
and better moves. `repaired_rules=False` keeps the rules as Chu & Stuckey
publish them, for comparison and regression. The C entry points kept for old
processes (`cs_decide_variant`, `cs_decide_fan`, `cs_decide`) still run the
published rules. Four tools that model the published rules now name
`repaired_rules=False`, and their pinned counts are unchanged:
`learning/fix_cost.py`, `paper2/search_check.py`'s `native_decide`,
`tests/test_fix_cost.py`, and the reference calls in
`tests/test_search_certificate.py`. The certificate emitter
(`learning/search_certificate.py`) still models only the published rules.

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

---

## Item 02: the repaired rules in the C (2026-10-01)

### What changed

`satisfiability/customer_search.c`:

- **A new entry point, `cs_decide_rules`**: `cs_decide_variant` plus one
  argument, `repaired_rules`. `cs_decide_variant` keeps its signature and calls
  `cs_decide_rules` with the flag off, so a process that loaded the library
  before today still gets the published rules. `cs_decide_fan` and `cs_decide`
  are unchanged wrappers. `native._build` still compiles to a scratch name and
  renames it into place.
- **`has_definite_matching(sets, count, need)`**: Kuhn's augmenting paths over
  the stacks of `o(q, S)` (at most 128, bit indices of a 128-bit word),
  recursion depth at most `need`. It returns at once when `need ≤ 0` or when
  `count < need`, and stops once `need` edges are matched. Only the yes/no
  answer is used, so its augmenting order need not follow the Python's.
- **Definite move**: when `repaired_rules` is set, a candidate that passes
  `close ≥ open` must also pass the matching over `{o(d, S) : d ≠ q, o(d, S) ⊆
  o(q, S)}` with `need = open(q, S) − 1`. A candidate that fails is passed over
  and the loop goes on to the next, as in the Python.
- **Better move**: while counting `close'`, the loop also collects the freed
  sets at the child, `left = N[d] − O(S ∪ {r})` for `d ≠ q` with `∅ ≠ left ⊆
  own`. When `repaired_rules` is set, a `q` that passes premises 3 and 4 but
  fails the matching does not cite (`IsRepairedBetter`). Under the
  `BM_OLD_CLOSE_COUNT` measurement variant the freed sets still exclude
  customers with nothing left to open, which matches the definition.
- The lines `paper2/search_soundness.md` quotes from the C (`closed_by++` with
  the premise-4 test, and `if (closed_by >= opened_by) pruned = 1;`) are kept
  word for word. The repaired test is a separate `continue` in front of them,
  and `tests/test_search_soundness_doc.py` passes.

`satisfiability/native.py`: `decide_native(..., repaired_rules=False)` calls
`cs_decide_rules`. `satisfiability/customer_search.py`: `repaired_rules=True`
**no longer forces the Python**. `decide` passes the flag to the C and falls
back to the Python only for the usual reasons (no compiler, more than 128
customers, `branch`, `expansion_prune`).

The default is still `repaired_rules=False`. Item 03 changes it.

### Tests

`tests/test_repaired_rules.py`, now 16 tests, 11 s. The item-01 test that the
flag forces the Python is replaced by these:

- **C = Python on `tests/test_native.py`'s generator**: 25 instances, every
  `k` from 0 to `n + 1`, 36 configurations (subset/definite in three
  combinations × better move off or `L ∈ {0, 1, 4}` × old move/memo in the
  three settings both run identically) × both settings. Status, nodes and
  witness must be equal.
- **C = Python on the counterexamples**: both `DEFINITE_CEX` graphs and the
  8- and 10-vertex Bug B instances, every `k`, the same 36 configurations. The
  test also requires that the two settings take different node counts
  somewhere, so the flag is really doing something.
- **The repaired C answers the oracle** (`s_searchsol_table`) on
  `DEFINITE_CEX` at every `k`.
- **Past 64 customers**: SP4 (100 customers) at 52 and 53, both settings,
  under a 3,000-node cap. This exercises the high half of the 128-bit words.
- **A real refutation**: SP2 at 18 under the repaired rules, C = Python, over
  1,000 nodes.
- **The old entry point**: `cs_decide_variant` called directly equals
  `decide_native(repaired_rules=False)` in status and nodes.

Old move together with the memo is left out of the node-for-node comparison
on purpose. With both on, the C runs both and the Python drops the memo, as
`tests/test_native.py` already documents.

### The full check

`paper2/solver_fix_c_check.py` runs the Python and the C on the same calls and
compares status, node count and witness. The C lists customers that need no
product as root free moves and the Python omits them, so the witness is
compared over active customers only. Both settings are run, with 50
configurations on the small families: the 48 of the matrix above with
subset/definite in all four combinations, plus degree fan order and the
restricted frontier. The corpus family uses 6 production-like configurations.

| family | instances | size | `k` | calls per setting | C ≠ Python (old) | C ≠ Python (repaired) | old ≠ repaired, nodes | old ≠ repaired, answer |
|---|---|---|---|---|---|---|---|---|
| `tests/test_native.py` generator | 400 | 1–8 customers | 0 … n+1 | 128,300 | 0 | 0 | 0 | 0 |
| pinned (`DEFINITE_CEX` ×2, Bug A, Bug B 8 and 10, `RUN_LOST_CEX`, 10×13, 17×9, 10×20) | 9 | 8–17 | 0 … n+1 | 6,450 | 0 | 0 | 213 | 0 |
| gadgets (`better_augment`) | 400 | 14–17 | 0 … n+1 | 360,350 | 0 | 0 | 2,547 | 0 |
| random sparse / C&S-shaped | 300 | 10–24 | 0 … n+1 | 278,850 | 0 | 0 | 3,782 | 0 |
| certified corpus, cap 30,000 nodes (≤ 40) or 10,000 (> 40) | 420 (300 at ≤ 40, 58 at 41–64, 62 at 65–125) | 10–125 | opt−1, opt | 5,040 | 0 | 0 | 33 | 0 |
| **total** | **1,529** | | | **778,990** | **0** | **0** | **6,575** | **0** |

So **1,557,980 calls, zero disagreements** between the C and the Python under
either setting, in status, nodes or witness. That covers 36.3 M C nodes per
setting, of which 6,023 calls per setting ended at the node cap; equality
under a cap means equality up to the abort node. The two settings took
different node counts on 6,575 configuration-`k` pairs and **never gave a
different answer**, except where one side hit the cap, which the count
excludes. The repaired rules cost 0.03% more nodes in total (36,263,084 →
36,274,154). That figure is only a hint, from capped runs on small and
gadget instances. Item 04 measures the cost.

The node-level soundness of the repaired filter was checked against the
oracle in item 01, on the Python. Since the C is the same search, node for
node, that check carries over to the C on the inputs where the two were
compared.

Two spot timings under the production configuration (better move, `L = 4`, old
move on), C, one core: SP2 at 18 refutes in 14,281 nodes (old) and 14,291
(repaired), 0.02 s each; SP3 at 33 refutes in 1,433,648 and 1,435,137 nodes,
1.05 s each.

**Size range.** The C–Python equality covers 1–24 vertices in full and
corpus instances at 10–125 customers under node caps. Nothing here is a cost
measurement above SP3.

### Regenerate

```
python -m pytest tests/test_repaired_rules.py -q
python -m paper2.solver_fix_c_check --workers 20   # writes paper2/data/solver_fix_c_check.json, ~2 min
python -m paper2.solver_fix_c_check --quick        # ~20 s
```

---

## Item 03: the pathwidth solver, and the default (2026-10-01)

### What changed

`pathwidth_solver/pathwidth/` runs the same search on graph masks, in three
implementations. All three now take `repaired_rules`:

- **`closing_search.c`**, the 128-bit legacy C, is again a byte copy of MOSP's
  `satisfiability/customer_search.c`, as `TRANSFER.md` says it is, so it
  carries item 02's diff and the entry point `cs_decide_rules`.
  `native.decide_native(legacy=True)` now calls `cs_decide_rules`.
- **`closing_search_w.c`**, the multiword C (built for 2, 4, 8 and 16 words of
  64 bits). It has the same diff in set operations. `has_definite_matching` is
  Kuhn's algorithm with an `owner` array of `64 · WORDS` entries, and each
  depth frame gets a scratch array `freed` of `n` sets. The definite move and
  the better move use that array in turn, never at once. `csw_decide` gained
  the parameter `repaired_rules` after `better_move_variant`. The library is
  rebuilt on first use because `native._build` compares modification times.
- **`search.py`**, the Python reference, gains `decide(..., repaired_rules=)`
  and, for the first time, **the better move**. Before this item,
  `better_move=True` was silently ignored on the Python path, as in MOSP before
  item 01. `_apply_dominance`, `_subset_survivors`, `_better_move_pass` and
  `_has_definite_matching` are MOSP's functions, unchanged except for comments.
  The order is `definite → subset → better`, citing only standing candidates.
- **`native.py`** passes the flag to both C builds.
- `src/customer_search.py` is left as it is. `TRANSFER.md` describes it as the
  pristine reference copy at `add832af5`, never edited.

**The default.** `repaired_rules=True` is now the default of `decide` and
`decide_native` in both solvers (see the status paragraph at the top). The
defaults had to change together, because
`pathwidth_solver/tests/test_identity_mosp.py` compares MOSP's search with the
pathwidth search under default flags. Four MOSP tools that model the published
rules now name `repaired_rules=False`. Without that, seven tests failed:
`tests/test_fix_cost.py` (5), `tests/test_search_certificate.py` (1) and
`tests/test_search_check.py` (1). Every one of them compares against counts or
code written for the published rules. One case shows the repair at work. On
the minimal 10×13 instance, the `prefix` revert (old close count plus old rule
order) gave a false refutation at the optimum under the published rules. With
the repaired premises on top of it, it answers `sat`: the extra matching test
blocks whatever pruning step lost the solution. Which step that was has not
been traced; it is not a claim about Bug A.

### Tests

`pathwidth_solver/tests/test_repaired_rules.py`, 8 tests, about 2.5 s:

- the matching itself, on hand cases;
- **the `DEFINITE_CEX` node**: at `S = {2}` the published filter keeps `0`
  alone, and the repaired filter does not;
- the Python better move now prunes, where before it was ignored;
- **Python = multiword C at every word count (2, 4, 8, 16) = legacy C**, called
  directly, so every build runs on small graphs. The check covers 30 random
  graphs at 4–16 vertices, a descent from `k = n`, and 7 configurations under
  both settings. Status, order and nodes must all be equal;
- **both counterexamples**: every implementation agrees, and the answer is the
  true pathwidth at `k − 2 … k + 2`, under both settings and all 7
  configurations;
- the 4- and 8-word builds match the Python above 128 vertices under the
  repaired rules;
- the default is `True` in `decide` and `decide_native`.

`pathwidth_solver/tests/test_identity_mosp.py` now runs its node-for-node
identity against MOSP under both settings. The Python test is parametrized,
14 cases instead of 7, and the C test runs better move off and on × both
settings. The MOSP test pinned to the pre-flag digest
(`test_with_the_flag_off_nothing_changed_node_for_node`) now names
`repaired_rules=False`, since the default it relied on has changed.

### The full check

`paper2/solver_fix_pw_check.py` runs every call through up to eight
implementations. They are the pathwidth Python, the multiword C at each word
count that fits (`w2`, `w4`, `w8`, `w16`), the legacy C (at most 128 vertices),
and MOSP's Python and C on the instance rebuilt from the masks. Status, node
count and order over active vertices must all be equal. Item 01 checked MOSP's
Python against the independent oracle at every node, and item 02 checked MOSP's
C against MOSP's Python. Equality here carries both checks over to every
pathwidth build on these inputs. The configurations are those of
`solver_fix_c_check.py`: 50 on the small families, 6 on the corpus, and 4 on the
wide graphs (better move off or on × old move or memo, C against the Python
only, since MOSP's C stops at 128).

| family | instances | size (vertices) | `k` | calls per setting | implementation-calls per setting | any ≠ (old) | any ≠ (repaired) | old ≠ repaired, nodes | old ≠ repaired, answer |
|---|---|---|---|---|---|---|---|---|---|
| `pathwidth_solver/tests/test_native.py` generator | 400 | 4–14 | 0 … n+1 | 220,600 | 1,764,800 | 0 | 0 | 90 | 0 |
| pinned (`DEFINITE_CEX` ×2, Bug A, Bug B 8 and 10, `RUN_LOST_CEX`, 10×13, 17×9, 10×20) | 9 | 8–17 | 0 … n+1 | 6,450 | 51,600 | 0 | 0 | 213 | 0 |
| gadgets (`better_augment`) | 300 | 14–17 | 0 … n+1 | 270,000 | 2,160,000 | 0 | 0 | 1,403 | 0 |
| random sparse / C&S-shaped | 300 | 10–24 | 0 … n+1 | 285,850 | 2,286,800 | 0 | 0 | 2,411 | 0 |
| certified corpus, cap 30,000 nodes (≤ 40) or 10,000 (> 40) | 280 (200 at ≤ 40, 80 at 41–125) | 9–125 | opt−1, opt | 3,360 | 26,880 | 0 | 0 | 16 | 0 |
| wide sparse G(n, c/n), cap 5,000 nodes | 30 | 129–992 | three per graph | 360 | 1,080 | 0 | 0 | 18 | 0 |
| **total** | **1,319** | | | **786,620** | **6,291,160** | **0** | **0** | **4,151** | **0** |

So **12,582,320 implementation-calls, zero disagreements**, under either
setting, in status, nodes or order. The two settings took different node
counts on 4,151 configuration-`k` pairs and never gave a different answer
(calls where one side hit the cap are excluded from that count; 6,196 calls
per setting hit it). Over these capped runs the repaired rules cost 0.02%
more nodes (38,645,344 → 38,654,094). That figure is a hint, not a cost
measurement; item 04 measures the cost.

Spot timings, pathwidth C (`decide`, default flags with old move, one core),
at `k = pw` (a refutation) and `k = pw + 1`:

| graph | n | `k = pw`: published / repaired, nodes | better move: published / repaired, nodes | seconds |
|---|---|---|---|---|
| Mycielski 5 | 23 | 477 / 477 | 477 / 477 | < 0.01 |
| Mycielski 6 | 47 | 685,211 / 685,211 | 631,994 / 631,994 | 0.27–0.30 |
| grid 7×7 | 49 | 1,577 / 1,577 | 1,283 / 1,283 | < 0.01 |
| grid 5×9 | 45 | 130 / 130 | 96 / 96 | < 0.01 |
| Petersen | 10 | 25 / 25 | 25 / 25 | < 0.01 |

At `k = pw + 1` every one is `sat`, in identical nodes under both settings.

**Size range.** The implementations agree on graphs of 4–24 vertices in full
(every `k`), on corpus instances of 9–125 customers under node caps, and on
sparse random graphs of 129–992 vertices under a 5,000-node cap. Nothing here
is a cost measurement.

### Regenerate

```
cd pathwidth_solver && python -m pytest tests/test_repaired_rules.py tests/test_identity_mosp.py -q
python -m paper2.solver_fix_pw_check --workers 20   # writes paper2/data/solver_fix_pw_check.json, ~7 min
python -m paper2.solver_fix_pw_check --quick        # ~3 min
```
