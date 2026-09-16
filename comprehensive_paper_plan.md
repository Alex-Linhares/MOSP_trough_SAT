# Paper Plan: Certified Optimal Solutions for the Minimization of Open Stacks Problem

**Status:** planning document. Figures marked *(measured)* come from runs in this
repository and are reproducible; everything else is a target or an assumption
still to be tested.

---

## 1. The claim

Every published optimal value for MOSP is an assertion of trust. Chu & Stuckey
(2009) report optima for the 2005 Constraint Modelling Challenge instances;
Frinhani et al. (2018) tabulate them; later work benchmarks against those tables.
None of it ships anything a reader can check. If a solver had a bug, the
literature would inherit the error silently, and the only recourse would be to
write another solver and hope the two agree.

We propose to make MOSP optima *checkable*: for each instance, a certificate
that a sceptical reader can verify without trusting our solver, our encoding, or
our hardware.

Three artifacts per instance:

| Direction | Certificate | Checked by |
|---|---|---|
| MOSP ≤ k | witness ordering | O(nm) simulation, trivially reimplementable |
| MOSP > k−1 | DRAT/LRAT refutation of the k−1 encoding | `cake_lpr` (verified in HOL4) |
| encoding is faithful | Lean 4 proof that the CNF is satisfiable iff MOSP ≤ k | Lean kernel |

The third is the one nobody does, and it is what upgrades "a SAT solver said so"
into "MOSP(I) = k, and here is why."

---

## 2. Why this is open

**No SAT treatment of MOSP exists.** *(measured)* Across the eight papers in
`literature/` — including Martin, Yanasse & Pinto (2022), a survey of
*mathematical models* for MOSP covering ILP and CP formulations — there are zero
mentions of SAT or satisfiability as a solving method. The single hit in Chu &
Stuckey (2009) is the word "satisfiability" applied to dominance between
subproblems, not to solvers.

This needs a proper literature search before the claim goes in a paper (§8), but
the corpus we hold is consistent with SAT being unexplored territory for this
problem.

**Proof logging has not reached this problem.** Certifying combinatorial
optimization is an active thread (VeriPB in the CP community, DRAT/LRAT in SAT),
but the MOSP literature reports values, not certificates.

---

## 3. What already exists in this repository

Assets the paper can be built on today, with measurements.

### 3.1 A direct SAT encoding

Position-based, three variable families plus two auxiliaries
(`satisfiability/mosp_encoding.py`). The technical content is the open-stack
constraint. Writing it over pairs of a customer's patterns costs
`|P_c|(|P_c| − 1)` clauses per (customer, step); two polarity-aware Tseitin
auxiliaries express the same condition in `2|P_c| + 1`.

*(measured)* On GP5 (100×100, customers requiring nearly every pattern):

| | pairwise | linear | ratio |
|---|---|---|---|
| clauses | 76,737,501 | 3,254,001 | 23.6× |
| encode memory | 10.3 GB | 461 MB | 22.3× |
| encode time | 59.7 s | 2.3 s | 26× |

The advantage grows with instance size (1.9× at n=8, 10.4× at n=40, 23.6× at
n=100), as expected from `|P_c|/2`. GP5 was not encodable in practice before this
change and now solves in 285 s.

### 3.2 A corpus of certified-by-simulation optima

*(measured)* Full sweep of the benchmark tree, 6,376 instances, 30 workers:

- 60 s budget: 5,499 solved, 877 timeout, 0 errors
- 900 s budget: in progress, 5,855 solved / 457 timeout at instance 6,312
- **0 value/simulation mismatches across every solved instance in both passes**

Each solved instance has its witness ordering persisted in `solutions/` (5,881
files at time of writing). The "0 mismatches" figure is meaningful because the
verification path (`mosp/verify.py`, simulate the sequence and count) shares no
code with the SAT encoding — agreement is evidence that the encoding means what
we think it means.

### 3.3 Agreement with published optima

*(measured)* Against Frinhani et al. (2018) / Chu & Stuckey (2009):

