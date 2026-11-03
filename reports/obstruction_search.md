# The duality gap of each lower-bound obstruction family, found by search

*Ralph loop0013, 2026-11-02 onward. The plan is `reports/obstruction_search_plan.md`
(§0.2 is the correction everything rests on; §0.5 the design decisions; §0.9
the kill criteria per family). §0 is the two-page summary, written last (item
10); then one section per item. Nothing here changes a solver default;
nothing re-solves an instance that is already proved; nothing is written
under `solutions/`.*

## What this document is about

**The question.** Every certified optimum in this project is a sandwich: a
witness layout above, found by a tuned search over orderings, and a
refutation below, a search tree whose dominance rules are proved sound. The
*bounds* that start the descent — the trivial bound, the clique bound,
contraction degeneracy + 1, Harper's expansion bound at a cap, the greedy
contraction-minor step — have only ever been **computed**: one formula, one
greedy rule, one budget each. None was ever **searched**. This loop runs a
real search over each family of lower-bound obstructions on instances whose
optimum is already known, so that every answer is a measurement, and reports
the family's **duality gap**: `optimum − best certified bound`.

**The families, and the direction of each** (plan §0.2). Two of the five
families the brief listed are *universal* statements, not maximisations, and
that shapes what a search can give:

| family | object | search gives | exact half | certificate | Lean |
|---|---|---|---|---|---|
| **E** (expansion: Harper and the empty pair) | `f(t) = min_{|C|=t} |N[C]|`; `s* = max_t min(t − 1, n − f(t))` | a **ceiling** `max_t (f̂(t) − t) + 1`: a found set only proves `f(t) ≤ b` | branch and bound to cap 12; SAT with DRAT per `(t, b)` | the CNF's hash and the DRAT proof per level | `exists_closedNbhd_card_le`, `card_sub_two_mul_emptyPairIndex_sub_two_le_pathwidth` (`EmptyPair.lean`) |
| **M** (contraction minors) | contraction sequences | a **floor**: the minor's proved width | the C program's refutation on the minor | the sequence, the minor's edge hash, the C output | `pathwidth_gt_of_minorOf`, `lt_mospValue_of_minorOf` (`Minor.lean`) |
| **B** (separator branches) | a separator `S` and three branches | a **floor**: third-largest certified branch width + 1 | branch widths by the C program, or M recursively | `S`, `A, B, D`, the links, the leaves' certificates | `branch_lemma_separator`, `branch_lemma` (`Sandwich.lean`) |
| **C** (baseline) | cliques; min-degree minors | floors on record (`lb_best`) | — | the clique; the ops list | `card_le_pathwidth_add_one_of_isClique`; `minDegreeIn_le_degeneracy`, `degeneracy_le_pathwidth` |
| **P** (on record) | pendant cliques | floor on record (loop0010 item 13) | — | `R, Q_i` | `pathwidth_ge_of_pendant_cliques` (`PendantCliques.lean`) |

The bound of family E is `pw ≥ min_{|A|=t} |N[A]| − t` for every `t` (Harper
1966; `exists_closedNbhd_card_le`), a minimum over **all** `t`-sets; a set
found by search gives a value *above* the true bound and is not a bound at
all. The exact floor needs the inner minimum proved, and the search's value
is a **ceiling** on what the family could ever certify. Cliques, minors and
separator branches are genuine maximisations whose search gives a floor with
a certificate.

**Units.** Every corpus bound is in optimum units (`pathwidth + 1`); "gap" is
`optimum − bound` in those units. The dataset's `width` is a pathwidth and its
floors are stated in pathwidth units (`degeneracy ≤ pw`, `MMD+ ≤ tw ≤ pw`,
`ω − 1 ≤ pw`); a gap is the same number in either unit. A value that is not a
valid bound is called a ceiling or an estimate in every table, never a bound.

**The reference.** `max(lb_best, tw + 1)` is the harness's reference
(`learning/bound_harness.py`; `ml_nature.md` §38); this loop's reference is
`floor0`, the best floor **on record** per instance (§1), which adds Harper at
cap 12, Lemma P and the minor certificates on record to it.

**The targets** (frozen by item 01 in
`reports/scratch/obstruction_search/01_ledger/targets.json`; nothing else
decides membership): `gap338` (the 338 corpus instances with
`optimum − lb_best ≥ 2`), `cs200` (the 200 Chu & Stuckey instances), `open24`
(the 24 open classes of the pathwidth dataset), `rest500` (500 other corpus
instances, stratified by the harness's seven size bands,
`numpy.random.default_rng(0)`) and `small` (every corpus instance at
`n ≤ 22`, for the exact comparisons).

