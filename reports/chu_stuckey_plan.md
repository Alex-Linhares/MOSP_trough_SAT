# Exploiting Chu & Stuckey (2009): A Complete Plan

Chu & Stuckey close SP3 in 410 ms and SP4 in 9,087 ms on 2009 hardware. We have
not closed either. This is the plan for extracting everything their paper offers,
ordered by what it is worth to us rather than by the order they present it.

It supersedes `chu_stuckey_transferable.md` on two points, both of which were
wrong. That report concluded the customer-order reduction could not be
formalised and that the dominance material was the whole of their edge. Section
0 below shows the reduction is sound under the claim their algorithm actually
uses, and §2 covers the relaxation technique the earlier report did not discuss
at all — which is, for us specifically, the most valuable thing in the paper.

Read against `literature/chu_stuckey_2009.pdf`.

---

**Status, 2026-09-18 evening — the plan has been executed as far as item 5, and
the body below is left as written, premises included.** It is a record of the
reasoning before the work, and restating its figures against the corpus it
produced would destroy that. Read the numbers in it (6,228 certified, 144
unproven Random, "six operations we implement none of") as of the morning it was
written. What happened:

| item | outcome |
|---|---|
| 1, `ub_MOSP` | done — `reports/ub_mosp_search.md` |
| 2, dominance rules | done, and built into a *complete* search rather than the heuristic. It refutes: 111 of the then-147 open instances closed in 45 minutes, SP3 among them. `reports/customer_search.md` |
| 3, contract + dedupe | done, measured — `reports/preprocessing_measurements.md` |
| 4, customer-order encoding | **not needed**: item 2 reached that space without a SAT encoding at all |
| 5, relaxation | done. `prove` closes nothing (it can only succeed when `ub` is already optimal); partial relaxation lifts SP4's certified bound from 27 to 45. `reports/relaxation.md` |
| 6, decomposition + dominance | done — `mosp/preprocess.py` |
| 7, certificate chain | open, and now harder: a customer-search refutation is not a DRAT proof |

The corpus stands at 6,340 certified optima with 35 instances open, against
6,228 and 148 when this was written.

---

## 0. Two results established before planning anything *(measured)*

Everything below rests on these. Both were checked against exhaustive search
before a line of the plan was written, following the rule that earned itself in
this project when the dominance clauses came back wrong on 53 of 250 instances.

### 0.1 The customer-order cost is exact as a minimum, not per order

Their cost of closing customer `c` when `S` is already closed is
`|O(S) - S ∪ o(c,S)|`, which simplifies to `|O(S ∪ {c}) - S|`, where
`O(S) = ⋃_{c∈S} N(c)` and `N(c)` is self-inclusive. For a customer order
`T`, write

```
cs(T) = max_i |O(S_i) - S_{i-1}|,   S_i = {T_1, …, T_i}
```

| claim | result |
|---|---|
| `cs(T)` equals the value of the product order built from `T` | **313 / 400** |
| `min_T cs(T)` equals the true optimum | **400 / 400** |

The earlier report tested the first claim, found it false, and abandoned the
encoding. The first claim is not what their algorithm needs. `MOSP(C,N)` searches
for *some* playable sequence of all customers under a budget `k`; it never
evaluates a fixed order. The second claim is the one that matters and it holds
without exception.

The worked counterexample in the earlier report stands and is now explained.
On `M = [[1,0],[1,1],[0,1]]` with `T = [c₂,c₁,c₃]` the formula charges 3 where
the constructed product order achieves 2 — because closing `c₂` first is not
realisable at all (`p(c₁) ⊆ p(c₂)`, so `c₁` always closes no later than `c₂`).
The formula over-charges an unrealisable branch, their dominance rule
(`o(cᵢ,S) ⊆ o(cⱼ,S) ⟹ prune cⱼ`) discards it, and the minimum is taken over the
branches that remain. Over-estimating a branch that cannot be optimal costs
nothing.

### 0.2 Lemma 1 holds, and the adjacency condition is load-bearing

> **Lemma 1.** If `G'` is some contraction of `G`, the customer graph, then `G'`
> is a relaxation of `G`.

