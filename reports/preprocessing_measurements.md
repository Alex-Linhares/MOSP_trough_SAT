# Contraction, Column Dedupe and Decomposition: What They Actually Buy

**Status:** measured, 2026-09-18. `mosp/preprocess.py`, wired into
`satisfiability.mosp_solver.decide_mosp`. Items 3 and 6 of
`reports/chu_stuckey_plan.md` §7.

*Every `ub` below is the cached upper bound on the morning of the measurement.
SP3's was 35; the customer search closed it at 34 later the same day, so a re-run
encodes at `k=34` and the SP3 rows shift slightly. The contraction room `|C| - ub`
moves with it. Nothing about the conclusions depends on that one column.*

---

## 1. What this had to decide

Item 3 exists to answer one question before the expensive item 4 is started:

> after contracting customers, do the columns collapse far enough that the
> **pattern-indexed** formula shrinks on its own — or does the relaxation driver
> (item 5) need the customer-indexed encoding (item 4) first?

The answer is that contract-then-dedupe shrinks the existing formula by 3× to
12× at the depths the driver works in, on the instances where the driver can
work at all, and that **where it does not, item 4 would not help either** — for a
reason that has nothing to do with the encoding. §4 gives that argument.

---

## 2. The measurement

For each instance: contract repeatedly by Chu & Stuckey's equation (1) ranking,
and at checkpoints drop dominated columns and encode `MOSP ≤ ub?` with the
current encoder. `ub` is the cached upper bound and is held fixed across all
rows of an instance, so the clause counts are comparable. `cl/orig` is clauses
as a fraction of the uncontracted instance's; the parenthesised figure is the
same contraction **without** the column dedupe, which isolates what dedupe adds.

| instance | ub | stage | \|C\| | m | cl/orig | without dedupe |
|---|---|---|---|---|---|---|
| Random-125-125-2-1_0 | 28 | dedupe only | 125 | 121 | 0.96 | — |
| | | −24 C | 101 | 104 | 0.58 | 0.73 |
| | | −48 C | 77 | 75 | 0.27 | 0.51 |
| | | −73 C | 52 | 44 | **0.08** | 0.34 |
| Random-125-125-4-1_0 | 63 | dedupe only | 125 | 122 | 0.97 | — |
| | | −16 C | 109 | 114 | 0.74 | 0.82 |
| | | −31 C | 94 | 103 | 0.53 | 0.68 |
| | | −46 C | 79 | 94 | **0.38** | 0.55 |
| Random-125-125-6-1_0 | 84 | dedupe only | 125 | 124 | 0.99 | — |
| | | −20 C | 105 | 119 | 0.75 | 0.79 |
| | | −31 C | 94 | 116 | **0.63** | 0.69 |
| Random-125-125-10-1_0 | 107 | dedupe only | 125 | 124 | 0.99 | — |
| | | −9 C | 116 | 124 | 0.90 | 0.91 |
| | | −14 C | 111 | 123 | **0.85** | 0.86 |
| SP3 | 35 | dedupe only | 75 | 72 | 0.95 | — |
| | | −20 C | 55 | 60 | 0.52 | 0.70 |
| | | −30 C | 45 | 55 | **0.37** | 0.57 |
| SP4 | 57 | dedupe only | 100 | 97 | 0.97 | — |
| | | −22 C | 78 | 90 | 0.64 | 0.73 |
| | | −32 C | 68 | 80 | **0.47** | 0.62 |
| GP5 | 95 | dedupe only | 100 | 100 | 1.00 | — |
| | | −4 C | 96 | 100 | 0.82 | 0.82 |

**The `|C| = ub` rows are excluded from this table and must be.** At that depth
the encoder drops the cardinality constraint outright — `encoding.py` posts it
only `if len(open_lits) > k` — because at most `|C|` stacks can be open at once.
The formula becomes trivially satisfiable and its clause count (0.01 to 0.36)
measures nothing. The driver's `while |C| > ub: merge_one` loop lands exactly
there, which is not a bug in the driver: that endpoint is where it starts
*unmerging*, and the rows above are the depths it then works in.

Two things read off the table:

- **Column dedupe alone is worthless** — 0.95 to 1.00 — and does nothing at all
  on dense instances. It only becomes productive once contraction has made
  columns coincide, which is why it is measured with contraction and not before.
