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
refutation under the old rules): **none so far** (item 05: none in 17.4 M
whole-search runs at 1–17 vertices and 1.79 M differential calls at 9–75).

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

---

## Item 04: what the repair costs (2026-10-01)

**The answer: almost nothing.** Over every measurement below the two
settings never gave different answers, and no certified value moved: every
finished refutation of `optimum − 1` came back `unsat` under both. On finished
pairs the repaired rules visit **+0.004% nodes on the corpus at n ≤ 40, +0.30%
on the Chu & Stuckey classes at 50–100, −0.01% on the 125 × 125 instances that
finish, and +2.0% in the pathwidth solver** (its total is dominated by Rome, and
the median pair there is 1.000). Per node, the repaired rules cost **about 2%**
in the MOSP C (range −0.1% to +5.8% over six hard instances, measured quietly)
and **about 6%** in the pathwidth solver's descents. The old test passes and the
matching then fails on **0.03–0.27%** of definite-move candidates and **0.02%**
of better-move pairs. The definite move stops firing at a node where it used to
fire at **0.04–0.08%** of filter calls on the hard classes.

### What changed in the code

Only instrumentation. Nothing about the search changed.

- `customer_search.c`: per-thread rule counters (`RC_*`), reset by every
  `cs_decide_rules` call and read back with the new entry point
  `cs_last_rule_counts`. They count: dominance-filter calls; definite-move
  candidates passing `close ≥ open`; those failing the matching; nodes where the
  definite move fires; nodes where some candidate passed the old test and none
  fired (`definite_lost`, the repair alone, since under the published rules a
  pass always fires); better-move `(r, q)` pairs passing premises 3 and 4; those
  failing the matching; and candidates pruned. `pathwidth_solver/pathwidth/closing_search.c`
  is again a byte copy. `closing_search_w.c` has no counters.
- `satisfiability/native.py`: `last_rule_counts()` and `RULE_COUNT_NAMES`.
- The counters cost nothing measurable. Against the C as it stood before them
  (`git show HEAD:`, built to a scratch file), the published rules run 1.4–5.4%
  *faster* per node with the counters in (table 5). That is code layout, not
  the counters. Node counts are unchanged, as the test below checks.
- `paper2/solver_fix_cost.py` (the paired runs, five stages) and
  `paper2/solver_fix_cost_tables.py` (the tables,
  `paper2/data/solver_fix_cost_tables.md`).

### Tests

`tests/test_repaired_rules.py::test_the_rule_counters_count_the_repair_and_change_nothing`
covers both `DEFINITE_CEX` graphs and the two Bug B instances, every `k`, all 36
matched configurations and both settings. It checks four things:

- reading the counters does not change the node count;
- the identities hold (fails ≤ passes, fires ≤ filter calls, zero passes for a
  rule that is off);
- under the published rules the matching never fails and nothing is lost;
- under the repaired rules the matching does fail somewhere on these graphs.

Gate: PASS (1,344 MOSP tests, 110 pathwidth_solver tests).

### Method

Each job runs the same decision twice in one worker process, once with
`repaired_rules=False` and once with `repaired_rules=True`. The order alternates
from job to job. The configuration is `csearch` (Theorem 2 by
`sparse_enough_for_better_move`, every earlier survivor a dominator); at
n ≤ 40 the `default` configuration (no Theorem 2) is run as well. `k` is
`optimum − 1`, from the certified corpus (`solutions/`, read only). The
pathwidth stage runs the whole descent `pathwidth.solve(G, time_budget=120)`
under each setting with default flags (no better move). It then runs one
counter pass: the refutation of the widest component's width − 1, posed as a
MOSP instance with one product per edge. Its MOSP graph is the component, and
the MOSP C equals the pathwidth C node for node. The pass covers components of
at most 128 vertices and is capped at 5 × 10⁷ nodes. All of this ran on 22
cores of 32, so the seconds in tables 1–4 carry load noise of ±25% on single
pairs; table 5 is the per-node measurement.

