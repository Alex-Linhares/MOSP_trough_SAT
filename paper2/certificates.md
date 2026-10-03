# Certificates for the repaired rules

*loop0008 item 05, 2026-10-03. This is section 4's proof object: a refutation
by the customer search under the repaired rules, written out so that a third
party can check it without our search code. Code:*

- *the emitter, `learning/search_certificate.py`, `emit(..., repaired_rules=True)`;*
- *the checker, `paper2/certificate_check.py`, standard library only;*
- *the study, `paper2/certificates.py`;*
- *the tests, `tests/test_certificate_check.py` (20).*

*Data: `paper2/data/certificates/`.*

```bash
python -m paper2.certificates --stage run --min-customers 41 --max-customers 75 --workers 4 --deadline 60   # 151 instances, 9 min on 4 workers
python -m paper2.certificates --stage run --max-customers 40 --workers 4 --deadline 60                      # 6,135 more, under 1 min
python -m paper2.certificates --stage failures                                                              # section 4: failures.json, bundles/
python -m paper2.certificates --stage tables                                                                # tables.md
python paper2/certificate_check.py paper2/data/certificates/bundles/example_repaired.json.gz                # check one bundle by hand
python -m pytest tests/test_certificate_check.py -q
```

The size range is the certified MOSP corpus at 9–75 customers: 6,286 instances
with optimum at least 2, each refuted at `optimum − 1`. Above 75 the Python
emitter does not finish within its budget (section 6). Nothing is written to
`solutions/`, and no solver default changes.

## 1. What changed from the published-rules certificate

The certificate of `reports/ml_nature.md` §32 records the search tree. Every
pruning step names its rule and its witness. The checker recomputes everything
else from the instance and the path, including the free moves, the cost cut,
Theorem 3's set `Q(S)` and the closed set at each node. That design is
unchanged. Two step types change:

| step | published (§32) | repaired (this item) |
|:--|:--|:--|
| definite move | `["definite", q]`, checked as `close(q,S) ≥ open(q,S)` | `["definite", q, M]` |
| better move | `["better", r, q]`, checked as premise 3 and `close' ≥ open'` | `["better", r, q, M]` |

`M` is a list of pairs `[d, s]`, the witness of `HasDefiniteMatching`
(`Search/DefiniteMatching.lean`). For the definite move at state `S`, the
checker requires all of the following:

- the `d` are distinct;
- the `s` are distinct;
- each `d ≠ q` is a remaining customer that `q` frees, meaning `o(d,S) ⊆ o(q,S)`;
- each `s ∈ o(d,S)`;
- `|M| ≥ open(q,S) − 1`.

The better move has the same conditions at the child `T = cl(S ∪ {r})`, with
`o(d,T) = N[d] ∖ O(S ∪ {r})` nonempty, and premise 3 is still checked. By
Theorem 4.8 (`isHereditarilyDefinite_iff_hasDefiniteMatching`), such an `M`
exists exactly when the repaired premise holds. The premise is an existential,
so the certificate carries the matching and the checker verifies it in linear
time. The checker never searches for a matching.

A published-rule step, one without `M`, is **rejected**, whatever its
counts say.

A certificate may also carry `start`, a closed set at the root. It then
claims "no closing order extending `start` costs at most `k`". Only
`start = ∅` gives `MOSP > k`, and the checker's output says which claim it
verified. `start` exists for the hand-built failures of section 4.

## 2. The checker, and what it trusts

`paper2/certificate_check.py` reads a bundle `{"matrix", "certificate"}`. It
imports nothing from this repository, and a test parses its imports to keep it
that way. It computes `N[c]` from the 0/1 matrix and checks the certificate's
SHA-256 of that matrix. It then walks the tree with an explicit stack. At each
node it verifies:

1. the listed free moves are exactly the remaining `c` with `N[c] ⊆ O(S)`;
2. the node is not a solution;
3. a memo node cites a completed refutation of the same closed set, and memo
   references are accepted only with old move off;
4. every step's premise, recomputed from the matrix and the state:
   - the subset rule with its index tie-break;
   - the definite and better moves as in section 1;
5. **exhaustiveness**: every candidate of cost at most `k` is a child or is
   covered, and every chain of covers ends at a child or in `Q(S)`, with no
   cycle;
