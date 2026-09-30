# Soundness of the customer search

Section 4 of *The pathwidth complex* (`plan.md` §4). Every certified
refutation in the corpus rests on one claim: that the pruning rules of Chu &
Stuckey's (2009) customer search never discard the last solution. Two
`better_move` bugs broke that claim in code, and testing caught both
(`../reports/better_move_bug.md` §1–§3 and §7). This document states the claim
precisely and then proves it.

- §1 models the search as a mathematical object.
- §2 states each rule *as the fixed code implements it*, quotes the code lines,
  and says which composition of rules is claimed sound.
- §3 (item 06) checks every statement by brute force.
- §4 (items 07–11) gives the Lean proofs.
- §5 (item 12) states the theorem and maps each premise the certificate checker
  verifies to the Lean lemma that justifies it.

§1–2 were written in loop0006 item 05 and contain no Lean.

**Code references** are to the tree at commit `8d824d034`:
`satisfiability/customer_search.py` (**Py**, the reference implementation),
`satisfiability/customer_search.c` (**C**), and
`learning/search_certificate.py` (**Cert**, the emitter and the independent
checker). Line numbers are given as `Py:238–252`. Page numbers for Chu & Stuckey (2009)
are those of `literature/chu_stuckey_2009.pdf`, the preprint, cited as "PDF p.".