### Table 1: the corpus at n ≤ 40 (6,135 certified instances, 9–40 customers)

| config | pairs | answers differ | nodes old → repaired | ratio | pairs more / fewer | s old → repaired |
|---|---|---|---|---|---|---|
| `default` | 6,135 | 0 | 228,147 → 228,154 | 1.00003 | 2 / 1 | 1.17 → 1.15 |
| `csearch` | 6,135 | 0 | 202,962 → 202,971 | 1.00004 | 6 / 3 | 1.01 → 0.99 |

Twelve instance-configuration pairs, on nine instances, differ in nodes, by at most 4%: `HS problem 2430`, `Random-30-30-4-3_0`,
`Random-40-40-2-2_0`, `Warwick 1599`, `p1540n7_0`, `p2540n2_0`, `p3040n2_0`,
`p3040n5_0`, `p4040n9_0`. Counters, repaired runs: the definite move's old test
passed 39,260 times (`default`) and 34,711 times (`csearch`), and the matching
failed 45 and 23 times (0.11%, 0.07%). The definite move stopped firing at a
node 15 and 6 times, never at 20 customers or fewer. Better-move pairs: 17,268, of
which 11 failed the matching.

### Table 2: the Chu & Stuckey classes at 50–100 (125 instances, `csearch`, 600 s per call)

| class | pairs | finished | nodes old → repaired (finished) | ratio | max / min pair ratio |
|---|---|---|---|---|---|
| 50 × 50, 50 × 100 (all densities) | 50 | 50 | 629,591 → 629,751 | 1.0003 | 1.003 / 1.000 |
| 75 × 75 (all densities) | 25 | 25 | 17,659,217 → 17,656,974 | 0.9999 | 1.004 / 0.996 |
| 100 × 50, density 2 | 5 | 5 | 5,877,966 → 5,877,392 | 0.9999 | 1.000 / 0.999 |
| 100 × 50, density 4 | 5 | 5 | 432,782,522 → 437,145,992 | **1.0101** | 1.013 / 1.001 |
| 100 × 50, density 6 | 5 | 5 | 71,551,557 → 71,798,460 | 1.0035 | 1.006 / 1.000 |
| 100 × 50, densities 8, 10 | 10 | 10 | 9,089,136 → 9,095,700 | 1.0007 | 1.001 / 1.000 |
| 100 × 100, density 4 | 5 | 3 | 800,520,212 → 800,010,791 | 0.9994 | 1.001 / 0.999 |
| 100 × 100, densities 6, 8, 10 | 15 | 15 | 19,986,470 → 19,990,150 | 1.0002 | 1.001 / 1.000 |
| 100 × 100, density 2 | 5 | 0 | — (censored, both sides) | — | — |
| **all** | **125** | **118** | **1,358,096,671 → 1,362,205,210** | **1.0030** | 1.013 / 0.996 |

Seconds on the 118 finished pairs: 1,190.9 → 1,204.1 (+1.1%). The answers
agree on all 118. Seven pairs hit 600 s on both sides: `Random-100-100-2-1…5_0`,
`-4-3_0` and `-4-5_0`. Those counts (7.27 × 10⁹ old, 6.87 × 10⁹ repaired nodes in
total) are lower bounds and say nothing about cost. Counters, repaired runs,
all 125 instances: the definite move's old test passed 2.38 × 10⁹ times and the
matching failed 3.04 × 10⁶ times (**0.13%**). The share is highest on the dense
100-customer classes (1.5% on `100-100-6` and `100-50-8`) and lowest on the
sparse ones (0.02% on `100-50-2`). The definite move stopped firing at
1.39 × 10⁶ of 3.61 × 10⁹ filter calls (**0.04%**). Better-move pairs:
7.00 × 10⁸, of which 1.65 × 10⁵ failed the matching (**0.02%**).

### Table 3: 125 × 125 (23 certified instances, `csearch`, 2 × 10⁸ nodes per call)