6. the children, recursively, with `Q` inherited by the reinsertion test.

It also checks that every child is a playable candidate and that every node is
reachable from the root.

**Trust.** The checker relies on the Lean theorems that make each accepted step
sound. Each link of a cover chain is one theorem:

| link | theorem | Lean |
|:--|:--|:--|
| subset | Lemma 4.9 | `searchSol_cl_insert_of_newlyOpened_subset` |
| definite | Theorem 4.7 | `solvable_cl_insert_of_hereditarilyDefinite`, with Theorem 4.8 for the matching |
| better | Theorem 4.14 | `solvable_cl_insert_of_repairedBetter` |
| old move | Lemma 4.15, inside Theorem 4.18's induction | `Exec.sound` |

Composing these per node is the argument of Proposition 4.17 and Theorem 4.18.
**The checker's acceptance condition itself is not a Lean statement.** The
filter of Theorem 4.19 is one particular way to produce covers. The checker
accepts any acyclic covering by checked links, and that this is sound is a
short paper argument, written in this section, not a formal one.

What the checker does **not** trust: the search, the emitter, the C, or the
certificate's `config`. The config only switches the old-move and memo
bookkeeping, and a certificate that lies about them fails step 5 or step 3.
This is the division a DRAT proof makes between resolution and the solver.

## 3. Results on the corpus, 9–75 customers

All certified corpus instances with optimum at least 2 were emitted at
`optimum − 1` with a 60 s emission budget, under two configurations:

- `default`: Theorem 1, the subset rule and Theorem 3;
- `csearch`: the same, with Theorem 2 where `sparse_enough_for_better_move`
  holds, and every earlier candidate allowed as a dominator.

Both use the repaired premises. Each certificate was checked by
`certificate_check.py` from a JSON round trip. Source: `paper2/data/certificates/tables.md`.

| band | config | instances | refuted | unknown (60 s) | verified | rejected | definite / better steps | matching edges | gz bytes median / max | check ms median / p90 / max |
|:--|:--|--:|--:|--:|--:|--:|:--|--:|:--|:--|
| 9–10 | csearch | 1,614 | 1,614 | 0 | 1,614 | 0 | 307 / 92 | 32 | 332 / 519 | 0.04 / 0.1 / 0.2 |
| 11–20 | csearch | 2,508 | 2,508 | 0 | 2,508 | 0 | 2,657 / 1,171 | 658 | 356 / 1,431 | 0.08 / 0.4 / 2 |
| 21–30 | csearch | 1,816 | 1,816 | 0 | 1,816 | 0 | 14,796 / 6,148 | 5,675 | 414 / 17,199 | 0.24 / 2.6 / 33 |
| 31–40 | csearch | 197 | 197 | 0 | 197 | 0 | 46,337 / 18,176 | 17,150 | 650 / 392,188 | 1.3 / 96 / 1,304 |
| 41–50 | csearch | 120 | 120 | 0 | 120 | 0 | 530,424 / 120,302 | 152,597 | 12,045 / 2,242,150 | 33 / 2,150 / 6,857 |
| 51–60 | csearch | 1 | 1 | 0 | 1 | 0 | 5,155 / 2,709 | 1,885 | 126,508 | 279 |
| 61–75 | csearch | 30 | 19 | 11 | 19 | 0 | 103,095 / 31,404 | 37,261 | 26,516 / 5,332,005 | 144 / 7,887 / 34,602 |
| 41–50 | default | 120 | 120 | 0 | 120 | 0 | 748,952 / – | 191,780 | 12,665 / 2,588,603 | 37 / 2,552 / 7,909 |
| 51–60 | default | 1 | 1 | 0 | 1 | 0 | 24,685 / – | 8,797 | 661,951 | 1,198 |
| 61–75 | default | 30 | 20 | 10 | 20 | 0 | 312,897 / – | 110,118 | 34,162 / 11,555,563 | 187 / 15,058 / 68,221 |

Below 41, `default` is within a few percent of `csearch` row by row, and
`tables.md` has both.

**Headline.** At 41–75 customers, **141 of 151 refutations verify under
`default` and 140 under `csearch`**, with no rejection. That is the same 141
that §32 verified under the published rules, less one `csearch` emission
(`Random-75-75-4-1_0`) that crossed the 60 s budget on a loaded machine. At
9–40, all 6,135 verify under both configurations. Corpus-wide, 6,276 and 6,275
of 6,286 verify, and 0 are rejected.