In matrix terms an edge contraction is an **OR of two rows that share a
product**. The merged customer needs the union of the two product sets, so its
neighbourhood is exactly the union of the two neighbourhoods and no other
adjacency changes. One line of code.

| merge | relaxation held |
|---|---|
| adjacent rows — a genuine edge contraction | **3167 / 3167** |
| non-adjacent rows | 1027 / 1044 |

So `MOSP(contracted) ≤ MOSP(original)`, and the optimum of a contracted instance
is a **certified lower bound** on the original. Merging non-adjacent customers is
not a contraction and really does break it, which is worth a test of its own
since the two operations differ by one predicate and would be easy to conflate.

The paper attributes Lemma 1 to Becceneri, Yanasse & Soma (2004), noting that
"only informal arguments are given for correctness" there. That paper is still in
`literature/MISSING.md`. The measurement above does not replace a proof, but it
is the same standard of evidence the contraction degeneracy bound already meets.

---

## 1. The customer-order encoding — the canonical form, properly

**What it is.** Replace the position-indexed encoding over patterns with one over
customer closing orders, scored by §0.1's set function.

**Why it is the right way to get their symmetry breaking.** The earlier report
tried to add §2's canonical form to the existing CNF as clauses and failed four
times. That was the wrong shape of fix. The canonical form says that orderings
differing only by permuting products inside one customer's block are equivalent.
In a pattern-indexed CNF those are distinct satisfying assignments and the
equivalence has to be asserted. In a customer-indexed CNF **they are not
representable in the first place** — the entire equivalence class collapses to
one assignment. The symmetry is removed by the choice of variables, not by
constraints layered on top. That is why it could not be reconstructed as clauses,
and it is the single most important structural point in this document.

**Encoding sketch.**

- `z[c,i]` — customer `c` closes at step `i`; permutation constraints as now
  (at-least-one plus ladder at-most-one).
- `w[c,i]` — `c` has closed by step `i` (prefix form of `z`, monotone, as `y` is
  to `x` today).
- `op[d,i]` — `d` is open at step `i`. Forced by
  `w[c,i] → op[d,i]` for every `d ∈ N(c)`, and released by `w[d,i]`.
- Objective: at most `k` of `op[·,i]` per step, by totalizer, exactly as now.

Sizes are `O(|C|²)` variables against today's `O(m²)`. On square instances that
is a wash — the win is not size on its own, it is §2, where contraction shrinks
`|C|` and nothing shrinks `m`.

**Validation protocol, non-negotiable.** Exhaustive agreement on ≥ 500 random
instances up to 7×7 before it is enabled anywhere; then agreement with the
existing encoding on every one of the 6,228 certified optima. `tests/test_dominance.py`
is the pattern. The four failures already recorded were each caught in minutes
this way and none was visible by inspection.

**Risk.** Moderate. §0.1 makes the objective sound, but CDCL performance on a
different variable set is not predictable from clause counts. It may simply be
worse. Budget the measurement, not the hope.

---

## 2. Relaxation — the largest opportunity, and the one we missed

This is §3.5 of the paper. The earlier report did not mention it. For our
situation it is worth more than everything else here combined, because it
attacks the one thing that is actually blocking us.

**Our problem, stated precisely.** Across the 144 unproven Random instances the
mean gap between cached upper bound and lower bound is 18.3 stacks. The upper
bounds are good and cheap to improve. The lower bounds are weak, and the only
tool we have for raising them is a refutation on the full instance, which does
not return — SP3 has now spent 2.5 hours at `k=34` across eight backends and 24
hours before that on one.

**What relaxation does.** Contract customers until the instance is small enough
to solve outright. By §0.2 its optimum is a valid lower bound on the original. If
that lower bound meets the cached upper bound, **the instance closes with no
refutation on the full instance at all** — the same mechanism that settled GP7
and GP8, but reached deliberately instead of by luck.

Their driver, adapted:

```
relax(I):
    ub  := ub_MOSP(I)                      # §3, fast incomplete search
    I'  := I
    while |C(I')| > ub:  I' := merge_one(I')
    while I' ≠ I:
        if ub_MOSP(I') < ub:  I' := unmerge_one(I')   # relaxed too far
        else:
            lb := solve_exact(I')
            if lb < ub:  I' := unmerge_one(I')
            else:        return ub          # closed: lb = ub
    return solve_exact(I)                   # relaxation failed
```