| density | pairs | finished | nodes old → repaired | s old → repaired |
|---|---|---|---|---|
| 10 | 5 | 5 | 628,798 → 628,799 | 0.94 → 0.88 |
| 8 | 5 | 5 | 28,482,502 → 28,482,330 | 23.9 → 24.1 |
| 6 | 5 | 1 | 61,858,208 → 61,850,290 (the finished one) | 52.6 → 52.6 |
| 4 | 5 | 0 | capped | — |
| 2 | 3 | 0 | capped | — |

The two open entries (`Random-125-125-2-2_0`, `-2-3_0`) have no certified
optimum and are not in the sample. On the 11 finished pairs the ratio is
0.99991 and the answers agree. On the 12 pairs capped on both sides (equal
nodes), seconds were 2,178.5 → 2,144.6. That is noise under load; table 5 does
it properly. The tree sizes at density 2 and 4 are 10¹¹ nodes and out of reach
here. Counters at the cap, all 23: the matching failed on **0.27%** of old-test
passes (1.08 × 10⁶ of 3.94 × 10⁸). The definite move stopped firing at **0.08%**
of filter calls. Better pairs failed at **0.02%**.

### Table 4: the pathwidth solver (`solve`, 120 s per descent, 880 graphs)

| set | graphs | both proved | proved by one side only | proved widths differ | nodes old → repaired (both proved) | ratio | s old → repaired |
|---|---|---|---|---|---|---|---|
| VSPLIB trees | 50 | 50 | 0 | 0 | 49,539,922 → 49,690,692 | 1.003 | 53.0 → 55.5 |
| VSPLIB grids | 50 | 9 | 0 | 0 | 42,139,983 → 42,842,268 | 1.017 | 33.7 → 35.4 |
| VSPLIB HB | 73 | 39 | 0 | 0 | 18,565,935 → 18,789,341 | 1.012 | 37.0 → 38.4 |
| DIMACS colouring | 58 | 30 | 0 | 0 | 190,513,249 → 192,703,052 | 1.011 | 123.3 → 130.4 |
| named | 149 | 125 | 0 | 0 | 342,295,019 → 343,456,465 | 1.003 | 187.3 → 191.3 |
| Rome, 500 sampled (seed 20261001) | 500 | 478 | 0 | 0 | 2,334,795,699 → 2,391,188,899 | 1.024 | 905.9 → 984.8 |
| **all** | **880** | **731** | **0** | **0** | **2,977,849,807 → 3,038,670,717** | **1.020** | **1,340 → 1,436** |

The 149 graphs unproved under the budget got the same width under both
settings. Every proved width, under either setting, equals the width recorded
in `pathwidth_solver/bench/results/*.csv` wherever that run was proved (1,340
graph-settings, zero differences). On Rome the median pair ratio is 1.000 and
the maximum 1.13 (`grafo7529.93`, 2.77 × 10⁸ → 3.13 × 10⁸). Excluded: the named
graph `DorogovtsevGoltsevMendesGraph` (3,282 vertices). It does not respect the
time budget on the Python path (its recorded run took 4,007 s), and its pool was
stopped after 1.8 h.

Per node, the pathwidth descents cost 0.388 → 0.412 µs on Rome, +6%. That is
more than the MOSP C's +2%. These are whole descents under load, including the
restricted upper-bound DFS. `closing_search_w.c`'s matching (per-frame `freed`
scratch, `owner[64·WORDS]`) is the candidate cause, unmeasured. Counter pass,
680 components of ≤ 128 vertices: the matching failed on 1.11 × 10⁵ of
5.39 × 10⁸ old-test passes (**0.02%**), highest on colouring (0.45%) and zero on
the trees. The definite move stopped firing at 42,420 of 6.32 × 10⁸ filter calls
(0.007%). Nodes: 1,355,670,489 → 1,359,336,939 (+0.27%).

### Table 5: per-node overhead, measured quietly (fixed node cap, 5 repetitions)