**What is on record and is not solved twice** (plan §0.3): 6,376 certified
optima (`solutions/`), the feature table `learning/data/instances.csv`, the
invariants table `learning/data/ensemble/conjecture_invariants.csv.gz`,
Lemma P's corpus values (`reports/scratch/pendant_cliques/harness_values.csv`),
the contraction-minor certificates (`reports/scratch/minor_certificates/`,
`reports/scratch/minor_bound/`; `reports/minor_bound_verification.md`), the
pathwidth dataset (`paper1/data/dataset/pathwidth_dataset.jsonl.gz`, 16,636
certified classes) and its 24 open classes (`reports/scratch/dataset_open/`).

**Compute and rules.** `nice -n 19`, at most 8 workers; the C program only on
minors and branches under caps; never the Python pathwidth solver; never a
whole proved graph re-solved. Every certificate is checked by
`paper1/obstruction_check.py`, which shares no code with the searches.
"We found no prior report", never "first". Harper (1966) and Ellis,
Sudborough & Turner (1994) are cited where the loop meets them.

---

## 0. Summary

*(written by item 10)*

---

## 1. The baseline ledger and the frozen targets (item 01)

*2026-11-02. Code `learning/obstruction_ledger.py`; tests
`tests/test_obstruction_ledger.py` (12); files under
`reports/scratch/obstruction_search/01_ledger/`: `ledger_corpus.csv` (6,376
rows, every bound on record and `floor0`), `harper12.csv` (the one new
computation), `ledger_dataset.csv.gz` (16,636 rows), `targets.json`,
`tables.md` (the tables below, generated), `run.log`, `harper_run.out`,
`gate_run.out`. Regenerate:
`nice -n 19 python3 -m learning.obstruction_ledger --stage corpus --workers 8`
(8 min wall; the Harper run resumes from `harper12.csv`), `--stage dataset
--workers 8` (6 s), `--stage targets`, `--stage tables`. Size range: corpus
9–134 customers, all 6,376; dataset classes to 1,024 vertices per component
(22 classes, all VSPLIB grids, have a larger component and their floors are
over the rest of the graph); Harper at cap 12 under 60 s per instance.*

### 1.1 What was done

**The record, joined.** For every certified corpus instance: `optimum`,
`lb_trivial`, `lb_contraction`, `lb_best`, `tw_min_fill`, `ub_best` from
`learning/data/instances.csv`; `omega`, `contraction`, `exp` (Harper at the
recorded cap, `exp_cap`), `tw_lo`, `tw_hi`, `tw_exact` from the invariants
table; Lemma P (`pendant`, optimum units) from loop0010 item 13's
`reports/scratch/pendant_cliques/harness_values.csv`; the excess
`e = (n_ones − m) / n`; the collection and the Chu & Stuckey class `(n, m, d)`
from the file path and the name; the provenance and value of every
`solutions/` file, read directly (`instances.csv` is a feature table of
2026-09-25 and lists four 125 × 125 instances as `solution`; the files say
`certified:refutation` on 6,374 and `certified:bound` on 2, and the values
agree on all 6,376). The contraction-minor certificates on record were read
from their files: `reports/scratch/minor_certificates/<name>_m*.json` (claim
`pw(G) ≥ K`, floor `K + 1`) and
`reports/scratch/minor_bound/<name>_*_recorded_certificate.json` (`refuted`
in MOSP units, floor `refuted + 1`; the `.out` files beside them confirm the
unit: `lower = refuted + 1`). That is **twelve** instances with a file-backed
minor floor, not the seven the survey's §5 table lists: loop0010's
`large@recorded` run left certificates for `Random-125-125-2-4_0`, `2-5_0`,
`4-2_0`, `4-4_0` and `4-5_0` as well. Two values of the survey table have no
file (`4-1_0` = 54 at 100 vertices min-d, `8-2_0` = 92 at 115–120; logged in
`reports/scratch/pw_lower_bounds/corpus_minor.out` and `corpus_minor_hi.out`);
they are carried in the column `minor_survey`, cited, and **not** inside
`floor0`.

**The one new computation: Harper at cap 12.** `expansion_bound(inst,
max_t=12, time_budget=60)` on all 6,376 instances, cheapest first, 8 workers
at `nice -n 19`: 479 s wall, **1.01 core-hours**. 6,341 instances completed
every level to cap 12; **35 were censored at the 60 s limit** (13 at 76–100
customers, 22 at 101–134; 33 of them Chu & Stuckey), having completed caps 7
to 11 — a censored value is still a valid floor, because the module discards
an abandoned level rather than using its incumbent (its docstring: an
overestimate of `f(T + 1)` would be a wrong answer, not a slow bound). The
cap-12 value is never below the recorded `exp` and improves it on **442**
instances, by up to 21 stacks (`Random-125-125-10-5_0`: 99 = optimum, from
the recorded cap). Per instance the ledger keeps `harper12`, the cap reached,
`complete`, seconds and the levels `f(1..t)`.

**`floor0`.** The best floor on record per instance,
`floor0 = max(lb_best, tw_lo + 1, harper12, lemmaP, minor)`, with the parts
attaining it in `floor0_source`. The harness's reference is
`max(lb_best, tw + 1)`; `floor0` adds Harper at cap 12, Lemma P and the minor
certificates to it.