**Which customers to merge.** Their ranking, equation (1):

```
F(c) = Σ_{c' ∈ N(c)} |N(c) - N(c')| / |N(c)|
```

Merge the `c` of highest `F(c)` with the neighbour `c'` maximising `|N(c) - N(c')|`.
The intuition is that a customer all of whose neighbours are interconnected is
forced open and closed again quickly, so it contributes little to the bound.
Low-degree-first is the naive alternative and they report it is clearly worse.

**Unmerge choice.** On unrelaxing, do not simply undo the last merge. Test each
candidate unmerge by whether the last solution found still extends to it; choose
one where it does not, since only that has a chance of proving the bound. This
repairs early greedy mistakes and they report it mattering on several instances.

**What we should expect, honestly.** Their gains are concentrated on sparse
instances — 3-4 orders of magnitude at density 2, nothing at density 8-10. Our
gaps run the other way:

| density | instances | mean gap | mean ub | mean lb |
|---|---|---|---|---|
| 2 | 21 | 9.2 | 21.7 | 12.4 |
| 4 | 29 | 17.2 | 38.8 | 21.6 |
| 6 | 32 | 21.1 | 52.6 | 31.5 |
| 8 | 31 | 21.5 | 62.6 | 41.2 |
| 10 | 31 | 19.3 | 68.7 | 49.5 |

Their hard region is our easy one. Relaxation removes the most customers exactly
where our gaps are smallest, so the density-2 instances should fall first and the
density 6-8 band — where most of our gap lives — will resist. This is a real
limitation of the technique for us and should be stated in the paper rather than
discovered by a referee. It is still the best lower-bound tool available, and
partial relaxation (below) pays even when full closure does not.

**Partial relaxation is worth having on its own.** They note that insisting only
on a bound 5 below the true optimum lets ~45 customers go on 125-125-4, provable
in seconds. We currently publish a lower bound for every instance; replacing a
bound of 41 with one of 55 improves the reported gap on all 148 even where
nothing closes. That is a table in the paper, not a footnote.

**Synergy with §1.** Contraction reduces `|C|` and leaves `m` untouched. Under
today's pattern-indexed encoding the formula barely shrinks and the permutation
search over `m` patterns is unchanged — so relaxation alone buys much less for us
than for them. Under §1's customer-indexed encoding, 125 customers down to 60 is
a 4× cut in variables on the dimension the search actually ranges over. **The two
items multiply, and §2 is substantially weaker without §1.** If only one is built,
build §1 first for that reason, not for its own sake.

A cheap partial substitute if §1 slips: after contracting, columns frequently
become duplicated or dominated (`c(q) ⊆ c(p)` lets `q` go), so a
contract-then-dedupe-columns pass shrinks `m` indirectly. Worth measuring before
committing to §1, since it is an afternoon's work.

---

## 3. The `ub_MOSP` incomplete search

§3.4. A DFS over customer closings restricted to **stacks that are currently
open** — `for (c ∈ R ∩ O(S))` in place of `for (c ∈ R)`. Not sound, so the search
is a heuristic, but they report it finding the optimum almost always, with
speedups of 104× and 3010× on 100-100-2 and 125-125-2.

Three reasons to build it:

1. It is the relaxation driver's "have we relaxed too far?" detector, called in
   the inner loop. §2 does not work without a fast, strong upper bound — they say
   so explicitly, and a weak one wastes the whole budget searching instances that
   could never prove the bound.
2. It should beat `customer-tabu`. Both search customer orders; theirs uses the
   structure of `O(S)` to prune rather than sampling a neighbourhood at random.
3. It composes with `customer-tabu` as a seed rather than replacing it.

Cheapest item in this document and on the critical path for the most valuable
one. Build it first.

---

## 4. Dominance relations — where each one can and cannot go

Corrected from the earlier report, which was right that these are not clauses and
wrong to stop there. They are not clauses, but three of the four have a home.

| rule | as CNF | where it does belong |
|---|---|---|
| §2 subset rule `o(cᵢ,S) ⊆ o(cⱼ,S)` | no | candidate filter in `ub_MOSP` and in `customer-tabu`'s neighbourhood |
| Theorem 1, definite moves | no | branch order in `ub_MOSP`; forced move, prunes all siblings |
| Theorem 2, better moves | no | same; subsumes Theorem 1, implement only this |
| Theorem 3, old moves | no | memoisation over `Q(S)`, maintained in `O(|C|)` per node |