Six processes, one per instance, beside a 10-worker run. Three variants
alternate: published, repaired, and published in the pre-counter C. The cap is
5 × 10⁷ nodes; `Random-100-50-4-1_0` and `Random-75-75-2-1_0` finish below it.
Each figure is the median of 5.

| instance | µs/node old | µs/node repaired | repaired / old | old / pre-counter C |
|---|---|---|---|---|
| Random-75-75-2-1_0 | 0.722 | 0.734 | 1.018 | 0.984 |
| Random-100-50-4-1_0 | 0.549 | 0.562 | 1.024 | 0.966 |
| Random-100-100-2-1_0 | 0.549 | 0.564 | 1.028 | 0.987 |
| Random-125-125-2-1_0 | 0.563 | 0.596 | 1.058 | 0.955 |
| Random-125-125-4-1_0 | 0.768 | 0.767 | 0.999 | 0.971 |
| Random-125-125-6-2_0 | 0.660 | 0.671 | 1.016 | 0.946 |

### How often the old test passes and the matching fails

| where | definite: old test passes | matching fails | rate | nodes where the move no longer fires (per filter call) | better pairs failing the matching |
|---|---|---|---|---|---|
| corpus n ≤ 40, `csearch` | 34,711 | 23 | 0.07% | 6 (0.007%) | 11 of 17,268 (0.06%) |
| corpus n ≤ 40, `default` | 39,260 | 45 | 0.11% | 15 (0.016%) | — |
| Chu & Stuckey 50–100 | 2.38 × 10⁹ | 3.04 × 10⁶ | 0.13% | 1.39 × 10⁶ (0.04%) | 1.65 × 10⁵ of 7.00 × 10⁸ (0.02%) |
| 125 × 125, to 2 × 10⁸ nodes | 3.94 × 10⁸ | 1.08 × 10⁶ | 0.27% | 6.85 × 10⁵ (0.08%) | 2.65 × 10⁴ of 1.17 × 10⁸ (0.02%) |
| pathwidth, components ≤ 128 | 5.39 × 10⁸ | 1.11 × 10⁵ | 0.02% | 42,420 (0.007%) | — (better move off) |

A failed matching is usually not a lost firing. Some later candidate passes
both tests and fires instead, which is why "no longer fires" is a half to a
third of "matching fails". The rest of the nodes lose the definite move and go
on to the subset rule and better move. That is where the extra nodes come from.

**Size range.** MOSP: 9–40 customers, the whole certified corpus; 50–100,
the 125 Chu & Stuckey instances, 118 finished; 125 × 125, 23 instances, 11
finished, the rest per-node only. Pathwidth: 22–1,000+ vertices over 880
graphs, 731 proved under both settings. Nothing here measures the tree size of
the day-long refutations (`Random-100-100-2`, `125-125-2/4`). There the
per-node figure (+0–6%) and the counter rates are what this item can say.

### Regenerate

```
python -m pytest tests/test_repaired_rules.py -q
python -m paper2.solver_fix_cost --stage mosp40 --workers 20                         # ~1 min
python -m paper2.solver_fix_cost --stage cs --workers 12 --deadline 600              # ~22 min
python -m paper2.solver_fix_cost --stage cs125 --workers 12 --max-nodes 200000000    # ~8 min
python -m paper2.solver_fix_cost --stage pw --workers 10 --pw-budget 120 --rome 500  # ~70 min, plus one graph that ignores its budget
python -m paper2.solver_fix_cost --stage overhead --reps 5 --max-nodes 50000000      # ~10 min
python -m paper2.solver_fix_cost --stage tables      # paper2/data/solver_fix_cost_tables.md
```

Data: `paper2/data/solver_fix_cost_{mosp40,cs,cs125,pw,overhead}.csv`.

---

## Item 05: soundness of the fixed solver (2026-10-01)

