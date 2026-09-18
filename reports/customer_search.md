# The Complete Customer Search: Refutations Without a SAT Solver

**Status:** implemented and measured, 2026-09-18.
`satisfiability/customer_search.py`. Item 2 of `reports/chu_stuckey_plan.md` §7,
which turned out to be a great deal more than item 2 was scoped as.

---

## 1. Why this stopped being a heuristic improvement

The plan's item 2 was "the dominance rules of §4 inside `ub_MOSP`", worth
1-2 orders of magnitude on a search that already finishes in 0.1 seconds. Table 1
of Chu & Stuckey (2009) changes what that is worth. Their *complete* search
closes the 125-customer instances at density 6, 8 and 10 in **9 s, 0.19 s and
0.02 s**. Those densities hold 94 of our 144 unproven Random instances, and our
SAT refutations do not return on them at all.

So the rules were not built into the heuristic. They were built into a complete
LOSP(k) decision procedure, which produces genuine refutations, and therefore
certified optima, with no SAT solver anywhere in the chain.

The two paths have opposite profiles, and that is the useful part:

| | SAT encoding | customer search |
|---|---|---|
| dense instances (d ≥ 6) | refutations do not return | seconds |
| sparse instances (d = 2) | refutations do not return | branching factor explodes |
| what it searches | product positions, `O(m²)` variables | customer closing orders |
| what it needs to be fast | small formula | small branching factor |

Sparsity is what the relaxation of `reports/relaxation.md` exists to repair, so
the two items compose exactly as the plan said they would — though not for the
reason it gave.

---

## 1a. The corpus sweep

`python -m benchmarks.csearch --unproven --timeout 900 --workers 20`, over the
147 instances whose optimality was open. **111 closed, in 45 minutes.**

| | proved | stacks saved |
|---|---|---|
| density 10 | **30 / 30** | 22 |
| density 8 | **29 / 31** | 31 |
| density 6 | 24 / 32 | 35 |
| density 4 | 15 / 29 | 38 |
| density 2 | 11 / 21 | 28 |
| SP and other | 2 / 4 | 10 |
| **total** | **111 / 147** | **164** |

The gradient is Chu & Stuckey's Table 1 reproduced on our corpus: everything at
density 10, almost everything at 8, and the sparse end resisting. 87 instances
also had their upper bound improved along the way, 164 stacks in total, because
a descent that fails to close still ratchets. SP4 fell from 57 to 53 — the
published optimum — without being proved.

The corpus went from 152 open files to 40 — and to 36 once four orphan
duplicates were deleted the same day, covering **35 distinct instances**, since
SP4 is stored under two names.

**Every one of the 111 was then re-verified independently**: its witness
re-simulated on the original instance, and the refutation at `value - 1` asked
again from scratch. 111 checked, 0 failed. The first twenty forked before the
guard in §4 landed, which is what prompted the pass; it is worth having for the
rest regardless, since the corpus is meant to be a published artifact and a
proof it cannot re-derive is a proof on trust.

---

## 2. The measure, and the one detail holding it up

A state is the set `S` of closed customers; `O(S) = ⋃_{c∈S} N(c)` with `N`
self-inclusive. Closing `c` costs `|O(S ∪ {c}) - S|`, counting `c` itself, which
is still open at the moment it closes. The minimum of the peak of this over all
closing orders is the true optimum — 400/400 against exhaustive search
(`chu_stuckey_plan.md` §0.1).

**Free moves are load-bearing.** A remaining customer whose whole neighbourhood
is already opened costs nothing to close, and is closed immediately rather than
branched on. This is the `open = 0` case of their Theorem 1. Without it the
measure keeps charging for stacks that are finished, and — the part that is easy
to miss — the `close` counts that Theorems 1 and 2 are *stated in terms of*
become wrong, because "the stacks that closing `q` releases" only releases them
if something actually closes them. The two halves have to be implemented
together or neither is right.

This showed up concretely. An early version returned a closing order whose
induced product sequence used 3 stacks where the search had scored it at 2, and
the cause was an index mapping in the relaxation driver rather than the measure —
but chasing it produced the guard in §4 that now protects every proof.

---

## 3. The rules, and which were not implemented

