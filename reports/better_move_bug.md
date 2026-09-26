# A false refutation in `better_move`

*2026-09-23. Found while profiling the C inner loop, which is not where anyone
was looking for it.*

## 1. What it is

Chu & Stuckey's Theorem 2 — "better move" — prunes a candidate `r` when some
other candidate `q` dominates it: if `S ++ [q]` and `S ++ [r, q]` are both
playable and `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})`, then any solution extending
`S ++ [r]` has one extending `S ++ [q]`, so `r` can go.

The C let **any** candidate dominate any other. So the relation could cycle: `q`
dominates `r` *and* `r` dominates `q`. Both are then discarded, and the argument
that justified each discard — "the other one covers it" — is satisfied by a
candidate that is no longer there. The branch holding the solution goes with
them, and the search answers **unsat to a satisfiable question**.

That is the one failure this project's verification chain cannot see. A false
refutation certifies an optimum one stack too high, and the witness at that
value really does achieve it, so `mosp/certify.py` confirms it happily.

## 2. The instance

`Warwick 1730: balanced orders, 3 orders per product`, 30×30, true optimum 9 —
agreed by the SAT encoding, by the cached value, and by the Python reference.

| `better_move_dominators` | memo | `old_move` | C answer at `k = 9` |
|---|---|---|---|
| 0 | on | on | **unsat** — false |
| 0 | on | off | **unsat** — false |
| 0 | off | off | **unsat** — false |
| 0 | off | on | sat |
| 1, 2, 4 | any | any | sat |

`better_move_dominators = 0` means "every candidate may be a dominator", which
makes a cycle almost certain. A small limit only makes it unlikely, never
impossible — nothing in the old code prevented the cycle, it just needed both
members to fall inside the first few entries.

**`benchmarks/csearch.py` passes `better_move_dominators=0`.**

## 3. The fix

Only an *earlier* candidate may dominate a later one:

```c
for (int qi = 0; qi < limit && qi < ri && !pruned; qi++) {
```

That makes the relation a forest. The first candidate is never pruned, and
whatever covers `r` is itself covered by something earlier, transitively — so a
survivor always remains and covers everything discarded.

Verified: zero wrong answers across 24 flag combinations on `Warwick 1730`, and
**93,472 decisions over 1,500 random instances with zero mismatches** against
the `better_move = False` reference.

### A wrong diagnosis first

The initial theory was in-place aliasing: the survivor compaction writes
`who[kept]` while the dominator loop reads `who[qi]`, so once anything is pruned
the loop reads slots that have been overwritten. That is a real defect and it was
fixed — but the fix made the symptom **worse**, turning a configuration that had
been correct (`dom=0, memo=off, old_move=on`) into a false refutation. That is
what ruled the theory out and pointed at the cycle. The non-aliasing rewrite is
kept regardless, because reading dominators out of an array being overwritten is
indefensible whether or not it was this bug.

## 3a. Chu & Stuckey are not wrong; we misread them

Theorem 2, as stated in the paper:

> Suppose `S ++ [q]` and `S ++ [r, q]` are playable and
> `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})`, then if `U' = S ++ [r] ++ R` is a
> solution there exists a solution `U = S ++ [q] ++ R'`.

That is a **pairwise conditional**: if a solution runs through `r`, one runs
through `q`. It licenses discarding `r` *while `q` is kept*, and says nothing
that permits discarding both. The paper then makes the usage explicit:

> Although "better move" seems weaker than "definite move" as it **prunes only
> one branch at a time** rather than all branches but one, it is actually a
> generalisation…

One branch at a time is exactly the discipline under which a cycle cannot arise.
`definite_move` is the rule that keeps one candidate and drops all the others;
we gave `better_move` those sweeping semantics, applying it as a simultaneous
filter over every pair in a single pass. Each discard was individually justified
by a candidate that another discard had just removed.

**The codebase already knew this hazard.** `subset_rule` carries an index
tie-break, in both the C and the Python reference:

```c
if ((other & ~own) == 0 && (other != own || d < c)) dominated = 1;
```