**The guard.** Every bound column against the optimum, and the dataset's
cheap floors against the width: **zero violations** on 6,376 × 9 bound
columns and 16,636 × 4 floors. `tests/test_obstruction_ledger.py` asserts
this on the committed files.

**The dataset.** For the 16,636 certified classes of
`paper1/data/dataset/pathwidth_dataset.jsonl.gz`: degeneracy, MMD+ with both
rules (least-c, min-d) and the largest clique `networkx.find_cliques` reaches
within 2 s or 200,000 cliques, each per connected component on bit masks, the
row's value the maximum over its components of at most 1,024 vertices; 48
core-seconds in all. No row of the jsonl lacks its edge list (the "78
header-only graphs" of the item's brief are not in this file; three classes
are edgeless, width 0, and are kept); 5 of the 430 `certified:minor` rows
carry no `minor_certificate` (`pwc-05116`, `05456`, `05480`, `14181`,
`14639`); 17 clique enumerations were censored.

### 1.2 Findings

1. **On the record, 89.9% of the corpus is closed by a bound** (`floor0`
   tight on 5,732 of 6,376) against 77.0% for the solver's own `lb_best`
   (4,909); the instances at gap ≥ 2 fall from 338 to **122**, the mean gap
   from 0.43 to 0.18 stacks, the maximum from 30 to 23. Treewidth + 1 is the
   strongest single bound (tight on 5,653; attains `floor0` alone on 898 and
   is the only part above `lb_best` on 789 tight instances). Harper at cap
   12 is tight on 4,065, above `lb_best` on 145, and the sole attainer on
   88. Lemma P is the sole attainer on 5 instances (gap 0 on 2 of them). The
   minor certificates attain alone on 11 and close 7.

2. **Of the 338, the record already closes 81 (24.0%)**: 67 by exact
   treewidth alone (the "67 gap instances would become bound-certified" of
   `ml_nature.md` §24, reproduced), **7 by Harper at cap 12 alone**
   (`Random-100-100-8-2_0`, `Random-125-125-10-3_0`, `Random-125-125-10-5_0`,
   `Random-75-75-6-3_0`, two Warwick 30-customer instances, `p4040n4_0`),
   **7 by a minor certificate alone** (`2-1_0`, `2-3_0`, `2-4_0`, `2-5_0`,
   `4-5_0`, `6-1_0`, `SP4`), none by Lemma P (it beats `lb_best` on 3 by one
   stack, as `excess_phase_diagram.md` §16 says). Against the harness's
   reference `max(lb_best, tw + 1)`, which closes 67, `floor0` is strictly
   above the reference on 104 corpus instances (96 of them in the 338) and
   closes 14 more. What is left on the 338: 135 at gap 1, 122 at gap ≥ 2
   (50 at 2, 12 at 3, 9 at 4, 8 at 5, 10 at 6, 33 at 7–23). The survey's "4
   of the 125s by minors" is 7 of 12 on file once loop0010's `large` records
   are counted (`2-2_0` at 24 of 25, `4-1_0` at 53 of 57, `4-2_0` at 55 of
   57, `4-4_0` at 50 of 51, `8-2_0` at 87 of 93 are the five short ones; the
   survey's file-less 54 and 92 would raise two of them by one and five).

3. **Where the record misses is where the solver is slow.** By size band
   (table a3) the mean `floor0` gap is 0.05 at 9–20 customers, 0.96 at
   41–60, 5.48 at 76–100 and 4.89 at 101–134; by collection (a2), Chu &
   Stuckey has 72 instances at gap ≥ 2 out of 200, Faggioli–Bentivoglio 33
   of 300, and every other collection at most 7. By Chu & Stuckey class (a6):
   mean `floor0` gap 0.2, 0.2, 0.64, 2.72, 6.64 and 4.96 at 30, 40, 50, 75,
   100 and 125 customers against `lb_best`'s 0.56, 0.84, 1.40, 4.52, 10.34,
   14.0; the 125 row sits below the 100 row only because the 125s have minor
   certificates on record and the 100s have none. Harper at cap 12 is the
   part that does the work on the **dense** classes (`125-125-10`: mean gap
   0.2; `100-100-8`: 0.8; `100-50-10`: 4.0 from `lb_best`'s 11.4) and is
   worse than `lb_best` on the sparse ones (`100-100-2`: 12.2 against 7.8;
   `75-75-2`: 6.4 against 4.8; `125-125-2`: 15.8 against 9.8) — the ridge
   classes, where contraction minors are the only part that reaches the
   optimum (`125-125-2`: 4 of 5 closed, mean gap 0.2). Pathwidth provably
   exceeds treewidth (`optimum > tw_hi + 1`) on 564 corpus instances and on
   156 of the 338: on those, no treewidth-side bound can close the gap.

4. **The dataset's cheap floors are tight on 31.4%** (5,231 of 16,636;
   table b1); MMD+ least-c is the best of the three (tight on 5,059; above
   min-d on 3,786 classes, below on 552; degeneracy alone 2,130; `ω − 1`
   970), with gap ≥ 2 on 5,541 classes and a maximum gap of 86 (the
   Carvalho & Soma MOSP classes, mean gap 63.9, where the floor is a degree
   bound on a graph of width 133). By provenance: the 3,535
   `certified:bound` classes are all tight (by construction), 1,696 of the
   12,630 `certified:refutation` classes, **0 of the 430 `certified:minor`**
   (mean gap 4.6: a class gets a minor certificate exactly where the cheap
   floor failed) and 0 of the 41 grids (gap 31.7). The 425 minor
   certificates all refute `width − 1` (so each proves its class exactly);
   their minors have median `size / n` 0.505 (0.33–0.84); the rule is min-d
   on 379 and least-c on 46. Rome (11,199 classes) has mean gap 1.29 and
   maximum 6; the control-flow graphs 0.41.

5. **The targets, frozen** (`targets.json`, seed 0, ledger sha256
   `e5918a4c…`): `gap338` 338 (102 of them Chu & Stuckey, 17 at `n ≤ 22`),
   `cs200` 200, `open24` 24 — every one with a recorded floor (`lower`) from
   `reports/scratch/dataset_open/results_quick.csv` and
   `results_quick_rescued.csv`, not from `results.csv` as the plan's §0.3
   says (that file holds solved classes only): the floor is `width − 1` on
   18 of the 24, and `pwc-15933` 4 of 5, `pwc-16471` 6 of 7, `pwc-17043` 2
   of 8, `pwc-04526` 3 of 10, `pwc-04517` 2 of 10, `pwc-17317` 3 of 10 on
   the other six — `rest500` 500 drawn from the 5,940 other corpus instances in
   proportion to the seven size bands (345 / 140 / 11 / 3 / 0 / 1 / 0; the
   pool has no instance above 100 customers outside `gap338 ∪ cs200`),
   disjoint from both, and `small` 4,123 (every corpus instance at
   `n ≤ 22`). The test re-derives `rest500` from the ledger and the seed.

### 1.3 Kill verdict and what this does not claim

**Kill: none for the item; the guard passed** (no bound on record above a
certified optimum; no dataset floor above a certified width). The harness's
validity stage (`learning/bound_harness.py`, "above optimum" must be 0) was
not re-run on the new floor: the ledger's guard is that same check, applied
to every bound column on every corpus instance, and the test asserts it on
the committed file. The item does
not claim anything about what a search would find; that `floor0` is the best
bound obtainable from the record (the minor certificates on file are those
of twelve instances; Harper is at cap 12 and censored on 35); that the
dataset's floors are more than the three cheap ones (its 430 minor
certificates are a fourth, exact by construction, not folded into
`floor_cheap`); or that the 24 open classes' recorded floors are the best
the record holds (they are the `lower` of the last quick run).

