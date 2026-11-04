# The checkpoint relaxation: nested prefixes at a few sizes

*2026-11-04. Code: `learning/checkpoint_bound.py` (the encoding, the pilot),
`learning/checkpoint_refine.py` (adaptive checkpoints), `learning/checkpoint_anatomy.py`
(the search's state census), `learning/checkpoint_report.py` (the join);
tests `tests/test_checkpoint_bound.py` (20). Data under
`reports/scratch/checkpoint/`. Nothing re-solved; `solutions/` untouched;
about 6 core-hours.*

## 0. Summary

**The question.** Every lower bound the project owns looks at one prefix of
the layout at a time, and Harper's vertex-isoperimetric bound is the best
such bound: on the record's residual its exact value sits below the optimum
(`reports/obstruction_search.md`, 320 of the 338 bound-gap instances), so no
single-prefix argument can close them. A layout has what one prefix lacks:
nesting. This pilot keeps `c` prefix sizes `i_1 < … < i_c` and asks for
nested sets `S_1 ⊂ … ⊂ S_c` of those sizes with every inner boundary
`|S_j| − |int(S_j)| ≤ b`. UNSAT proves `vs ≥ b + 1`, i.e. `MOSP ≥ b + 2`.
One checkpoint is Harper's bound at that size; all `n − 1` is the exact
problem. The question was how many checkpoints, and which, the residual
needs: few means a compact certificate exists and a new bound family with
it; many means the obstruction is diffuse and the bound work should stop
looking for formulas.

**The answer is diffuse.** On 77 instances at 30–75 customers where Harper's
exact ceiling is below the optimum (gaps 1–4 stacks):

- one checkpoint reproduces Harper's recorded value on 66 of 66 (§2, the
  sanity check);
- a few checkpoints buy a quarter of a stack: two to six evenly spaced ones
  gain 0.03–0.25 on average and close at most 3 of 66; sixteen gain 0.74 and
  close 18 (§2);
- chosen adaptively (counterexample-guided: add a checkpoint wherever the
  witness chain cannot be filled in, §4), the certificate still needs a
  **median of a third of all sizes** (13 at gap 1, 20–27 at gaps 2–3), in a
  contiguous band from about a quarter to nine tenths of the vertices;
  **shrunk to a locally minimal set (§5) the median is 6 checkpoints, and
  at gap 1 it is 5 (2–12), consecutive sizes in a window at `0.5–0.7 n`**:
  where Harper is one short, the certificate is compact; where it is three
  short, it is a quarter of the chain;
- the full chain, all `n − 1` sizes, is an exact encoding with `2n²` main
  variables and no position variables; it closes 62 of 64 at 30–50
  customers in a median of 3 s at 40 and 17 s at 50, and at 75 with 10⁷
  conflicts 7 of 13 — every dense one (densities 4 and 6, SP3) in 3–41
  minutes and none of the five ridge instances (density 2) (§3, §6).

**What this buys.** Not a bound: the gain of a compact relaxation is a
quarter of a stack, and the certificate the residual needs is most of the
chain, which is the exact problem under another name. What it settles is
*why* the single-prefix bounds died: the obstruction is not at a prefix size
but spread over a band of consecutive sizes, roughly `[0.25 n, 0.9 n]`, and
within that band nearly every size is load-bearing. The anatomy of the
search's refutation says the same from the other side (§7): the states the
customer search visits peak at prefix size `0.42 n` and half of them sit in a
window 12% of `n` wide, but the checkpoints a certificate needs are not
where the states are; they are the whole band after it.

**What is new, and what to keep.** The nested-chain encoding is a compact
exact encoding of vertex separation (graph only, independent of the pattern
count `m`); at 41–50 customers it refutes `optimum − 1` in seconds where the
project's direct position encoding is bounded by `m² · k` (`reports/ml_nature.md`
§17); §8 measures the two head to head. If it wins, it is a second proof
object for the 41–75 band, with DRAT, beside the search certificate of §32.
That is an engineering result, not a bound.

## 1. The relaxation

