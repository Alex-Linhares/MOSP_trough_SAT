# Independent verification of the contraction-minor lower bounds

*2026-10-12. Checks the bounds found on 2026-10-11
(`reports/pathwidth_lower_bounds_survey.md`, `paper1/todo.md`, "The
contraction-minor lower bound") with code written from scratch for this
purpose. Everything is in `reports/scratch/minor_certificates/`.*

## Summary

Every claimed bound holds, and every one is now certified without our dominance
rules. Each claim was checked in two parts:

- **(i) the minor.** An independent replay of the contraction sequence: every
  step must contract an edge of the current graph. The resulting minor is
  compared with the one recorded on 2026-10-11 and agrees exactly. A second
  route from the branch sets gives the same quotient graph.
- **(ii) the refutation of `pathwidth(H) <= w` on the minor.** A rule-free
  exact search, independent of the project's searches, with a proof object: the
  family of refuted prefixes, checked by a separate 80-line checker.

SAT with DRAT, the preferred method, **did not produce a proof in the time
available on any of these minors**. It was tried on three of them, with this
report's own CNF encoding and standalone CaDiCaL 2.1.2. The proof files grew
past 4–8 GB in 25–40 minutes. The rule-free certificates replace DRAT here;
the trade-off is discussed in its own section below.

| claim | minor (vertices / edges) | method | time | proof size | verdict |
|---|---|---|---|---|---|
| myciel6: pw >= 38 | 58 / 691 (min-d) | rule-free search + checkF | 0.02 s search, 0.02 s check | 24,321 sets, 195 KB raw, 64 KB xz (kept) | **certified** |
| myciel6: pw >= 38 | 60 / 693 (min-d) | rule-free search + checkF | 0.04 s, 0.06 s | 46,620 sets, 373 KB raw, 128 KB xz (kept) | **certified** |
| myciel6: pw >= 38 | 58 / 691 | own CNF + CaDiCaL 2.1.2, binary DRAT | stopped at 7,398 s | 9.4 GB, unfinished | no answer |
| myciel7: pw >= 71 | 110 / 2,198 (min-d) | rule-free search + checkF | 3.7 s, 6.5 s | 3,398,378 sets, 47.6 MB raw, 13.2 MB xz (kept) | **certified** |
| Random-125-125-2-3_0: MOSP >= 21 (pw >= 20) | 70 / 250 (least-c) | rule-free search + checkF | 2.8 s, 4.4 s | 2,698,884 sets, 24.3 MB raw, 10.3 MB xz (kept) | **certified** |
| Random-125-125-2-3_0 | 70 / 250 | own CNF + CaDiCaL, DRAT | stopped at 2,401 s | 7.9 GB, unfinished | no answer |
| Random-125-125-2-1_0: MOSP >= 24 (pw >= 23) | 87 / 311 (min-d) | rule-free search + checkF | 255 s (19.7 GB RAM), 249 s | 139,289,255 sets, 1.53 GB raw; not kept (xz > 50 MB) | **certified** |
| Random-125-125-2-1_0 | 87 / 311 | own CNF + CaDiCaL, DRAT | stopped at 1,530 s | 4.4 GB, unfinished | no answer |
| Random-125-125-6-1_0: MOSP >= 81 (pw >= 80) | 120 / 2,079 (min-d) | rule-free search + checkF | 39 s, 81 s | 23,576,438 sets, 354 MB raw, 102 MB xz; not kept | **certified** |
| SP4: MOSP >= 53 (pw >= 52) | 96 / 1,037 (min-d) | rule-free search + checkF | 17 s, 22 s | 11,415,333 sets, 137 MB raw, 44.3 MB xz (kept) | **certified** |
| myciel7: pw >= 72? | 130 (min-d), 130 (least-c), 140 (min-d) | rule-free search | 510–640 s each | – | **unknown** (250 M sets each, no answer) |
| myciel7: pw <= 71? | full graph, 191 | simulated annealing, 4 x 900 s + 2 x 1,800 s; DFS | 2 h | – | **not found** (best 72) |

Times are wall-clock on the shared machine, one core each, with the load
average around 40 on 32 cores.

**What changes.** On the evidence here, the following hold independently of
the corrected dominance rules:

- `pw(myciel6) = 38`;
- `pw(myciel7) >= 71`;
- the four corpus optima `Random-125-125-2-3_0 = 21`, `2-1_0 = 24`,
  `6-1_0 = 81` and `SP4 = 53`.

The upper bounds are witnessed. myciel6 has a width-38 layout found and checked
here. The four corpus witnesses were re-simulated by `mc_witness.py`, written
for this report, to exactly their stored values. Two theorems connect a minor's
pathwidth to MOSP. `MOSP = pathwidth(MOSP graph) + 1` is proved in Lean
(`MOSPGraph.lean`). That contraction does not increase pathwidth is standard
(Fellows & Langston 1987, Lemma 4.2) and is not yet formalised (todo item
"Lean").

**What still rests on our code.** Nothing in the six certified bounds rests on
the dominance rules. Two pieces of code have to be trusted:

- the checker `checkF.c`, 80 lines, which replaces trust in the search;
- the replay in `mc_graph.py`.

No DRAT proof was obtained, so no bound here has a certificate checkable by a
standard third-party tool.

## Disagreements and things that failed

- **No disagreement anywhere.** Every recorded minor (`myciel6_minor58_edges.json`,
  `myciel6_minor60.json`, `myciel7_minor110_branch_sets.json`, the two corpus
  branch-set files) was reproduced exactly by the independent contraction code.
  Every rule-free refutation agrees with the 2026-10-11 rule-based one. Each
  minor's pathwidth sits exactly at the bound: the rule-free search finds a
  layout at `w + 1` for every one of them.
- **SAT with DRAT does not scale to these minors.** The position encoding (a
  layout as a permutation, a sequential counter per step) took 1,459 s with
  CaDiCaL 1.9.5 on the 58-vertex myciel6 minor on 2026-10-11. With this
  report's own encoding and CaDiCaL 2.1.2 it gave no answer in 7,398 s and was stopped, with a 9.4 GB proof. Both corpus SAT
  runs were stopped unfinished. Their proofs were 4.4 GB and 7.9 GB, and
  drat-trim on proofs of that size takes many hours.

  The same minors fall to a rule-free search in seconds, and the 58-vertex
  myciel6 minor in 24,321 states. A SAT layout encoding fixes a vertex's
  *position*, so it has to rule out every permutation. The prefix search
  identifies all orders of the same prefix set.
- **The inner-boundary search form is much slower.** `vsmemo` was first run
  without `-o`. It stores prefixes by their inner boundary (placed vertices with
  an unplaced neighbour). On the 70-vertex corpus minor it had used 6.5 GB
  without finishing after 11 minutes. With `-o` it finishes in 2.8 s: it uses
  the outer boundary `|N(P) - P|`, the form our customer search also uses.

  Both forms decide the same question: the outer boundary of a prefix is the
  inner boundary of its complement, which is a prefix of the reversed layout.
  They visit very different numbers of sets.
- **Two certificates are too large to keep under 50 MB**, `2-1_0`
  (1.53 GB raw) and `6-1_0` (102 MB after xz). They are deterministic: the
  commands below regenerate them byte for byte, and the SHA-256 of each raw file
  is recorded in `results.log`.

## myciel7: 71 or 72

**Unsettled.** `71 <= pw(myciel7) <= 72`.

- **Lower bound 72.** By contraction, minors of 115–125 vertices all have a
  width-71 layout. Up to 120 vertices this was confirmed here: the rule-free
  search finds a width-71 layout of the 120-vertex min-d minor at once. So a
  certificate of 72 needs a minor of at least about 126 vertices.

  On the 130-vertex minors (both rules) and the 140-vertex min-d minor, the
  rule-free search exhausted a cap of 250 million stored sets (about 20 GB)
  without an answer. The rule-based search of 2026-10-11 also stopped
  unfinished there, at 50–237 million nodes in 300 s.

  The proved forced-vertex rule (`-f`, below) did not help. On the
  110-vertex minor it visits the same 3,398,378 sets. On the 130-vertex min-d
  minor it also stopped at 250 million sets, after 1,113 s.
- **Upper bound 71.** Four 900-second simulated-annealing runs on the full
  graph (`vsanneal.c`) reached 73, 74, 72 and 72; the last of these started from the width-72
  layout. Two further 1,800-second runs from that layout stayed at 72. In 20–30 s the same annealer reaches the
  optimum on myciel6 (38) and on the 70-vertex corpus minor (20). A depth-first search for a width-71 layout of the
  full graph, ordered by boundary, gave no answer after 100 million sets. The
  same search finds a width-72 layout in 211 nodes
  (`myciel7_w72_order.txt`, checked by `mc_layout_check.py`).

So the evidence, such as it is, leans towards 72. A certificate of 72 would
need either a smarter minor than the two greedy rules produce, or a
refutation on 130+ vertices with more memory or a sound pruning rule. The
forced-vertex rule below is the only one used here, and it is proved.

## Method

### (i) Replaying the minors

`mc_graph.py` uses no networkx and imports nothing from the project. It
provides:

- readers for `.dgf` and for both MOSP file formats, building the MOSP graph:
  customers as vertices, a clique per pattern;
- the two greedy contraction rules, rewritten from their description. The
  minimum-degree vertex, ties by label, is contracted into a neighbour: min-d
  takes the neighbour of least degree, least-c the neighbour with fewest common
  neighbours;
- `replay`, which applies a sequence `[(keep, absorbed), ...]` and asserts that
  each pair is an edge of the *current* graph. It merges the two endpoints,
  unions their neighbourhoods and drops the loop. It then rebuilds the quotient
  graph independently from the resulting branch sets and asserts it equals the
  replayed graph.

For each claim, `mc_build.py` regenerates the sequence, replays it, and replays
a second sequence derived from the branch sets alone (a BFS tree inside each
branch set), so connectivity of every branch set is checked as well. It then
compares the minor with the 2026-10-11 record and writes `<claim>.json`:
sequence, branch sets, minor edges and hash.

`mc_crosscheck_readers.py` is the only file that imports project code. It checks
that the readers here produce the same labelled graphs as
`pathwidth_solver/bench/readers.read_any` and
`customer_inter.customer_graph.build_customer_graph`. They do, for all six
input graphs.

Two claims had no minor recorded on 2026-10-11, `6-1_0` at 120 vertices and
`SP4` at 96. For them, the minor certified here is the one the same rule
produces.

### (ii) The rule-free refutation and its certificate

`vsmemo.c` decides `pathwidth(H) <= w` by depth-first search over layout
prefixes. Its pruning is limited to the following:

- a prefix `P` is admissible iff `|N(P) - P| <= w`;
- a prefix is extended by any one vertex that keeps it admissible;
- every prefix from which the full set was not reached is stored.

Storing the failures is sound because reachability of the full set from `P`
depends on `P` alone. There is no dominance rule and no bound.

On UNSAT, `-w` writes the stored family `F`. `checkF.c` reads the graph, `w` and
`F`, and checks three things:

1. the empty set is in `F`;
2. the full vertex set is not in `F`;
3. for every `S` in `F` and every vertex `v` outside `S` with
   `|N(S + v) - (S + v)| <= w`, the set `S + v` is in `F`.

Then no layout has every prefix boundary at most `w`. Its prefixes start in
`F` by (1) and stay in `F` by (3), and they would end at the full set,
contradicting (2). The checker computes every boundary from the adjacency
itself, sorts `F` and looks every extension up. It shares nothing with the
search but the file format.

Both programs were tested against a brute-force subset DP (`mc_sat.vs_brute`):

- `mc_vsmemo_test.py`: 1,500 random graphs to 13 vertices, at `pw - 2 .. pw`,
  in all four modes;
- `mc_checkF_test.py`: 365 genuine certificates verify. Each with one set
  deleted is rejected (365 of 365), and none verifies at `w = pw`.

**The forced-vertex rule (`-f`, only in the myciel7 probes).** A vertex `v`
outside `P` with `N(v)` contained in `P` is added at once. It is sound: moving
such a `v` to directly after `P` in any layout removes `v` from every later
outer boundary, and adds nothing to it, since `N(v)` is already placed. It is
proved here, not taken from the literature. No certified row uses it.

### SAT with DRAT

`mc_sat.py` is a CNF written for this report. It does not reuse
`bench/myciel6_sat.py`'s encoding. Its variables:

- `y[v,t]`, v placed by step t, monotone in t;
- `d[v,t]`, v placed exactly at step t, defined both ways, with exactly one
  per step by a clause and a sequential at-most-one;
- `s[v,t]`, forced by `y[v,t] and not y[u,t]` for every edge `uv`.

A Sinz sequential counter bounds the `s` variables of each step by `w`. No
symmetry is broken. `mc_sat.py selftest` checks it against the brute force on
300 random graphs at `pw - 1` and `pw`.

`mc_refute.py` writes the DIMACS file, runs the CaDiCaL 2.1.2 binary shipped
with the Lean toolchain, and logs the SHA-256 of the CNF. It writes a binary
DRAT proof and checks it with `tools/drat-trim`; a proof is kept xz-compressed
if under 50 MB. CNF hashes:

| CNF | vars | clauses | SHA-256 |
|---|---|---|---|
| myciel6_m58, w = 37 | 133,553 | 343,598 | `cfda64b1d6ae63608dee87f83374e97f64c0402879a12c3172c1526085d26c60` |
| Random-125-125-2-3_0_m70, w = 19 | 109,919 | 252,818 | `87ab87e060b1fbd1941b8f39a449c02871b06452491c7d0bd755e273e6c42e8b` |
| Random-125-125-2-1_0_m87, w = 22 | 192,814 | 436,968 | `852b703ce05e2f33bb731249faaec1d32b2404f92f485edb1fe389d364d1edf4` |

## Certificates kept

In `reports/scratch/minor_certificates/`:

- `<claim>.json`: contraction sequence, branch sets, minor edge list (labels
  0..m-1 in increasing order of the surviving representative), minor SHA-256,
  and the comparison with the 2026-10-11 record;
- `<claim>_edges.json` / `.txt`: the minor as an edge list;
- `proofs/<claim>_w<w>.F.xz`: refuted-prefix families. Raw format: one set per
  `ceil(m/8)` bytes, bit `v` of byte `v/8`, in hash-table order;
- `myciel6_w38_order.txt`, `myciel7_w72_order.txt`: upper-bound layouts, in
  outer-boundary form; reversed, they are vertex-separation layouts;
- `myciel7_m{120,130,140}_*.json`: the larger myciel7 minors probed;
- `results.log`: every run, with times, sizes and hashes.

## Reproducing

From `reports/scratch/minor_certificates/`:

```bash
gcc -O2 -march=native -o vsmemo vsmemo.c
gcc -O2 -o checkF checkF.c
gcc -O2 -march=native -o vsanneal vsanneal.c -lm

python mc_sat.py selftest                 # the CNF against brute force
python mc_vsmemo_test.py                  # vsmemo against brute force
python mc_checkF_test.py                  # checkF accepts genuine, rejects damaged certificates
python mc_build.py                        # replay every minor, compare with the 2026-10-11 record
(cd ../../.. && python reports/scratch/minor_certificates/mc_crosscheck_readers.py)
python mc_witness.py                      # corpus witnesses re-simulated

# one row of the table: rule-free refutation, certificate, check (MC_WORK = a scratch directory)
MC_WORK=/tmp/mc bash mc_rulefree.sh myciel6_m58 37
MC_WORK=/tmp/mc bash mc_rulefree.sh myciel6_m60 37
MC_WORK=/tmp/mc bash mc_rulefree.sh myciel7_m110 70
MC_WORK=/tmp/mc bash mc_rulefree.sh Random-125-125-2-3_0_m70 19
MC_WORK=/tmp/mc bash mc_rulefree.sh Random-125-125-2-1_0_m87 22     # about 20 GB of RAM
MC_WORK=/tmp/mc bash mc_rulefree.sh Random-125-125-6-1_0_m120 79
MC_WORK=/tmp/mc bash mc_rulefree.sh SP4_m96 51

# check a kept certificate directly
xz -dk proofs/myciel7_m110_w70.F.xz && ./checkF myciel7_m110_edges.txt 70 proofs/myciel7_m110_w70.F

# the satisfiable side: a layout at w + 1 exists on every minor
./vsmemo myciel7_m110_edges.txt 71 -o

# SAT with DRAT (did not finish on these minors)
MC_WORK=/tmp/mc python mc_refute.py myciel6_m58 37

# myciel7 probes
python mc_myciel7_minors.py 120 130 140 150
bash mc_myciel7_lb.sh                     # w = 71 on minors of 120-140 vertices
bash mc_myciel7_ub.sh                     # annealing for a width-71 layout
./vsmemo myciel7_full_edges.txt 72 -o     # a width-72 layout
python mc_layout_check.py ../../../pathwidth_solver/bench/instances/coloring/myciel7.dgf myciel7_w72_order.txt
```