**The answer: no failure anywhere.** The repaired search, written out from the
theorems with the oracle's own predicates, equals the C and the production
Python node for node on **16,279,232 runs over 40,592 graphs at 1–16 vertices**
and **1,152,000 runs over 12,000 gadget graphs at 12–17**. It answers the oracle
on every run, and it keeps a child with a solution at all **51,454,712 nodes
checked**. The differential harness, run with the solver's defaults (now
repaired), finds **zero disagreements, zero contradictions and zero witness
failures** on all **43,935 certified instances at 9–40 customers** (1,757,280
calls) and on all **1,231 at 50–75** (29,544 calls, none censored). No
certified value changed: `python -m benchmarks.corpus` still reads 6,374 of
6,376 certified, and `solutions/` is untouched.

### What changed in the code

Nothing in the solvers. New files:

- `paper2/solver_fix_soundness.py`. `repaired_decide` is `search_check.search_decide`
  (the §1.5 search ported from the document) with the two repairs stated from
  the theorems. It uses only `paper2/search_check.py` and nothing from
  `satisfiability/`:
  - the definite move picks the first playable `q` in index order with
    `close ≥ open` **and** `d_hereditary` (`IsHereditarilyDefinite`, by
    enumerating every intermediate set rather than by a matching);
  - the better move cites `q` for `r` only under premises 3 and 4 **and**
    `d_hereditary` at `cl(S ∪ {r})` (`IsRepairedBetter`).

  So the matching code in the C and the Python (`has_definite_matching`,
  `_has_definite_matching`) is checked here against the enumeration, inside
  whole searches.
- One test in `tests/test_repaired_rules.py`,
  `test_the_c_runs_the_repaired_search_as_the_theorems_state_it` (1.4 s). It
  covers `DEFINITE_CEX[0]` at every `k` and `RUN_LOST_CEX` at 5–7, which are
  graphs where the repaired runs differ from the published ones.

### The checks

At every `k` and under all 64 search configurations (the definite move, the
subset rule, the better move off or at `L` = 0, 1, 2, old move and memo each
on and off; for gadgets, the 32 with the definite move on), the checks are:

- **answer fails**: the port's answer differs from `Sol_k(∅)` (`s_searchsol_table`);
- **node losses**: at an expanded node with a solution, and with an old-move
  set that is genuinely refuted, no kept child has a solution;
- **C mismatches**: `decide_native(..., repaired_rules=True)` returns a
  different (answer, nodes) from the port;
- **Python node mismatches**: `decide(native=False, repaired_rules=True)` gives a
  different answer, or different nodes. Nodes are compared on the three
  settings where the Python runs the same search; with old move and memo both
  on, it drops the memo by design (item 02);
- **witness fails**: a satisfiable C witness that simulates above `k`;
- **runs differing from the published port**: the runs on which
  `search_check.search_decide` (the published rules) gives a different
  (answer, nodes). These are the runs where the check can tell the two rule
  sets apart. With zero C mismatches, these runs show the C is running the
  repaired rules and not the published ones.

| family | graphs | k values | port runs | nodes checked | node losses | answer fails | C mismatches | Python node mismatches | witness fails | runs differing from the published port |
|---|---|---|---|---|---|---|---|---|---|---|
| every labelled graph, 1–6 | 33,867 | 202,013 | 12,928,832 | 28,641,076 | 0 | 0 | 0 | 0 | 0 | 0 |
| atlas 7, identity + 4 labellings | 5,220 | 36,540 | 2,338,560 | 5,593,881 | 0 | 0 | 0 | 0 | 0 | 344 |
| random sparse / cover, 8–13 | 1,500 | 15,746 | 1,007,744 | 5,727,350 | 0 | 0 | 0 | 0 | 0 | 664 |
| pinned (both `DEFINITE_CEX`, Bug A, Bug B, `RUN_LOST_CEX`), 8–16 | 5 | 64 | 4,096 | 25,243 | 0 | 0 | 0 | 0 | 0 | 194 |
| gadgets (`definite_hunt_gen.py` family 4), 12–17, at opt − 1, opt, opt + 1 | 12,000 | 36,000 | 1,152,000 | 11,467,162 | 0 | 0 | 0 | 0 | 0 | 3,001 |
| **total** | **52,592** | **290,363** | **17,431,232** | **51,454,712** | **0** | **0** | **0** | **0** | **0** | **4,203** |