### 1.4 Tables (generated; `tables.md`)


#### (a1) every bound on record, corpus, optimum units

| bound          |   instances |   tight |   gap 1 |   gap ≥ 2 |   mean gap |   max gap |   above optimum |
|:---------------|------------:|--------:|--------:|----------:|-----------:|----------:|----------------:|
| lb_trivial     |        6376 |     238 |     726 |      5412 |       6.15 |        86 |               0 |
| lb_contraction |        6376 |    4164 |    1083 |      1129 |       0.98 |        44 |               0 |
| lb_best        |        6376 |    4909 |    1129 |       338 |       0.43 |        30 |               0 |
| omega          |        6376 |    2803 |     877 |      2696 |       2.95 |        86 |               0 |
| exp_rec        |        6376 |    3996 |    1688 |       692 |       0.81 |        40 |               0 |
| harper12       |        6376 |    4065 |    1790 |       521 |       0.58 |        30 |               0 |
| tw1            |        6376 |    5653 |     531 |       192 |       0.63 |        61 |               0 |
| lemmaP         |        6376 |    2809 |     895 |      2672 |       2.84 |        86 |               0 |
| minor          |          12 |       7 |       2 |         3 |       1.17 |         6 |               0 |
| floor0         |        6376 |    5732 |     522 |       122 |       0.18 |        23 |               0 |

#### (a2) floor0 by collection

| collection           |   instances |   lb_best tight |   lb_best mean gap |   floor0 tight |   floor0 gap 1 |   floor0 gap ≥ 2 |   floor0 mean gap |   floor0 max gap |
|:---------------------|------------:|----------------:|-------------------:|---------------:|---------------:|-----------------:|------------------:|-----------------:|
| Challenge            |          46 |              31 |               0.91 |             37 |              6 |                3 |              0.52 |                9 |
| Chu & Stuckey        |         200 |              53 |               5.42 |             88 |             40 |               72 |              2.83 |               23 |
| Faggioli-Bentivoglio |         300 |             125 |               1.02 |            168 |             99 |               33 |              0.57 |                4 |
| Harvey               |        2130 |            1605 |               0.28 |           2000 |            128 |                2 |              0.06 |                2 |
| Miller               |           1 |               1 |               0.00 |              1 |              0 |                0 |              0.00 |                0 |
| SCOOP                |          24 |               6 |               1.04 |              7 |             14 |                3 |              1.00 |                6 |
| Shaw                 |          25 |              14 |               0.44 |             20 |              5 |                0 |              0.20 |                1 |
| Simonis              |        3630 |            3058 |               0.18 |           3394 |            229 |                7 |              0.07 |                2 |
| Wilson               |          20 |              16 |               1.55 |             17 |              1 |                2 |              0.50 |                6 |