All four condition on the partial sequence already committed. A clause cannot say
"given what has been decided so far", which is why encoding them went wrong
before, in a milder form. But `ub_MOSP` is a search and has exactly the state
they need — every one of them applies there unchanged.

Their Table 4(a) is the guide to effort: "better move" and "old move" each buy 1-2
orders of magnitude, and **nogood recording is worth ~1.0× once "old move" is on**
(0.64-1.21 across their instances). We get nogood recording free from CDCL and
should not build a nogood table. Note also that "old move" reduced their memory
from exponential to under 2 MB — the relevant comparison for us is that clause
learning is generic memoisation over position-indexed literals while theirs is
MOSP-specific memoisation over customer sets. Theirs targets the structure; ours
does not know the structure exists.

---

## 5. Preprocessing we still do not do

They discard instances whose customer graph decomposes, to keep their benchmark
honest. That tells us decomposition is worth enough to control for.
`MOSP(I) = max over connected components`, and the components are independent
subproblems. `CLAUDE.md` already lists cluster decomposition as one of six
Yanasse & Senne operations we implement none of. Pair it with column dedupe and
pattern dominance, which become newly productive after contraction (§2).

---

## 6. What is genuinely new here, for the paper

Their relaxation drives a DP. Using it to make **SAT refutations** tractable is a
different thing, and the difference is checkability:

- a contraction sequence is a list of row merges, verifiable in linear time;
- a refutation on the contracted instance is a DRAT proof, verifiable by an
  independent checker;
- the matching upper bound is a witness ordering, already verified by
  `mosp/certify.py`, which shares no code with the solver.

Chain those and an optimum comes with an **end-to-end certificate a third party
can check without trusting any of our code**. Nobody has published that for MOSP.
It also fits what this project already is: the contribution is checkable optima
at scale, not speed. The honest framing stays as recorded — their DP closes SP3 in
410 ms and we do not close it at all — but "we cannot match their speed" and "we
produce certificates they do not" are both true and only one of them is a
weakness.

The DRAT corpus problem noted earlier (~10 MB/s of solving, 1.1 TB) is much
smaller here: certificates are only needed for the contracted refutations, which
are by construction the small ones.

---

## 7. Order of work

Sequenced by dependency and by value per unit of effort, not by paper order.

| # | item | effort | depends on | payoff |
|---|---|---|---|---|
| 1 | `ub_MOSP` incomplete search (§3) | small | — | better bounds now; unblocks 2 and 5 |
| 2 | dominance rules inside `ub_MOSP` (§4) | small | 1 | 1-2 orders of magnitude, per their Table 4(a) |
| 3 | contract + column dedupe, measure formula shrink (§2) | small | — | decides whether 4 is needed for 5 |
| 4 | customer-order encoding (§1) | **large** | §0.1 | removes the symmetry; makes 5 pay |
| 5 | relaxation driver (§2) | medium | 1, 4 | certified lower bounds; the actual goal |
| 6 | component decomposition + pattern dominance (§5) | small | — | cheap, independent |
| 7 | end-to-end certificate chain (§6) | medium | 5 | the publishable claim |

Items 1, 3 and 6 are each under a day and independent — they can go first
regardless of what happens to the rest. Item 4 is the one that can fail on
performance rather than correctness, so item 3 exists to find out how much of
item 5 survives without it.

**Kill criteria, set in advance.** Item 4 is abandoned if the customer-order
encoding is not within 2× of the current encoding on the certified corpus. Item 5
is abandoned if relaxation closes nothing on the density-2 instances, which are
its best case by their own results and ours.

## 8. Still blocking

**Becceneri, Yanasse & Soma (2004)** remains the most valuable missing reference.
It carries Lemma 1's proof, which §2 rests on, and would settle whether our
contraction degeneracy bound is already the arc contraction bound of Yanasse et
al. (1999) — the open novelty question in `lower_bounds.md` §10. §0.2 measures
the lemma on 3,167 contractions but does not prove it.
