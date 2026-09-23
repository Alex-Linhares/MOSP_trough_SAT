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
