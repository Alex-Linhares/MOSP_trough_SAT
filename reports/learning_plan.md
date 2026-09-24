# The learning plan, revised: measurement, not machinery

*2026-09-24. Supersedes the "Next, in order" list in `reports/learning.md` §4
and the forward-looking half of `reports/learned_search.md` §4.*

## 1. What the first plan assumed, and what is now measured

The premise was a chain: **corpus → model → better answers → better solver.**
The first two links hold. The third does not, and it was tested three separate
ways with three different negatives:

| attempt | result | why it failed |
|---|---|---|
| learned upper bound (`learned+cs-dfs`) | better on 709 instances, 40% faster, **shortens no proof** | the descent's cost is the refutation at `optimum-1`; a better upper bound only removes the cheap satisfiable calls above it |
| expansion lower bound at the root | mean gap 31.4 → 5.2, changes the search by **2s out of 7,629** | a floor below the optimum leaves the `k` sequence identical; when tight it skips a 0.2s refutation for 28s of work |
| per-node expansion pruning | cuts **0.05%** of nodes | Chu & Stuckey's dominance rules collapse the node before any learned quantity is consulted |

The cost is `627 million nodes × 0.65 µs`. That is throughput. No amount of
answer quality reaches it, and the plan should stop trying.

## 2. What the work actually produced

Every real contribution of the learning folder has been a **finding about the
solver**, not a component of it:

- the feature table showed the **clique bound has never once helped** in 6,376
  instances, while `_lower_bound` grants it a 5-second budget per call;
- the prediction study showed **structure predicts the optimum better than our
  proved bound does** (exact on 71.2% against 65.3%), which is what sent us
  looking for the expansion bound;
- the corpus-sweep harness, built to score a learned strategy, established that
  **the SAT path was the wrong default** — 63/63 and 49/49 decision calls to the
  customer search;
- and `learning/descent_bench.py`, a performance experiment, is what found the
  **false-refutation bug** in `better_move`, by running the same descent twice
  with different flags and getting two different answers.

That last one is worth dwelling on. Nothing in the test suite, the corpus audit
or witness verification could have found it: they all confirm a value is
*achievable*, and none checks that a refutation is *sound*. A measurement
harness found a correctness bug that the verification machinery was structurally
blind to.

**So the reframe is not a consolation prize.** Measurement is where this has
paid, every time.

## 3. What to seek to know

Four questions, ranked by how much the evidence supports them.

### 3.1 Which configuration should run on this instance?

The strongest candidate, because the effects are **multiplicative** and the
failure mode is benign — a wrong configuration costs time, never correctness.

| choice | measured spread |
|---|---|
| memo on/off | 3–7× fewer nodes on sparse with `better_move`; a 15–18% **loss** on dense |
| `better_move` | 28× node reduction on `Random-100-50-4-1_0`; worthless on dense |
| `better_move_dominators` 0 vs 4 | 10× on the calibration set |
| csearch vs SAT | 63/63 and 49/49 decision calls |

And the selector deciding the 28× choice today is, in full:

```python
return float(instance.matrix.sum()) / instance.n_customers <= 5.0
```

One hand-picked threshold on one statistic. We have 6,376 instances to generate
labels on and a feature pipeline already built.

**Build:** a configuration × instance benchmark (nodes and seconds per cell),
then a selector over the existing features. **Kill criterion:** if it does not
beat the hand-tuned threshold by ≥20% of total solve time on instances grouped
out by source file, drop it — the threshold is free and already written.

### 3.2 How long will this instance take?

We are running **five-day budgets blind**. Two instances finished at 10.2 and
13.3 hours; six have been going for over a day with no way to tell whether they
need another hour or another month. Every sweep this project runs allocates
budget uniformly because it has no alternative.

**Build:** a runtime/node-count predictor from instance features, trained on the
timings already in the ledger and the sweep CSVs. **Kill criterion:** if
budget allocated by predicted difficulty does not close more instances per
core-hour than uniform allocation on a held-out sweep, drop it.

### 3.3 Where are two sound configurations most likely to disagree?

The verification gap this week exposed. **A differential harness across
configurations should exist regardless of machine learning** — it is the only
tool the project has that can see an unsound refutation, and it has already
found one. Build it first as plain random differential testing.

ML's role is secondary and clearly bounded: predict which instances are most
likely to expose a disagreement, so the search for bugs is not uniform over a
corpus that is 93% easy. **Kill criterion:** if guided selection does not find
disagreements at a higher rate than random sampling, use random sampling — and
keep the harness either way.

### 3.4 What is the optimum where we can never certify?

A 125×125 refutation costs 60 billion nodes. 200×200 is permanently out of
reach, and will stay so. A predictor with **calibrated uncertainty** is the only
way to say anything at all about that regime.

This is the one place a prediction is the product rather than a step toward one,
and it must be labelled as such every time it is quoted. **Kill criterion:**
if the intervals do not cover at their stated rate on held-out certified
instances, the model says nothing and should say nothing.

## 4. What is closed

Do not rebuild these. Each is measured, reported, and has a report explaining
the mechanism rather than just the outcome:

- **learned upper bounds** as a route to faster solving (`reports/learned_search.md` §2)
- **learned or learned-adjacent lower bounds** as a route to faster solving (`reports/expansion_bound.md` §6)
- **learned branching inside the search** (`reports/expansion_bound.md` §7)

The artefacts stay, behind off-by-default flags, with their numbers attached.
`learned+cs-dfs` remains the best upper-bound heuristic here and is the right
thing to run if the corpus ever re-opens with instances a ratchet must attack.

## 5. The rule that does not change

**A prediction is never a bound.** `_lower_bound` is a correctness dependency: a
bound one point above the true optimum makes the search start above it and
return a wrong answer whose witness verifies. Nothing learned may enter that
path. Orderings a model proposes are checked by `max_open_stacks` like any
other, which is what makes §3.1 safe and §3.4 honest.

## 6. One premise that was wrong on its own terms

`reports/learning.md` opens by saying the corpus is unusual because its labels
are proofs rather than a solver's best effort — supervised learning with no
label noise.

**One of those labels was wrong.** `Random-100-100-2-2_0` was recorded as
optimal at 21; the optimum is 20. It was certified by a refutation that a bug
made false, and nothing downstream could detect it.

The lesson generalises past this corpus: a label that comes with a proof is only
as good as the proof checker, and this project's checker can verify achievability
but not refutation. Until item 7's proof objects exist, "certified" means "our
search said so", and our search has been wrong once that we know of.
