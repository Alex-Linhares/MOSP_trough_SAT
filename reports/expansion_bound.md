# A lower bound that is not about degree

*2026-09-22. `satisfiability/expansion_bound.py`, `tests/test_expansion_bound.py`.*

## 1. Why the old bounds could not be improved

Every lower bound this project had was degree-based: the trivial bound (largest
product), the clique bound, degeneracy, and contraction degeneracy — which
`reports/lower_bounds.md` §3 established *is* the arc contraction bound of
Yanasse, Becceneri & Soma (1999). On the instances that cost compute they all
sit near the **average degree**, while the optimum is roughly twice it:

| instance | optimum | old bound | average degree | degeneracy |
|---|---|---|---|---|
| `Random-125-125-8-5_0` | 91 | 47 | 43.2 | 29 |
| `Random-125-125-6-1_0` | 81 | 40 | 33.7 | 22 |

The strongest standard improvement in the treewidth literature was tried and
did nothing. LBN (Bodlaender, Koster & Wolle's improved-graph technique) scores
**12 points worse** than contraction degeneracy; LBN+, which improves the graph
and *then* contracts, gains **exactly zero** on all six worst instances. This is
not an implementation gap. Bounds built from minimum degree over subgraphs and
contractions are capped by a quantity that lives near the average degree, and
pathwidth on a dense graph is nowhere near there.

## 2. The argument

MOSP equals vertex separation plus one. Fix any ordering of the customers and
let `V_i` be its first `i`. The stacks open after `i` steps are `i - |C_i|`,
where `C_i = {v ∈ V_i : N[v] ⊆ V_i}` is the customers already finished. Since
`N[C_i] ⊆ V_i`,

> `|N[C_i]| ≤ i`

So with `f(t) = min_{|C| = t} |N[C]|` — non-decreasing in `t`, because any `C` of
size `t+1` contains one of size `t` whose closed neighbourhood is no larger — no
set of size `t` fits inside a prefix of size `i` unless `f(t) ≤ i`. Hence
`|C_i| ≤ M(i) := max{t : f(t) ≤ i}`, and for every ordering and every `i`:

> `vs(G) ≥ max_i ( i − M(i) )`,  so  `MOSP(I) ≥ max_i ( i − M(i) ) + 1`

This measures how fast closed neighbourhoods **expand**. A dense graph expands
fast, which is exactly the regime where the degree bounds die.

### The mistake that makes it worth stating carefully

`f` is computed only to some cap `T`, so `M(i) ≤ T` is proved **only** for
`i < f(T+1)`, and **only** if that `f(T+1)` is exact. The first draft ignored
the range restriction and returned **122 against an optimum of 91**. A lower
bound above the optimum is not a slow bound, it is a wrong answer: the search
starts above the optimum and returns a value whose witness verifies, so nothing
downstream catches it.

Two consequences in the implementation. `f` is computed by exhaustive branch and
bound, not heuristically — a heuristic `f` *overestimates* the minimum, which
would widen the usable prefix range and is unsound in exactly the dangerous
direction. And a level whose search is abandoned on budget is **discarded**,
never used at its incumbent value.

## 3. What it is worth

All 6,376 certified optima, cap 8, 3-second budget per instance:

| | mean gap | tight | max gap |
|---|---|---|---|
| before | 0.979 | 65.3% | 44 |
| **with the expansion bound** | **0.437** | **77.0%** | **30** |

**Zero violations.** It beats the previous bound on 1,329 instances. The whole
corpus costs 196 seconds; the slowest instance is 4.2 s and 21 hit the budget,
falling back to a shallower cap, which stays sound.

By class, at cap 4 (the first validated run):

| population | n | mean gap | tight |
|---|---|---|---|
| Chu & Stuckey `Random` | 200 | 12.76 → 8.82 | 1.5% → 18.5% |
| everything else | 6,136 | 0.59 → 0.33 | 67.3% → 77.1% |
| GP / SP / NWRS | 40 | 2.25 → 2.25 | 80.0% |

### Depth is where the hard instances move

The cap is a dial. On the 125×125 instances that cost 19.2 hours on 25 cores to
certify:

| instance | optimum | old bound | t=4 | t=6 | t=8 | t=10 |
|---|---|---|---|---|---|---|
| `Random-125-125-10-5_0` | 99 | 59 | 80 | 92 | 97 | **98** |
| `Random-125-125-8-4_0` | 94 | 53 | 68 | 81 | 88 | **91** |
| `Random-125-125-8-2_0` | 93 | 51 | 66 | 77 | 84 | **89** |
| `Random-125-125-8-3_0` | 95 | 53 | 61 | 75 | 84 | **89** |
| `Random-125-125-8-5_0` | 91 | 47 | 58 | 71 | 80 | **85** |
| `Random-125-125-6-1_0` | 81 | 40 | 46 | 56 | 63 | **71** |

A gap of **40 becomes a gap of 1** on the first one. The cost, on those same
instances: t=8 is 0.5–0.8 s, t=10 is 3–6 s, t=12 is 17–70 s. The knee is at
about t=10, and `_lower_bound` defaults to 8 because that is what the corpus-wide
validation covers.

It is also exactly tight in places the old bound was not: **GP5 comes out at 95,
its published optimum, in 0.00 s**, where the old bound gave 45.

## 4. What this does and does not rest on

The clique bound is proved directly from the MOSP semantics and needs nothing
else. Contraction degeneracy and this bound both go through Yanasse's
`MOSP = pathwidth(MOSP graph) + 1`, so a closure resting on either inherits that
theorem. `BOUND_SOURCES` now carries `expansion` so the provenance records which.

**Prior art is unsettled and no novelty is claimed.** This is a
vertex-isoperimetric argument over the vertex-separation formulation, and
something equivalent may well be known — Ellis, Sudborough & Turner (1994) on
vertex separation is the obvious place to look, and the MOSP literature's LB3/LB4
(subgraph and minimum-degree bounds, Yanasse et al. 1999 §3.1) are its
neighbours without being it. `literature/MISSING.md` carries the question. The
same discipline as the arc contraction bound, which turned out to be something we
already had under another name.

## 4a. Where it works, and where it does not at all

The corpus-wide averages hide a clean split. On the 25 125×125 instances, by
density (cap 8):

| density | mean gap before | after |
|---|---|---|
| 2 | 9.8 | **9.8** |
| 4 | 27.4 | **27.4** |
| 6 | 39.2 | 26.0 |
| 8 | 41.8 | 12.2 |
| 10 | 38.8 | **3.0** |

**Zero gain on density 2 and 4.** Sparse graphs do not expand — `f(t)` stays low,
`M(i)` stays high, and the argument gives nothing. That is the exact structural
mirror of why the degree-based bounds fail on dense graphs, and it matters
because the sparse instances are **97% of the recorded compute** (278,683 s of
286,895 s). At a deeper cap of 11-12 density 4 does move (27 → 35-37) but
density 2 stays flat and can even come out *below* the old bound, which costs
nothing since the best of the two is taken.

Pushed to cap 12 over all 25, **4 reach the optimum exactly** — all at density
10 — where the descent then exits with `proof="bound"` and the refutation never
runs.

## 4b. The complement: contraction on the sparse end

`satisfiability/relaxation.py` repairs exactly what the expansion bound cannot,
because contracting makes an instance smaller *and denser*. Sweeping the
contraction target on the ten sparse 125×125 instances rather than using a
single one:

| contract to | 40-80 | 85 | 90 | 95 | 100 |
|---|---|---|---|---|---|
| `Random-125-125-4-2_0` (opt 57) | 42 | 44 | 47 | 48 | **50** |
| `Random-125-125-4-1_0` (opt 57) | 40 | 43 | 46 | 47 | **50** |

**Mean gap over the ten: 18.6 → 6.2**, against an old bound gap of 18.6 and an
expansion-bound gain of zero. Beyond 100 of 125 customers the contracted
instance becomes as hard as the original and the call returns nothing, so the
knee is there.

So the two bounds are complementary and neither is general: expansion for dense,
contraction for sparse, and the max of the two is free.

## 5. Next

1. **Settle the prior art** before this is written up anywhere outward-facing.
2. **Re-run the hard instances with it.** The 125×125 instances were certified
   by descending from an upper bound through forty values of `k`; starting from
   98 instead of 59 changes what that costs by orders of magnitude. This is the
   first bound improvement that could actually shorten a proof rather than
   decorate it.
3. **Push the cap adaptively.** Cost grows steeply but so does the bound; a
   budget-aware schedule that goes deeper only while the bound is still moving
   would get most of t=10 for most of the price of t=8.
4. ~~**Combine with the relaxation.**~~ **Measured, §4b.** They are
   complementary rather than overlapping: expansion carries the dense end,
   contraction the sparse end, and together the mean gap over the 25 hardest
   instances falls much further than either alone. What is *not* yet shown is
   that a smaller gap shortens a proof — `customer_search.solve` only skips the
   refutation when the floor **equals** the optimum, so a gap of 6 saves nothing
   in the current descent. That is the question the re-certification run asks.

---

## 6. The bound is better and the solver is slower. All of it.

*Added after the re-certification run. This section is the one that matters.*

A better floor was supposed to shorten proofs. It does not, and the reason is
architectural rather than numerical.

`customer_search.solve` descends `k` from an upper bound and stops at the first
refutation. The floor appears in one place only — the loop condition `while k >=
lower` — so it changes the search **only when it truncates the loop**, which
happens only when `floor >= optimum`. A floor of 50 against an optimum of 57
leaves the identical sequence of `k` to be visited. It is not a weaker
improvement; it is no improvement.

And where the floor *is* exactly tight, what it saves turns out to be nothing.
Controlled A/B over the 25 hardest instances — same code, same budget, only the
floor differs, bound-computation time charged to the side that pays it:

| instance | optimum | old floor → | new floor → | verdict |
|---|---|---|---|---|
| `Random-125-125-10-1_0` | 105 | refutation, **0.2 s** | tight, but **28.0 s** to compute | 140× worse |
| `Random-125-125-10-5_0` | 99 | refutation, 0.4 s | tight, 47.3 s | 118× worse |
| `Random-125-125-8-3_0` | 95 | refutation, 4.7 s | 133.3 s, descent **4.7 s** | pure overhead |
| `Random-125-125-6-2_0` | 77 | refutation, 435.0 s | 66.8 s, descent **442.5 s** | pure overhead |
| `Random-125-125-6-4_0` | 80 | refutation, 299.5 s | 254.3 s, descent **292.2 s** | pure overhead |
| `Random-125-125-4-1_0` | 57 | open at 600 s | 369.7 s, still open | pure overhead |

Read the middle rows carefully: 217.2 s against 215.8 s, 299.5 against 292.2,
435.0 against 442.5. The descent is **identical**, exactly as the loop condition
predicts, and the bound is added cost. **Not one of the 25 instances benefits.**

Totalled over all 25, the result is as clean as it could be:

| | old floor | new floor |
|---|---|---|
| **search time** | **7,629 s** | **7,627 s** |
| bound computation | 0 s | 8,646 s |
| total | 7,629 s | 16,273 s (**2.13×**) |
| instances certified | 14 | 14 |

7,629 against 7,627 seconds of actual search. To within 0.03% the bound changes
the search by *nothing*, certifies the same 14 instances, and doubles the wall
clock. The four refutations it does skip are worth 0.2-0.4 s each.

### What went wrong in the reasoning, not the mathematics

The bound is sound and the gap numbers are real: mean gap over these 25 falls
from 31.4 to 5.2, and over the whole corpus from 0.98 to 0.44 with zero
violations. None of that is retracted.

What was never checked, before the work went in, is **what the refutation
actually costs**. The baseline used to justify chasing the bound was the compute
ledger — 286,895 s across these instances, 19.19 hours on the worst. Much of
that is timeouts recorded by an older configuration. Today's customer search,
with `better_move` on the sparse instances, refutes the density-10 ones in
**0.2 seconds**. Avoiding a 0.2-second call was never going to pay for a
28-second bound, and one measurement of the refutation would have said so before
any of this was built.

The instances that genuinely cost hours are density 2 and 4, and there the
expansion bound contributes nothing at all (§4a) — sparse graphs do not expand.
So the bound is strong exactly where the problem is already easy.

### Consequently: off by default

`_lower_bound` takes `expansion_budget`, and it now defaults to `None`. The
module stays, the validation stays, and the bound is available for analysis and
for any future search whose cost profile differs. It is not on the solver's path,
because on every instance measured it is a tax.

### The use that is still open

The same argument applied **inside** the search rather than at the root. `decide`
already prunes with a one-step lower bound — it cuts a branch when the immediate
cost reaches `k`. A per-node version of the expansion argument, on the induced
subgraph of the customers still open, would prune the refutation itself, which is
where the hours are. Whether it can be made cheap enough per node is the
question; the root-level version costs far too much to evaluate at every node, so
it would need an incremental formulation. That is a real lever and it is
untested. The root-level floor is not.
