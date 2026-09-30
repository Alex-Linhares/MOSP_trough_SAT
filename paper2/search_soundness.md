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
- §3 (item 06) checks every statement by brute force (done: zero failures for the fixed rules; both bad forms fail).
- §4 (items 07–11) gives the Lean proofs (§4.1, the model and the free move, done in item 07; §4.2, the definite move, item 08: false as stated, repaired and proved; §4.3, the subset rule, item 09: sound as coded, on its own and after the repaired definite move, and its index tie-break is necessary).
- §5 (item 12) states the theorem and maps each premise the certificate checker
  verifies to the Lean lemma that justifies it.

§1–2 were written in loop0006 item 05 and contain no Lean.

> **Finding (item 08, 2026-09-30): the definite move is unsound as Chu &
> Stuckey state it and as the code implements it.** Their Theorem 1
> (`close(q, S) ≥ open(q, S)` and `q` playable ⇒ some solution from `S`
> begins with `q`) is false. `Search/DefiniteMove.lean` proves a
> counterexample, `definiteMove_counterexample`. On a 14-customer graph at
> the free-closed state `S = {2}` with `k = 6`:
>
> - the node invariant holds;
> - customer `0` is playable, with `close = open = 3`, and is first in index
>   order;
> - the Python port of the filter keeps only `0`;
> - a solution from `S` exists, and none from the child `{0, 2, 3, 4}`.
>
> The C (`customer_search.c:313–330`) and the Python (`Py:404–412`) both
> implement this unsound form, and **every configuration that produced a
> refutation in the corpus runs it** (§2.9). The rule is sound under a
> stronger premise, which is proved in Lean (§2.2, §4.2). No wrong `unsat`
> answer on a whole instance has been found:
>
> - the pinned instances answer correctly;
> - a hunt over 690,000 random graphs found none (§4.2.4);
> - the harness's zero disagreements stand.
>
> But the proof that the corpus refutations are sound no longer covers the
> definite move as coded. The solver is unchanged; the owner decides.

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
claims until items 06–12 settle them. *(Item 08: the definite move's
conclusion is false. Its smallest known counterexample has 14 customers,
far above this spot check's 8 and item 06's exhaustive 7. See §2.2.)*

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

**Finding (item 08): the conclusion is false.** `Sol_k(S) ⇒ Sol_k(S·q)` fails
for the premise above. The counterexample is `cexGraph` of
`Search/DefiniteMove.lean`, 14 customers and 26 edges:

- `N(0) = {3,4,7,11}`, `N(2) = {1,3,4}`, `N(3) = N(4) = {0,2}`;
- at `S = {2}` with `k = 6`, `o(0, S) = {0, 7, 11}`;
- `close(0, S) = |{0, 3, 4}| = 3`.

Closing `3` and `4` first opens only the stack `0` and finishes both of them,
which leaves 2 open stacks. The rule instead jumps straight to `{0, 2, 3, 4}`,
which leaves 3 open stacks (`1, 7, 11`). From `S` there is a solution, but
none from `{0, 2, 3, 4}`: only 7 states are reachable from it within 6
stacks, and none of them is complete.

The paper's proof (PDF p. 6) moves `q` to the front of a solution `U′` and
claims that after each prefix there are "at most open(q, S) extra stacks
open, but at least close(q, S) extra stacks closed". That fails for the
customers `d` that `U′` had *already* closed before `q`. Two such `d`
sharing one new stack are counted twice in `close` and gain nothing when `q`
moves forward.

There is a second, independent slip. The literal sequence
`S ++ [q, c₁, …]` is not a solution even where the theorem holds, because a
customer that `q` finishes stays open until its turn comes. The smallest
case has 4 customers (`§4.2.4`). The argument needs the free moves.

**The repair** (`IsHereditarilyDefinite`, proved sound). Write `b(T)` for
`|O(T) ∖ T|` and `X` for `cl(S ∪ {q})`. The repair requires
`b(X) ≤ b(B)` for every `B` with `S ⊆ B ⊆ X` and `q ∉ B`. The code's premise
is the case `B = S`, because `open ≤ close ⇔ b(X) ≤ b(S)`
(`isDefinite_iff`).

An equivalent form is cheap to compute. By Hall's theorem with deficiency,
which is checked here and not proved, the repair holds iff there is a
matching of size `open(q, S) − 1` from the customers `X ∖ S ∖ {q}` to
distinct stacks `y ∈ o(d, S)`. The Lean proves the direction that matters,
`isHereditarilyDefinite_of_matching`, so the matching form is sound. Every
`q` with `open(q, S) ≤ 1` qualifies. A C implementation would add one small
bipartite matching per candidate that passes `close ≥ open`.

**What the C does.** It implements the unsound form, with no matching.

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

**Item 09: sound as coded, proved** (`Search/SubsetRule.lean`, §4.3). The
covering `Sol_k(S·r) ⇒ Sol_k(S·d)` holds whenever `o(d, S) ⊆ o(r, S)` and `r`
is playable. It needs no invariant, no free-closed state and no tie-break, and
unlike the definite move's it has no collision weakness: the paper's one-line
argument is right. The filter is node-sound on its own, with any family `Q` of
refuted old moves. After the definite move, it is node-sound with the repaired
premise and not with the code's premise, and that loss is the definite move's.
**The tie-break is not decorative.** Without it, twins (equal `o`) dominate
each other and both go. If some other candidate survives, the fallback does
not fire, and the last solution can be lost. The smallest case found has 7
customers and is proved in Lean (`noTieBreak_counterexample`). The code's
tie-break (`d < r` on equality) and the paper's (`d < r` always) both prevent
this.

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