Vertex separation of a layout `σ` is `max_i |∂_in(S_i)|`, where `S_i` is the
`i`-prefix and `∂_in(S) = S ∖ int(S)`, `int(S) = {v ∈ S : N[v] ⊆ S}`. Harper
keeps one `i`: `vs ≥ min_{|S| = i} |∂_in(S)|`; the record's `expansion_bound`
computes the same thing through `f(t) = min_{|C| = t} |N[C]|`, and
`learning/obstruction_expansion.py` proves it exactly by SAT with a DRAT proof
at 30–60 customers. The checkpoint relaxation CHK(sizes, b):

    ∃ S_1 ⊂ S_2 ⊂ … ⊂ S_c,  |S_j| = i_j,  |∂_in(S_j)| ≤ b  for all j.

Every layout of vertex separation `≤ b` satisfies it (take its prefixes), so
UNSAT proves `vs ≥ b + 1`. Encoding, per checkpoint `j` and vertex `v`:
`s_j[v]` and a claimed-interior `c_j[v]` with `c_j[v] → s_j[u]` for all
`u ∈ N[v]`; `s_j[v] → s_{j+1}[v]` and `c_j[v] → c_{j+1}[v]` (the interior is
monotone under inclusion); `|S_j| = i_j` and `|C_j| ≥ i_j − b` by the
totalizer of `obstruction_expansion._totalizer`. A SAT model is checked by
recomputing every boundary from the masks (`check_witness`), never from
`c`. Exact sizes are implied by the layout and are the strongest form; a
censored call at `b` falls through to `b − 1`, which is easier to refute.

Sanity (`tests/test_checkpoint_bound.py`): the full chain agrees with
brute-force vertex separation on six small graphs; fewer checkpoints never
prove more; one checkpoint at size `i` equals `min_{|S| = i} |∂_in S|` on
every `i`; the refinement of §4 answers `unsat` at `vs − 1` and `sat` at
`vs`.

## 2. The pilot: even grids, pairs, singles

Population: the 77 corpus instances at `n ≤ 75` in the record's SAT table
(`reports/scratch/obstruction_search/03_sat/instances.csv`) whose Harper
ceiling is below the optimum — 1 at 30, 19 at 40, 44 at 50, 13 at 75; Harper's
exact value is settled at `n ≤ 50` and is the ceiling at 75 (reference
`harper_ref`). Configurations per instance: every single size (`n − 1`
calls), even grids of `c ∈ {2, 3, 4, 6, 8, 12, 16}` checkpoints, all 28 pairs
from the 8-grid, and the full chain; each scanned down from `b = optimum − 2`
(UNSAT certifies the optimum) to `harper_ref − 2`, 10⁶ conflicts per call,
11 workers, 28 minutes. 6,660 rows, `reports/scratch/checkpoint/pilot/pilot.csv`.

Best floor per instance and family, optimum units (66 instances with at
least one UNSAT; the 11 others are 75-customer instances censored at every
`c ≥ 2`):

| family | instances | closes | mean gain over Harper | mean distance to optimum |
|---|---|---|---|---|
| single, best size | 66 | 0 | 0.00 | 1.58 |
| pair, best of 28 | 66 | 3 | 0.23 | 1.35 |
| even 2 | 32 | 0 | 0.03 | 1.78 |
| even 3 | 40 | 1 | 0.23 | 1.70 |
| even 4 | 55 | 3 | 0.25 | 1.42 |
| even 6 | 62 | 1 | 0.24 | 1.37 |
| even 8 | 66 | 4 | 0.35 | 1.23 |
| even 12 | 66 | 10 | 0.56 | 1.02 |
| even 16 | 66 | 18 | 0.74 | 0.83 |
| full chain | 66 | 62 | 1.50 | 0.08 |

**Single checkpoint = Harper on 66 of 66** (equal, none above, none below):
the encoding reproduces the record. An even grid of `c` sizes can sit below
Harper when it misses Harper's size (the "instances" column counts those
with any UNSAT at all). The best pairs sit at `0.55–0.68 n` on the 40s and
`0.66–0.78 n` on the 50-100 class, not at Harper's `t*`.

By size, the full chain and the 16-grid:

