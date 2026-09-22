# Can we manufacture instances whose optimum we already know?

*2026-09-22. Prompted by a question about packed gate-matrix layouts. Short
answer: yes, easily, and within every construction tried the optimum is known
**because** our weakest bound is tight on it. The two properties are the same
property.*

## 1. Why we want them

The corpus is closed but lopsided: 5,938 of 6,376 instances have 30 or fewer
customers, and the 125×125 instances that hold the compute are 25 rows. Anything
learned from it is learned from small instances (`reports/learning.md` §3). A
generator for instances with known optima would break that ceiling — training
data at sizes we cannot certify, scale tests for bounds, and a way to ask "how
does this bound behave at 500 customers", which today has no answer.

## 2. Three constructions, and what each is worth

### Known-pathwidth graph classes

MOSP is `pathwidth(MOSP graph) + 1`, so any graph family with settled pathwidth
gives instances with settled optima. Realise the graph as an instance by making
each edge a product with two customers.

**Grids.** `pw(P_k × P_n) = min(k, n)`, so the optimum is `min(k,n) + 1`.
Verified on 8 grids from 2×3 to 5×5: **8 of 8 exact**. And useless — our
existing lower bound is tight on *every one of them*. Free to make, worth
nothing as a test.

**Trees.** Pathwidth of a tree is computable in linear time, and for the complete
binary tree of height `h` it is `⌈h/2⌉`. These are the only constructed instances
found where our bound is **not** tight:

| family | customers | optimum | our bound | gap |
|---|---|---|---|---|
| complete binary, h=5 | 63 | 4 | 3 | 1 |
| complete binary, h=6 | 127 | 4 | 3 | 1 |
| complete ternary, h=4 | 121 | 5 | 3 | 2 |
| random tree, n=100 | 100 | 4 | 2 | 2 |

Worth noting how that was checked: a quick pathwidth recursion written for the
occasion predicted 7 for the h=6 binary tree and the solver said 4. **The solver
was right** — `⌈6/2⌉ + 1 = 4` — so the construction and the solver cross-validate
each other, and the ad-hoc formula was the thing that was wrong.

### Packed gate-matrix layouts

A gate-matrix layout is the same picture as a MOSP schedule: nets are customers,
gates are products, and a net occupies a track from its first gate to its last.
Suppose the layout is **packed** — every track starts at column 1, and as each
interval ends another begins, so `k` tracks tile the whole width.

**That layout is optimal, and the proof is one line.** Every track is occupied at
column 1, so every one of those `k` nets has its interval *starting* there, so
all `k` require the gate in column 1. That column of the matrix carries `k` ones,
so the trivial bound of Yuen & Richardson (1995) is at least `k`; the layout
achieves `k`; done. Verified on 6 packed layouts from 4×12 to 12×40: optimum `=
k` every time, and the trivial bound `= k` every time.

The packing is far stronger than the proof needs. Only column 1 does any work:
*any* layout whose peak equals the size of its first product's customer set is
optimal. Everything to the right is decoration.

### Optimum-preserving inflation

Adding a **dominated** product — one whose customers sit inside another's —
provably preserves the optimum. That is `mosp/preprocess.py` run backwards, so
any of the 6,376 certified seeds inflates arbitrarily. Rigorous and unlimited.
And our own preprocessor strips exactly that structure back out, so it
manufactures work only for solvers that lack dominance detection. Hardness is
inherited here, never created.

## 3. The trap, stated as an experiment

Break the packing and watch the guarantee die. Stagger the track starts, keep the
tiling, and measure. `k = 7`, 30 columns, five layouts per setting:

| stagger | optimum `= k`? | trivial bound | gap to our bound |
|---|---|---|---|
| 0 (flush both edges) | **5/5** | 7.0 | **0.00** |
| 3 | 4/5 | 5.4 | 0.80 |
| 9 | 2/5 | 5.4 | 0.40 |
| 15 | **1/5** | 4.6 | 0.20 |

Staggering does lower the trivial bound. It also **destroys the optimum
guarantee**: by stagger 15 only one layout in five is still optimal, because a
better gate order beats the packed one. You do not get a hard instance with a
known optimum — you get an instance whose optimum you no longer know.

*(A first attempt staggered only the left edge and changed nothing, because every
track still ends flush at the last column, so the last gate carries all `k` nets
by the mirror argument. Both edges have to break — and breaking both is what
costs the guarantee.)*

**The general claim.** Knowing an optimum by construction means possessing a
short proof of it. Finding short proofs is what the solver does. So constructed
instances are drawn from exactly the population where short proofs exist, which
is the complement of the population that costs us 79.7 core-hours.

## 4. The one escape, and what to look for

Trees escape because their optimum comes from a **theorem our solver does not
encode** — a linear-time algorithm for tree pathwidth — rather than from a
structure our bounds detect. We hold the answer externally. That is the
mechanism, and it points at what to hunt: not cleverer instance constructions,
but graph families whose pathwidth is settled by hard mathematics and whose
structure our degree- and expansion-based bounds cannot see. Tree gaps are only
1–2 on optima of 3–5, so the mechanism is right and the scale is wrong.

## 5. What to build anyway

Even trivially-easy generated instances earn their place three ways:

1. **Scale tests.** How does `expansion_bound` behave at 500 customers? There is
   no way to ask today.
2. **Solver correctness at scale**, where certification is impossible.
3. **As a negative control**, which is the sharpest use. A bound tight on every
   constructed instance but loose on random ones is detecting structure rather
   than measuring difficulty. That test would have said something about the
   degree-based family before an afternoon went into LBN+.