**Item 08: the claim is false as stated whenever `definite_move` is on**, and
it is on in every row of the table. The definite move can discard the last
solution at a node (§2.2, `definiteMove_counterexample`). The claim holds
with the repaired premise in place of `close ≥ open`. As stated, the claim is
now a conjecture about whole instances: it would say that the misfires never
combine into a wrong `unsat`. Nothing found so far contradicts that (§4.2.4),
and nothing proves it. Item 12 must either state the theorem for the repaired
rule or name this gap.

*(Item 09: the subset rule is not what breaks it. `definite → subset` is
node-sound with the repaired premise, `repairedFilter_sound`.)*

The claim covers the old-move-plus-memo combination (§2.7) and is **false** for
the variant bits `BM_OLD_CLOSE_COUNT` and `BM_OLD_RULE_ORDER` (§2.4). Item 06
is to confirm both of those failures by brute force, and item 10 is to prove a
Lean counterexample to each.

---

## 3. The brute-force check (item 06)

`paper2/search_check.py` implements §1–2 **from this document**, sharing no
code with `satisfiability/` or `learning/`. It checks every statement against
an exact oracle. Run it with `python -m paper2.search_check`: 1,030 s on 30
cores, writing `paper2/data/search_check.json`. Tests are in
`tests/test_search_check.py`.

### 3.1 What is implemented

- **The oracle.** `Model.sol` is `Sol_k` of §1.3, computed by memoised
  recursion over free-closed states. `Model.plain` is `P_k` of §1.3, over all
  closed sets with no free-closing. A test checks both against a literal
  minimum over all closing orders, on every labelled graph with ≤ 4 vertices.
- **The filter.** `node_filter` computes, in this order:
  - the candidates (`R(S) ∖ Q` under old move);
  - the cost cut;
  - `definite_move` (§2.2: first `q` in index order, `close` counted over
    `R(S)`);
  - `subset_pass` (§2.3: dominators range over `R(S)`, index tie-break,
    all-dominated fallback);
  - `better_pass` (§2.4: survivors in index order; covers are earlier `q`
    among the first `L`; premise 3 in the paper's measure; the corrected close
    count).

  Each variant composes these in its own order (below). Every discard records
  the link `r → c` that justifies it.
- **The search.** `search_decide` implements §1.5 steps 1–8: free moves, the
  memo keyed on the closed set, `Q ← Q ∩ R(S)`, the filter, the sort by
  (cost, index), and the loop with `seen` and the inheritance test of §2.6.
- **The variants.**
  - `fixed`: today's rule, the only one §2.9 claims.
  - `old_close`: Bug A.
  - `old_order`: Bug B.
  - `prefix`: both bugs, the pre-2026-09-26 rule.
  - `bm_first`: the measured-only `BM_SUBSET_RESTRICTED`.

### 3.2 What is checked

At every `k` from 0 to `n`, the checker runs the following. Here `S·c` is the
child of §1.3.

1. **Lemma F.** `P_k(T) ⇔ Sol_k(cl T)` for every `T` with `|O(T) ∖ T| ≤ k`.
2. **Node soundness (§2.0).** The check runs at every free-closed state `S`,
   for every filter configuration, and for every old-move set `Q` in a family
   of *genuinely refuted* children: all subsets when at most 4 children are
   refuted, otherwise ∅, all of them, the singletons, and random subsets up to
   16. The condition: if some playable candidate has `Sol_k(S·c)`, then some
   `c ∈ L` has it.

   The filter configurations are:
   - every subset of {definite, subset, better};
   - better move with `L ∈ {0, 1, 2}`;
   - every variant, 46 configurations in all.
3. **The rule's conclusion, as cited.** Every link `r → c` the filter records
   satisfies `Sol_k(S·r) ⇒ Sol_k(S·c)`.
4. **The rule's conclusion, over all pairs.** The same implication is checked
   for every pair meeting the premise, not only the pairs the filter happens
   to cite:
   - `definite`: `Sol_k(S) ⇒ Sol_k(S·q)`;
   - `subset`: every playable `r` and every `d ∈ R(S)`;
   - `better`: every ordered playable pair, in the corrected form and in
     Bug A's. Applications are counted only where `Sol_k(S·r)` holds, the only
     place the conclusion can fail.

   This is the measure of `better_move_bug.md` §7.
5. **The covering condition (§2.0).** From every discarded candidate, the
   cited links reach `L` or `Q`. This is the certificate checker's step 5, and
   a cycle fails it.
6. **The whole search.** `search_decide` is run in all 184 flag combinations:
   the 46 filters × old move on/off × memo on/off. Its answer must equal
   `Sol_k(cl ∅)`.
7. **The port is the code.** The same runs go through the C
   (`decide_native` on a matrix with one product per edge). **Answer and node
   count** must both agree. Node-for-node agreement is what shows that §2
   states what the C does. Agreement in answer alone would not show it.

### 3.3 Instances