| n | instances | full closes | full median s | full max s | even-16 closes | even-16 median s |
|---|---|---|---|---|---|---|
| 30 | 1 | 1 | 0.2 | 0.2 | 0 | 0.1 |
| 40 | 19 | 19 | 2.9 | 5.2 | 7 | 1.4 |
| 50 | 44 | 42 | 16.5 | 96.0 | 10 | 4.5 |
| 75 | 13 | 0 | 246 | 476 | 1 | 92 |

## 3. The full chain as an exact encoding

With all `n − 1` sizes the relaxation is exact: `2 n (n − 1)` main variables,
the nesting clauses and `2(n − 1)` totalizers; no position variables and no
pattern variables, so the formula depends on the MOSP graph only. At 50
customers it refutes `optimum − 1` in a median of 17 s and closes 42 of 44;
at 75 it censors at 10⁶ conflicts on all 13 (4–8 minutes each). §6 gives it
10⁷ and §8 compares it with the position encoding.

## 4. Adaptive checkpoints

Counterexample-guided refinement (`learning/checkpoint_refine.py`): start
with one checkpoint at `n/2`; a SAT answer gives nested sets; for every
segment `(A, B)` of the chain (with `∅` before the first and `V` after the
last) ask *exactly* whether `B ∖ A` can be laid out after `A` with every
intermediate boundary `≤ b` (CHK over the sizes strictly between, `A` forced
in and `V ∖ B` forced out: a problem on `|B ∖ A|` vertices). If every
segment fills, the chain extends to a layout and `vs ≤ b` is true. Otherwise
add the midpoint size of every segment that does not fill and repeat. UNSAT
ends it, and the checkpoint set in hand is a certificate of `vs ≥ b + 1`.
Bisection is greedy, so the count is an upper bound on the smallest
certificate; §5 shrinks it.

All 64 instances at 30–50 refuted at `b = optimum − 2` (2 × 10⁶ conflicts
per call, 5 workers, 3.5 minutes; `reports/scratch/checkpoint/refine/refine.csv`):

| n | instances | checkpoints median (min–max) | fraction of sizes | band (first, last size) / n | density in band | rounds | median s |
|---|---|---|---|---|---|---|---|
| 30 | 1 | 11 | 0.38 | 0.50–0.87 | 0.92 | 5 | 0.5 |
| 40 | 19 | 14 (2–26) | 0.36 | 0.25–0.88 | 0.54 | 6 | 3.3 |
| 50 | 44 | 17.5 (3–35) | 0.36 | 0.24–0.86 | 0.68 | 7 | 16.5 |

By the Harper gap: gap 1 (35 instances) needs a median of 13 checkpoints
(0.29 of the sizes); gap 2 (22) 20.5 (0.44); gap 3 (6) 26.5 (0.57). The
band is the same at every gap, `0.24–0.9 n`; what grows with the gap is how
densely it must be filled. The smallest certificates: `Random-40-40-2-4_0`
(gap 1) with two checkpoints at sizes 20 and 30; `Random-50-50-4-5_0` with
three at 25, 31, 37; five instances at 50 with five, all at 25, 28, 31, 34,
37 — the bisection's first rounds — so the compact cases are the gap-1
instances where Harper is one short and a short chain through the middle
already forbids the last stack.