The ten that time out under both configurations are:

- `SP3` and `SP3_0`;
- `Random-75-75-2-{1..5}_0`;
- `Random-75-75-4-{3,4,5}_0`.

They are the ten §32 could not emit either. Each budget-limited emission visited
0.7–1.6 × 10⁶ branches before its deadline.

**Size and time.** Over the 6,275 `csearch` certificates:

- 3.35 M nodes and 1.62 M steps;
- 702,771 definite, 738,554 subset and 180,002 better steps;
- 215,258 matching edges;
- **35.5 MB gzipped**, checked in **147 s**, which is 44 µs per node in pure
  Python.

The largest single certificate is 11.6 MB gzipped (`default`, 75 customers),
and the slowest check takes 68 s.

**The matchings are cheap.** They add 0.07 edges per node, and most definite
steps carry an empty matching. That is because `open ≤ 1` there, and the
repair adds nothing at depth 1 (Lemma 4.24). The checker is 3× slower per
node than §32's (44 against 14.8 µs). That is the cost of a stack-based walk
and of rebuilding the covering at every node, not of the matchings.

**Fidelity of the emitter.** The emitter is part of the evidence only to the
extent that it emits the search's tree. Its status and branch count equal:

- `decide(native=False, repaired_rules=True)` at every `k` up to the first
  satisfiable one, under three configurations, on 300 random instances at
  2–16 customers: 2,463 refutations, every one checked;
- the C (`native=True, memo=False, repaired_rules=True`, Theorem 2 with every
  dominator) on 200 sparse instances at 8–16 customers: 968 decisions.

The tests repeat both on 40 instances each. The C runs the memo beside old
move, which the certificate cannot carry (§32), so the emitted tree is the C's
tree without the memo.

## 4. Hand-built failures

**The published rules on `DEFINITE_CEX`.** Counterexample 4.5's two graphs, on
14 and 16 customers (`paper2/search_check.py`), are rooted at
`start = S = {2}` with `k = 6` and `k = 7` respectively. The published rules
keep only `q = 0` at the root (`close = open = 3`). Every extension of
`cl(S ∪ {0})` fails (`cex_not_solvable_child`), so the published emitter
returns a complete, exhaustive tree with status `unsat`. Its claim is "no
solution extends {2}", and that claim is false.

| graph | config | published tree | §32's checker (published premises) | `certificate_check.py` | same, with a largest matching attached | repaired emitter from {2} |
|:--|:--|:--|:--|:--|:--|:--|
| 14 customers, k = 6 | default | unsat, 7 branches | **accepts** | rejects: *definite move on 0: no matching witness* | rejects: *matching has 1 edges, open − 1 = 2* | sat, order `2, 3, 4, 1, 6, 12, 13, 0, …`, cost 6 |
| 14, k = 6 | csearch | unsat, 5 | **accepts** | rejects (same) | rejects (same) | sat, cost 6 |
| 16, k = 7 | default | unsat, 8 | **accepts** | rejects (same) | rejects (same) | sat, cost 7 |
| 16, k = 7 | csearch | unsat, 6 | **accepts** | rejects (same) | rejects (same) | sat, cost 7 |

The "largest matching" column is the strongest forgery possible: a
maximum matching between the customers `0` frees and its new stacks, attached
to the root step. It has one edge, `[3, 0]`, where two are needed, which is
Lean's `not_isHereditarilyDefinite_cex` seen from the witness side.

**What this shows.** The published certificate is accepted by a checker of the
published premises and is a false claim. The repaired checker rejects it. The
repaired emitter, run from the same state, finds the solution, which the test
re-simulates. No whole-instance false refutation exists on these graphs: from
`∅` both rule sets answer correctly at every `k`, which is why the root had to
be `{2}`.

**Corrupted matchings.** The base certificate is the repaired `csearch`
certificate of *Warwick 877* (`wbo_20_10.txt`, 20 × 10, optimum 8) at `k = 7`.
It has 55 nodes, and both its definite and its better steps carry two-edge
matchings. It verifies as emitted. Each single corruption is rejected for the
stated reason:

| corruption | reason |
|:--|:--|
| drop an edge (definite, node 28) | matching has 1 edges, open − 1 = 2 |
| give the second edge the first's stack | stack 8 matched twice |
| give the second edge the first's customer | customer 8 matched twice |
| an edge to a stack outside `N[d]` | stack 1 is not newly opened by 8 |
| an edge from `q` itself | matched customer 0 is not one the move frees |
| drop an edge (better (1, 0), root) | matching has 1 edges, open − 1 = 2 |
| strip the matching | no matching witness (a published-rule step) |

Five tree corruptions are rejected too:

- raise `k`;
- mark a leaf `sat`;
- mark the certificate `sat`;
- drop a child;
- change the digest.

So is Bug B. The rule-order revert of `reports/better_move_bug.md` §7 on
`CYCLE_10x20`, emitted under the repaired premises, still refutes the optimum
4. Every step's premise holds, matching included, and the checker rejects it
as a *covering cycle through [6, 9]*. Bug A, the old close count, produced no
refutation to reject on the three pinned instances under the repaired premises
(17 × 9, 10 × 13 and `CYCLE_10x20`): the matching test refused the
over-strong cites there. That is three instances, not a claim.

All are in `paper2/data/certificates/failures.json`. The `DEFINITE_CEX`
certificates and the Warwick example are bundles in `bundles/`, checkable with
the command at the top.

## 5. A C emitter, proposed and not built

The Python emitter stops at about 10⁶ branches a minute, which is why 10
instances at 75 customers are unknown here. The refutations that matter most,
the 125 × 125 values of `solver_fix.md`, have 10¹⁰–10¹¹ nodes. Proposed:

- **Where.** A third flag on `search_t` in `satisfiability/customer_search.c`,
  `FILE *cert`. When it is set, `search()` writes one record per node in visit
  order, and `dominance_filter` / `better_move_pass` write each step as they
  take it. The matching is already in hand: `has_definite_matching` fills
  `owner[]` before it returns true. It only needs copying out, instead of
  being recomputed.
- **Format.** Binary, not JSON. A node is
  `move:u8, nfree:u8, free[]:u8, nsteps:u16, steps[], nchildren:u16`. A step is
  `rule:u8, r:u8, q:u8, nm:u8, (d,s)[]:u8×2`. `free` can be dropped, since the
  checker recomputes it. That is about 8–12 bytes a node, against 60 in
  JSON. A streaming gzip or zstd layer on top, and a JSON transcoder for small
  cases.
- **Configuration.** Memo off, or memo with old move off. The checker cannot
  accept memo references under old move (§32, §4.4.2). Measured cost: the memo
  saves the C 40% of nodes at `n ≤ 40` (§32). That cost is the price of
  checkability.
- **Splitting.** The root split of `paper2/solver_fix_split.py` (Theorem 4.18,
  `Search/Split.lean`) already refutes each root child in its own process
  from its own state with an empty `Q`. With `start` (section 1), each task
  emits its own certificate, and the root certificate cites the children's.
  A small extension to the checker accepts a child as "refuted by a cited
  certificate rooted at its state", provided the cited certificate verifies
  with `start` equal to that state and an empty `Q`. That makes the
  certificate as parallel as the search.
- **Price.** At the measured 10 bytes per node and ×4 compression, a
  10¹¹-node refutation is about 250 GB compressed. A C checker at the C
  search's per-node cost would check it in about the search's own time. So the
  emitter makes the 125 × 125 certificates *possible*, not shippable. For the
  dataset, a practical boundary is about 10⁸ nodes, about 250 MB. Which
  corpus instances fall inside it above 75 customers is not measured here;
  §33 and §34 of `reports/ml_nature.md` have the node counts to decide it.

## 6. Limits

- The Python emitter's reach is 75 customers at 60 s. Ten corpus instances
  there are unknown, and none above 75 was attempted.
- The certificate covers the MOSP corpus. The section 4 dataset's
  `certified:refutation` graph records (`paper2/dataset.md`) are refuted by the
  graph solver in `pathwidth_solver/`, which runs the same rules on
  neighbourhood masks. The checker needs only `N[c]`, so it extends to graphs
  by reading an edge list instead of a matrix. This is not done here.
- The acceptance condition is argued on paper from Lean lemmas, not stated in
  Lean (section 2).