The repaired rules already change runs at 7 vertices (344 runs in the atlas).
The old-move hypothesis held at every node checked: no node had an old-move
set holding a solvable child. That is expected, because such a set can only
arise downstream of a lost node.

The differential harness is `learning.differential` with the solver's
defaults. It runs the identity, the relabellings (8 at n ≤ 40, 4 at 50–75) and
one re-covering, under both configurations (`default`, `csearch`). On each it
calls `decide(optimum − 1)`, expected `unsat`, and `decide(optimum)`, expected
`sat`, with the witness simulated. The deadlines are 60 s and 300 s per call.
The 50–75 set is `learning.differential_scale`'s: the campaign, eight per cell,
and the whole corpus.

| set | instances | n | calls | censored | disagreements | contradictions | witness fails | lattice oracle checked / mismatches |
|---|---|---|---|---|---|---|---|---|
| campaign | 37,800 | 10–40 | 1,511,880 | 0 | 0 | 0 | 0 | 10,800 / 0 |
| corpus | 6,135 | 9–40 | 245,400 | 0 | 0 | 0 | 0 | 2,812 / 0 |
| campaign | 1,080 | 50–75 | 25,920 | 0 | 0 | 0 | 0 | — |
| corpus | 151 | 50–75 | 3,624 | 0 | 0 | 0 | 0 | — |

This is the whole of each set, not a sample. Every refutation came back
`unsat`, including the 10 refutation calls that §33's budget had skipped. On
the 12,310 refutations at 50–75 that both this run and the committed
`differential_scale.csv` (published rules) settled, the repaired search took
0.998× the nodes. The two runs are separate, not paired in one worker. Item 04
is the cost measurement.

**Corpus.** `python -m benchmarks.corpus`: 6,372 `certified:refutation`, 2
`certified:bound`, 2 open. This is the table of 2026-09-30, unchanged.
`solutions/` has no change against `HEAD` (last touched 2026-09-27). The
(name, value, provenance) digest over all 6,376 files is `229207b225a666a5`.

**Size range.** Whole-search checks: 1–17 vertices (exhaustive to 6, every
graph at 7). Differential: 9–75 customers, every certified instance in the
named sets. The 76–125 range is not re-checked here. Item 04's paired
refutations at 50–125 (every finished pair `unsat` under both settings) are
the record there.

### Regenerate

```
python -m pytest tests/test_repaired_rules.py -q
python -m paper2.solver_fix_soundness --stage port --workers 5      # ~12 min
python -m paper2.solver_fix_soundness --stage gadget --count 12000 --workers 6   # ~19 min
python -m paper2.solver_fix_soundness --stage diff40 --workers 8    # ~11 min, 0.2 core-hours of calls
python -m paper2.solver_fix_soundness --stage diff75 --workers 6    # ~80 min, 3.7 core-hours of calls
python -m paper2.solver_fix_soundness --stage tables                # paper2/data/solver_fix_soundness_tables.md
python -m benchmarks.corpus
```

Data: `paper2/data/solver_fix_soundness_{port,gadget}.json`,
`paper2/data/solver_fix_{diff40,diff75}.csv.gz` (one row per instance, labelling and
configuration), `paper2/data/solver_fix_{diff40,diff75}_summary.csv` (verdicts
per instance).

---

## Item 06: which certified values rested only on the customer search (2026-10-01)

### The question

Every certified value has a witness that re-simulates to it, so its upper half
is never in doubt. The lower half, that `value − 1` is infeasible, came from one
of several sources. Until item 03 the customer search applied Chu & Stuckey's
definite move as published (false as stated), and before 2026-09-26 it applied a
`better_move` with known bugs. So a refutation that came from the customer search
alone is not covered by the soundness theorem. This item reads the records and
sorts every certified instance by the evidence it has that does **not** go
through the customer search. Nothing was run except bound recomputation, and
nothing was written to `solutions/`.

