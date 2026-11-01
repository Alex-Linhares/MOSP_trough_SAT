# Counting events, not witnesses: the separator first moment — plan for Ralph loop0011

*2026-11-01. The sequel to loop0010's item 08 (`reports/excess_phase_diagram.md`
§8), which killed the nested-pair count and located the slack of `β*` in the
union bound over clustered empty pairs. The loop files are
`Ralph_Loops/loop0011/`; each item there is self-contained. This document says
what the loop stands on, what it asks, in what order and at what price, and
where the record corrects the brief that produced it. Nothing here changes a
solver default; nothing re-solves an instance that is already certified.*

## 0. What the loop stands on

**The count on record.** For `G(n, p)` and for random clique covers the proved
inequality is a union bound over *empty pairs* `(A, R)` at exact sizes
`|A| = t = ⌈(n − k)/2⌉`, `|R| = n − k − t` (`FirstMoment.lean`,
`weightedSum_graphsOfPathwidthLe_le`; `CliqueCoverMoment.lean`,
`prob_coversOfMospValueLe_le`): every layout of vertex separation `≤ k` has, at
the prefix of size `t`, the prefix and the inactive suffix as an empty pair
(`EmptyPair.lean`, `exists_empty_pair_of_layout`). Its exponent on
`G(n, c/n)` is `H(a, a, 1 − 2a) − c a²`, `a = (1 − β)/2`, the constant `β*(c)` is
its root (`0.0087, 0.061, 0.171, 0.263, 0.337` at `c = 3, 4, 6, 8, 10`,
`reports/random_graph_first_moment.md` §3), the threshold is `c = 4 ln 2`; on
covers the exponent is `H(a, a, 1 − 2a) + μ E_s ln(2(1 − a)^s − (1 − 2a)^s)`,
`β*(d, μ)` is its root and the threshold is excess `μ(d − 1) = 1`
(`reports/scratch/clique_cover_moment/REPORT_generator.md` §3).

**The truth it misses.** Fitted slopes of exact pathwidth on `G(n, c/n)`:
`0.099, 0.158, 0.268, 0.360, 0.415` at `c = 3, 4, 6, 8, 10`
(`reports/random_graph_pathwidth_survey.md` §7(d), `n ≤ 70–120`), `0.08–0.10`
above `β*`; certified slopes `b` on covers (`excess_phase_diagram.md` §2.5):
`(4, 1)`: `0.348` against `β* = 0.288`; `(6, 1)`: `0.577` against `0.513`;
`(10, 1)`: `0.795` against `0.757`; Chu & Stuckey `d = 2, 4, 6, 8, 10` at
`m = n`: `0.146, 0.396, 0.599, 0.722, 0.804` against `0.105, 0.327, 0.532,
0.673, 0.763`. The pathwidth is linear for every `c > 1` (Lee–Lee–Oum 2012),
so the method's threshold `4 ln 2 ≈ 2.77` is an artefact of the count.

