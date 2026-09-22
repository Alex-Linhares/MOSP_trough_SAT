# Learning from the solved instances — in plain English

## The situation

This project has solved 6,376 scheduling puzzles and *proved* that each answer
is the best possible. Each solved puzzle comes with the schedule that achieves
it. That is a large pile of worked examples with the answers in the back of the
book, and this folder asks a simple question: can a machine learning model look
at the pile and pick up anything we did not already know?

The puzzle, briefly. A factory has a list of products to make and a list of
customers, each waiting on some subset of those products. A customer's "stack"
opens when the first product they want gets made and closes when the last one
does. Make the products in a bad order and dozens of stacks sit open at once,
each taking floor space. The question is what order to make things in so that
the worst moment is as good as it can be. It is NP-hard, which is the formal way
of saying nobody knows a shortcut.

Everything in this folder is trained on those 6,376 worked examples.

## Why the pile is unusual

Normally, when people train a model on a hard optimization problem, the training
answers came from a solver that was given a time limit and wrote down whatever
it had when the clock ran out. Some of those answers are right and some are the
solver giving up, and the model has no way to tell which is which — so it learns
the solver's bad habits alongside the actual problem.

Ours are different. Every answer here was *proved* optimal: the solver showed
both that the answer is achievable and that nothing better exists. The model is
learning from correct answers only. That is the main reason this folder is worth
having.

## The one safety rule

There are two ways a model could feed into the solver, and only one is safe.

**Unsafe: letting a model guess how good the answer will be.** The solver starts
its search from a "lower bound" — a proved statement that the answer is at least
such-and-such. If that number is ever too high by even one, the solver starts
its search above the true answer, finds something that works there, and reports
it as optimal. The schedule it hands back genuinely achieves the number it
claims, so checking the schedule does *not* catch the error. A guess dressed up
as a bound would break the solver silently. We don't do it.

**Safe: letting a model propose a schedule.** A schedule can be simulated
directly — run the products in that order, count the stacks, done. If the model
proposes a bad schedule we find out immediately and we've lost a little quality
and nothing else. There is no way for a bad model to produce a wrong *answer*
this way, only a mediocre one.

So: the model in `policy.py`, which proposes schedules, has a route into the
solver. The study in `study_optimum.py`, which predicts numbers, does not.

## What we found

Full numbers and method in [`reports/learning.md`](../reports/learning.md). Four
findings, in plain terms.

### 1. The shape of a puzzle says more about its answer than our proof does

Feed a model nothing but structural facts about an instance — how many
customers, how many products, how the overlaps between customers are
distributed — and it lands on the exact answer 71% of the time on puzzles it has
never seen. Our best *proved* lower bound is exact 65% of the time.

This does not mean the model should replace the bound. The bound is a proof and
the model is a guess, and a guess cannot be used where a proof is required. What
it means is that the information needed to pin down the answer is sitting in the
instance's structure, and our proof technique is not yet extracting all of it.
That is a hint about where to look for a better bound, not a replacement for one.

### 2. A model taught by watching our solved schedules beats the textbook rule

Every method for building a schedule answers the same question over and over:
given what's already finished, what should come next? The literature's standard
answer is a rule called MCN — roughly "close out whichever customer is cheapest
to close right now."

Our 6,376 proved-optimal schedules contain 2.27 million such decisions, each one
made by a method that demonstrably reached the best possible answer. We trained a
model to imitate those decisions and then used it as a schedule builder.

Against MCN, on puzzles held out from training, it overshoots the best possible
answer by 0.46 stacks on average versus MCN's 1.63, and nails the optimum 75% of
the time versus 51%. Same cost, better answers.

### 3. The real win: it makes an existing search twice as accurate

The project already has a stronger method than MCN — a depth-first search from
Chu & Stuckey's 2009 paper. It takes a starting schedule as a hint, and the
better the hint, the more of the search tree it can skip.

Give it our learned schedule as the hint instead of MCN's, and run that over
**every one of the 6,376 puzzles** — each one scored by a model that was never
shown anything from its own generator setting:

| method | average overshoot | exact | worst case | total stacks over |
|---|---|---|---|---|
| MCN (textbook rule) | 1.63 | 51% | +27 | — |
| our learned builder | 0.38 | 78% | +34 | 2,439 |
| the existing search | 0.24 | 85% | +10 | 1,538 |
| **the search, with our hint** | **0.11** | **93%** | **+8** | **670** |

Put head to head against the existing search on the same puzzles, the hinted
version is **better on 709 of them and worse on 13**. Of the 988 puzzles where
the existing search does not find the best possible answer, the hint recovers
**571**. The biggest single gain: a 100-customer instance where the best possible
answer is 48 stacks, the existing search finds 58, and the hinted version finds
51.

Two things worth noticing. Our learned builder *on its own* has a worse worst
case than the search (+34 vs +10) — good on average, occasionally falls apart,
which is what a method with no search behind it looks like. Its value is as the
hint, not as the answer. And the 13 cases where the hint makes things worse are
all off by exactly one, for a reason that was already written down in the code:
the search measures its progress with a formula that slightly over-charges, so a
better starting point can occasionally lead it to cut off a branch that would
have turned out well.

### And it is *faster*

This was the surprise. Measured properly, the hinted search takes **11.6
milliseconds** per puzzle against the unhinted search's **19.3**. Producing the
hint costs 2 milliseconds and saves 10, because a better starting point lets the
search throw away more of the tree without looking at it. So it is not a
trade — it is better and cheaper at the same time.

### 4. We can predict which puzzles will be easy