| instance | size | published | ours | time |
|---|---|---|---|---|
| GP1 | 50×50 | 45 | 45 | 14.2 s |
| GP2 | 50×50 | 40 | 40 | 26.1 s |
| GP3 | 50×50 | 40 | 40 | 21.9 s |
| GP4 | 50×50 | 30 | 30 | 16.3 s |
| GP5 | 100×100 | 95 | 95 | 284.8 s |
| GP6 | 100×100 | 75 | 75 | 875.4 s |
| SP2 | 50×50 | 19 | 19 | — |
| GP7, GP8, SP3, SP4 | | 75, 60, 34, 53 | unsolved at 900 s | |

Eleven for eleven where we finish. GP6 finishing at 875 s against a 900 s cap
suggests the remaining four sit just past the wall rather than out of reach.

### 3.4 A partial Lean 4 formalization

`lean/MOSPFormalization/` contains vertex separation, path decompositions,
pathwidth, MOSP instances and open-stack counting, with VS = PW (Kinnersley 1992)
proven sorry-free in both directions. *(measured)* `Reduction.lean` carries 2
`sorry`s. **None of this yet formalizes the SAT encoding**, which is the piece
§5.3 needs.

---

## 4. Contributions, in the order they should be claimed

1. **Certified MOSP optima.** The first MOSP results shipping machine-checkable
   certificates in both directions, plus a formally verified encoding closing the
   trust gap that DRAT alone leaves open.
2. **A verified corpus.** ~5,900 instances with certified-optimal values and
   witness orderings, an order of magnitude more than any published table, as a
   reusable artifact.
3. **A linear open-stack encoding** that makes SAT competitive on dense
   instances, with the measured effect above.
4. **An empirical account of the pathwidth reduction's tightness** (§6), turning
   a folklore equality into a measured claim.

---

## 5. Work to be done

### 5.1 Proof emission

*(measured)* `pysat` emits DRAT from `Glucose4` and `Lingeling`; the `Cadical153`
binding accepts `with_proof=True` but returns zero lines. Two routes:

- **(a)** switch the refutation call to Glucose4/Lingeling — works today, weaker
  solver, so fewer instances close;
- **(b)** shell out to an external `cadical` binary with proof output — keeps the
  solver, costs a DIMACS round-trip.

**Recommended:** (b), with (a) as the fallback. Decide by prototyping on an
already-solved instance and measuring proof size and checking time.

Only the *k−1 UNSAT* call needs a proof. The SAT side is certified by the
ordering, which is far cheaper.

### 5.2 Proof checking

Check with `drat-trim` first (easier to obtain), then `cake_lpr` for the verified
story. Report per-instance: proof size, emission time, checking time. Expect
proofs on hard instances to be very large; **this is a headline measurement, not
a failure** — "certifying MOSP optimality costs X GB at 50×50" is a result.

### 5.3 Lean: encoding faithfulness

The new theorem, in a new `MOSPFormalization/Encoding.lean`:

> for an instance `M` and bound `k`, the CNF produced by the encoding is
> satisfiable iff `M.mospValue ≤ k`.

Forward direction: from a satisfying assignment extract an ordering and show it
has ≤ k open stacks at every step. Backward: from an ordering construct the
assignment. The permutation and prefix-linking constraints are routine; the work
is the open-stack constraint, where the argument is exactly the polarity argument
in §3.1 — `any` false unless forced, `all` true whenever permitted — which must
become a real lemma rather than a comment.

This is the highest-risk, highest-value item. **Scope control:** formalize the
encoding as a function over finite types and prove the equivalence; do *not*
attempt to verify the Python implementation. State that gap explicitly (§7).

Deciding whether to close the two existing `sorry`s in `Reduction.lean` is
separate — they concern the pathwidth reduction, which the SAT solver no longer
relies on. **Recommendation: leave them and say so.** They are not load-bearing
for this paper.

### 5.4 Finish the open instances

GP7, GP8, SP3, SP4. Route: `solve_parallel one --workers 28` with a multi-hour
budget, which starts the expensive UNSAT proof immediately rather than reaching
it last. GP6's 875 s single-core result is the encouraging precedent.

If they close, the paper reports 11/11 against published optima *with
certificates*. If not, report honestly and characterize what makes them hard.

### 5.5 Incremental SAT (optional)

