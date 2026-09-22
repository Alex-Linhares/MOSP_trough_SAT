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
4. **Combine with the relaxation.** `satisfiability/relaxation.py` lifts SP4
   from 27 to 45 by contraction; the expansion bound gives 37 there at cap 8.
   They are different arguments and their max is free.