### What counts as independent

In order of precedence. The first that applies is the instance's "first
evidence".

| evidence | what it is | record |
|---|---|---|
| lattice | subset-lattice optimum (path counting), equal to the value, n ≤ 15; shares no code with the search | `learning/data/degeneracy.csv` (`min_search = min_construction = value`) |
| drat | refutation of `value − 1` through the direct SAT encoding, checked by drat-trim | `learning/data/proofs.csv`, `proofs_200k.csv` (`unsat`, `verified`, `k = value − 1`) |
| sat | the direct SAT binary search reported `solved` at this value | `sweep_full`, `sweep_long`, `overnight_20260917_0033_round{1,2}` (status `solved`, same value); SAT `refutation` in `learning/data/race_*.json` |
| bound | `_lower_bound` (trivial, clique, contraction degeneracy) equals the value; each part comes with a checkable object, a clique or a contraction sequence | `learning/data/instances.csv` `lb_best`, **recomputed** for the 33 instances where this is the only evidence (all 33 reproduced) |
| isomorph | an instance with the same MOSP graph (nauty certificate) has one of the above at the same value | `learning/data/canonical.csv` |

Why the SAT sweeps can be trusted, from the code at the time. All four files
were finished before the ratchet (`859fa9299`, 2026-09-17 16:24) and the customer
search (`3f5faa03b`, 2026-09-18 19:33) existed. At that time the only writer of
`solutions/` was `solve_mosp_sat` (checked at `60a68f4e3`). It ran a plain binary
search over `_sat_decision` with no time limit per call, and saved only after
the search finished. So a `solved` row was certified by SAT refutation or by the
clique bound, even when it was served from the cache. The fifth overnight file
(`overnight_20260917_1442_round1.csv`) overlaps the ratchet's first commit and a
symmetry-breaking experiment that was found unsound and disabled that afternoon
(`231f4db73`), so it is **not** counted. It would have added nothing: it covers no
listed instance. The SAT count, 6,226, matches the figure in `CLAUDE.md`.

**Recorded but not counted** as independent, because each is a search with no
proof object of its own:
- `tw_lo + 1`: a refutation by `learning.treewidth`'s decision search. It is a
  valid bound via `tw ≤ pw`.
- the expansion bound: `f(t)` is computed by branch and bound.

Treewidth is the only extra evidence for 8 listed instances, all at 40–50
customers (`secondary_evidence` column). The expansion bound is the only extra
evidence for none.

**Published optima are not independent either.** For GP1–8 and SP2–4, Frinhani
et al. (2018) computed the values with Chu & Stuckey's own solver. That solver
applies the same published Theorem 1. GP1–8 have SAT or bound evidence anyway.
SP3 and SP4 are on the list. SP2 has SAT evidence.

### Results

First independent evidence, by size (6,374 certified instances; the 2 open
entries are out of scope):

| customers | lattice | drat | sat | bound | customer search only | all |
|---|---:|---:|---:|---:|---:|---:|
| 1–15 | 2,812 | 0 | 0 | 0 | 0 | 2,812 |
| 16–40 | 0 | 2,902 | 417 | 2 | **2** | 3,323 |
| 41–75 | 0 | 0 | 79 | 28 | **44** | 151 |
| 76–100 | 0 | 0 | 14 | 3 | **46** | 63 |
| 101–134 | 0 | 0 | 2 | 0 | **23** | 25 |
| all | 2,812 | 2,902 | 512 | 33 | **115** | 6,374 |

No instance was rescued by isomorphism. The 115 listed instances are 113
distinct graphs, because SP3 and SP4 are each stored twice. Each source counted on its own
(not exclusive): lattice 2,812, DRAT 5,646, SAT 6,226, bound 4,909. No proved
bound (including treewidth and expansion) sits above any stored value.