#### (a3) floor0 by size band

| band    |   instances |   lb_best tight |   lb_best mean gap |   floor0 tight |   floor0 gap 1 |   floor0 gap ≥ 2 |   floor0 mean gap |   floor0 max gap |
|:--------|------------:|----------------:|-------------------:|---------------:|---------------:|-----------------:|------------------:|-----------------:|
| 9–20    |        4122 |            3617 |               0.13 |           3913 |            208 |                1 |              0.05 |                2 |
| 21–30   |        1816 |            1134 |               0.45 |           1598 |            208 |               10 |              0.13 |                2 |
| 31–40   |         197 |              99 |               0.82 |            143 |             46 |                8 |              0.31 |                2 |
| 41–60   |         121 |              45 |               1.64 |             51 |             34 |               36 |              0.96 |                4 |
| 61–75   |          30 |               5 |               4.47 |              6 |             11 |               13 |              2.77 |                9 |
| 76–100  |          63 |               9 |               8.78 |             11 |             12 |               40 |              5.48 |               17 |
| 101–134 |          27 |               0 |              13.26 |             10 |              3 |               14 |              4.89 |               23 |

#### (a4) which part attains floor0

| part     |   attains floor0 |   attains alone |   attains alone and tight |   on the 338: attains alone |   on the 338: closes alone |
|:---------|-----------------:|----------------:|--------------------------:|----------------------------:|---------------------------:|
| lb_best  |             5344 |              16 |                         0 |                          16 |                          0 |
| tw1      |             6172 |             898 |                       789 |                         176 |                         67 |
| harper12 |             4480 |              88 |                        13 |                          82 |                          7 |
| lemmaP   |             2920 |               5 |                         2 |                           3 |                          0 |
| minor    |               11 |              11 |                         7 |                          11 |                          7 |

#### (a5) the 338 against the record

| bound    |   with a value |   closes (gap 0) |   gap 1 |   gap ≥ 2 |   mean gap |   max gap |   beats lb_best |
|:---------|---------------:|-----------------:|--------:|----------:|-----------:|----------:|----------------:|
| lb_best  |            338 |                0 |       0 |       338 |       4.78 |        30 |               0 |
| tw1      |            338 |               67 |     116 |       155 |       8.88 |        61 |             199 |
| harper12 |            338 |                7 |      41 |       290 |       3.99 |        30 |             127 |
| lemmaP   |            338 |                0 |       3 |       335 |      13.80 |        83 |               3 |
| minor    |             12 |                7 |       2 |         3 |       1.17 |         6 |              12 |
| floor0   |            338 |               81 |     135 |       122 |       2.33 |        23 |             290 |

#### (a6) the 200 Chu & Stuckey by class