The binary search currently re-encodes and re-solves from scratch at each k,
discarding all learned clauses. Keeping one solver alive with assumptions would
carry learning across the search. Cheap and independently useful, but it
complicates proof emission — **defer until the certificate pipeline works.**

---

## 6. The pathwidth-tightness experiment

`MOSP = pathwidth(G) + 1` is cited throughout this literature. This repository
already found it failing in both directions: the agreement graph undercounting,
the customer graph overcounting (SP2 at 21 against a true 19).

With ~5,900 certified optima we can measure this properly: compute exact
agreement-graph pathwidth where tractable and report the distribution of
`MOSP − (pw + 1)` against instance density, size, and patterns-per-customer.

Care required: the customer-graph overcounting is partly an artifact of a
*heuristic* customer-to-pattern ordering derivation, not of the theory. The
agreement-graph undercounting is the interesting direction, since pathwidth there
is computed exactly. **Do not claim a counterexample to a theorem until it is
clear which is being contradicted — the published claim, or our reading of it.**
Read Yanasse (1997) and Linhares & Yanasse (2002) closely on exactly what is
asserted, under what hypotheses.

---

## 7. Threats to validity, to state in the paper

- **The Python encoder is unverified.** A Lean-verified encoding does not verify
  the code that emits the CNF. The honest framing: the *encoding* is verified,
  the *implementation* is tested. Note the mitigation — every solved instance is
  independently re-simulated, and 0 mismatches across ~5,900 instances bounds how
  wrong the implementation can be on the SAT side.
- **`pysat`, CaDiCaL and the proof checker are trusted** unless `cake_lpr` is
  used, which is precisely why it is worth using.
- **Timeouts are not negative results.** An instance unsolved at 900 s says
  nothing about its difficulty in absolute terms; report the budget everywhere.
- **The published optima we agree with are themselves uncertified.** Agreement is
  mutual corroboration, not proof that either is right — which is the paper's
  own argument for certificates.
- **Benchmark provenance.** Instances are parsed from two formats by
  `from_benchmark_file`; a parsing error would silently change the problem. Worth
  a spot-check of a sample against the original files.

---

## 8. Before writing

- [ ] Proper literature search for SAT/MaxSAT/PB approaches to MOSP and to
      pathwidth, beyond the eight papers held locally. The "no SAT treatment"
      claim is load-bearing and currently rests on a small corpus.
- [ ] Check whether De La Banda & Stuckey (2007) or later work ships anything
      certificate-like.
- [ ] Confirm the provenance of every published value in the comparison table —
      currently taken from Frinhani et al. (2018) quoting Chu & Stuckey (2009).
- [ ] Obtain the remaining paywalled references in `literature/MISSING.md`.

## 9. Target venues

- **CP** or **SAT** — the certification angle is native to both; SAT is the
  better fit if proof sizes turn out to be the interesting story.
- **INFORMS Journal on Computing** or **EJOR** — the OR audience that publishes
  MOSP, where "certified optima" is the novel framing.
- **ITP/CPP** — only if the Lean encoding proof grows into the main contribution.

**Recommendation:** target CP/SAT first. The OR venues are where MOSP lives, but
the contribution is methodological and the reviewers who will recognize it read
the former.

## 10. Sequencing

1. Prototype the certificate pipeline end to end on one small solved instance:
   emit DRAT, check it, record sizes. **This de-risks everything else and should
   happen before any writing.**
2. Scale certificate generation across the corpus; measure proof size and
   checking time by instance size.
3. In parallel: attack GP7, GP8, SP3, SP4 with `solve_parallel one`.
4. In parallel: the pathwidth-tightness experiment (§6) — independent of the
   certificate work and the most likely source of a genuine scientific finding.
5. Lean encoding proof (§5.3) — start early, it is the long pole.
6. Literature search (§8) before committing to novelty claims.
7. Write.

**The riskiest assumption** is that DRAT proofs for interesting instances are
small enough to emit, store and check. Step 1 tests it directly. If proofs prove
impractical at scale, the paper survives by reporting certificates for the range
where they are practical and measuring precisely where that boundary falls —
which is itself a useful finding, but it changes the framing from "here is a
certified corpus" to "here is how far certification currently reaches."