| family | graphs | what |
|---|--:|---|
| `labelled` | 33,867 | every labelled graph on 1–6 vertices; C cross-check to 5 |
| `atlas7` | 26,100 | every graph on 7 vertices (1,044, networkx atlas) × the identity and 24 random labellings; `Q` families and the C cross-check on the identity |
| `random` | 6,000 | sparse random graphs and random Chu & Stuckey-shaped matrices (products of 2–3 customers), 8–16 vertices; better-move configurations with `L = 0` only, `k ≥ n/5` |
| `pinned` | 3 | the 10 × 13 and 17 × 9 minimal instances and the drawn 10 × 20 (`tests/test_customer_search.py`, `tests/test_differential.py`), every `k` |

Labellings matter, because every tie-break in §2 is by index. That is why
graphs with ≤ 6 vertices are taken labelled and not up to isomorphism.
Labelled graphs on 7 vertices (2²¹) were out of budget, and their 25
labellings per graph are a sample.

### 3.4 Results

**The rules as §2 states them: zero failures of any kind.**

| family | node checks | cited links | pair applications (definite + subset + better/fixed) | tree runs | C runs (node-equal) | Lemma F |
|---|--:|--:|--:|--:|--:|--:|
| `labelled` | 111,288,536 | 166,758,137 | 23,448,891 | 43,401,920 | 1,196,736 | 10,026,384 |
| `atlas7` | 90,915,044 | 254,705,231 | 40,831,575 | 38,419,200 | 1,538,240 | 17,261,225 |
| `random` | 355,181,036 | 2,512,124,140 | 1,821,467,454 | 1,683,108 | 1,683,108 | 834,093,681 |

For `fixed`, the table covers every rule singly and every composition:

- 0 node-soundness failures;
- 0 link failures and 0 pair failures for `definite`, `subset` and
  `better/fixed`;
- 0 covering-condition failures;
- 0 wrong answers.

Lemma F never fails. **The port equals the C in answer and node count on all
4,418,084 runs**, and that includes the bad variants. Old move in these
counts means **old move together with the memo**, which is the §2.7 claim:
the tree runs with both on and the fixed rule are 7,114,880 at ≤ 7 vertices
and 240,444 at 8–16, all of them agreeing with the oracle. That is evidence
for §2.7, not a proof. Item 11 must still prove it.

`bm_first` also never fails, at any level, on any family. This supports the
C comment's claim that the composition is sound. It is not claimed here.

**Both bad forms fail, and they fail in the two different ways §2.4 says:**

| | Bug A (`old_close`) | Bug B (`old_order`) |
|---|---|---|
| kind of fault | the rule's own conclusion is false | every premise is true; the chain has no end |
| cited-link / pair failures | 146 links, 496 of 1,536,555,241 pair applications (random); 6 pairs on the 17 × 9 | **none**, at any size checked |
| covering-condition failures (cycles) | none | from **6 vertices** (exhaustive): 11,847 node checks at ≤ 6 with `subset+better/L0` |
| lost the last solution at a node | above 12 vertices (random, 14 with the rule alone); the 17 × 9 | none at ≤ 7 (exhaustive to 6, sampled at 7); first at **8 vertices** (random) |
| false refutation (tree) | the 17 × 9 only (none of the 6,000 random) | first at **10 vertices** (random), with Bug B alone |
| first pair failure | 12 vertices (random) | — |