**Where the slack is (§8.5).** Two instruments agree that the union bound, not
the necessary condition, carries it: on 650 certified `(6, 1)` instances at
30–75 the empty-pair condition (Harper's bound) is within 0.4–1.2 stacks of the
pathwidth while the floor sits 1–3 stacks below it and growing; and the
second moment of the pair count at `(6, 1)` is `E[X²]/E[X]² = e^{0.23 n}` at
`β*`, with the extremal overlap of two empty pairs the *reversed* pair
perturbed through the separator (`0.186 n` of each side retained, `0.057 n`
of each side exchanged with `S`). §8.6 (2): any count that names *more*
vertices than the pair pays `Θ(ε log(1/ε))` of entropy for `Θ(ε)` of
constraint; a richer count must name *fewer*. §14 item 1: a
cluster-representative count is the one route left that could lift `β*`.

**The idea of this loop.** Count the *event* a narrow layout forces — a set
`S` of `k` vertices whose removal leaves a balanced empty bipartition — once
per `S`, with the inner probability `P(G − S` has a balanced empty
bipartition`)` computed from the component structure of `G(n − k, p)` instead
of by a union bound over the bipartitions:

    P(pw ≤ k) ≤ C(n, k) · P_{N = n − k}(E_bip),
    E_bip = {the components of G(N, p) can be grouped into two sides of sizes t and N − t with no edge between them}.

The deterministic implication is one line from `exists_empty_pair_of_layout`;
the inner probability is a large-deviation question about the giant component
of a sparse random graph; and two further representatives — the *closed* pair
(`S = N(A) ∩ N(R)`, the minimal-separator form) and the *weighted* count
`Y = Σ_P 1[P empty] / Z(P)` for any `Z(P) ≤ X` — are on the same ladder, each a
valid first moment, each merging a different part of the cluster.

### What the planner computed before writing the items (ten seconds of Python; to be replaced by items 05–07, never quoted)

Three first moments on `G(n, c/n)`, exponents per vertex with `a, r` the side
fractions, `s = 1 − a − r` the separator, `q(x) = 1 − e^{−c x}`:

| count | exponent | threshold in `β` at `c = 6` | at `c = 10` |
|---|---|---|---|
| pairs (on record) | `H(a, a, s) − c a²` at `a = (1 − β)/2`, `s = β` | `β* = 0.1706` | `0.3371` |
| `R` only, `A = V ∖ N[R]` (Harper's count) | `H(a, 1 − a) − (1 − a)·KL(β/(1 − a) ‖ q(a))` | `0.1752` | `0.3410` |
| closed pairs, `S = N(A) ∩ N(R)` | `sup_{a, r ≥ (1−β)/2, s ≤ β} [H(a, r, s) − c a r + s ln q(a) + s ln q(r)]` | `0.1803` | `0.3453` |

The exponent's slope at `β*` is `3.3–3.4` per unit of `β`, so a gain of `g`
nats per vertex moves the constant by `g / 3.3`. The closed-pair count gains
`0.027–0.032` nats, i.e. **`+0.008–0.010` in `β`**; the separator count's
same-`S` merging (flipping the small components of the two sides of a planted
empty bipartition; the planted sides are `G(N/2, c/n)` with mean degree
`c(1 − β)/2 ≈ 2.5–3.3`, whose isolated vertices are `e^{−3.3} = 3.7%` of them)
is worth about `(1 − β) e^{−c(1−β)/2} / 2 = 0.012–0.034` nats, **`+0.004–0.010`
in `β`**. Both are below the brief's kill of `0.02` at `c = 6` and `10`. They
are *estimates of the same-separator and single-move sub-clusters*; the
`e^{0.23 n}` of §8.5 is across separators, so if it is the typical cluster size
the representative that merges it is neither of these, and item 04 is where
that is decided.

Near the threshold the picture is different. The inner probability is bounded
on both sides by two routes the planner can write down: from below by one
fixed empty bipartition, `P(E_bip) ≥ e^{−c'N/4}` with `c' = c(1 − β)`, and by
the *thinning* route — `G(N, c'/N)` with only `(ln 2) N` edges has a giant of
half its vertices, at Poisson cost `c'/2 − ln 2 + ln 2 · ln(2 ln 2 / c')` per
vertex; from above by the first moment over bipartitions, `e^{−(c'/4 − ln 2) N}`,
which is the pair count itself. So the rate `I(c')` of `E_bip` satisfies
`c'/4 − ln 2 ≤ I(c') ≤ min(c'/4, thinning)`. At `c = 10` the bracket is
`[0.964, 1.537]` and the truth sits at the bottom plus the flip entropy (the
optimistic end would put `β_sep(10) = 0.427`, *above* the fitted slope
`0.415`, so it is not the truth). At `c = 3` the bracket is `[0.05, 0.22]` and
the pair count is nearly vacuous (`β* = 0.009`): `β_sep(3)` lies in
`[0.009, 0.056]` against a fitted slope of `0.099`, and **where in that
bracket is the most informative number this loop can produce.** And at
`β → 0` the event `E_bip` forces the giant of `G(N, c/N)` to be at most half,
which is typical for `c < 2 ln 2` and a lower deviation of the giant for
`c > 2 ln 2 ≈ 1.386`: if the giant's lower tail is exponentially small
(O'Connell 1998, to be held and read in item 01), **the separator count's
threshold is `2 ln 2`, not `4 ln 2`** — halfway, in the logarithm, from the
method's threshold to the true one at `c = 1`. The same mechanism on random
clique covers moves the onset of the floor from excess `1` to the line where
the giant of the MOSP graph is half the customers, which lies between
`e_g(r)` and `1`, inside regime II of the phase diagram ("the giant component,
no floor").

### Where the record corrects the brief

1. **The brief attributes the `e^{0.23 n}` clumping to one separator**
   ("every way of distributing the components of `G − S` onto two sides and
   every sub-pair"). §8.5 (a)'s extremal overlap table says otherwise: the
   second pair takes `0.057 n` vertices *from `S`* into each side and returns
   `0.186 n` of each side, so the pairs that dominate `E[X²]` have different
   separators. What the separator count merges is the component flips at
   fixed `S`, estimated above at `e^{0.01–0.03 n}`. The plan keeps the
   separator count as the brief asks, pre-registers that estimate, and puts
   the measurement that decides it (item 03, the counts; item 04, the planted
   cluster) before the constants.
2. **There are no sub-pairs in the count.** The Lean inequality and
   `finite_bound_cs.py` count pairs at exact sizes (`|A| = t`, `|R| = n − k − t`
   or `t − 1`; §8.4 and §8.6 (4) on the two conventions). The overcount at
   fixed `S` is the number of balanced bipartitions of the components, not
   sub-pairs.
3. **"No component larger than about `N/2`" is a strict relaxation of the
   event, and not a harmless one.** The brief says the number-partitioning
   condition on the small components "is harmless when they are small". The
   relaxed event has a second route the bipartition event does not: `G − S`
   globally thinned to the half-giant point, at cost `c'/2 − ln 2 + ln 2 ·
   ln(2 ln 2/c')` per vertex, which is `1.19` at `c' = 4.98` (`c = 6`) against
   `c'/4 = 1.245` for a fixed bipartition — already the cheaper route there,
   and far cheaper below. The item counts the bipartition event
   (components groupable into two sides of the forced sizes), uses the
   relaxed event only for the threshold statement and as the Lean-cheap
   form, and says which is which.
4. **A kill at `c = 6` and `10` alone would miss where the gain is
   predicted.** By the bracket above the gain is small at `c ≥ 8` and
   unknown but possibly large at `c = 3–4`, and the threshold result is at
   `β → 0`. The brief's kill is kept for the headline constants, and the
   near-threshold constants and the threshold itself are separate,
   pre-registered findings with their own criteria (items 06, 07).
5. **Kloks 1994 is held as a two-page preview only**
   (`literature/1994-Kloks-...-LNCS842-ch12-PREVIEW-2pp.pdf`), and the
   survey records his first moment "as restated by Do–Erde–Kang, Gao and
   Perarnau–Serra" with the DOI "from memory, not resolved". The literature
   item must not assert what his inner probability is without the chapter;
   it says "as restated" or obtains the chapter. Lee–Lee–Oum 2012 is not a
   first moment at all (rank-width via the expander in the giant), so it
   belongs in the "what is known" column, not the "who counts triples"
   column.
6. **The pilot's exact pathwidths stop before `n = 120` at `c ≥ 3`**
   (`gnp_pilot/results.csv`: 6,542 of 6,715 proved; at `n = 120` only
   `c ≤ 2` fully and 3 of 13 at `c = 3`; at `n = 100`, `c ≤ 3`). "The finite
   form at `n = 60` and `120` against the pilot's minima" is against minima
   at `60` and against the solver's lower bounds at `120`, as §5 of
   `random_graph_first_moment.md` already does.

And one thing the brief would have had the loop do twice: the Harper values
on the 650 certified `(6, 1)` instances (`reports/scratch/structured_count/slack_6_1.csv`)
and the second-moment table at `(6, 1)` exist; item 11 reuses them.

## 1. The questions and their items

Order: the literature (01), the deterministic lemmas (02), the two
measurements that de-risk (03 the counts, 04 the planted cluster), the inner
probability exactly (05), the constants (06 on `G(n, c/n)`, 07 on covers), the
theorems on paper (08), the branch (09, the weighted count's lower tail),
Lean (10), the slack ledger (11), the write-up (12), the reserve (13).
Dependencies: 01 → 06, 08; 02 → 03, 08, 10; 03 → 04 → 09; 05 → 06 → 11;
02, 05 → 07; 08 → 10; 06, 07, 09, 11 → 12.

**Literature (01).** Who has counted balanced separators, bisections or
vertex separators of sparse random graphs with a non-product inner
probability; the large-deviation rates for the giant and for all cluster
sizes (O'Connell 1998, Puhalskii 2005, Andreis–König–Patterson 2021); what
the bisection literature knows about representative counts (Díaz–Serna–Wormald
2007's locally optimal bisections, Kolesnik–Wormald 2014's improved
isoperimetric bounds, Lichev–Mitsche 2023, Díaz–Diner–Serna–Serra 2022 on
*vertex* bisection) and about the exact constant (Dembo–Montanari–Sen 2017).
Held papers read in full; open preprints fetched into `literature/`; the
answer to "did a representative count ever move a first-moment cut constant,
and by how much" written down with the numbers.

**The deterministic lemmas (02)** — A. Three forms, each from
`exists_empty_pair_of_layout`: the balanced separator at exact sizes
(`|A| = t`, `|R| = N − t`, `|S| = k`, `A ∪ R ∪ S = V`, no `A–R` edge); its
relaxation (every component of `G − S` has at most `t` vertices); the closed
pair (`S = N(A) ∩ N(R)`, sides at least the forced sizes, `|S| ≤ k`), by the
monotone alternating closure. Checked on every graph to 9 vertices and
samples at 10–12 before any is called a lemma; the MOSP forms on random covers.

**The clumping decomposed (03)** — B. On graphs with exact pathwidth at
`n = 14–24` (new tiny solves by the subset DP and the C program, layouts
kept) and on certified covers at `n ≤ 22`: at `k = pw`, the number of exact-size
empty pairs `X₁`, of distinct separators `X₂`, of closed pairs `X₃`, of
move-classes `X₄`; the growth rates of `X₁/X₂`, `X₁/X₃`, `X₁/X₄` with `n`.
*Pre-registered:* the separator and closure ratios grow at `≤ 0.035` nats per
vertex at `c = 10`, far below the `0.066` a `0.02` gain needs.

**The planted cluster (04).** Condition on an empty pair (delete the `A–R`
edges of a fresh `G(n, c/n)`) and count the *other* empty pairs at the
forced sizes, their overlap with the planted one and the mechanism
(low-degree separator vertices recombined); the median against the
second-moment prediction. Decides whether the `e^{0.23 n}` is the typical
cluster or a rare-instance artefact of `E[X²]` — the two outcomes send the
loop down different branches, and both are findings.

**The inner probability, exact (05)** — C. `P_N(E_bip)` by Gilbert's
connectedness recursion and a sum over partitions of `N` (exact to `N = 60`,
`80` if cheap); the relaxed event by the `O(N²)` DP to `N = 400`; against the
product bound `C(N, t)(1 − p)^{t(N − t)}`; the finite separator bound at the
pilot cells. *Kill:* at most one stack over the pair floor at every pilot
cell → recorded as a rounding, as the exact-size pair was.

**`β_sep(c)` (06)** — D. The rate of `E_bip` from the exact computation's
growth in `N` (a fit, labelled), from the two analytic routes that bracket it,
and from the literature rate if item 01 found one usable; `β_sep(c)`,
`β_closed(c)` and their combination at `c = 2–20` against `β*(c)` and the
slopes; the threshold statement `2 ln 2` with its citation status. *Kill
(the brief's):* `β_sep − β* < 0.02` at `c = 6` and `10` → the route is closed
for the headline constants. *Separate finding:* the near-threshold constants
at `c = 2–4` and the threshold.

**The MOSP version (07)** — E. On random clique covers: the closed-pair count
by inclusion–exclusion over `S` (the `NestedStructure` machinery), the
component flips by the isolated-customer generating function, the half-giant
line of the random intersection graph as the floor's new onset in excess
coordinates; constants on the `(d, μ)` grid against `β*(d, μ)` and `b`; the
0.01 floors on the 200 Chu & Stuckey instances, zero violations required.
*Kill:* `< 0.02` at `(6, 1)` and `(4, 1)`. *Separate finding:* the onset line.

**The theorems on paper (08)** — F, first half. The separator first moment in
finite form, the closed-pair theorem, the weighted-count identity
`Y = Σ_P 1[P empty] / Z(P) ≥ 1[X > 0]` with the flip bound as its first
instance, and the threshold corollary; every lemma numbered, every inequality
named, every statement checked by enumeration at `n ≤ 7` first.

**The representative count's lower tail (09)** — the branch. For
`Z(P)` = the number of recombinations of low-degree separator vertices around
`P`, the planted lower tail from item 04's instances and the Laplace transform
of its computable lower bound; the constant it would give. *Kill:* no
computable `Z` beats the closed-pair count by `0.02` → recorded, with the
mechanism (the lower tail is dominated by instances with no movable vertex,
at cost `q β` per side).

**Lean (10)** — F, second half. `SeparatorMoment.lean`: the three
deterministic lemmas, the union bound over `S` with the inner weighted count
(a factorisation of `gnpWeight` over an induced subgraph, which
`FirstMoment.lean` does not have), the MOSP form. No `sorry`; a named `Prop`
with the obstacle is a deliverable.

**The slack ledger (11).** On the 650 certified `(6, 1)` instances (Harper
values on record) and the pilot `c = 10` cells: pair floor → exact-size floor
→ separator / closed floor → Harper → pathwidth, per instance, so the write-up
can say in stacks what each count buys and what is left.

**The write-up (12)** — H. `reports/separator_moment.md` §0 and assembly, the
Appendix E paragraph ("we found no prior statement", never "first"), the
`CLAUDE.md` paragraph drafted and not applied.

**Reserve (13).**

## 2. Budget

Modelled on loop0010 (13 items, 13 sessions, 10.5 h wall, $176). Compute is
small: the exact optima exist; the only solver runs are tiny graphs for item
03 (`n ≤ 24`, milliseconds each) and enumerations.

| item | sessions | wall-clock | dollars | compute (core-hours, nice 19) |
|---|---|---|---|---|
| 01 literature | 1 | 1 h | 15 | 0 |
| 02 deterministic lemmas | 1 | 1 h | 15 | 0.5 (all graphs to 9, samples to 12) |
| 03 the clumping decomposed | 1 | 1.5 h | 20 | ≤ 3 (enumerations at `n ≤ 24`) |
| 04 the planted cluster | 1 | 1.5 h | 20 | ≤ 3 |
| 05 inner probability | 1 | 1 h | 15 | ≤ 1 (partitions to `N = 60–80`) |
| 06 `β_sep(c)` | 1 | 1 h | 20 | 0.2 |
| 07 the MOSP version | 1 | 1.5 h | 20 | ≤ 1 |
| 08 theorems on paper | 1 | 1 h | 20 | 0.1 |
| 09 the lower tail | 1 | 1 h | 15 | 0.5 |
| 10 Lean | 1–2 | 1.5 h | 25 | 0 (lake build) |
| 11 slack ledger | 1 | 0.5 h | 10 | 0.5 |
| 12 write-up | 1 | 1 h | 20 | 0 |
| 13 reserve | 1 | 1 h | 15 | ≤ 2 |
| **total** | **13–14** | **≈ 14 h** | **≈ $230** | **≤ 12** |

Per-session cap 4 h (`knobs.json`), fix cap 45 min, three fix attempts; the
gate (lake build, two pytest suites, the paper's `make check`) takes about
10 min and is run once per item.

## 3. Risks

1. **The headline constants do not move.** The planner's estimates put the
   separator and closed-pair gains at `+0.004–0.010` in `β` at `c = 6` and
   `10`, below the brief's kill. If items 05–07 confirm that, the loop's
   value is the threshold (`4 ln 2 → 2 ln 2`, conditional on a cited
   large-deviation result), the near-threshold constants at `c = 2–4`, the
   onset line on covers, a finite theorem with its Lean form, and the
   decomposition of the slack — not a new `β` at `(6, 1)` or `c = 10`. The
   plan is shaped so that these are delivered either way.
2. **The inner rate may rest on a fit.** The exact computation reaches
   `N = 60–80`; the analytic routes only bracket the rate; the literature
   rates (O'Connell, Andreis–König–Patterson) are for the giant's size and the
   cluster-size empirical measure, and translating them to "a balanced
   empty bipartition exists" is a variational problem no item is told to
   solve in full. `β_sep(c)` may be reported as "exact finite bound to
   `N = 80`, fitted rate beyond", labelled as such and not quoted as a
   theorem.
3. **Lean's union bound over `S` is not two lines.** The deterministic
   lemmas are cheap, but bounding `Σ_{G: pw ≤ k} w_p(G)` by
   `C(n, k) · Σ_{H ∈ 𝓗} w_p(H)` needs the `G(n, p)` weight factorised over an
   induced subgraph and its complement, which `FirstMoment.lean` does for an
   empty pair's forbidden edges but not for an induced subgraph. Item 10 is
   allowed to leave that as a named `Prop` with the obstacle.

Two smaller ones: the planted-cluster measurement at `n ≤ 32` may not see the
asymptotic regime (§14 of `reports/ml_nature.md`: `n ≤ 40` constants failed at
125), so item 04's verdict is stated at its sizes with the growth in `n`
beside it; and the closed-pair inclusion–exclusion on covers at `n = 125`
alternates over `2^{|S|}` terms with catastrophic cancellation, so item 07 is
told to use exact rationals or 200-digit arithmetic and to check against
enumeration at `n ≤ 8` first.

## 4. What would count as success

The deterministic lemmas proved on paper and in Lean with brute-force checks
on record; the clumping of §8 decomposed into what each representative merges,
measured on instances with exact pathwidth; the inner probability computed
exactly to a stated `N` and bracketed analytically beyond; `β_sep(c)` and
`β_sep(d, μ)` tabulated against `β*` and the slopes with the brief's kill
applied honestly; the threshold statement with its exact citation status; the
weighted-count identity stated and its first instance computed; the slack
ledger in stacks; and a report whose every number carries its size range and
regenerate command. The plan does not promise the constant: it promises to
find out, with pre-registered predictions, whether counting events instead of
witnesses moves it, and by how much, and where.
