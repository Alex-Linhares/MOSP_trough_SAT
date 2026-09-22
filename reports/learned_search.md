# Putting the learned policy inside the solver, not beside it

*2026-09-22. Code: `learning/guided_search.py`, `learning/descent_bench.py`,
`satisfiability/race.py`, `benchmarks/race_sweep.py`.*

`reports/learning.md` established that a policy trained on the certified
witnesses makes a better *upper bound* than anything else here. This report asks
the next question: does it make the solver **certify** faster? Three places it
could enter, measured separately, because they turned out to have three
different answers.

Throughout: the corpus is closed, so there is no instance left to win. The
currency is nodes and seconds to re-prove what is already proved.

**Summary: all three are negative, and the third overturns a premise.** Learned
branching does nothing except on sparse satisfiable calls, where it halves the
nodes but can also turn 65 nodes into a timeout. A better starting bound does
not speed up certification, because the cost is the refutation and both
configurations must do it. And racing the SAT encoding against the complete
customer search pays nothing, because they are not complementary -- the customer
search won 63 of 63 decision calls, and the belief that the two fail on disjoint
instance sets turns out never to have been measured.

---

## 1. Learned branching inside the complete search

`customer_search.decide` expands the surviving candidates cheapest-first. That
is a one-step-lookahead policy, and the corpus holds 2.27M examples of what a
provably optimal closing order does at the same decision point. `decide` now
takes a `branch` hook (a permutation of the candidates the dominance rules
left), and `learning.guided_search` supplies one that scores them with the
policy.

**The hook cannot change an answer.** The cost cut, the memo and every dominance
rule are properties of the state, not of the order it is reached in, so any
permutation decides the same way — checked exhaustively in
`tests/test_learning.py` against reversed and randomly shuffled orders.

### On ordinary instances it does nothing

25 instances up to 75 customers, drawn at random from the corpus:

| call | instances | plain nodes | guided | ratio |
|---|---|---|---|---|
| sat (`k` = optimum) | 25 | 215 | 214 | 0.995 |
| unsat (`k` = optimum − 1) | 25 | 61,304 | 61,287 | 1.000 |

The node counts say why: the dominance rules have already collapsed the fan to
almost nothing by the time `branch` is called. There is no ordering decision
left to make well.

### On sparse instances the sat call halves

Sparsity is where the branching factor explodes, and it is the half of the
corpus the customer search is worst at. 14 Chu & Stuckey `Random` instances at
density 2, 400,000-node cap:

| call | instances | plain nodes | guided | ratio | win | lose | tie |
|---|---|---|---|---|---|---|---|
| sat | 9 | 40,646 | **16,065** | **0.395** | 6 | 2 | 1 |
| unsat | 8 | 187,829 | 179,649 | 0.956 | **8** | 0 | 0 |

Two readings, and they pull in opposite directions.

**The sat call is where order matters, and the policy is good at it.** 60% fewer
nodes. This is what it was trained for: the search stops at the first order that
works, and the policy's whole job is to propose orders that work.

**The refutation barely moves, but it never loses.** 4% fewer nodes, on 8 of 8.
A refutation exhausts the space, so its node count should be order-independent —
the 4% is the `old_move` rule, whose pruning depends on what an ancestor already
searched. Small, consistent, and not worth anything on its own.

**The variance is severe and the table hides it.** Two instances are excluded
because one run hit the cap and the other did not, and they are the two largest
effects in the sample, in opposite directions:

| instance | plain | guided |
|---|---|---|
| `Random-100-100-2-5_0` | capped at 400,001 | **50,117** |
| `Random-100-100-2-3_0` | **65** | capped at 400,001 |

A policy that turns 65 nodes into a timeout is not a policy to trust alone. What
this argues for is running both orders, which is the same argument §3 makes
about running both procedures.

### So: do not port it to C

`decide` runs in C by default, about 120× faster, and the C cannot call back
into Python. A per-node model call would have to be reimplemented natively to be
worth anything, and the case for that work is: no effect on ordinary instances,
a real effect on sparse sat calls, and a tail that can be catastrophic. That is
not enough. The measurement exists so the decision is on the record rather than
on intuition.

---

## 2. Starting the descent from a better bound

`customer_search.solve` descends `k` from an upper bound until a refutation
lands, so every stack the starting bound saves is one whole `decide` call the
descent never makes. `solve` now takes `upper_strategy`, and `learned+cs-dfs`
starts strictly lower than the `cs-dfs` default on 709 of the 6,376 corpus
instances.

Those 709 are the only instances where the change can do anything, so the
benchmark draws from exactly them rather than from the corpus at large --
pooling in the thousands where the two bounds agree would dilute any effect to
nothing. 50 of them, re-certified from scratch under both:

| | seconds | nodes |
|---|---|---|
| `cs-dfs` | 4.6 | 3,726,211 |
| `learned+cs-dfs` | 4.4 | 3,722,029 |

48 certified under both, ratio 0.955, median speedup 0.97x, faster on 16 and
slower on 27. That is noise with a slight adverse bias, and the bias is
explicable: the policy costs about 2 ms per call, which is more than the whole
descent on most of these.