The C agrees with the port on every one of these runs, so the failures are
the C's failures. Bug A needs more customers than Bug B, as
`better_move_bug.md` §7 found ("the second bug needs more customers than the
first"). Bug B's cycles are common: 712,758 node checks at 8–16 with
`subset+better/L0`. Only rarely does the cycle take the last solution with
it.

**Two new small witnesses for Bug B**, both pinned in the tests and both
candidates for item 10's Lean counterexample:

- **A node, 8 vertices.** Masks `[139, 59, 12, 15, 178, 242, 224, 241]`,
  `k = 4`, state `S = {2}`, playable `P = [0, 3, 6]`. Better move discards 3
  citing 0. The subset rule then discards 0 citing 3, since `o(3) ⊆ o(0)`.
  That leaves `L = [6]`, which has no completion, while 0 and 3 both have one.
  Under `fixed` and under `bm_first` the node keeps a solution.
- **A false refutation, 10 vertices, Bug B alone.** Masks
  `[523, 519, 678, 73, 16, 548, 72, 388, 384, 551]`: optimum 3, and
  `old_order` answers `unsat` at 3. This is smaller than the 10 × 13
  (10 customers too), which needs both bugs at the tree level (§31).

**The pinned instances reproduce the record exactly**, in the port and in the
C, with equal node counts, at the optimum:

- the 17 × 9 falls to `old_close` and `prefix`, and to no other variant;
- the 10 × 13 falls only to `prefix`, although at the node level it already
  fails under `old_order` alone;
- the drawn 10 × 20 falls to `old_order` and `prefix` with the subset rule
  on.

**A planted fault is caught.** The test suite includes a mutation: better move
letting *any* candidate cover, not only an earlier one (the `Warwick 1730`
cycle), but keeping the list when everything would go, as the C's `if (kept)`
does. It is clean on every labelled graph with ≤ 5 vertices, and it fails on
60 of the 32,768 labelled graphs on 6. The test pins one of them.

### 3.5 What this does and does not establish

It establishes that §2 is a faithful statement of the C: node-equal on 4.4 M
runs. It also establishes that every statement of §2 holds on every graph
with ≤ 6 vertices (labelled), on every graph with 7 vertices under 25
labellings, and on 6,000 random graphs at 8–16 vertices.

It does not reach the sizes where Bug A lives, except by sampling:

- Bug A has no failure at ≤ 11 vertices;
- the smallest failure of its pairwise conclusion found here has 12 vertices;
- the smallest false refutation known is still the 17 × 9.

A check of this kind would have caught Bug B from 8 customers and Bug A only
from 12. The proofs of items 07–11 are what cover every size.


---

## 4. The Lean proofs

### 4.1 The model, Lemma F and the free move (item 07)

`lean/MOSPFormalization/Search/Basic.lean`, namespace
`MOSPFormalization.Search`. It has no `sorry`, and its axioms are `propext`,
`Classical.choice` and `Quot.sound` only (the new lines in
`axiom_check.lean`). Every statement was checked before it was proved, by
`python -m paper2.search_check --model` (§4.1.4).

#### 4.1.1 Definitions

The graph `G` is any finite simple graph, and every customer is a vertex. The
definitions follow §1.2–§1.3 word for word, on *arbitrary* closed sets `T`,
not only on free-closed states.

| §1 | Lean | definition |
|---|---|---|
| `N[c]` | `nbhd G c` | `{d : d = c ∨ G.Adj c d}` |
| `O(T)` | `opened G T` | `T.biUnion (nbhd G)` |
| `fin(X)` | `finished G X` | `{c : nbhd G c ⊆ X}` |
| `cl(T)` | `cl G T` | `finished G (opened G T)` |
| `cost(T, c)` | `stepCost G T c` | `(opened G (insert c T) \ T).card` |
| cost of a closing order | `orderCost G T l` | `0` on `[]`; `max (stepCost G T c) (orderCost G (insert c T) l)` on `c :: l` |
| closing order from `T` | `IsClosingOrder T l` | `l.Nodup ∧ ∀ c, c ∈ l ↔ c ∉ T` |
| `P_k(T)` | `Solvable G k T` | `∃ l, IsClosingOrder T l ∧ orderCost G T l ≤ k` |
| `Sol_k(S)` | `SearchSol G k S` | inductive: `S = univ`, or `c ∉ S`, `stepCost G S c ≤ k`, and `SearchSol G k (cl G (insert c S))` |

`SearchSol` is the predicate the search decides, stated as the search
computes it: its children are the free closures of `S ∪ {c}`, as in Py:364
and C:482. It is not defined in terms of `Solvable`, so Lemma F is a theorem
and not a definition.

#### 4.1.2 What is proved

- **Basic facts** (§1.2):
  - `subset_cl` (`T ⊆ cl T`);
  - `opened_cl` (`O(cl T) = O(T)`, the reason the memo may key on the
    closed set);
  - `cl_empty` (the root is free-closed);
  - `card_opened_insert_sdiff_lt` (the node invariant at a child is below
    the parent's step cost);
  - `stepCost_of_free` (a free move costs exactly `|O(T) ∖ T|`).
- **Monotonicity** (`solvable_mono`): if `T ⊆ T'` and `O(T') ⊆ O(T)`, then
  `P_k(T) → P_k(T')`. More closed with nothing more opened never hurts. The
  proof deletes `T'`'s customers from a closing order from `T`
  (`orderCost_filter_le`). Every remaining step closes the same customer with
  at least as much closed and no more open, so its cost cannot rise.
- **The free move is sound.**
  - `solvable_insert_of_free`: if `N[c] ⊆ O(S)`, then `P_k(S) → P_k(S ∪ {c})`.
    This is the special case `T' = S ∪ {c}` of monotonicity, and it needs no
    hypothesis.
  - `solvable_insert_iff_of_free`: under the node invariant
    `|O(S) ∖ S| ≤ k` the two are equivalent, because the free move then costs
    at most `k`.
  - `solvable_cl`, `solvable_cl_iff`: the same for all free moves at once.
- **Lemma F** (`solvable_iff_searchSol_cl`): if `|O(T) ∖ T| ≤ k`, then
  `P_k(T) ↔ Sol_k(cl T)`.
  - (→) is `searchSol_cl_of_solvable`, which needs no hypothesis. A first
    move of a solvable order from `cl T` is playable, and its child is
    solvable (`exists_first_move`). Induction on `|V ∖ T|`.
  - (←) is `solvable_of_searchSol` plus `solvable_cl_iff`. Unfold `Sol_k` and
    prepend each move (`solvable_of_solvable_insert`). At each child, the
    invariant is the parent's step cost minus one, so it is at most `k`.
  - At the root, `solvable_empty_iff`: `P_k(∅) ↔ Sol_k(∅)`.
- **Cost = out-narrowness** (`orderCost_ofFn_eq_outNarrowness`). For a layout
  `τ`, the closing order `orderOfLayout τ` closes `τ⁻¹ 0, τ⁻¹ 1, …`. Its cost
  is `Complex.outNarrowness G τ`, the narrowness of the out-sequence `τ` in
  Kornai & Tuza's dual shack process. The `i`-th step opens exactly the shack
  just before `wᵢ` leaves (`stepCost_orderOfLayout`). By
  `exists_orderOfLayout`, every full closing order is of this form.
  - `orderCost_ofFn_eq_vertexSepOfLayout_add_one` gives the same cost as
    `vs(τ) + 1` for nonempty `V`, in the development's convention (the active
    suffix of `τ` itself, not of its reverse).
- **The search decides pathwidth and MOSP.**
  - `solvable_empty_iff_narrowness_le`: `P_k(∅) ↔ ν(G) ≤ k`.
  - `searchSol_empty_iff_narrowness_le` and
    `searchSol_empty_iff_vertexSeparation_add_one_le`.
  - `searchSol_empty_iff_pathwidth_add_one_le`: `Sol_k(∅) ↔ pw(G) + 1 ≤ k`
    for nonempty `V`.
  - `searchSol_mospGraph_iff_mospValue_le`: for an instance with at least one
    requirement, `Sol_k(∅)` on `mospGraph M` holds iff `mospValue M ≤ k`.
    This goes through `mospValue_eq_pathwidth_add_one` (`MOSPGraph.lean`).
    So the only thing a refutation `¬ Sol_k(∅)` may mean is `mospValue > k`,
    which is the sentence of §1.4 that item 07 was to turn into a lemma.

#### 4.1.3 Modelling notes

- **Inactive customers.** The search drops customers with no product
  (Py:193–194). `mospGraph` keeps them as isolated vertices. Closing one costs
  one stack plus whatever is already open, so the model's `Sol_k(∅)` on
  `mospGraph` and the search's on the active customers agree for every
  `k ≥ 1`, and both are false at `k = 0` once some requirement exists. The
  final theorem is stated on `mospGraph`, where no case split is needed. The
  statement about the active subgraph is item 12's.
- **Where the invariant matters.** Lemma F's (←) direction and the free
  move's converse are false without `|O(T) ∖ T| ≤ k`. The smallest case is
  `K₂` with one customer closed at `k = 0`: `cl T` is everything, so
  `Sol_0(cl T)` holds, but closing the other customer costs one. The check
  counts 3.55 M such cases for Lemma F and 3.76 M for the free move
  (`lemma_f_needs_invariant`, `free_move_iff_needs_invariant`), so the
  hypothesis is not decorative. The invariant holds at every node the search
  visits (§1.4). Items 08–11 carry it as a hypothesis on states.
- **What is not yet modelled.** This item does not model `Q`, the dominance
  filter, the memo or the search procedure (the order of §1.5). Items 08–11
  add each rule's statement in terms of `Solvable`/`SearchSol` on states.

#### 4.1.4 The check

`python -m paper2.search_check --model` (48 s on 30 cores; writes
`data/search_model_check.json`) transcribes the Lean definitions literally.
`Solvable` is computed by its prepend recursion and `SearchSol` by its
inductive clauses, both on all `2ⁿ` sets. `outNarrowness` and
`vertexSepOfLayout` are transcribed from `Narrowness.lean` and
`VertexSeparation.lean`. The check covers every labelled graph on 0–6
vertices and every atlas graph on 7 (34,912 graphs), with every layout and
every `k ≤ n + 1`, and checks:

| statement | cases | failures |
|---|---|---|
| `orderCost = outNarrowness = vs + 1`, per layout | 28,979,190 | 0 |
| `O(cl T) = O(T)`, `T ⊆ cl T`, `cl ∅ = ∅` | every `T` | 0 |
| `solvable_mono`, every `T ⊆ T'` with `O(T') ⊆ O(T)` | 91,517,418 | 0 |
| free move, and its converse under the invariant | 32,972,900 | 0 |
| Lemma F, both directions, `solvable_cl`, `solvable_of_searchSol` | 18,215,784 | 0 |
| root: `P_k(∅) = Sol_k(∅) = (min cost ≤ k)` | every graph and `k` | 0 |

The tests (`tests/test_search_check.py`, four new) pin:

- hand values on `P₃` and `K₁,₃`;
- the `K₂` case where the invariant is needed;
- a mutation, a step cost that forgets the customer being closed, which
  breaks `cost = vs + 1`.

### 4.2 The definite move (item 08): false as stated, repaired and proved

`lean/MOSPFormalization/Search/DefiniteMove.lean`, namespace
`MOSPFormalization.Search`, about 450 lines. It has no `sorry`, and its axioms
are `propext`, `Classical.choice` and `Quot.sound` only (`../paper2/axiom_check.lean`).

#### 4.2.1 Definitions

| §2.2 | Lean |
|---|---|
| `b(T) = \|O(T) ∖ T\|`, the open stacks | `openStacks G T` |
| `o(c, S) = N[c] ∖ O(S)` | `newlyOpened G S c` |
| `open(c, S)` | `openCount G S c` |
| `close(q, S)`, counted over `V ∖ S` as the code counts it at a free-closed `S` | `closeCount G S q` |
| the code's premise `open ≤ close` | `IsDefinite G S q` |
| the repaired premise | `IsHereditarilyDefinite G S q` |

#### 4.2.2 What is proved

- `openStacks_submodular`: `b(A ∪ B) + b(A ∩ B) ≤ b(A) + b(B)`. The proof
  combines `|O(A ∪ B)| = |O(A) ∪ O(B)|` and `O(A ∩ B) ⊆ O(A) ∩ O(B)` with
  `b(T) + |T| = |O(T)|` (`openStacks_add_card`). Every other result here
  rests on it.
- `stepCost_eq_openStacks_insert_add_one`: closing `c ∉ T` costs
  `b(T ∪ {c}) + 1`.
- `closeCount_eq` and `isDefinite_iff`: `close(q, S) = |cl(S ∪ {q}) ∖ S|`, so
  the code's premise says exactly `b(cl(S ∪ {q})) ≤ b(S)`.
- **Soundness of the repair**:
  - `solvable_cl_insert_of_hereditarilyDefinite`: if `q` is hereditarily
    definite at `S` and `q ∉ S`, then `P_k(S) → P_k(cl(S ∪ {q}))`. It needs
    no invariant and no playability.
  - `searchSol_cl_insert_of_hereditarilyDefinite` gives the search's form:
    `Sol_k(S) → Sol_k(S·q)` under the node invariant.

  The proof (`solvable_union_cl_of_hereditarilyDefinite`) is by uncrossing.
  Write `X` for `cl(S ∪ {q})`. Along any solution from `S`, replace each
  prefix `T` taken before `q` by `T ∪ X`:
  - a customer already in `X` is skipped;
  - for any other customer `c`, submodularity at `Z = T ∪ {c}` gives
    `b(Z ∪ X) ≤ b(Z) + b(X) − b(Z ∩ X) ≤ b(Z)`. The last step is the
    hypothesis applied to `B = Z ∩ X`, which lies between `S` and `X` and
    avoids `q` (`stepCost_union_cl_le`).

  Once the solution closes `q`, `T ∪ X` has the same opened set as `T ∪ {q}`
  and more closed customers, and `solvable_mono` ends the proof.
- **Sufficient conditions**:
  - `isHereditarilyDefinite_of_openCount_le_one`: every `q` that opens at
    most one new stack qualifies. These are the cases where the code's rule
    is right for free.
  - `isHereditarilyDefinite_of_matching`: `q` qualifies if the customers
    `M ⊆ X ∖ (S ∪ {q})` inject into distinct stacks `f(d) ∈ o(d, S)`, with
    `open(q, S) ≤ |M| + 1`.
  - `IsHereditarilyDefinite.isDefinite`: the repair implies the code's
    premise.
- **The counterexample**:
  - `definiteMove_counterexample` holds on `cexGraph`, with every premise of
    the code: `S = cl(S)`, the invariant, `q ∉ S`, playability,
    `IsDefinite`, and no smaller playable definite customer. Its conclusion
    is `Solvable` and `SearchSol` at `S` together with `¬ Solvable` and
    `¬ SearchSol` at the child.
  - The positive half is an explicit closing order, `cex_solvable`.
  - The negative half is `not_solvable_of_invariant`, applied to the family
    of the 7 states reachable from the child within 6 stacks
    (`cexFamily_closed`). That family is closed under playable moves and
    misses `V`, and `decide +kernel` checks it in about 30 s.
  - `not_isHereditarilyDefinite_cex` shows that the repair rejects the
    counterexample, at `B = {2, 3, 4}`.

#### 4.2.3 Why the paper's proof cannot be patched locally

Take the natural construction, "close `q` and its free customers first, then
follow `U′`, skipping customers already closed". Its prefixes are `T ∪ X`,
and the step costs obey `new ≤ old` exactly when
`|o(q, S) ∖ O(T ∪ {c})| ≤ |X ∖ T|`. That inequality holds on every graph up to 7 customers (exhaustive) and
fails at 8 (random samples). The weaker bound
`new ≤ max(old, cost(S, q))` held on 25 M random cases at 9–12 customers.
It first fails at 14, which is also where the theorem first fails:

- On a 14-customer graph, `U′` closes `11, 9, 4, 5, …` at costs
  `4, 3, 3, 6, …`.
- The construction closes `5` at cost 7 > 6.
- There the theorem still holds, through a different solution that closes
  `q`'s new stacks early.

Submodularity shows what separates the two cases. If some `B` with
`S ⊊ B ⊊ X` and `q ∉ B` has `b(B) < b(X)`, then `B` is a strictly better
place to stand than `X`, and nothing forces a solution through `X`. The
repair excludes exactly this.

#### 4.2.4 The check

`python -m paper2.search_check --definite` takes 16 s on 30 cores and writes
`data/search_definite_check.json`. It transcribes the Lean definitions and
runs on every labelled graph on 1–6 vertices, every atlas graph on 7, and
2,000 random sparse and cover graphs on 10–13 vertices, 36,911 graphs in all.
At every free-closed `S` with the invariant, every `k` and every `q`:

| statement | cases | failures |
|---|---|---|
| `openStacks_submodular`, all pairs to 5 customers, 2,000 sampled beyond | 72,689,508 | 0 |
| `isDefinite_iff`, `closeCount_eq` | 35,666,255 | 0 |
| repair ⇔ matching form (Hall with deficiency, not in Lean) | 35,666,255 | 0 |
| repair ⇒ code premise; `open ≤ 1` ⇒ repair | 35,666,255 | 0 |
| repair sound: `P_k(S) ⇒ P_k(cl(S ∪ {q}))` | 29,086,891 | 0 |
| code rule fires (playable, `open ≤ close`) | 23,978,489 | — |
| … but the repair does not | 20,857 | — |
| … and the last solution is lost | 0 here; 1 in each pinned instance | — |

The code's rule fires without the repair in 20,857 cases on these graphs, and
never loses a solution there. A loss needs a larger instance with a specific
shape. The two pinned instances (`DEFINITE_CEX`: the Lean graph and the first
16-customer one found) lose it, and on both `decide` at the optimum still
answers correctly.

The counterexamples were found with `definite_hunt.c` and
`definite_hunt_gen.py`, which check every premise-satisfying `(S, q, k)`
exactly by dynamic programming over all `2ⁿ` sets:

- **Where losses first appear.** Under the code's premise there is no loss
  on any graph up to 9 vertices (exhaustive, 274,668 graphs at 9). There is
  none on the 88,802 connected graphs on 10 vertices with at most 14 edges.
  There are 2 among 90,000 random graphs of the generator's five families at
  10–16 vertices, both at 16 and both of the gadget's shape.
- **The gadget family.** It was built from the failed proof: a closed `s`
  whose open neighbours share one new stack with `q`. It gives 5 of 90,000,
  and 4 of 90,000 on a rerun from the committed generator.
- **Minimising.** Deleting vertices and edges while a loss remains reaches 14
  customers and 26 edges, never fewer.
- **The repair.** Under the repair and under the matching form there are
  zero losses in 2.05 G premise checks (60,000 random graphs and all 12,346
  graphs on 8 vertices). A further 9,000 gadget graphs give 272 M checks,
  also with zero losses.
- **Whole instances.** A port of the search with free moves, the cost cut,
  the definite move and the memo was run at the optimum. It found **no false
  refutation** on 600,000 random graphs of all five families at 10–18
  vertices, nor on 90,000 gadget graphs at 12–17.

So far the misfire is local: the search recovers through another branch. No
proof of that is known.

The tests are `tests/test_search_check.py`, seven new:

- a quick run;
- the Lean graph equals `DEFINITE_CEX[0]`;
- the loss on both pinned instances, including that the port's filter keeps
  `q` alone;
- the Lean certificates (the solution, the closed family, `B = {2, 3, 4}`);
- repair and matching sound and equal on every graph to 4 vertices;
- a mutation: replacing the repaired premise by the code's makes the
  checker report the repair unsound.

The 4-customer example of the literal-sequence slip in §2.2:

- edges `0–3` and `1–2`, `S = ∅`, `q = 0` (`open = close = 2`);
- `U′ = [1, 2, 0, 3]` costs 2, but `[0, 1, 2, 3]` costs 3, because `3` stays
  open while `1` and `2` are closed;
- closing `3` right after `0` fixes it.

### 4.3 The subset rule (item 09): sound as coded; the tie-break is necessary

`lean/MOSPFormalization/Search/SubsetRule.lean`, namespace
`MOSPFormalization.Search`, about 390 lines. It has no `sorry`, and its axioms
are `propext`, `Classical.choice` and `Quot.sound` only (`../paper2/axiom_check.lean`).
Customers carry a `LinearOrder`, which is the index order of the tie-break.

#### 4.3.1 Definitions

| §2.3 | Lean |
|---|---|
| `d` dominates `r`: `d ≠ r`, `o(d, S) ⊆ o(r, S)`, and `o(d, S) ≠ o(r, S)` or `d < r` | `Dominates G S d r` |
| some `d ∈ R(S) = V ∖ S` dominates `r` (dominators range over all of `R(S)`, `Q` included) | `IsSubsetDominated G S r` |
| the cost cut `[c ∈ K : cost(S, c) ≤ k]` | `playable G k S K` |
| the survivors, and the rule with its all-dominated fallback | `subsetKept G S P`, `subsetFilter G S P` |
| the code's order, `definite_move → subset_rule`: the least `q ∈ P` meeting a premise `D`, alone, else the subset filter | `definiteThenSubset G D S P` |
| that filter at node `(S, Q)`, candidates `(V ∖ S) ∖ Q`, with `D` the code's premise / the repair | `codeFilter G k S Q` / `repairedFilter G k S Q` |
| domination without the tie-break (the counterexample only) | `WeakDominates`, `weakSubsetFilter` |

`playable G k S (V ∖ S)` is the candidate list without old move, where `Q = ∅`.
`definiteThenSubset` is stated for an arbitrary premise so that one theorem
covers both premises.

#### 4.3.2 What is proved

- **The covering** (`searchSol_cl_insert_of_newlyOpened_subset`). Suppose
  `o(d, S) ⊆ o(r, S)` and `cost(S, r) ≤ k`. Then `Sol_k(S·r) → Sol_k(S·d)`.
  The statement holds for every `S` and needs no invariant or tie-break. The
  proof has four steps:
  - closing `r` opens `N[d]`, so `d ∈ S·r`
    (`mem_cl_insert_of_newlyOpened_subset`);
  - `S·d ⊆ S·r` (`cl_insert_subset_of_newlyOpened_subset`);
  - from `S·d`, closing `r` opens exactly `O(S ∪ {r})`
    (`opened_insert_cl_insert_of_newlyOpened_subset`), so it lands on `S·r`
    (`cl_insert_cl_insert_of_newlyOpened_subset`) at a cost no greater than
    `cost(S, r)`, because `S ⊆ S·d`;
  - if `r` is already in `S·d`, then `S·d = S·r`.

  `stepCost_le_of_newlyOpened_subset` shows that the dominator is playable.
- **A strict order.** `not_dominates_self` and `Dominates.trans` together
  mean the rule alone cannot cycle. `exists_undominated` says that every
  `r ∉ S` lies above an undominated `m ∉ S` with `o(m, S) ⊆ o(r, S)`. Take
  the least `m` by `(|o(m, S)|, m)`. Then one covering step reaches a
  survivor, and no chain argument is needed.
- **Node soundness on its own** (`subsetFilter_sound`). Assume `S ≠ V`,
  `¬ Sol_k(S·q)` for every `q ∈ Q`, and `Sol_k(S)`. Then some `c` in
  `subsetFilter G S (playable G k S ((V ∖ S) ∖ Q))` has `Sol_k(S·c)`. It
  holds for any `Q`, and `Q = ∅` is the rule without old move. On the way,
  `subsetKept_nonempty` shows that when a solution exists the fallback never
  fires.
- **After the definite move** (`definiteThenSubset_sound`). Suppose the
  premise `D` is sound at `S`: for every `q ∉ S`, `D q`, playability and
  `Sol_k(S)` give `Sol_k(S·q)`. Then the composition is node-sound.
  `repairedFilter_sound` instantiates this with `IsHereditarilyDefinite` at
  any node with the invariant `|O(S) ∖ S| ≤ k`, using item 08's
  `searchSol_cl_insert_of_hereditarilyDefinite`.
- **With the code's premise it is not** (`codeFilter_counterexample`). On
  item 08's `cexGraph` at `S = {2}`, `k = 6`, `Q = ∅`, `codeFilter = {0}`,
  `Sol_k(S)` holds and `Sol_k(S·0)` does not. The subset rule never runs at
  that node, so the loss is the definite move's.
- **The tie-break is necessary** (`noTieBreak_counterexample`). `tieGraph` has
  7 customers and edges `0–2, 0–3, 0–6, 1–4, 1–6, 3–6, 4–5, 4–6`. At
  `S = {2}` with `k = 3` and the invariant, the playable candidates are
  `{0, 3, 5}`:
  - `o(0, S) = o(3, S) = {3, 6}` and `o(5, S) = {4, 5}`;
  - without the tie-break, `0` and `3` dominate each other and both go;
  - `5` survives, so the fallback does not fire and the filter keeps `{5}`;
  - a solution exists from `S` (`0, 3, 1, 4, 5, 6`), and none from
    `S·5 = {2, 5}`, where no move costs `≤ 3`;
  - with the tie-break, only `3` goes and `subsetFilter = {0, 5}`.

  The paper's own form (PDF p. 5) removes `j` only when some `i < j` has
  `o(i) ⊆ o(j)`. It is a subrelation of the code's, uses the same covering,
  and is acyclic by index. It is checked here, not stated in Lean.

**What the certificate checker needs from this.** Cert step `["subset", r, d]`
checks that `r` is playable, that `d ∈ R(S)` with `d ≠ r`, and that the
tie-broken inclusion holds (Cert:617–627). That is exactly the premise of
`searchSol_cl_insert_of_newlyOpened_subset`, whose conclusion is the link
`r → d` the checker records. Cert checks the tie-break itself. Without that
check, step 5's cycle check would be the only guard, and it would reject the
twin cycle `0 → 3 → 0` of `noTieBreak_counterexample`.

#### 4.3.3 The check

`python -m paper2.search_check --subset` takes 80 s on 30 cores and writes
`data/search_subset_check.json`. It transcribes the Lean definitions.

- **Graphs.** Every labelled graph on 1–6 vertices, checked at every set `T`,
  not only at states. Every atlas graph on 7, and 1,500 random sparse and
  cover graphs on 10–13, checked at the search's states (free-closed, with
  the invariant). 2,000 gadget graphs on 12–16, built from the definite
  move's gadget with the rule's twist and randomly relabelled so that the
  tie-break cannot see the construction, checked at `k ∈ {opt − 1, opt,
  opt + 1}`. The pinned counterexamples of items 08 and 09.