**At 75** (`reports/scratch/checkpoint/refine75/refine.csv`, 5 × 10⁶
conflicts per call, 2 workers, 2.4 hours): the refinement certifies the
optimum on **3 of 13** — `Random-75-75-6-4_0` with three checkpoints at
37, 56, 65 in 27 s, `Random-75-75-4-2_0` with eight, `Random-75-75-4-1_0`
with thirteen — and censors on the other ten, usually in a call with two to
four checkpoints (`37 46 56` recurs: the bisection's first rounds). On the
five ridge instances the single-checkpoint call at two below the optimum
already takes 100–460 s. The full chain of §6, one call with 10⁷ conflicts,
refuted seven of the same thirteen: at this size the relaxation's SAT calls
are the cost, and splitting the budget over rounds and segment checks loses
to spending it once on the whole chain.

## 5. Locally minimal certificates

Greedy shrink of each §4 certificate: drop one checkpoint, farthest from
the band's middle first, and keep the drop if the relaxation is still UNSAT
(`reports/scratch/checkpoint/shrink/run.py`, 2 × 10⁶ conflicts per call, a
median of 15 calls and 52 s per instance, max 675 s;
`reports/scratch/checkpoint/shrink/shrink.csv`). The result is locally
minimal, an upper bound on the smallest certificate.

| Harper gap | instances | minimal checkpoints, median (min–max) | fraction of sizes | band / n |
|---|---|---|---|---|
| 1 | 35 | 5 (2–12) | 0.10 | 0.52–0.70 |
| 2 | 22 | 8.5 (3–21) | 0.21 | 0.46–0.72 |
| 3 | 6 | 14.5 (9–27) | 0.30 | 0.41–0.80 |
| 4 | 1 | 16 | 0.33 | 0.32–0.80 |

Bisection's median of 15 shrinks to **6**, 15% of the sizes. **At gap 1 the
certificate is compact**: six instances need two checkpoints (`Random-50-50-4-5_0`
at sizes 31 and 37; `p4050n6_0` at 31 and 34; `Random-40-40-2-4_0` at 20 and
30), the median is five, and the band is `0.5–0.7 n`, a narrow window just
past the middle. At gap 3 it is a quarter of all sizes, consecutive. The
consecutive checkpoints of a minimal set are a median of one size apart
(IQR 1–2, max 10): what survives shrinking is a *dense short run*, not a
spread of landmarks. So the certificate of one missing stack is "no nested
chain of boundary `≤ b` crosses the sizes `0.5–0.7 n`", witnessed by a few
consecutive levels; the certificate of three missing stacks is most of the
chain.

This corrects §4's reading. The obstruction is a band, as §4 says, but at
gap 1 the band is short and a handful of consecutive levels carries it. The
hard open instances on the record are gap-1 cases (`reports/obstruction_search.md`:
best floors one below the optimum on four of the eleven dense-shoulder
instances), which is where this is worth something — if a relaxation with
five checkpoints at `0.5–0.7 n` can be refuted at 125 vertices when the full
problem cannot. §6 and §4's run at 75 are the first step up.

## 6. The full chain at 75 with 10⁷ conflicts

The 13 instances at 75 customers, the full chain at `b = optimum − 2`, 10⁷
conflicts, 6 workers (`reports/scratch/checkpoint/full75/full75.csv`;
formulas of 60–76 K variables and 0.84–0.93 M clauses):

| instance | optimum | Harper | gap | result | conflicts | seconds |
|---|---|---|---|---|---|---|
| Random-75-75-6-4_0 | 47 | 46 | 1 | **refuted** | 1.1 M | 196 |
| Random-75-75-4-2_0 | 35 | 33 | 2 | **refuted** | 2.6 M | 437 |
| Random-75-75-4-1_0 | 35 | 34 | 1 | **refuted** | 4.7 M | 566 |
| Random-75-75-4-5_0 | 32 | 31 | 1 | **refuted** | 7.8 M | 2,205 |
| SP3, SP3_0 | 34 | 33 | 1 | **refuted** | 8.9 M | 2,290 |
| Random-75-75-4-4_0 | 32 | 31 | 1 | **refuted** | 8.6 M | 2,446 |
| Random-75-75-4-3_0 | 37 | 36 | 1 | censored | 10 M | 1,572 |
| Random-75-75-2-1_0 … 2-5_0 (five) | 13–17 | 11–16 | 1–2 | censored | 10 M | 1,837–2,262 |

**7 of 13 refuted, every one on the dense side** (densities 4 and 6 and
SP3), in 3–41 minutes; the five density-2 instances, the ridge class, all
censor. That is the record's hardness map (`reports/ml_nature.md` §11) seen
through a SAT solver: the ridge is where the chain is long and every level
is loaded. The §4 refinement at 75 (`reports/scratch/checkpoint/refine75/`)
says the same from the other side: on `Random-75-75-2-1_0` even a
**single**-checkpoint call at `b = 12` takes 153 s and a three-checkpoint
call at `b = 14` censors at 5 × 10⁶ conflicts, so on the ridge the
relaxation's own SAT calls are the bottleneck before the number of
checkpoints is. The record's Harper-by-SAT already settled "almost none" of
its levels at 75 (`reports/obstruction_search.md`); nesting does not make
those calls easier.

## 7. The anatomy of a refutation

`learning/checkpoint_anatomy.py` emits the search certificate of §32
(`learning.search_certificate.emit`, configuration `csearch`, at
`k = optimum − 1`) and tabulates its nodes by the prefix size in vertex
separation terms, `p = |N[S]|` for the closed set `S` (every pattern of a
closed customer is produced, so every neighbour is open; the boundary is the
open count). 64 instances at 30–50, all refuted, 15 s in total
(`reports/scratch/checkpoint/anatomy/anatomy.csv`):

- nodes per refutation: 80 at 30 customers, median 5,394 at 50, max
  241,414; distinct closed sets a third of that at the median;
- the peak prefix size is at `0.42 n` (IQR 0.36–0.48), and the smallest
  window of sizes holding half the nodes is 3–9 sizes wide, median 5, i.e.
  12% of `n`;
- the best pair of checkpoints sits inside that window on 12 of 128 sizes.
  The states the search *visits* cluster before the band the certificate
  *needs*: the search branches most at `0.4 n` and the refutation's load is
  carried by the sizes after it.

## 8. The nested chain against the direct position encoding

The project's direct encoding (`satisfiability.mosp_encoding.encode_mosp_decision`,
positions of patterns, open-stack variables, totalizer) at `k = optimum − 1`
on the same 44 instances at 50 customers, CaDiCaL 1.9.5, 10⁶ conflicts, no
preprocessing on either side (`reports/scratch/checkpoint/direct50/direct50.csv`):