|   n |   m |   d |   instances |   mean opt |   lb_best gap |   harper12 gap |   tw1 gap |   lemmaP gap |   floor0 gap |   floor0 tight |   harper12 complete |   harper12 s |
|----:|----:|----:|------------:|-----------:|--------------:|---------------:|----------:|-------------:|-------------:|---------------:|--------------------:|-------------:|
|  30 |  30 |   2 |           5 |       8.60 |          1.00 |           1.40 |      0.80 |         3.20 |         0.80 |              2 |                   5 |         0.21 |
|  30 |  30 |   4 |           5 |      16.00 |          1.00 |           1.00 |      0.00 |         7.00 |         0.00 |              5 |                   5 |         0.06 |
|  30 |  30 |   6 |           5 |      21.20 |          0.40 |           0.40 |      0.20 |         8.40 |         0.20 |              4 |                   5 |         0.02 |
|  30 |  30 |   8 |           5 |      25.20 |          0.20 |           0.20 |      0.00 |         6.60 |         0.00 |              5 |                   5 |         0.01 |
|  30 |  30 |  10 |           5 |      27.00 |          0.20 |           0.40 |      0.20 |         2.60 |         0.00 |              5 |                   5 |         0.00 |
|  40 |  40 |   2 |           5 |      11.00 |          2.20 |           1.60 |      0.20 |         4.20 |         0.20 |              4 |                   5 |         0.87 |
|  40 |  40 |   4 |           5 |      20.20 |          1.40 |           1.00 |      1.60 |        11.40 |         0.80 |              1 |                   5 |         0.36 |
|  40 |  40 |   6 |           5 |      28.20 |          0.40 |           0.40 |      0.00 |        15.80 |         0.00 |              5 |                   5 |         0.13 |
|  40 |  40 |   8 |           5 |      32.60 |          0.20 |           0.20 |      0.00 |        15.00 |         0.00 |              5 |                   5 |         0.02 |
|  40 |  40 |  10 |           5 |      35.40 |          0.00 |           0.00 |      0.00 |        11.20 |         0.00 |              5 |                   5 |         0.01 |
|  50 |  50 |   2 |           5 |      13.20 |          3.20 |           2.80 |      2.20 |         6.60 |         2.00 |              0 |                   5 |         2.90 |
|  50 |  50 |   4 |           5 |      23.80 |          3.60 |           1.20 |      6.80 |        14.60 |         1.20 |              0 |                   5 |         1.76 |
|  50 |  50 |   6 |           5 |      35.20 |          0.80 |           0.80 |      3.60 |        22.00 |         0.80 |              1 |                   5 |         0.43 |
|  50 |  50 |   8 |           5 |      40.40 |          0.20 |           0.20 |      0.00 |        21.60 |         0.00 |              5 |                   5 |         0.09 |
|  50 |  50 |  10 |           5 |      44.40 |          0.40 |           0.40 |      0.00 |        19.40 |         0.00 |              5 |                   5 |         0.02 |
|  50 | 100 |   2 |           5 |      21.20 |          4.80 |           2.00 |      9.40 |        14.40 |         2.00 |              0 |                   5 |         5.10 |
|  50 | 100 |   4 |           5 |      34.60 |          0.40 |           0.40 |      5.40 |        23.60 |         0.40 |              3 |                   5 |         0.57 |
|  50 | 100 |   6 |           5 |      42.40 |          0.20 |           0.20 |      0.00 |        23.20 |         0.00 |              5 |                   5 |         0.06 |
|  50 | 100 |   8 |           5 |      46.20 |          0.20 |           0.20 |      0.00 |        16.40 |         0.00 |              5 |                   5 |         0.01 |
|  50 | 100 |  10 |           5 |      47.80 |          0.20 |           0.20 |      0.00 |         5.40 |         0.00 |              5 |                   5 |         0.00 |
|  75 |  75 |   2 |           5 |      15.80 |          4.80 |           6.40 |      9.40 |         9.20 |         4.80 |              0 |                   5 |        27.47 |
|  75 |  75 |   4 |           5 |      34.20 |         12.80 |           6.80 |     22.00 |        24.80 |         6.80 |              0 |                   5 |         9.78 |
|  75 |  75 |   6 |           5 |      50.00 |          4.00 |           1.00 |     27.80 |        37.00 |         1.00 |              1 |                   5 |        13.31 |
|  75 |  75 |   8 |           5 |      59.40 |          0.60 |           0.60 |     26.00 |        41.20 |         0.60 |              2 |                   5 |         2.39 |
|  75 |  75 |  10 |           5 |      64.80 |          0.40 |           0.40 |     20.00 |        42.00 |         0.40 |              3 |                   5 |         0.46 |
| 100 |  50 |   2 |           5 |      11.60 |          2.80 |           7.40 |      3.80 |         3.80 |         2.80 |              0 |                   5 |        15.84 |
| 100 |  50 |   4 |           5 |      26.40 |         10.40 |          12.40 |     17.00 |        16.80 |        10.40 |              0 |                   5 |        22.83 |
| 100 |  50 |   6 |           5 |      44.00 |         18.00 |          11.80 |     30.20 |        31.40 |        11.80 |              0 |                   5 |        20.15 |
| 100 |  50 |   8 |           5 |      56.20 |         15.60 |           7.60 |     35.40 |        40.00 |         7.60 |              0 |                   5 |        23.44 |
| 100 |  50 |  10 |           5 |      67.20 |         11.40 |           4.00 |     38.20 |        49.00 |         4.00 |              0 |                   5 |        13.70 |
| 100 | 100 |   2 |           5 |      20.20 |          7.80 |          12.20 |     11.80 |        11.80 |         7.80 |              0 |                   0 |        60.00 |
| 100 | 100 |   4 |           5 |      45.00 |         19.20 |          13.80 |     32.60 |        34.80 |        13.80 |              0 |                   1 |        54.13 |
| 100 | 100 |   6 |           5 |      64.60 |         14.00 |           6.60 |     42.00 |        51.40 |         6.60 |              0 |                   3 |        43.73 |
| 100 | 100 |   8 |           5 |      76.60 |          3.40 |           0.80 |     41.40 |        59.20 |         0.80 |              1 |                   5 |        42.63 |
| 100 | 100 |  10 |           5 |      84.60 |          0.80 |           0.80 |     36.20 |        63.60 |         0.80 |              1 |                   5 |         9.07 |
| 125 | 125 |   2 |           5 |      22.80 |          9.80 |          15.80 |     15.80 |        15.80 |         0.20 |              4 |                   0 |        60.00 |
| 125 | 125 |   4 |           5 |      53.00 |         27.40 |          25.00 |     41.60 |        43.00 |         6.00 |              1 |                   0 |        60.00 |
| 125 | 125 |   6 |           5 |      78.40 |         22.20 |          15.60 |     55.80 |        65.00 |        13.60 |              1 |                   0 |        60.00 |
| 125 | 125 |   8 |           5 |      93.60 |          8.80 |           4.80 |     57.40 |        77.00 |         4.80 |              0 |                   0 |        60.00 |
| 125 | 125 |  10 |           5 |     103.20 |          1.80 |           0.20 |     52.00 |        83.40 |         0.20 |              4 |                   3 |        52.67 |