`(other != own || d < c)` exists for one reason: to stop both members of an
*equal* pair being discarded. The symmetric case of precisely this problem,
handled deliberately, in two languages — and missed in the one rule that had no
second language to be handled in.

## 4. Why it survived

`tests/test_native.py` checks the C against the Python reference, exhaustively,
and that is the project's main guard on the search. But **`better_move` exists
only in the C** — the Python has no implementation of Theorem 2 — so the
comparison never covered it. It was the one rule with nothing to check it
against, and it was the one rule that was wrong.

The invariant that catches it immediately is one line: *a dominance rule may
change the cost of a search, never its answer.* That test now exists
(`tests/test_customer_search.py`), over random instances × every `k` × four
dominator settings × memo on and off, plus the instance that exposed it.

## 5. What it cost the corpus

55 entries were certified by `csearch` on instances sparse enough for
`better_move` to run. Re-verified with the fixed code by asking whether
`value - 1` is really refutable:

| | |
|---|---|
| re-certified | **41** |
| **wrong** | **1** — `Random-100-100-2-2_0`, certified at 21; true optimum **20** |
| unresolved within a 900 s budget | **13** |

`SP3` (34) and `SP4` (53) re-certify, and match the published optima of Frinhani
et al. independently.

The 13 have had their optimality claim **withdrawn** — provenance demoted to
`solution`. Their values stand as verified upper bounds; what is gone is the
proof. They have no independent certification to fall back on: the direct SAT
path has solved rows for 6,226 instances and `csearch` for 147, and **the
overlap is zero**, so `csearch` was the only thing that ever proved them.

`Random-100-100-2-2_0` has been corrected: `k = 19` refutes and `k = 20` is
satisfiable with a witness simulating to 20, so it is certified again at the
right value. It had been recorded as optimal at 21 since the sweep that closed
the corpus.

The corpus is **6,363 of 6,376 certified**, not closed.

## 6. What this says about the method

Three things worth keeping.

**The guard was real but had a hole exactly where the unique code was.** Testing
the C against the Python is an excellent discipline, and it silently covers
nothing in the parts that exist only in the C. Any rule implemented on one side
only needs an invariant of its own — and the acyclicity precaution this rule
needed was already written, correctly, in the rule right next to it.

**The bug was found by profiling, not by verification.** It surfaced because a
performance experiment ran `solve` twice with different flags and the two
answers disagreed. Nothing in the test suite, the corpus audit, or the witness
verification had any chance of noticing it, because every one of them checks
that a claimed value is *achievable* and none checks that a refutation is *sound*.

**A refutation is the half of an optimality claim nobody can check.** The README
already said so, as a limitation of the customer search having no proof object.
This is what that limitation looks like when it bites.

## 7. The second one, 2026-09-26: two bugs, neither the diagnosed one

`reports/ml_nature.md` §15 ran the differential harness and found the C with
`better_move` on answering `unsat` at the optimum on 56 of 17,527 sparse
instances at 10–40 customers (88 false answers), and diagnosed a cross-rule
cycle: `better_move` discards `r` citing `q`, then `subset_rule` discards `q`
citing `r`. That cycle is real — it is the whole story on the 10 × 13 minimal
instance — but the section's control, "`better_move` alone is sound on all
88", was vacuous: the filter's early exit read
`if (!subset_rule && !definite_move) goto sorted;`, so with the other two
rules off `better_move` never ran (node counts identical to `better_move=False`,
7 / 6 / 183 on the three test instances). Run genuinely alone it refutes the
17 × 9 minimal instance at its optimum of 5.

**Bug A, inside the rule.** `close(q, S ∪ {r})` was counted over every customer
not yet closed after `r`, including those `r` finishes on its own — customers
with nothing left to open, which the child node closes as free moves before
`q` is ever played. Theorem 1's proof needs stacks closed *in addition* to
those. `definite_move` and `subset_rule` never counted them (their `ids` skip
size-0 customers); `better_move`, with no Python side, did. At the root of the
17 × 9 instance, `1` pruned `2` with `closed_by = 2 ≥ opened_by = 2`, the two
being `1` itself and `8`, whose whole neighbourhood sits inside `N[2]`.