| rule | status | why |
|---|---|---|
| subset, their §2 | implemented | `o(cᵢ,S) ⊆ o(cⱼ,S)` discards `cⱼ` |
| Theorem 1, definite move | implemented | `close(q,S) ≥ open(q,S)` discards every sibling |
| Theorem 3, old move | implemented | `Q(S)`, maintained in `O(|C|)` per node |
| Theorem 2, better move | **not implemented** | see below |

**Theorem 2 is the one left out.** Its condition ranges over *pairs* of
candidates — `close(q, S ∪ {r}) ≥ open(q, S ∪ {r})` for each `r` — and each
`close` is itself a pass over the remaining customers, so it is `O(|R|³)` per
node against `O(|R|²)` for Theorem 1, which is its special case (the `q` that
beats every `r` at once). At `|R| = 125` that is two million operations per node
in Python. It is the right thing to add in a compiled implementation and the
wrong thing to add here.

**Old move and the memo do not compose**, which is a soundness point rather than
a performance one. A failure found with old-move pruning depends on which
branches an *ancestor* had already searched: it is a property of the path, not
of the state `S`. Recording it in a memo keyed on `S` alone would refute states
that are not refuted. Chu & Stuckey report nogood recording worth about 1.0×
once old move is on, so they are alternatives rather than a loss; `decide` raises
if both are requested.

---

## 3a. What each rule is actually worth here

SP3's refutation at `k = 33`, the call that settles the instance. Each
configuration answers the same question; "unknown" means the 600-second cutoff
came first.

| configuration | result | nodes | time | nodes/s |
|---|---|---|---|---|
| memo only, no dominance | unsat | 8,900,666 | 160.5 s | 55,000 |
| subset + definite, no memo | **unknown** | 11,993,088 | 600 s | 20,000 |
| subset + definite + memo *(default)* | unsat | 3,942,231 | 134.3 s | 29,000 |
| subset + definite + old move, no memo | unsat | 2,873,961 | 153.6 s | 19,000 |

Three readings, none of them the one the plan projected:

- **The memo is what makes this instance land.** Without it the dominance rules
  burn 12 million nodes and do not finish. With it and nothing else, the
  refutation takes 160 seconds.
- **The dominance rules cut nodes 2.3× and time 1.2×.** They cost about twice as
  much per node as they save in nodes visited. The plan expected 1-2 orders of
  magnitude from their Table 4(a); that is a measurement of a C++ search where
  the per-node arithmetic is nearly free, and it does not transfer to a Python
  one. This is the same category of error as reading their Table 1 timings as
  though they were ours.
- **Old move prunes hardest and still loses on the clock** — 27% fewer nodes
  than the default, 14% more time, because maintaining `Q(S)` costs per node
  what it saves in branches. It stays off by default and stays implemented: its
  advantage is in nodes, so it should win where the memo degrades, which is
  exactly the large sparse instances the default cannot finish. That is worth a
  measurement of its own and has not had one.

---

## 4. What makes a proof a proof

A refutation at `k` says the optimum is above `k`. Claiming it *is* `k + 1`
additionally needs a witness that achieves `k + 1`, and the witness is only ever
trusted at the value it simulates to on the original instance, via
`mosp.verify.max_open_stacks`. If the descent holds a witness at `k + 2` when
the refutation at `k` lands, `solve` reports **no proof** rather than assuming
the two meet.

This matters because the search scores closing orders while the corpus records
product sequences, and the construction between them is the one piece of the
chain justified by measurement (`§0.1`, 400/400) rather than by a proof in this
repository. Four formalisations of this same material have already been wrong
here. The guard costs one comparison and removes the whole class.

---

## 5. Validation

`tests/test_customer_search.py`, plus two larger runs kept out of the suite for
time.

- **Every rule combination, against exhaustive search.** The point where the
  answer flips from unsat to sat must be the brute-force optimum, with each rule
  varied one at a time — including the two configurations that use old move.
  400 instances in the wider run, 0 disagreements; 60 per combination in the
  suite.
- **700 instances beyond brute force, against the SAT solver.** Sizes to 16×14,
  where enumeration is hopeless and the SAT encoding is exact and shares no code
  with this search. 0 disagreements.
- **All eleven published optima** (GP1-8, SP2-4) reproduce.
- **A budget abort returns "unknown", never "unsat"**, and is kept out of the
  memo, where it would otherwise turn one timeout into a permanent false
  refutation.
- **The restricted variant may never claim a refutation.** It discards branches
  it cannot justify, so exhausting what remains proves nothing, and the type
  enforces that.