The solver's fast heuristic already finds the optimal answer on most instances —
the expensive part is *proving* nothing better exists. A model can tell, before
any of that work starts, whether the fast answer is likely to be the right one,
and it is right about that far more often than chance (AUC 0.965, where 0.5 is a
coin flip and 1.0 is perfect).

That is a scheduling signal: instances predicted "easy" need one proof attempt,
instances predicted "hard" need the full search. The project's notes already
list a portfolio decision like this as a wanted feature.

### A bonus finding that has nothing to do with machine learning

Building the feature table meant computing our lower bound two different ways
across all 6,376 instances. One of the two ways — an expensive clique search the
solver gives up to 5 seconds per call — **never once produced a better number**
than the cheap method it runs alongside. Not on a single instance in the corpus.

This is a measurement on our instances, not a proof that it can never help, and
the clique bound has a separate virtue worth keeping (it stands on its own,
without relying on Yanasse's pathwidth equivalence). But five seconds a call for
something that has not helped once is worth a second look.

## Two ways this could have fooled us

**Nearly-identical puzzles.** Instances in the same benchmark file came out of
one generator with one setting, so they are near-copies of each other. Split
them randomly into "training" and "testing" and the model gets tested on
near-copies of what it studied — the scores look great and mean nothing. Every
number above splits by *source file* instead, so a model is always tested on
generator settings it has never seen. We also report the random-split number
beside it to show how much it flatters: 0.34 versus 0.45. Small, but real, and
we would rather have it on the record than in a footnote.

**The pile is not the problem.** Of the 6,376 instances, 5,938 have 30 or fewer
customers, and 3,975 are settled by simple bounds before any real search begins.
The instances that actually cost us a day of compute on 25 cores — the big dense
ones — are 25 rows out of 6,376. A model trained here is a model of *this
collection*. We report results separately on the harder subset throughout, but
no amount of careful splitting fixes a population that is 93% easy.

## We then tried to make it solve faster. It doesn't.

Finding a good schedule and *proving no better one exists* are different jobs,
and the second is what the hard instances cost. So the obvious next step was to
put the learned model inside the proving machinery. Three places, three
measurements, three negatives — written up in
[`reports/learned_search.md`](../reports/learned_search.md):

1. **Letting the model choose what the proof search tries first.** No effect on
   ordinary puzzles — the search's existing rules have already narrowed the
   choice to almost nothing by the time the model is consulted. On sparse
   puzzles it cuts the work to find a schedule by 60%, but on one puzzle it
   turned a 65-step search into a timeout. Too unreliable to ship.
2. **Starting the proof from the model's better answer.** No effect. The
   expensive part of a proof is showing that one-better is impossible, and both
   versions have to do that part. What a better start skips is the easy steps.
3. **Running the two provers at once and taking whichever finishes first.** No
   effect, and this one overturned an assumption the project had been carrying:
   the two provers were believed to fail on different puzzles, so running both
   should win. They don't. One of them won 63 out of 63 contests. Checking the
   records showed the belief had never actually been tested — the two provers
   had never been run on the same puzzle.

The honest summary: our model makes better *answers*, and the hard puzzles are
not short of answers, they are short of *proofs*. That was predicted in the
project's own notes before any of this was built; it is now measured.

The most useful thing to come out of it is the third point's corollary. The
project reaches for the SAT prover first and the other one as a fallback. On
this evidence that is backwards.

## How you actually use it, and what is still open

You can now ask for the hinted method by name. Where the code used to say
`cs-dfs`, it can say `learned+cs-dfs`:

```python
from satisfiability.heuristics import upper_bound
value, ordering = upper_bound(instance, "learned+cs-dfs")
```

**The solver still runs without any of this installed.** Someone who clones the
project and never runs `pip install -r learning/requirements.txt` sees no
difference: nothing breaks, because the machine learning library is only loaded
at the moment somebody asks for one of these two methods by name. That is the
only thing "soft import" means.

**If you ask for it and it isn't there, you get an error, not a shrug.** We
could have made a missing model fall back quietly to the old method. We
deliberately didn't, because then a benchmark run would print results labelled
"learned" that were actually produced by the old method, and nobody would ever
know. An error message says `no trained policy at ...; run python -m
learning.policy train`, and you fix it in seven seconds.

**Nothing uses it unless you ask.** Every existing script, sweep and solver call
behaves exactly as before. Making the hinted method the *default* would mean
this project, which currently needs only a SAT solver and numpy to run, would
also need a machine learning library and a trained model file present before it
could solve anything. That is a decision about what the project wants to depend
on, and the measurements cannot make it for you — they only say the method is
better and faster.

`reports/learning.md` §4 lists what to do next. The most promising: use the
learned scorer *inside* the search rather than only to start it.

## Running it

```bash
pip install -r learning/requirements.txt   # pandas, scikit-learn, lightgbm

python -m learning.dataset          # build the feature table   (~20s)
python -m learning.study_optimum    # the prediction study      (~2 min)
python -m learning.policy train     # fit the schedule builder  (~7s)
python -m learning.policy evaluate  # held-out comparison       (~3 min)

python -m learning.policy train-folds                        # (~40s)
python -m learning.corpus_sweep --strategy learned+cs-dfs --folds   # (~8 min)
python -m learning.corpus_sweep --strategy cs-dfs                   # (~20s)
```

```
learning/
    features.py         turns an instance into 36 numbers a model can read
    dataset.py          pairs every instance with its proved answer
    study_optimum.py    findings 1 and 4 above
    policy.py           findings 2 and 3 above
    corpus_sweep.py     scores a strategy against all 6,376 known answers
    data/instances.csv  the feature table      (not committed; rebuilt in 20s)
    models/policy.txt   the trained model      (not committed; refitted in 7s)
```