**Bug B, between rules.** As §15 said: `subset_rule` ran after `better_move`
and measured survivors against every remaining customer, discarded candidates
included.

**Bug C, the flag.** The early exit above.

### What the theorem needs in this search's cost model

The paper's open-stack count after playing a set is a function of the set;
this search closes free moves automatically, so its cost of `c` after closed
set `C` is `|O(C ∪ {c})| − |C|`, which depends on `C` and not only on
`C ∪ {c}`. Theorem 2's proof plays `q` first and `r` second, and the cost of
that second move is `|O(C) ∪ N(q) ∪ N(r)| − |fin(O(C) ∪ N(q))|`, which the
paper's playability quantity `|O(C) ∪ N(r) ∪ N(q)| − |C| − 1` bounds from
above. So the "inexact" playability check the C already made is the right one,
and making it exact — subtracting `r`'s free moves — would be wrong. Brute
force over every reachable state, every `k` and every ordered candidate pair
on 320 random sparse instances at 12–15 customers, checking the theorem's
*conclusion* (a solution through `r` implies one through `q`) by plain search:

| hypotheses | applications | conclusion fails |
|---|--:|--:|
| old C (free-after-r counted, paper playability) | 126,073,945 | **57**, every one `close = 1, old_close = 2` |
| corrected close, *exact* playability | 125,216,007 | **726** |
| corrected close, paper playability (**the fix**) | 124,110,139 | **0** |
| corrected close, exact playability + `S ++ [q, r]` playable | 125,188,900 | 0 |
| Theorem 1 as `definite_move` implements it | 17,005,993 | 0 |

On 200 instances at 5–11 customers the old hypotheses never fail
(1,579,898 applications) and the exact-playability variant fails 43 times:
the second bug needs more customers than the first.

### The fix

`satisfiability/customer_search.c`, `dominance_filter`: the early exit honours
`better_move`; `subset_rule` runs before `better_move`, over the remaining
customers, none of which anything has yet discarded, and `better_move` runs
last over the subset survivors alone, so every chain of coverings ends at a
better-move survivor (its first input is never pruned) or at a customer
outside the candidate set, which under old move is one an ancestor searched;
and `close(q, S ∪ {r})` skips customers with nothing left to open after `r`.
The Python reference has no `better_move` and its own composition
(`definite_move` then `subset_rule`) is unchanged.

Verified: the harness (`python -m learning.differential --workers 12`,
512 s) on all 43,935 certified instances at 9–40 customers, ten labellings,
both configurations: **878,580 of 878,580 `unsat` at `optimum − 1`, 878,700
of 878,700 `sat` at the optimum, 0 disagreements, 0 contradictions, 0
unknown, 0 witness failures, 0 lattice-oracle mismatches on 13,612** — against
56 / 88 before. A C-versus-Python sweep on 2,000 random instances at 6–16
customers with 1–4 products per customer, every `k`, all 16 flag combinations
× 4 dominator limits: 502,464 decision calls, 0 mismatches. The 96
configurations on the three §15 instances all agree with the reference.

### What it costs

Node counts from the same harness rows, identity labelling, `csearch`
configuration, `decide(optimum − 1)`, the 17,527 instances on which Theorem 2
is switched on: 6,642 changed, ratio (after + 1)/(before + 1) median **1.000**,
p90 **1.18**, p99 **1.80**, max **6.52** (`p1540n10_0`, 68 → 449), min 0.82;
6,381 instances cost more and 261 fewer; total nodes 6,101,183 → 6,544,638
(**+7.3%**). By size band the p90 rises from 1.00 at ≤ 10 customers to 1.28
at 31–40. Every `default` count is unchanged: 439,350 of 439,350 rows at
both `k`. Nothing above 40 customers was measured.

### Lessons, added to §6

The control that "proves" a rule sound alone must be shown to *run* the rule:
a node count equal to the rule-off count is the one-line check. And a rule
ported from a paper carries the paper's cost model with it; where this search
departs from that model (free moves close themselves), each hypothesis has to
be re-derived, not transcribed.