- **Contraction does most of the work through `|C|`, dedupe roughly halves what
  remains** on the sparse instances (0.08 against 0.34; 0.37 against 0.57), and
  contributes almost nothing at density ≥ 6 (0.63 against 0.69, 0.85 against
  0.86).

---

## 3. Where preprocessing fires at all

Over the 6,376 instances in `benchmarks/instances`:

| reduction | instances where it fires | effect |
|---|---|---|
| pattern dominance | 3,409 (53%) | 17,699 columns removed in total |
| component decomposition | 154 (2.4%) | mostly SCOOP and Warwick |

Restricted to the 148 instances whose optimality was open when this was measured
— the ones that mattered, and now 35 after the customer-search sweep — the
rates are 93 for dominance (348 columns, under 3% of their width) and **zero**
for decomposition. That zero is not an accident of our corpus: Chu & Stuckey
(2009) say they discard decomposable instances from their generator's output to
keep the benchmark honest, so their absence there is by construction.

Both are now applied on every SAT call, in `decide_mosp`, used by the solver's
binary search and by `benchmarks/ratchet.py` alike. Both preserve the optimum,
so an UNSAT from a reduced instance refutes the original and the provenance
recorded stays truthful. The gain on the hard corpus is a few percent of the
formula; the reason to wire it in anyway is that it costs milliseconds, it is
the only path by which a decomposable instance would ever be split, and item 5
will produce contracted instances where dominance stops being marginal.

---

## 4. The answer to item 3's question, and what it implies for item 4

Item 4's stated payoff (`chu_stuckey_plan.md` §1) is that contraction cuts `|C|`
while leaving `m` untouched, so a customer-indexed encoding shrinks where a
pattern-indexed one does not — "125 customers down to 60 is a 4× cut in
variables on the dimension the search actually ranges over".

That argument is conditional on the contraction room `|C| − ub`, and the room is
not there at high density:

| instance | \|C\| | ub | contraction room |
|---|---|---|---|
| Random-125-125-2-1_0 | 125 | 28 | 97 (78%) |
| Random-125-125-4-1_0 | 125 | 63 | 62 (50%) |
| SP3 | 75 | 35 | 40 (53%) |
| SP4 | 100 | 57 | 43 (43%) |
| Random-125-125-6-1_0 | 125 | 84 | 41 (33%) |
| Random-125-125-10-1_0 | 125 | 107 | 18 (14%) |
| GP5 | 100 | 95 | 5 (5%) |

Down to 60 customers is available on the density-2 instance and nowhere else.
And on exactly those instances the pattern-indexed formula is already at 0.08 to
0.38 after contract-then-dedupe. So:

- **item 5 does not need item 4 first.** Build the relaxation driver on the
  current encoding.
- **item 4's marginal value over item 3 is small in the only regime where
  relaxation has room**, and in the regime where it would be a large cut — high
  density — there are 18 contractions available out of 125, so neither encoding
  gets a small instance out of it.

This does not retire item 4. It removes the argument that item 5 depends on it,
which was the argument for building it. The kill criterion stated in §7 (within
2× of the current encoding on the certified corpus) is unchanged and remains the
thing to measure if it is built.

The limitation the plan predicted is confirmed and sharpened. Relaxation removes
the most customers where our gaps are smallest, and the mechanism is now
explicit: contraction room is `|C| − ub`, our `ub/|C|` rises with density, and at
density 10 it is 0.86.

---

## 5. Validation

`tests/test_preprocess.py`, all against exhaustive enumeration rather than
against other parts of the same reasoning:

- pattern dominance preserves the optimum on 300 random instances, with the
  reduction required to have fired on more than 100 of them or the test fails as
  vacuous; its lift is checked on *every* permutation of the reduced instance;
- decomposition's optimum equals the maximum over components, and the
  concatenated ordering attains it, on 200 instances of which more than 20 must
  actually split;
- contraction relaxes — `MOSP(contracted) ≤ MOSP(original)` — over every
  adjacent pair of 200 instances, more than 500 contractions;
- contraction **refuses** a non-adjacent merge, which is the operation that
  differs from it by one predicate and breaks the bound (17 violations in 1,044
  in `chu_stuckey_plan.md` §0.2);
- equation (1)'s scores match their definition computed independently.

`tests/test_mosp_sat.py` checks the wiring rather than the reductions: that
`decide_mosp` flips from unsat to sat exactly at the brute-force optimum, that
its witness achieves the `k` it was asked for, and that it handles both a
decomposable instance and a product nobody needs.