#### (a7) Harper at cap 12 by band

| band    |   instances |   run |   complete to cap 12 |   censored at 60 s |   mean cap reached |   core-seconds |   harper12 > exp_rec |   harper12 > lb_best |   harper12 tight |
|:--------|------------:|------:|---------------------:|-------------------:|-------------------:|---------------:|---------------------:|---------------------:|-----------------:|
| 9–20    |        4122 |  4122 |                 4122 |                  0 |               1.47 |           3.14 |                   10 |                    0 |             2933 |
| 21–30   |        1816 |  1816 |                 1816 |                  0 |               2.88 |          35.83 |                  203 |                   32 |              989 |
| 31–40   |         197 |   197 |                  197 |                  0 |               4.56 |          38.28 |                   64 |                   26 |               92 |
| 41–60   |         121 |   121 |                  121 |                  0 |               6.93 |         122.51 |                   68 |                   26 |               31 |
| 61–75   |          30 |    30 |                   30 |                  0 |               8.67 |         317.28 |                   21 |                   12 |                6 |
| 76–100  |          63 |    63 |                   50 |                 13 |               9.08 |        1651.41 |                   49 |                   31 |               10 |
| 101–134 |          27 |    27 |                    5 |                 22 |               9.93 |        1471.06 |                   27 |                   18 |                4 |

Harper rows without a value (not reached under the wall): 0.

#### (a8) the instances with a minor certificate on record

| instance_name        |   optimum |   lb_best |   harper12 |   tw1 |   lemmaP |   minor | minor_source                                                                       |   minor_survey |   floor0 |
|:---------------------|----------:|----------:|-----------:|------:|---------:|--------:|:-----------------------------------------------------------------------------------|---------------:|---------:|
| Random-125-125-2-1_0 |        24 |        13 |          8 |     8 |        8 |      24 | reports/scratch/minor_certificates/Random-125-125-2-1_0_m87.json                   |            nan |       24 |
| Random-125-125-2-2_0 |        25 |        13 |          7 |     6 |        6 |      24 | reports/scratch/minor_bound/Random-125-125-2-2_0_large_recorded_certificate.json   |            nan |       24 |
| Random-125-125-2-3_0 |        21 |        12 |          6 |     7 |        7 |      21 | reports/scratch/minor_certificates/Random-125-125-2-3_0_m70.json                   |            nan |       21 |
| Random-125-125-2-4_0 |        24 |        15 |          8 |     8 |        8 |      24 | reports/scratch/minor_bound/Random-125-125-2-4_0_large_recorded_certificate.json   |            nan |       24 |
| Random-125-125-2-5_0 |        20 |        12 |          6 |     6 |        6 |      20 | reports/scratch/minor_bound/Random-125-125-2-5_0_large_recorded_certificate.json   |            nan |       20 |
| Random-125-125-4-1_0 |        57 |        27 |         33 |    12 |       10 |      53 | reports/scratch/minor_bound/Random-125-125-4-1_0_default_recorded_certificate.json |             54 |       53 |
| Random-125-125-4-2_0 |        57 |        27 |         32 |    12 |       11 |      55 | reports/scratch/minor_bound/Random-125-125-4-2_0_large_recorded_certificate.json   |            nan |       55 |
| Random-125-125-4-4_0 |        51 |        24 |         21 |    11 |        9 |      50 | reports/scratch/minor_bound/Random-125-125-4-4_0_large_recorded_certificate.json   |            nan |       50 |
| Random-125-125-4-5_0 |        46 |        23 |         23 |    10 |        8 |      46 | reports/scratch/minor_bound/Random-125-125-4-5_0_large_recorded_certificate.json   |            nan |       46 |
| Random-125-125-6-1_0 |        81 |        63 |         71 |    23 |       14 |      81 | reports/scratch/minor_certificates/Random-125-125-6-1_0_m120.json                  |            nan |       81 |
| Random-125-125-8-2_0 |        93 |        84 |         89 |    37 |       16 |      87 | reports/scratch/minor_bound/Random-125-125-8-2_0_default_recorded_certificate.json |             92 |       89 |
| SP4                  |        53 |        37 |         44 |    16 |       13 |      53 | reports/scratch/minor_certificates/SP4_m96.json                                    |            nan |       53 |