**The negative result is structural, not a sampling accident.** A descent's cost
is dominated by the refutation at `optimum - 1`, and *both* configurations have
to do that one. What a lower start skips is the satisfiable calls above the
optimum, which are the cheap ones -- they succeed. So the saving is real and
worth almost nothing.

This is the sharpest thing the learning work has produced about its own limits:
**the 709 improved upper bounds buy bound quality, not proving time.** A better
upper bound helps a ratchet, which only ever asks satisfiable questions, and it
is what `reports/learning.md` measures. It does not help a procedure whose cost
is the proof.

---

## 3. Racing the two decision procedures

`satisfiability/race.py` runs the SAT encoding and the complete customer search
at once on separate cores and takes the first definitive answer. The premise, from
`reports/customer_search.md` §1, was that the two "have opposite profiles" --
SAT failing on dense instances, the customer search on sparse ones -- so that
whichever a caller picked, picking wrong cost the whole budget.

**The premise does not survive measurement.** 20 Chu & Stuckey `Random`
instances, 10 at density 2 and 10 at density 8, 60-second budget, SAT running on
`kissat404` -- the backend `benchmarks/solver_portfolio.py` measured at 6/6 on
hard refutations, the strongest one here:

| | instances | csearch certified | SAT certified | race certified | calls won by SAT |
|---|---|---|---|---|---|
| density 2 | 10 | 8 | **0** | 8 | **0 / 33** |
| density 8 | 10 | 10 | **0** | 10 | **0 / 30** |

Sixty-three decision calls, and the SAT encoding won none of them. Where the
customer search certifies at all it certifies in 0.0-13 s; the SAT path does not
return inside a minute on any of the twenty. The race pays about 4% for the
second process (7.1 s to 7.4 s, 20.2 s to 21.0 s) and arrives exactly where
`csearch` alone would have.

### What the records say, once the two paths are told apart

The corpus history says the same thing, and it took a correction to see it. A
first pass compared "SAT times" from `benchmarks/results/sat_*.csv` against
`csearch` ledger times and found SAT winning by up to 931x. Those files carry
`pathwidth` columns: they are the **pathwidth** path, computing
`pathwidth(G_c) + 1`, which this project records as an upper bound that
overcounts on sparse instances. A different question, and not a comparable one.
Restricted to the direct-MOSP runs:

- 6,226 instances have a `status=solved` row from the direct SAT path;
- 147 instances have a `csearch` ledger row;
- **the overlap is zero.**

`csearch` was only ever pointed at what SAT had already failed to solve, so the
two have no head-to-head record at all -- which is why the claim of opposite
profiles was never tested, only inherited.

### Where they do both fail

At 125x125 density 2 neither returns. The ledger has `csearch` taking 41,197 s
(11.4 hours) on `Random-125-125-2-5_0`, and the SAT sweeps time out on it at
3,600 s. In the sweep above, `Random-125-125-2-1_0` and `-2-4_0` exhaust the
60-second budget under both. So the hardest corner is hard for both procedures,
not for one of them.

### So the portfolio does not pay, and that is the finding

A portfolio's value is the variance between its members, and here there is none
to harvest: one procedure dominates on everything measured. `satisfiability/race.py`
stays, because it is the harness that establishes this and the natural place to
add a third procedure that *does* differ -- but nothing should be routed through
it today.

The corollary is worth more than the portfolio was: **the SAT path is not the
right default for the hard instances, and it was.** `benchmarks.solve_parallel`
sweeps with SAT; `benchmarks.csearch` exists as the thing you reach for when
that fails. On this evidence the order should be the other way round.

---

## 4. What the three answers add up to

Three places the learned policy or a portfolio could enter the certification
path, and three negatives -- but not the same negative:

| where | effect | why |
|---|---|---|
| branching inside `decide` | nothing on ordinary instances; **-60% nodes** on sparse sat calls, with a catastrophic tail | the dominance rules leave nothing to order, except where the branching factor is large |
| starting bound for the descent | none | the cost is the refutation, which a lower start does not skip |
| racing SAT against the customer search | none, minus 4% overhead | the two are not complementary; one dominates |

The unifying observation is that **`reports/learning.md`'s gains were gains in
bound quality, and bound quality is not what the remaining hard instances are
short of.** That was already written down -- `reports/lower_bounds.md` §1 says
the refutation at `k-1` dominates runtime, and `chu_stuckey_plan.md` §2 predicted
the gap on these instances is a lower-bound problem no upper bound will close.
This is that prediction meeting a learned upper bound and holding.

What would follow the evidence instead:

1. **Reverse the default.** `benchmarks.solve_parallel` sweeps with SAT and
   `benchmarks.csearch` is the fallback. On 63 of 63 decision calls across both
   density extremes the customer search won, and the two paths have no
   head-to-head record anywhere in the corpus history. The order should be the
   other way round, and the sweep that establishes it is one command.
2. **Learn a *lower* bound signal, not an upper one.** §1 of
   `reports/learning.md` found that instance structure alone predicts the
   optimum better than `_lower_bound` does -- exact on 71.2% against 65.3%. A
   prediction is not a bound and can never be one, but a predictor that accurate
   is evidence that a *provable* bound is being left on the table, and the lower
   bound is what the hard instances are short of.
3. **Leave the race in place, unused.** It is the harness that settled the
   portfolio question and the place a genuinely different third procedure would
   plug in. Nothing should route through it today.
