# What Transfers from Chu & Stuckey (2009) to a SAT Encoding

Their solver closes SP3 in 410 ms and SP4 in 9,087 ms on 2009 hardware. Ours has
a solution of 35 for SP3 against a published 34, and spent 12.5 hours on a single
call at 34 without answering. That gap is the thing a reviewer will press on, so
it is worth knowing precisely what they do that we do not, and which parts of it
a CNF can express at all.

Read against `literature/chu_stuckey_2009.pdf`.

---

## 1. The one structural fact everything rests on

Stated in each of their proofs, in passing:

> the number of open stacks "only depend[s] on the set of customers closed and
> not the order"

The objective is a function of a **set**, not a sequence. Every result below is a
consequence, and the distance between their approach and ours is mostly the
distance between exploiting that and not.

Our encoding indexes everything by position: `x[p,t]` says pattern `p` sits at
step `t`. Two orderings that close the same customers in the same grouping, but
permute products within a group, are different satisfying assignments reaching
identical states. The solver rediscovers their equivalence through conflict
analysis, and because the variables are position-indexed, a lemma learned about
step `t` does not transfer to step `t'`.

---

## 2. The customer-search reduction — transferable, and probably their edge

From §2 of the paper:

> Given a product order `U`, define a customer close order `T` as the order in
> which customer stacks can close given `U`. Construct `U'` such that we first
> schedule all the products needed by `c1`, then any products required by `c2`,
> and so on. If `U` is a solution, then so is `U'`.
>
> **"It is sufficient to search only product orderings where every product is
> required by the next stack to close."**

This is a canonical form. Every solution has a representative in which products
are grouped by the customer whose closure they complete, so the search may be
restricted to those representatives without losing any optimum.

It is exactly the kind of statement a SAT encoding *can* take: it constrains
solutions, not search states, so it becomes clauses rather than a pruning rule.
That makes it the one part of their advantage we can plausibly adopt.

**Sketch.** Introduce `z[c,t]`, "customer `c` closes at step `t`", already
definable from the `all[c,t]` auxiliary the encoding carries. Then require of
each product placed at `t` that it be needed by the customer closing next —
i.e. the product at `t` belongs to `P_c` for the `c` with the earliest close at
or after `t`. Products needed by no still-open customer are forced to positions
where they complete a closure.

**Caveats, learned the hard way.** The dominance rules from Yanasse, Becceneri &
Soma were implemented here as symmetry-breaking clauses and were *unsound as
encoded* — 53 of 250 random instances came back wrong, mostly by making the
formula unsatisfiable outright (see `satisfiability/mosp_encoding.py`). The rule
was sound; the translation was not. Any attempt at the above must be validated
against exhaustive search on small instances before it is enabled, and the
existing `tests/test_dominance.py` is the pattern to follow.

---

## 3. Theorems 1–3 — not transferable

The three dominance relations are **relations between search states**, not
between solutions, and a CNF has neither a search state nor a history.

- **Theorem 1, "definite moves."** If `close(q,S) ≥ open(q,S)` then closing `q`
  next is always safe, so every other branch at that node can be pruned. The
  condition is a function of `S`, the partial sequence already committed. A
  clause cannot say "given what has been decided so far."
- **Theorem 2, "better moves."** Same shape, comparing two candidate moves under
  the current partial state. Subsumes Theorem 1.
- **Theorem 3, "old move."** Purely a memoisation rule: prune `q` here because
  the subtree for `q` was already searched at an ancestor, *provided* the
  reordered sequence is playable. Their own note records that [8] stated this
  incorrectly by omitting the playability condition. This has no CNF analogue at
  all — it prunes on what the search has already done.

A CDCL solver does have its own memoisation, in learned clauses, and that is the
honest comparison: their dominance rules are hand-built, MOSP-specific
memoisation over customer sets, while clause learning is generic memoisation
over position-indexed literals. Theirs targets the structure; ours does not know
the structure exists.

**Consequence.** No amount of symmetry breaking closes the whole gap. §2's
canonical form is worth adopting and might be worth a large constant, but
Theorems 1–3 argue for a different algorithm rather than a better encoding.

---

## 4. Lemma 1 — bears directly on our lower bound

> **Lemma 1.** If `G'` is some contraction of `G`, where `G` represents the
> customer graph of an MOSP instance, then `G'` is a relaxation of `G`.

This matters for `reports/lower_bounds.md`. Our contraction degeneracy bound is
currently justified through treewidth — contraction degeneracy lower-bounds
treewidth, treewidth lower-bounds pathwidth, and `MOSP = pathwidth + 1` — a chain
whose last link this project has specific reason to treat carefully, which is why
the bound is validated against 6,226 known optima rather than argued for.

Lemma 1 offers a **MOSP-specific justification instead**: if every contraction of
the customer graph is a relaxation, a bound computed on a contracted graph bounds
the original directly, with no appeal to the pathwidth equality. That would move
contraction degeneracy from "validated" to "proved" in our terms.

Two cautions before claiming it. The paper attributes the result to Becceneri,
Yanasse & Soma (2004), noting that "only informal arguments are given for
correctness" there — and that paper is the one still listed in
`literature/MISSING.md`. It is also further evidence that our contraction bound
may simply *be* the arc contraction bound of Yanasse et al. (1999), which §10 of
the lower bounds report already flags as blocking any novelty claim.

---

## 5. What to do

1. **Implement §2's canonical form as symmetry breaking**, validated against
   exhaustive search before being enabled by default. It is the only item here
   that is both transferable and plausibly large.
2. **Do not attempt Theorems 1–3 as clauses.** They are search-state dominance;
   encoding them is what went wrong last time, in a milder form.
3. **Chase Becceneri, Yanasse & Soma (2004)** for Lemma 1's proof. It would give
   our lower bound a direct justification and settle the novelty question at the
   same time. It remains the single most valuable missing reference.
4. **State the performance gap plainly in the paper.** Their DP closes SP3 in
   410 ms; we do not close it at all. Our contribution is checkable optima at
   scale, not speed, and the comparison should be made rather than avoided.