- **Node checks.** Every node with a solution, over the item 06 families `Q`
  of genuinely refuted children.

| statement | cases | failures |
|---|---|---|
| pair facts: `d ∈ S·r`, `S·d ⊆ S·r`, `cost(S, d) ≤ cost(S, r)` | 836,775,009 | 0 |
| the covering `Sol_k(S·r) ⇒ Sol_k(S·d)`, `r` playable | 533,196,647 | 0 |
| `Dominates` irreflexive and transitive (≤ 6 vertices) | 183,565,518 triples | 0 |
| `exists_undominated` | 78,372,969 | 0 |
| the Lean filter = the item 06 port of the code, with and without the definite move, `Q = ∅` | 12,596,190 nodes | 0 |
| `subsetKept_nonempty`, `subsetFilter_sound`, `repairedFilter_sound`, the paper's form | 8,517,471 nodes each | 0 |
| no tie-break: the last solution lost | 4,730 nodes | — |
| the code's `definite → subset` loses it | 0 here; 11 `Q`-nodes on each pinned definite counterexample | — |

The form without the tie-break loses nothing on any graph with ≤ 6 vertices.
Its first losses are at 7 vertices. The Lean graph was found among the atlas
graphs on 7 under random labellings. Removing the tie-break from the checker
(the mutation test) makes it report `fail_subset_node` and
`fail_exists_undominated` on that graph.

The tests are `tests/test_search_check.py`, five new:

- a quick run;
- every statement at every set to 4 vertices;
- the Lean graph and its certificates (`tie_solvable`, `tie_cl_insert`, the
  invariant family `{{2, 5}}`);
- the mutation;
- the code's and the repaired composition on `DEFINITE_CEX[0]`.