#### (b1) dataset: 16636 certified classes, cheap floors against the width (pathwidth units)

| floor (pw units)   |   classes |   tight |   gap 1 |   gap ≥ 2 |   mean gap |   max gap |   above width |
|:-------------------|----------:|--------:|--------:|----------:|-----------:|----------:|--------------:|
| degeneracy         |     16636 |    2130 |    3106 |     11400 |       3.63 |       109 |             0 |
| mmd_leastc         |     16636 |    5059 |    5804 |      5773 |       1.70 |        86 |             0 |
| mmd_mind           |     16636 |    4744 |    5347 |      6545 |       1.94 |        88 |             0 |
| omega1             |     16636 |     970 |    2626 |     13040 |       4.47 |       249 |             0 |
| floor_cheap        |     16636 |    5231 |    5864 |      5541 |       1.67 |        86 |             0 |

Rows with a component above 1024 vertices (floors over the rest): 22; omega censored (2 s / 200000 cliques): 17; edgeless classes: 3; seconds total: 48.

#### (b2) by collection

| collection                   |   classes |   mean n |   mean width |   floor_cheap tight |   gap ≥ 2 |   mean gap |   max gap |   skipped |
|:-----------------------------|----------:|---------:|-------------:|--------------------:|----------:|-----------:|----------:|----------:|
| Rome graphs                  |     11199 |    52.87 |         5.49 |                2896 |      3916 |       1.29 |         6 |         0 |
| MOSP: Challenge 2005         |      3169 |    21.86 |        14.37 |                1459 |       794 |       0.97 |        26 |         0 |
| freetdi control-flow graphs  |      1061 |    55.78 |         2.66 |                 662 |        35 |       0.41 |         3 |         0 |
| MOSP: Faggioli & Bentivoglio |       274 |    31.66 |         8.42 |                  74 |       125 |       1.53 |         5 |         0 |
| MOSP: Chu & Stuckey          |       200 |    71.25 |        40.16 |                   3 |       183 |      12.71 |        44 |         0 |
| PACE 2017 exact              |       129 |   254.86 |        33.81 |                   7 |       116 |       5.33 |        15 |         0 |
| freetdi named graphs         |       126 |    42.79 |        15.63 |                  23 |        84 |       6.71 |        52 |         0 |
| Small (Marti et al. 2008)    |        84 |    20.29 |         3.13 |                  52 |         0 |       0.38 |         1 |         0 |
| PACE 2017 bonus              |        78 |   197.22 |        15.29 |                   0 |        77 |       6.12 |        14 |         0 |
| PACE 2016                    |        70 |    83.66 |        20.09 |                  20 |        31 |       4.10 |        29 |         0 |
| VSPLIB grids                 |        50 |  1078.50 |        29.50 |                   0 |        49 |      26.88 |        54 |        22 |
| VSPLIB Harwell-Boeing        |        44 |   230.73 |        13.73 |                   8 |        29 |       3.64 |        14 |         0 |
| MOSP: Carvalho & Soma 2015   |        38 |   167.11 |       133.18 |                   0 |        38 |      63.89 |        86 |         0 |
| TreewidthLIB colouring       |        33 |   124.24 |        36.79 |                  13 |        15 |       9.27 |        60 |         0 |
| VSPLIB trees                 |        28 |   137.71 |         4.43 |                   0 |        28 |       3.43 |         4 |         0 |
| MOSP: SCOOP                  |        24 |    45.71 |         6.75 |                   6 |         3 |       1.08 |         6 |         0 |
| PACE 2017 heuristic          |        19 |   176.63 |        61.26 |                   3 |        15 |       6.11 |        25 |         0 |
| VLSI gate matrix circuits    |        10 |    30.10 |         7.80 |                   5 |         3 |       0.90 |         3 |         0 |

#### (b3) the certified:minor classes

|   certified:minor classes |   with certificate |   mean size/n |   median size/n |   min size/n |   max size/n |   least-c |   min-d |   refuted = width − 1 |   floor_cheap tight |
|--------------------------:|-------------------:|--------------:|----------------:|-------------:|-------------:|----------:|--------:|----------------------:|--------------------:|
|                       430 |                425 |         0.568 |           0.505 |        0.329 |        0.838 |        46 |     379 |                   425 |                   0 |

#### (c) targets

```
{
 "gap338": 338,
 "cs200": 200,
 "open24": 24,
 "rest500": 500,
 "small": 4123,
 "pool_for_rest500": 5940,
 "pool_by_band": {
  "9\u201320": 4105,
  "21\u201330": 1659,
  "31\u201340": 131,
  "41\u201360": 32,
  "61\u201375": 3,
  "76\u2013100": 10,
  "101\u2013134": 0
 },
 "rest500_by_band": {
  "9\u201320": 345,
  "21\u201330": 140,
  "31\u201340": 11,
  "41\u201360": 3,
  "76\u2013100": 1
 },
 "gap338_and_cs200": 102,
 "small_and_gap338": 17
}
```