| | direct position encoding | nested chain |
|---|---|---|
| refutes within 10⁶ conflicts | 20 of 44 | 42 of 44 |
| median seconds where both refute (19) | 3.8 | 15.7 |
| faster where both refute | 16 | 3 |
| formula at 50 customers, median | 15,660 vars, 65,161 clauses (`m` median 30) | 28,066 vars, 277,348 clauses (SP2) |
| refutes with `m > 60` (5 instances) | 0 | 5 |

The two are complementary: the position encoding is four times faster where
it finishes and censors on 24 of 44, every instance with more than 60
patterns among them, because its size is `m² · k`; the chain's size is in
`n` alone, and it finishes on 42. For a DRAT proof object at 41–50
customers the chain is the encoding that returns; neither reaches 75 at 10⁶
(§6).

## 9. Verdict and what follows

- **As a bound family: closed.** A relaxation with few *fixed* checkpoints
  gains a quarter of a stack on the residual. Compact certificates exist at
  gap 1 (five consecutive sizes at `0.5–0.7 n`, §5), but finding them took
  exact segment checks, and at 75 the relaxation's own SAT calls censor on
  the ridge before the number of checkpoints matters (§4, §6). The
  obstruction is a band of consecutive nested levels: the exact problem,
  localised. This was the last argument aimed at the property that killed
  the single-prefix bounds, and it does not give a floor.
- **Reusable, and the result worth keeping**: the nested chain as an exact
  encoding with a DRAT proof object. At 41–50 customers it refutes twice
  what the position encoding does in the same budget and every instance
  with many patterns; at 75 it refutes every dense instance in under an
  hour (§6, §8). A Lean statement of its soundness is one lemma (a layout's
  prefixes are nested and bounded) and is proposed if it is adopted for
  `learning.proofs`.
- **One solver idea with a measured reason** (§5, §7): the search's states
  peak at `0.42 n` and the certificate's checkpoints sit at `0.5–0.7 n`, so
  the forward search enumerates everything reachable before the wall and
  only then meets it. A search from the other end, or a meet-in-the-band
  with the two frontiers, is cheap to test in nodes at 50–75 and is the one
  untested change with a chance of moving the cost of the 125 refutations.
- **Not done**: 100–125 customers, where nothing here reaches; the
  general CEGAR loop of §4 is sound and general (vertex separation with
  exact segment checks) but loses to one whole-chain call at 75.
