# Contraction Relaxation: What It Closes, and What It Actually Gives Us

**Status:** implemented and measured, 2026-09-18. `satisfiability/relaxation.py`.
Item 5 of `reports/chu_stuckey_plan.md` §7 — "the actual goal", per the plan.

---

## 1. Summary

Contracting an edge of the MOSP graph relaxes the instance, so the optimum of a
contraction is a **certified lower bound** on the original's (Chu & Stuckey's
Lemma 1). Two ways to use that were built, and they came out very differently:

| use | what it asks | result |
|---|---|---|
| `prove(I, ub)` | is `ub - 1` refutable on some contraction? | **closes nothing we could not already close** |
| `lower_bound(I, target)` | what is the optimum of *this* contraction? | **lifts SP4's certified bound from 27 to 45** |

The first is the plan's stated goal and it does not deliver. The second is the
"partial relaxation worth having on its own" that §2 mentions almost in passing,
and it is the part that pays.

The reason is worth stating plainly because it was not anticipated: `prove` can
only ever succeed when `ub` is *already the true optimum*. It tries to refute
`ub - 1`; if a solution at `ub - 1` exists, no contraction can refute it, because
contraction only ever makes solutions easier to find. On the instances where we
most want a proof — the sparse ones — our upper bounds were not tight, so the
driver was being asked to prove something false.

---

## 2. The reformulation that made it cheap

Their driver computes `MOSP(I')` exactly at each relaxation level and compares
it against `ub`. We never need that number: only whether `MOSP(I') >= ub`, which
is one refutation at `ub - 1` on a small instance rather than a full descent on
it. A refutation there refutes `ub - 1` on the original by Lemma 1, which is
precisely the certificate wanted. The calls are cheaper and they stop earlier.

The search shape is theirs: contract greedily down to `ub` customers, where at
most `ub` stacks can be open and so nothing can be proved, then unmerge one
group at a time until the refutation lands. Unmerging is guided by the witness —
a group whose splitting the current solution survives cannot be what holds the
bound down, so a group it does not survive is chosen instead. That repairs the
greedy merge order, which they report mattering on several instances.

---

## 3. What `prove` did

**On SP3, where `ub = 34` is tight, it proves — and is slower than not
relaxing.**

| | groups | calls | nodes | time |
|---|---|---|---|---|
| `prove(SP3, 34)` | 74 of 75 | 41 | 5,023,825 | 139 s |
| direct descent, no relaxation | 75 | 1 | 3,942,306 | 71 s |

The bound only held once 74 of the 75 customers had been unmerged — that is,
after one single contraction. Every looser relaxation was satisfiable at 33. So
on SP3 the relaxation destroys the bound almost immediately, and the 40 calls
spent discovering that are pure overhead.

**On Random-125-125-2-1_0 it walked back to the original instance in 2 seconds**
and reported the instance itself satisfiable at `k = 27`, against a cached upper
bound of 28. Not a proof — a better upper bound, which the driver returns as a
witness. This is the case described above: the question asked was unanswerable
because `ub` was not the optimum.

**The kill criterion, honestly.** §7 says to abandon item 5 if relaxation closes
nothing on the density-2 instances, its best case. It closed nothing there. But
the criterion assumed tight upper bounds, and on the density-2 instances we did
not have them — the run above found a better one within seconds of being asked.
The honest verdict is that `prove` is not retired, it is *out of order*: it can
only be judged after the descent of `reports/customer_search.md` has made the
upper bounds tight, and that descent is still running on the sparse instances.
What can be said now is that it closed nothing on its best case at its first
attempt, which is not encouraging.

---

## 4. What `lower_bound` gives, which is the part that works

Solving a contraction outright yields a certified bound whatever that optimum
comes to. On SP4 — 100 customers, upper bound 57, and nothing here has ever
closed it:

| contract to | certified lower bound | time |
|---|---|---|
| (current bound, clique + contraction degeneracy) | 27 | — |
| 57 customers | 33 | 1 s |
| 68 customers | 39 | 7 s |
| 78 customers | **45** | 94 s |
| 89 customers | — (budget) | 120 s |

The gap on SP4 was 30 stacks; it is now 12, for 94 seconds of work and with a
proof rather than a heuristic at the bottom end. The trade is exactly as
expected and is monotone in the obvious direction: contract further and the
bound is weaker but nearly free; contract less and it is stronger but the
contracted instance becomes as hard as the original.

The same on two Random instances, where the gains are real but smaller:

| instance | ub | current lb | best certified by contraction | at | time |
|---|---|---|---|---|---|
| SP4 | 57 | 27 | **45** | 78 of 100 customers | 94 s |
| Random-125-125-4-1_0 | 63 | 27 | **39** | 78 of 125 | 59 s |
| Random-125-125-2-1_0 | 28 | 13 | **16** | 76 of 125 | 79 s |

Three points the table makes that the SP4 column alone would not:

- contracting to `ub` itself is worthless — 9 against an existing bound of 13 on
  the density-2 instance, 32 against 27 on the density-4 one. The loosest
  relaxation is not merely weak, it is below what clique and contraction
  degeneracy already give for free.
- the useful band is narrow and sits around 60-80% of the customers, and the
  level above it times out. The method has a knee rather than a dial.
- the gain is much larger on SP4, a structured instance, than on the Random
  ones. The Random generator's instances resist contraction for the same reason
  they resist everything else here.

This is what §2 called "a table in the paper, not a footnote", and it is the
outcome to carry forward for every instance the search cannot close.

---

## 5. Validation

`tests/test_relaxation.py`. The failure that matters is a *false proof*, since a
wrong bound here would be recorded as certified:

- **A proof is only ever offered at the true optimum.** For every instance, a
  proof is requested at every `ub` from the brute-force optimum up to the
  customer count, and exactly one of them may succeed. 120 instances, with a
  floor on how many proofs must actually occur so the test cannot pass by never
  proving anything.
- **Every partition the driver can reach is a relaxation**: its optimum is at or
  below the original's, over every contraction of 60 instances.
- **Splitting undoes exactly one merge**, preserves the customer partition, and
  terminates at the original instance.
- **A returned witness really beats the bound** it was returned against, checked
  by simulation on the original instance.

The last of these is what caught a real bug: the driver returned a witness in
*group* indices while claiming customer indices, which passes silently whenever
the groups happen to be in customer order and is wrong the moment a split
reorders them.