**115 certified values rest on the customer search alone.** All are Chu &
Stuckey `Random` instances plus SP3 and SP4 (each stored twice), at 40–125 customers:

| size | instances |
|---|---:|
| 40 × 40 | 2 |
| 50 × 50 | 12 |
| 50 × 100 | 10 |
| 75 × 75 | 22 (incl. SP3, SP3_0) |
| 100 × 50 | 20 |
| 100 × 100 | 26 (incl. SP4, SP4_0) |
| 125 × 125 | 23 (all certified 125 × 125 Chu & Stuckey instances) |

The run that certified each one. It is read from the commit that first
recorded the current value as certified (`git log` of the solution file), the
compute ledger, and `recertify/results.json`. **Every one of these runs applied
the definite move as published.**

| certifying run | Theorem 2 | `better_move` code | instances |
|---|---|---|---:|
| customer-search sweep 2026-09-18 ("Close 111 of the 147"): `solve()` defaults (definite, subset, memo); each re-refuted the same way | off | — | 81 |
| `benchmarks.csearch` 2026-09-18: `solve()` defaults | off | — | 8 |
| `benchmarks.csearch` 2026-09-21/22, dense instances | off | — | 7 |
| `benchmarks.csearch` 2026-09-21/22, sparse instances; re-refuted 2026-09-23 with the first fix (part of the 41 of 55) | on | original (bugs A, B), then first fix | 7 |
| re-refutation after the first fix, 2026-09-23 (`Random-100-100-2-2_0`, corrected 21 → 20) | on | first fix | 1 |
| `benchmarks.recertify` 2026-09-24 to 09-29 (the 11 re-certified of the 13 withdrawn) | on | first fix (pre-`0eb33915`) | 11 |

So **96 of the 115 never used Theorem 2**. Their only exposure is the published
definite move, plus the subset rule, memo and old move, which are proved sound
as coded. The other 19 also used a `better_move` older than the second fix.

**What item 07 can reuse.** Items 04 and 05 already refuted `value − 1` with
`repaired_rules=True` on **94 of the 115**: item 04's paired runs (`cs`, `cs125`,
`mosp40`) and item 05's differential harness (`diff40`, `diff75`). Those
refutations are covered by `exec_repairedFullFilter_mospValue` as far as the code
matches the theorem. They are not independent of the search. The 21 not yet
re-refuted are exactly the hard ones that item 04 censored:
- `Random-100-100-2-{1..5}`, `-4-3`, `-4-5`;
- SP4 and SP4_0;
- `Random-125-125-2-{1,4,5}`, `-4-{1..5}`, `-6-{2..5}`.

Among them are the five day-long recertify refutations at 125 × 125, of 4.9 ×
10¹⁰ to 4.6 × 10¹¹ nodes. For these, item 07's cheaper path, checking
`CodeNodeRepaired` along the old run's certificate, is out of reach at the
current emitter's scale (§32: 10¹¹ nodes are not shippable). They will most
likely be marked censored.

### Size range

The whole corpus, 9–134 customers. Instances below 40 customers are all covered
by the lattice, DRAT, SAT or the bound. The list starts at 40 customers.

### Regenerate

```
python -m paper2.solver_fix_provenance     # ~15 s; reads records and git history, recomputes 33 bounds
python -m pytest tests/test_solver_fix_provenance.py -q
```

Data:
- `paper2/data/solver_fix_provenance.csv`: **the list**, 115 rows. Columns:
  instance, value, configuration, Theorem 2, `better_move` code, definite move,
  size, bounds, secondary evidence, certifying commit and date, ledger and
  recertify node counts, the loop0007 repaired refutations, graph certificate,
  and files.
- `paper2/data/solver_fix_provenance_all.csv.gz`: every corpus instance with
  every evidence flag.
- `paper2/data/solver_fix_provenance_tables.md`: the tables.
