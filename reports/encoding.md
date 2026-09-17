# The SAT Encoding

The decision problem is: *given a MOSP instance and a bound $k$, can the patterns
be sequenced so that at most $k$ customer stacks are open at any step?* This
document states the CNF that asks it.

Three artifacts should agree, and this document is the bridge between them:

| | |
|---|---|
| `satisfiability/mosp_encoding.py` | what the solver actually emits |
| `lean/MOSPFormalization/Encoding.lean` | the proof that this encoding is faithful |
| here | the formulation both are meant to implement |

---

## 1. Notation

An instance is a binary matrix $M \in \{0,1\}^{n \times m}$ over $n$ customers
and $m$ patterns, with $M_{cp} = 1$ when customer $c$ requires pattern $p$.
Write

$$P_c = \{\, p : M_{cp} = 1 \,\}$$

for the patterns customer $c$ needs, and let $t \in \{0, \dots, m-1\}$ range over
production steps. A solution is a permutation of the patterns; $c$'s stack is
open from the step its first required pattern is produced until the step its last
one is, **inclusive at both ends**.

## 2. Variables

| Variable | Meaning | Count |
|---|---|---|
| $x_{p,t}$ | pattern $p$ is produced at step $t$ | $m^2$ |
| $y_{p,t}$ | pattern $p$ is produced at or before step $t$ | $m^2$ |
| $o_{c,t}$ | customer $c$'s stack is open at step $t$ | $nm$ |
| $a_{c,t}$ | some pattern of $c$ is produced by step $t$ | $\le nm$ |
| $A_{c,t}$ | every pattern of $c$ is produced by step $t$ | $\le nm$ |

$a$ and $A$ are Tseitin auxiliaries introduced only for customers with
$\lvert P_c \rvert \ge 2$; see §5.

## 3. Permutation

Every pattern takes exactly one step, and every step takes exactly one pattern:

$$\bigvee_{t} x_{p,t} \quad \forall p
\qquad\qquad
\bigvee_{p} x_{p,t} \quad \forall t$$

$$\mathrm{AMO}\big(\{x_{p,t}\}_{t}\big) \quad \forall p
\qquad\qquad
\mathrm{AMO}\big(\{x_{p,t}\}_{p}\big) \quad \forall t$$

$\mathrm{AMO}$ is at-most-one, emitted as a ladder encoding.

## 4. Prefix linking

$y$ is the prefix relation of $x$: pattern $p$ is *placed by* step $t$ exactly
when it was placed at some step no later than $t$.

$$x_{p,t} \rightarrow y_{p,t}
\qquad
y_{p,t} \rightarrow y_{p,t+1}
\qquad
y_{p,t} \rightarrow y_{p,t-1} \vee x_{p,t}
\qquad
y_{p,0} \rightarrow x_{p,0}$$

The third holds for $t > 0$; the fourth is its base case. Together they pin
$y_{p,t} \leftrightarrow \exists s \le t,\; x_{p,s}$, which is the content of
`y_iff_posOf_le` in the Lean development.

## 5. Open stacks

This is the only MOSP-specific family, and the only one where our implementation
has gone wrong. A stack is open at $t$ when one of its patterns is produced at
$t$, or when one has been produced and another has not:

$$x_{p,t} \rightarrow o_{c,t} \qquad \forall c,\ \forall p \in P_c \tag{5a}$$

$$y_{p,t} \rightarrow a_{c,t}
\qquad
A_{c,t} \rightarrow y_{p,t}
\qquad \forall p \in P_c \tag{5b}$$

$$a_{c,t} \wedge \neg A_{c,t} \rightarrow o_{c,t} \tag{5c}$$

### Why the auxiliaries, and why only these polarities

Stating (5b)–(5c) over *pairs* of a customer's patterns is the obvious
alternative,