**Status of the statements.** Every conclusion in §2 was spot-checked before
it was written down, using a throwaway script (not item 06's deliverable).
The script computes the predicate `Sol` of §1.4 exactly by dynamic programming
over closed sets, on 300 random graphs with 2–8 vertices at every `k`, 1,461
`(graph, k)` pairs in all. The checks were:

- Lemma F (free moves);
- the conclusion of the definite move at every playable `q` meeting its
  premise, in every state `cl(T)` with `|O(T) ∖ T| ≤ k`;
- the conclusion of the subset rule for every ordered pair;
- the corrected better move for every ordered pair.

There were zero failures. This is evidence, not proof: the statements are
claims until items 06–12 settle them.

---

## 1. The search as a mathematical object

### 1.1 Instance, customers, neighbourhoods

An instance is a 0/1 matrix `M` with rows as customers and columns as products.
The search sees only the **active** customers `C`, those with at least one
product (`Py:225`). A customer with no product never opens a stack, and the
search leaves it out of the witness (`Py:193–194`). On `C`, `N[c]` is the
self-inclusive neighbourhood in the MOSP graph: `d ∈ N[c]` iff `d = c` or some
product is needed by both (`Py:224`, `_neighbour_masks`; Cert has its own
`neighbourhoods`, which shares no code with the search).

Chu & Stuckey observe (2009, §2, PDF p. 4) that the products matter only through
this graph: "all functions c(p) that produce the same customer graph have the
same minimum number of stacks". So everything below is a statement about a
finite graph `G` on `C` and an integer `k ≥ 0`.

### 1.2 Opened sets and the quantities the rules use

For `T ⊆ C`:

| symbol | definition | code |
|---|---|---|
| `O(T)` | `⋃_{c ∈ T} N[c]`, the stacks *opened* so far (`O(∅) = ∅`) | `opened` |
| `fin(X)` | `{c ∈ C : N[c] ⊆ X}`, the customers finished once `X` is open | `free_moves`, Py:238–252 |
| `o(c, T)` | `N[c] ∖ O(T)`, what closing `c` next would newly open | `opens[c]`, Py:285–291; C:431–441 |
| `open(c, T)` | `|o(c, T)|` | `own.bit_count()`, `sizes[j]` |
| `close(c, T)` | `|{d ∈ C ∖ fin(O(T)) : o(d, T) ⊆ o(c, T)}|` | Py:408, C:320–323 |

Two facts are used everywhere, and both are immediate:

- `T ⊆ fin(O(T))`;
- `O(fin(O(T))) = O(T)`. Every `N[c]` with `c ∈ fin(O(T))` lies inside `O(T)`,
  and `T ⊆ fin(O(T))` gives the reverse inclusion.

`close` is Chu & Stuckey's count (PDF p. 4), "the number of new stacks that will
close", with one difference. The paper's `d` ranges over every customer, while
the code's ranges only over customers not yet finished, the `d` with
`o(d, T) ≠ ∅`. The code closes every finished customer before any rule runs
(§1.3), so at the states where the rules run the two ranges differ only by
customers already closed. `close(c, T)` counts `c` itself whenever
`o(c, T) ≠ ∅`.

### 1.3 Moves, costs, and free-closed states

**A move** closes one customer. At closed set `T`, closing `c ∉ T` costs

    cost(T, c) = |O(T ∪ {c}) ∖ T| = |O(T) ∖ T| + open(c, T),

the stacks open at the moment `c` closes, counting `c` itself (Py:17–22,
Py:321; C:275–287 computes it in the second form, as `open_now + sizes[j]`).
This is the paper's `|O(S) − S ∪ o(c, S)|` (PDF p. 4). The move is **playable**
when `cost(T, c) ≤ k`. A **closing order from `T`** is an enumeration
`c₁, …, c_m` of `C ∖ T`, and its cost is `max_i cost(T ∪ {c₁, …, c_{i−1}}, c_i)`
(0 when `m = 0`).

**The plain predicate.** `P_k(T)` means that some closing order from `T` has
cost at most `k`.

**Free-closed states.** The search never stops at an arbitrary `T`. On entering
a node it closes every remaining customer whose neighbourhood is already open
(the *free moves*, Py:259–266 and C:431–448). A free move opens nothing, and
opening nothing creates no new free moves, so one pass suffices (Py:241–243).
The node's closed set is therefore

    cl(T) = fin(O(T)),

and by §1.2 the opened set `O(cl(T)) = O(T)` is a function of the closed set.
This is why the memo can key on the closed set alone (Py:148–150, C:451). A
**state** is a free-closed set `S = cl(S)`. Its **remaining** customers are
`R(S) = C ∖ S`, and each has `o(c, S) ≠ ∅`. The **child** of `S` by `c ∈ R(S)`
is `S·c = cl(S ∪ {c})`. The search calls itself on `closed | bit(c)`, and the
callee closes the free moves (Py:364, C:482).

**The search's predicate.** For a state `S`, `Sol_k(S)` holds iff `S = C`, or
some `c ∈ R(S)` has `cost(S, c) ≤ k` and `Sol_k(S·c)`.

The root is `∅ = cl(∅)`, because every `N[c]` is nonempty.

### 1.4 The decision question

The search answers the question: **is there a closing order of cost ≤ k from
∅?** When the cost cut is its only pruning, it returns `sat` exactly when
`Sol_k(∅)`. The whole point of §2 is to show that the rules do not change this
answer.

Two facts connect this question to MOSP. Both are for items 07 and 12 to prove
in Lean.

**Lemma F (free moves).** Suppose `|O(T) ∖ T| ≤ k`. Then
`P_k(T) ⇔ Sol_k(cl(T))`.

*Why.* (⇒) In any closing order from `T`, a customer `f ∈ fin(O(T)) ∖ T` can be
moved to the front. That changes no opened set, and every step before `f`'s old
position gets cheaper by one, because `f ∈ O(T)` was counted as open there.
(⇐) Closing the free customers one at a time costs at most `|O(T) ∖ T| ≤ k`
each. The hypothesis holds at the root (`0`) and at every child, where it is
the parent's step cost minus one. So it holds at every node the search visits.

**Cost = out-narrowness = pathwidth + 1.** Take a full closing order
`τ = c₁, …, c_n` from `∅`, and write `S_i = {c₁, …, c_i}`. Its `i`-th step costs
`|N[S_i] ∖ S_{i−1}|`. That is `outShackBeforeMove τ (i−1)` of Kornai & Tuza's
dual shack process, formalised in `Complex/Narrowness.lean` (`EnteredBy`,
`outShackBeforeMove`). The shack just after the move is a subset of it. So the
cost of `τ` is `outNarrowness τ`, and

    min_τ cost(τ) = outNarrownessGraph = narrowness = pw(G) + 1

(`outNarrownessGraph_eq_narrowness`, `narrowness_eq_pathwidth_add_one`, for
nonempty `C`). By `mospValue_eq_pathwidth_add_one` (`MOSPGraph.lean`), this is
the MOSP value. Inactive customers are isolated vertices of the MOSP graph and
change neither side.

**So `¬ Sol_k(∅)` means MOSP > k.** This is the only thing an `unsat` answer
is allowed to mean. Chu & Stuckey state the correspondence in their §2
(PDF p. 4); the project had measured it 400/400
(`../reports/chu_stuckey_plan.md` §0.1). Item 07 turns it into a lemma.

### 1.5 The search tree

`search(S, Q)` is called with a state and a set `Q ⊆ R(S)` of *old moves*
(`seen`, §2.6). The node does the following, in the order of Py:254–381 and
C:414–494:

1. Close the free moves. If `S = C`, answer `sat`.
2. Memo: if `S` is recorded as refuted, answer `false` (§2.7).
3. `Q ← Q ∩ R(S)`. The **candidates** are `K = R(S) ∖ Q` under old move, and
   `K = R(S)` otherwise (Py:274–276, C:453–455).
4. The **cost cut**: the playable candidates are
   `P = [c ∈ K : cost(S, c) ≤ k]`, in increasing customer index (Py:315–323,
   C:282–289).
5. The **dominance filter** turns `P` into a sublist `L` (§2.2–§2.5; Py:325–327
   via `_apply_dominance`, C:270–358 `dominance_filter`).
6. Sort `L` by cost, with ties broken by index, or by the degree fan order
   (Py:329–332, C:360–391). This changes only the order in which children are
   visited.
7. For each `c ∈ L` in that order:
   - recurse on `S·c` with the inherited old moves `Q'(c)` (§2.6);
   - on `true`, answer `true`;
   - otherwise add `c` to `seen` for the later siblings (Py:335–373,
     C:467–489).
8. Record `S` as refuted, unless the run aborted, and answer `false`
   (Py:378–379, C:491).

The cost cut in step 4 is not a rule. It is the definition of playability, and
it is exact: an unplayable move is not a move of `Sol_k`. Everything else in
steps 2, 3 and 5 is a rule, and each needs a soundness argument.

---

## 2. The rules, as the fixed code implements them

### 2.0 What "sound" means at a node

Fix a node `(S, Q)` with playable candidates `P` and filtered list `L ⊆ P`.

**Node soundness.** Assume every old move is refuted: `¬ Sol_k(S·q)` for every
`q ∈ Q`. Then `Sol_k(S)` implies that `Sol_k(S·c)` for some `c ∈ L`.

Every rule below is justified by a **covering** of the same shape: a discarded
move `r` is *covered by* `c` when `Sol_k(S·r) ⇒ Sol_k(S·c)`. Coverings compose
transitively. So node soundness follows once the coverings the rules use
satisfy one condition: **every chain of coverings from a discarded playable
candidate ends in `L` or in `Q`.** That is exactly what the certificate
checker's step 5 enforces (Cert:641–657), and a cycle violates it.

A rule's premise can be true of every pair it cites while its composition is
still unsound. That is the 2026-09-26 bug.

Unplayable customers need nothing. Customers in `Q` are covered by the
hypothesis.

### 2.1 The free move

**Premise.** `c ∈ C ∖ T` with `N[c] ⊆ O(T)`, i.e. `c ∈ fin(O(T))`, and
`|O(T) ∖ T| ≤ k`.

**Conclusion.** No completion is lost by closing every such `c` immediately:
`P_k(T) ⇔ Sol_k(cl(T))` (Lemma F).

**Code.**

```python
# Py:246-251
bits = full & ~closed
while bits:
    ...
    if masks[bit.bit_length() - 1] & ~opened == 0:
        found |= bit
```

```c
/* C:434-436 */
mask_t own = s->neighbour[c] & ~opened;
int size = popcount128(own);
if (!size) { free_now |= bit; continue; }
```

**Order.** Free moves are closed first, on entry to every node, before the
terminal test and the memo. Chu & Stuckey have no separate rule for it: it is
the `open = 0` case of Theorem 1 (Py:24–29), with `close ≥ 1 ≥ 0`. The code
makes it unconditional, and every quantity below is computed at the free-closed
state. This is the modelling choice behind Bug A of `better_move_bug.md` §7.

### 2.2 The definite move (Chu & Stuckey Theorem 1)

**Paper.** "Suppose S ++ [q] is playable and close(q, S) ≥ open(q, S), then if
U′ = S ++ R is a solution, there exists a solution U = S ++ [q] ++ R′" (PDF p. 6).

**Premise, as the code checks it.** At state `S`:

- `q ∈ P`: `q` is a candidate, not in `Q` under old move, and
  `cost(S, q) ≤ k`;
- `close(q, S) ≥ open(q, S)`, where `close` counts
  `d ∈ R(S)` (including `q` itself, and including customers in `Q`) with
  `o(d, S) ⊆ o(q, S)`.

**Conclusion.** `Sol_k(S) ⇒ Sol_k(S·q)`: some optimal completion from `S`
begins with `q`. So `q` covers every other playable candidate.

**Action.** `L = [q]`, for the **first** such `q` in index order. The filter
stops there: neither the subset rule nor the better move runs at this node.

```python
# Py:404-412
if definite_move:
    for cost, q in playable:
        own = opens[q]
        opened_by_q = own.bit_count()
        closed_by_q = sum(1 for other in opens.values() if other & ~own == 0)
        if closed_by_q >= opened_by_q:
            return [(cost, q)]
```

```c
/* C:313-330 */
for (int j = 0; j < n_remaining; j++)
    if (sizes[j] <= opened_by && (opens[j] & ~own) == 0) closed_by++;
if (closed_by >= opened_by) {
    costs[0] = costs[i]; who[0] = c;
    count = 1;
    goto sorted;
}
```

`opens` (Py) and `ids`/`opens` (C) range over `R(S)` after the free moves. So
no finished customer is counted, and customers in `Q` are counted. `close` is a
property of the state and does not depend on the candidate set.

**Acyclic by construction.** One candidate is kept and every other one is
covered by it directly.

**Checker.** Step `["definite", q]`. Cert:602–616 recomputes that `q` is
playable and that `close ≥ open` over `R(S)`, and makes `q` the cover of every
other playable candidate. It does not check that `q` is the first in index
order, which soundness does not need.

### 2.3 The subset rule (Chu & Stuckey §2, with an index tie-break)

**Paper.** "if o(cᵢ, S) ⊆ o(cⱼ, S) and i < j, then clearly, we can always play
i before j rather than playing j immediately, since closing j will close i in
any case. Hence move j can be removed" (PDF p. 5).

**Premise, as the code checks it.** At state `S`, for a playable candidate
`r ∈ P`: some `d ∈ R(S)` with `d ≠ r` satisfies

    o(d, S) ⊆ o(r, S)   and   (o(d, S) ≠ o(r, S)  or  d < r).

The dominator `d` ranges over **all remaining customers**, not just the
candidates. In particular it can be a customer in `Q`. It is never an
unplayable customer, because `o(d) ⊆ o(r)` gives `cost(S, d) ≤ cost(S, r) ≤ k`.

**Conclusion.** `Sol_k(S·r) ⇒ Sol_k(S·d)`. Closing `r` makes `d` free
(`N[d] ⊆ O(S) ∪ o(r, S) = O(S ∪ {r})`), and `d` then `r` reaches
the same state as `r` alone, at no greater cost. The inclusion alone gives the
covering. The tie-break is there for acyclicity only.

**Action.** Every `r ∈ P` with such a `d` is dropped, and the list keeps its
index order. **Fallback:** if every candidate would be dropped, `P` is kept
whole. Under old move this can happen only when every chain ends in `Q`
(Py:426–428, C:162–164). The fallback discards nothing, so it is trivially
sound.

```python
# Py:417-428
for cost, q in playable:
    own = opens[q]
    dominated = any(
        other & ~own == 0 and (other != own or d < q)
        for d, other in opens.items() if d != q
    )
    if not dominated:
        kept.append((cost, q))
return kept or playable
```

```c
/* C:151-158, subset_pass with exclude = 0 */
for (int j = 0; j < n_remaining && !dominated; j++) {
    if (sizes[j] > own_size) continue;
    int d = ids[j];
    if (d == c) continue;
    if (exclude && ((exclude >> d) & 1)) continue;   /* 0 in today's rule */
    mask_t other = opens[j];
    if ((other & ~own) == 0 && (other != own || d < c)) dominated = 1;
}
```

**Acyclic by construction.** "`d` dominates `r`" means `o(d) ⊊ o(r)`, or
`o(d) = o(r)` with `d < r`. This is a strict partial order on `R(S)`. So every
chain ends at a minimal element `m`. That `m` is undominated in `R(S)`, and it
is either a candidate, which then survives the subset pass, or a member of `Q`.

**Order.** The subset rule runs after the definite move (only when the definite
move did not fire) and **before** the better move. Its dominators are measured
against `R(S)`, and nothing has been discarded from `R(S)` when it runs. That
ordering is the 2026-09-26 fix (§2.4).

**Checker.** Step `["subset", r, d]`. Cert:617–627 checks that `r` is playable,
that `d ∈ R(S)` with `d ≠ r`, and that the tie-broken inclusion holds. It also
rejects a candidate that is discarded twice.

### 2.4 The better move (Chu & Stuckey Theorem 2, corrected), C only

**Paper.** "Suppose S ++ [q] and S ++ [r, q] are playable and close(q, S ∪ {r})
≥ open(q, S ∪ {r}) then if U′ = S ++ [r] ++ R is a solution there exists a
solution U = S ++ [q] ++ R′" (PDF p. 6). It "prunes only one branch at a time"
(PDF p. 6). `better_move_bug.md` §3a argues that this rule is a *pairwise*
conditional. It licenses discarding `r` only while `q` is kept.

**Where it runs.** Only in the C (`better_move_pass`, C:169–266), only when the
`better_move` flag is on, and only when the filtered list after the subset rule
has at least two entries. The Python reference has no such rule. Cert ports the
C (`_better_pass`, `_better_premise`, Cert:440–489), and the port agrees with
the C in node counts (Cert docstring).

**Input.** `W = [w₀, w₁, …]`, the **survivors of the subset rule**, in
increasing index order. The list is not yet sorted by cost; the sort happens
after the filter, at C:360.

**Premise.** Let `S_r = S ∪ {r}` and `X_r = O(S) ∪ N[r]`. The code uses `S_r`
itself, not `cl(S_r)`, but `O(cl(S_r)) = X_r` either way. Then `r = w_i` is
dropped if some `q = w_j` satisfies all of the following:

1. **Earlier and among the first `L`.** `j < i` and `j < L`, where
   `L = better_move_dominators` (default 4 in `decide`; `0` means every earlier
   survivor). `csearch` and `recertify` pass `0`
   (`benchmarks/csearch.py:101`, `benchmarks/recertify.py:70–71`). The C
   comment at C:178 says "only the cheapest few q"; the loop in fact takes the
   first few *by index*. That is a documentation inaccuracy with no bearing on
   soundness.
2. **`S ++ [q]` playable.** `q ∈ W ⊆ P`.
3. **`S ++ [r, q]` playable in the paper's measure.**
   `|(X_r ∪ N[q]) ∖ S_r| ≤ k`. The free moves `r` would trigger are
   deliberately *not* subtracted.
4. **Corrected close count.** `close′ ≥ open′`, where
   - `open′ = |N[q] ∖ X_r|`;
   - `close′ = |{d ∈ C ∖ (S_r) : ∅ ≠ N[d] ∖ X_r ⊆ N[q] ∖ X_r}|`.

   `S` here is the free-closed set of the node. The count leaves out every
   customer that `r` finishes on its own.

`r = w₀` is never dropped. The dominator `q` may itself be dropped by an
earlier `q′`: the loop does not consult `survives[qi]`.

**Conclusion.** `Sol_k(S·r) ⇒ Sol_k(S·q)`.

*Why (for item 10).* Premise 4 is the definite-move premise (§2.2) for `q` at
the child state `cl(S_r)`. The remaining set of that state is exactly
`C ∖ S_r` minus the `d` with `N[d] ⊆ X_r`. Premise 3 bounds `q`'s cost at that
state from above, so §2.2 applies there and gives `Sol_k(S·r) ⇒ Sol_k(cl(S_r)·q)`.
If instead `r` finishes `q` on its own (`N[q] ⊆ X_r`), then `q` is already
closed in `cl(S_r)`, and the swap below needs only premises 2 and 3.

The paper's swap then plays `q` before `r`. The cost of `q` first is at most
`k` by premise 2. The cost of `r` second is
`|(X_r ∪ N[q]) ∖ fin(O(S) ∪ N[q])|`. Since `r, q ∈ X_r ∪ N[q]`, this is at most
`|(X_r ∪ N[q]) ∖ S_r|`, which premise 3 bounds by `k`. Both orders reach the
state `cl(S ∪ {q, r})`.

`better_move_bug.md` §7 measures the alternatives:

- the uncorrected count (Bug A) fails on 57 of 126 M applications;
- "exact" playability (subtracting `r`'s free moves) fails on 726 of 125 M;
- the corrected count with paper playability fails on none of 124 M.

```c
/* C:213-251 */
for (int qi = 0; qi < limit && qi < ri && !pruned; qi++) {
    int q = who[qi];
    if (q == r) continue;
    if (popcount128((opened_r | s->neighbour[q]) & ~closed_r) > s->k)
        continue;                                   /* premise 3 */
    mask_t own = s->neighbour[q] & ~opened_r;
    int opened_by = popcount128(own);
    int closed_by = 0;
    for (mask_t bits = remaining_r; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        mask_t left = s->neighbour[lowest_index(bit)] & ~opened_r;
        if ((left || count_finished) && (left & ~own) == 0) closed_by++;   /* premise 4 */
    }
    if (closed_by >= opened_by) pruned = 1;
}
```

`count_finished` is `BM_OLD_CLOSE_COUNT` (C:195). It is `0` in today's rule and
exists only to measure the revert.

**Acyclic by construction.** Every covering points to a strictly earlier index,
so `w₀` survives and every chain ends at a survivor.

**The composition, and the two bad forms.** Today's order is
`definite_move → subset_rule → better_move` (C:353–358):

```c
} else {
    if (s->subset_rule)
        count = subset_pass(s, ids, opens, sizes, n_remaining, 0, costs, who, index_of, count);
    if (s->better_move)
        count = better_move_pass(s, closed, opened, costs, who, index_of, count, NULL);
}
```

Under this order a chain of coverings is a run of subset links followed by a
run of better links, never the other way round. The reason is that the subset
rule has finished before any better-move link exists. A better link's target is
a subset survivor, so the next link, if there is one, is again a better link,
to a strictly earlier index. Every chain therefore ends at a better-move
survivor, which is in `L`, or at a customer in `Q`. The C comment at C:293–312
gives the same argument.

The two known bad forms are:

- **Bug A, the close count** (`BM_OLD_CLOSE_COUNT`). Premise 4 also counts the
  `d` with `N[d] ⊆ X_r`. The rule's own premise is then too weak, and the
  conclusion of the rule fails on its own.
- **Bug B, the cross-rule cycle** (`BM_OLD_RULE_ORDER`, C:348–352). The better
  move runs first. The subset rule then measures its survivors against every
  customer in `R(S)`, including those the better move discarded. So `r` can go
  citing `q`, and then `q` can go citing `r`: every premise is true, and the
  chain has no end.

Bug C (the early exit at C:290 ignored `better_move`) was a flag bug. It did
not make the rule unsound; it made a soundness control vacuous. A third,
measured-only composition, `BM_SUBSET_RESTRICTED` (C:337–347), runs the better
move first and then the subset rule, excluding the better move's discards. It
is argued sound in the C comment and is not claimed here.

**Checker.** Step `["better", r, q]`. Cert:628–637 checks that `r` and `q` are
playable and recomputes `_better_premise` (premises 3 and 4). It does not check
premise 1 (the earlier index or `L`); step 5's cycle check stands in for it.
`_better_premise` is shared with the emitter, so for this rule the checker and
the emitter are not independent in the premise's *formula*. They are
independent in its evaluation on the certificate's states.

### 2.5 The filter as a whole

At a node where the definite move does not fire, `L` is the list of better-move
survivors of the subset survivors of `P`. It is `P` itself when the subset
fallback triggers and the better move is off. When the definite move fires,
`L = [q]`. The rules are **not** applied to a fixpoint: each runs once, over
the list the previous one left.

### 2.6 The old move (Chu & Stuckey Theorem 3)

**Paper.** "Suppose that S′ = [s₁, …, s_m, q, s_{m+1}, …, s_n] is playable, then
if U′ = S ++ [q] ++ R is a solution then U = S′ ++ R is a solution" (PDF p. 7).
It adds: "if … at some ancestor node, the q branch has been searched and U is
playable, then q can immediately be pruned". The paper also maintains the set
`Q(S)` incrementally (PDF p. 7).

**What the code maintains.** `Q` is the `seen` argument.

- At the root, `Q = ∅`.
- At a node `(S, Q)`, a candidate `c` whose subtree has returned `false`
  without aborting is added to `seen` (Py:373, C:488).
- A later sibling `c′` passes to its child

      Q′(c′) = {q ∈ seen : |(O(S) ∪ N[q] ∪ N[c′]) ∖ (S ∪ {q})| ≤ k}

  (Py:350–363, C:401–412, `inherit_old_moves`). That is `cost(S ∪ {q}, c′)`:
  the step `c′` is playable with `q` reinserted before it.
- On entry, the child intersects with its remaining set (Py:275, C:454).

**Invariant (for item 11).** Suppose `q ∈ Q(S)` at a node `S` on the current
path. Then there is an ancestor `A` on that path at which `q` was a searched
sibling whose subtree has **completed** with `false`. Write the moves from `A`
to `S` as `a₁, …, a_t`. Then the reinserted path, which starts at `cl(A ∪ {q})`
and closes `a₁, …, a_t` in turn, is playable, with each `a_j` skipped if `q`
has already made it free. It ends at `S·q = cl(S ∪ {q})`.

*Why.* Take the step through `a_j`, say from `T` to `T′`. Its opened set with
`q` inserted is `O(T) ∪ N[q]`, and its closed set contains `T ∪ {q}`. So its
cost is at most the quantity the inheritance test bounds. The paper's remark
that the playability condition "is in fact crucial" is this test.

**Premise at the node.** `q ∈ Q(S)`.

**Conclusion.** `¬ Sol_k(S·q)`, as long as the refutation of `cl(A ∪ {q})` is
genuine. By the invariant, `Sol_k(S·q) ⇒ Sol_k(cl(A ∪ {q}))`.

**Action.** `q` is removed from the candidates before the cost cut, and it may
end a covering chain (§2.0).

**Not implemented.** The paper's "synergy" (PDF p. 7): if `q ∈ Q(S)` is better
than `r`, add `r` to `Q(S)`. Neither implementation does this.

**Checker.** Old move records no steps. Cert re-derives `Q` from the path with
the same inheritance test (Cert:659–669) and lets chains end in it
(Cert:648–649).

### 2.7 The memo (nogood recording)

**Premise.** The closed set `S` of the current node (after free moves) was
recorded as refuted. Recording happens only when a node's loop finishes
without `true` and without an abort (Py:375–379, C:491; `memo_add` also stops
past `memo_limit` or 70% load, C:96–97). That only stores fewer entries, which
is sound.

**Conclusion.** `¬ Sol_k(S)`. Answer `false` without searching.

**Why a key on `S` alone suffices.** By §1.3, `O(S)` is a function of `S`, so
`Sol_k(S)` is a property of `S`, not of the path that reached it. The memo is
checked after the free moves and before anything else (Py:268–272,
C:450–451).

**Old move and the memo together.** The implementations disagree:

- The **Python refuses** the combination and drops the memo when both are
  asked for (Py:217–222). Its stated reason (Py:48–55;
  `../reports/customer_search.md` §3) is that "a failure reached with old-move
  pruning depends on which branches an ancestor had searched … and recording
  it against `S` alone could refute a state that some other path would not".
- The **C runs both**, as Chu & Stuckey do (PDF p. 12: "better move", "old move"
  and nogood recording on together). **This is the configuration of every
  production refutation**, because `decide`'s defaults are `old_move=True,
  memo=True` and they go to the C (Py:127–128, Py:199–215). That covers
  `csearch`, `recertify` and the harness's `default`.
- **Cert refuses to check** a certificate in that configuration (Cert:526–528).

The argument of §2.0 and §2.6 says the combination is **sound**, and the
Python's stated reason does not hold as a soundness argument. The argument is
an induction on the order in which subtrees complete:

- every refutation completed so far is genuine;
- a node's `Q` entries rest only on refutations completed before the node was
  entered (§2.6);
- so each `Q` entry is genuinely refuted, `¬ Sol_k(S·q)`, and not merely
  refuted relative to the path;
- then a refutation of `S` reached with old-move pruning is a genuine
  `¬ Sol_k(S)`, and recording it against `S` is correct.

What *is* path-dependent is **local checkability**, which is Cert's point: to
check a memo reference under old move, a checker must re-derive the cited
subtree's `Q`, or trust the global induction. That is a property of the
certificate format. It does not make the search unsound.

The empirical record agrees with the argument:

- 10,476 exhaustive C decisions with both on agree with brute force (Py:218);
- the differential harness runs both configurations through the C with both
  on, and recorded 0 disagreements on 878,580 + 878,700 calls at 9–40
  customers (`better_move_bug.md` §7) and on 25,800 calls at 50–100
  (`../reports/ml_nature.md` §33).

Item 11 is to prove this or find the counterexample. Until then it is a
**claim, not a finding**.

### 2.8 Out of scope

- **`restrict=True`** (their `ub_MOSP`, Py:277–282, C:456–459) branches only on
  already-open customers. It is unsound by design, and it never answers `unsat`
  (Py:386–387, `native.py:211`).
- **`expansion_prune`** (Py:293–313) is a whole-node cut that exists only in
  the Python and is off by default. It is not claimed here.
- **`branch` and `fan_order`** only reorder `L` (Py:329–334) and cannot change
  the answer.
- **`max_nodes` and `deadline`** produce `unknown`, never `unsat`, and they
  suppress memo recording (Py:337–345, Py:378).

### 2.9 The composition claimed sound

**Claim (to be proved as item 12's theorem).** Fix an instance and `k ≥ 0`.
Run `decide` with `restrict=False`, `expansion_prune=False`, `branch=None`,
`better_move_variant = 0`, any fan order, and any setting of the following:

- `subset_rule ∈ {on, off}`;
- `definite_move ∈ {on, off}`;
- `better_move ∈ {on, off}` (C), with any `better_move_dominators = L ≥ 0`;
- `old_move ∈ {on, off}`;
- `memo ∈ {on, off}`, with the rules applied in the order of §1.5 and §2.5:
  free moves, memo, the old-move candidate set, the cost cut, and then
  `definite_move → subset_rule → better_move`, each once, each citing only
  customers still standing or in `Q`.

If `decide` answers `unsat`, then `¬ Sol_k(∅)`, so MOSP > k and pw(G) > k − 1.

The configurations that produced the corpus's refutations are all instances of
the claim:

| name | rules | where |
|---|---|---|
| Python reference | free, definite, subset, old move (memo dropped) | `decide(native=False)` |
| C default | free, definite, subset, old move, **memo** | `decide()`; harness `default` |
| `csearch` | the C default plus better move with `L = 0` when ≤ 5 products per customer | `benchmarks/csearch.py:101` |
| `recertify` | the C default plus better move with `L = 0`, always | `benchmarks/recertify.py:70–71` |
| Cert `memo` | free, definite, subset, memo (no old move) | `learning/search_certificate.py` |

The claim covers the old-move-plus-memo combination (§2.7) and is **false** for
the variant bits `BM_OLD_CLOSE_COUNT` and `BM_OLD_RULE_ORDER` (§2.4). Item 06
is to confirm both of those failures by brute force, and item 10 is to prove a
Lean counterexample to each.