$$y_{p,t} \wedge \neg y_{q,t} \rightarrow o_{c,t}
\qquad \forall p, q \in P_c, \; p \ne q, \tag{5b$'$}$$

and it is logically equivalent. But it costs
$\lvert P_c \rvert\left(\lvert P_c \rvert - 1\right)$ clauses per
$(c,t)$ against $2\lvert P_c \rvert + 1$, so the formula grows with
$\sum_c \lvert P_c \rvert^2 m$ rather than $\sum_c \lvert P_c \rvert m$. On dense
instances that dominates everything else: GP5 encodes to 76.7M clauses under
(5b$'$) and 3.25M under (5b), which is the difference between 10.3 GB and 461 MB
of memory and between unencodable and solved in 285 s. Pass
`pairwise_open_stacks=True` for (5b$'$); it is retained for equivalence testing.

Neither auxiliary is pinned to its full definition — only the polarities above
are asserted. That is sound because the solver has no reason to set them
otherwise: $a_{c,t}$ occurs negatively in (5c), so it stays false unless some
$y_{p,t}$ forces it true, and $A_{c,t}$ occurs positively, so it goes true
whenever every $y_{p,t}$ permits. Hence $o_{c,t}$ is forced exactly when $c$ is
genuinely open — never spuriously, which would over-tighten §6 and could turn a
satisfiable instance unsatisfiable.

### Inclusivity

(5a) fires when a pattern of $c$ sits exactly at $t$, including the step that
*closes* the stack. This is deliberate and matches the standard definition:
Yanasse & Senne (2010) define the objective through the fill-in matrix, where a
row's zeros between two ones become ones and the original ones remain, so the
column holding a customer's final pattern still counts it.

The Lean formalization originally defined an open stack as requiring a pattern
*strictly* after $t$, which disagreed: on one customer needing one pattern it
gave 0 where (5a), `mosp/verify.py` and the literature all give 1. The main
theorem is false under that reading, because (5a)'s witness must serve both sides
of the definition at once.

## 6. Width bound

At most $k$ stacks open at any step:

$$\sum_{c} o_{c,t} \le k \qquad \forall t$$

emitted as a totalizer, and only when the number of active customers exceeds $k$.

## 7. Symmetry breaking

A sequence and its reverse have the same maximum (Yanasse 1997c), so the pattern
required by the most customers may be confined to the first half:

$$\bigvee_{t < \lfloor m/2 \rfloor + 1} x_{p^\ast, t},
\qquad p^\ast = \arg\max_p \lvert \{c : p \in P_c\} \rvert$$

This is the only symmetry breaking currently applied, against $m!$ symmetric
assignments. Dominance-based constraints were attempted and withdrawn as unsound;
see `satisfiability/mosp_encoding.py`.

## 8. Correctness

`lean/MOSPFormalization/Encoding.lean` proves

$$\big(\exists\, \alpha,\; \mathrm{Encodes}(M, k, \alpha)\big)
\;\longleftrightarrow\;
\mathrm{MOSP}(M) \le k$$

with no `sorry`, depending on no axioms beyond `propext`, `Classical.choice` and
`Quot.sound`. Left to right is what licenses reporting a refutation at $k-1$,
together with a witness at $k$, as a proof that the optimum is $k$. Right to left
says the encoding never excludes a sequence that exists.

Three things it does not establish, in order of how much they matter:

1. **That `mosp_encoding.py` emits these clauses.** The Lean describes an
   encoding; that the Python produces *this* one is a reading of the code.
2. **The cardinality encodings.** $\mathrm{AMO}$ and the totalizer are modelled
   by their meaning rather than their clause form. Both are standard and their
   correctness is independent of MOSP, but it is assumed here.
3. **That any particular formula is unsatisfiable.** The theorem says what UNSAT
   *means*; establishing it for a given instance still rests on the solver, and
   would need a proof log — see the certification discussion in the README.

## 9. Size

For an instance with $n$ customers, $m$ patterns and $\bar{P}$ patterns per
customer on average, the formula has $O(m^2 + nm)$ variables and, under (5b),
$O(m^2 + n\bar{P}m)$ clauses before cardinality encodings. Measured:

| instance | size | variables | clauses |
|---|---|---|---|
| SP3 | 75×75 | 74,625 | 381,376 |
| SP4 | 100×100 | 136,400 | 826,401 |
| GP8 | 100×100 | 137,000 | 2,311,101 |
| GP5 | 100×100 | 137,200 | 3,254,001 |

GP5 and SP4 have identical dimensions; the 4× difference in clauses is entirely
the $\sum_c \lvert P_c \rvert$ term, GP5 being dense enough that its customers
need nearly every pattern.
