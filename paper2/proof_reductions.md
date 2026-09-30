# Faults found in the published reductions, and their corrections

Companion to `equivalences.md` (what each Table 1 problem is, and how it
relates to pathwidth) and `popularity.md`. This file records the places where
a published *proof* of one of the reductions is wrong as written, even though
the theorem it proves is true, together with the corrected argument. Each
entry says how the fault was found and how far it is checked.

## 1. Kirousis & Papadimitriou (1986), Theorem 4.1: the lower bound

**Source.** L.M. Kirousis and C.H. Papadimitriou, "Searching and pebbling",
*Theoretical Computer Science* 47 (1986) 205-218, Theorem 4.1, p. 216:
"For an arbitrary graph G, ns(G) = vs(G) + 1", where ns is the node search
number and vs the vertex separation. PDF: `literature/10_kirousis_papadimitriou_1986.pdf`.

**Status.** The theorem is true (for graphs with at least one edge; on an
edgeless graph ns = 0). It is proved in Lean for the monotone game,
`monotoneNodeSearch_eq_vertexSeparation_add_one` in
`../lean/MOSPFormalization/Complex/NodeSearch.lean` (loop0005 item 10), by the
corrected argument below. The fault in the published proof was found by that
item's session and **is proved in Lean** (2026-09-30), with no `sorry` and only
the standard axioms: `kirousisPapadimitriou_claim2_false` in
`../lean/MOSPFormalization/Complex/KirousisPapadimitriouGap.lean`.

**Verdict: a gap, not a wrong theorem, and the paper holds the repair.** The
proof as written assumes only an optimal recontamination-free strategy, and
under that assumption claim (2) is false. The paper's own Corollary 2.4
supplies a normal form under which claim (2) is true, but the proof does not
cite it (see *The repair inside the paper*).

### The published argument (p. 217)

The upper bound, ns ≤ vs + 1, is fine. For the lower bound the proof runs:

1. Take an optimal recontamination-free node-searching strategy S.
2. Define a layout L by first placement: L(v) < L(w) iff v *accepts a
   searcher* before w does.
3. Let D_i = {v : L(v) ≤ i and v has a neighbour w with L(w) > i}, and let
   i₀ maximise |D_i|. Then vs(G) ≤ |D_{i₀}| (their (1)).
4. Consider the point of S at which exactly the vertices with L(v) ≤ i₀ have
   accepted a searcher, and let u₁, …, u_n be those among them that carry a
   searcher at that point. **Claim (2): D_{i₀} ⊆ {u₁, …, u_n}**, "since the
   vertices in D_{i₀} are joined to vertices not yet cleared".
5. If the next move places a searcher, n < ns(G) (3); if it removes one from
   some u_l, then u_l ∉ D_{i₀} because recontamination is not allowed (4).
   Either way |D_{i₀}| < ns(G), so vs(G) < ns(G).

### Where it fails

Claim (2) assumes that a vertex which has *accepted* a searcher still holds
one while it has an uncleared neighbour. A strategy may place a searcher and
remove it again without clearing anything. That removal recontaminates
nothing, because nothing had been cleared, so the strategy stays
recontamination-free, and it can stay optimal.

**Counterexample.** G = K_{1,3}, with centre c and leaves a, b, d.
ns(G) = 2 and vs(G) = 1.

| step | move | guarded | edges clear |
|---|---|---|---|
| 1 | place a | a | — |
| 2 | remove a | — | — |
| 3 | place b | b | — |
| 4 | remove b | — | — |
| 5 | place d | d | — |
| 6 | remove d | — | — |
| 7 | place c | c | — |
| 8 | place a | c, a | ca |
| 9 | remove a | c | ca |
| 10 | place b | c, b | ca, cb |
| 11 | remove b | c | ca, cb |
| 12 | place d | c, d | ca, cb, cd |

It never uses more than 2 searchers, so it is optimal. No clear edge is ever
recontaminated: steps 1-6 clear nothing, and after step 8 the centre is
guarded throughout, so no searcher-free path joins a clear edge to a
contaminated one.

The first-placement order is a, b, d, c, so D₁ = {a}, D₂ = {a, b} and
D₃ = {a, b, d}. The maximum is at i₀ = 3, with |D₃| = 3. The point at which
exactly a, b, d have accepted a searcher is just after step 5, when only d
holds one. So D₃ = {a, b, d} ⊄ {d}, and claim (2) is false. The chain then
gives 3 = |D_{i₀}| < ns(G) = 2, which is false: the argument derives a false
inequality from its own hypotheses.

The conclusion vs < ns is still true here (1 < 2). The proof, not the
theorem, is broken as written, and the same useless placements can be added
to an optimal strategy on any graph.

### The repair inside the paper

The paper proves the normal form the argument needs, earlier and for another
purpose. **Corollary 2.4** (p. 210): "There is always an optimal
node-searching strategy in which no vertex is visited twice by a searcher,
and in which every searcher is deleted immediately after all the edges
incident on it have been cleared." Under that form claim (2) holds: a vertex
visited only once must keep its searcher until all its edges are clear, since
an edge is cleared only while both endpoints are guarded. The paper also
says, on p. 208, "In the sequel we shall consider only strategies of the above
type". But that sentence follows Corollary 2.2, about *edge*-searching, and
comes before node searching is defined. So it does not obviously cover the
node-searching strategy of Theorem 4.1, whose proof says only "optimal,
recontamination-free". Our strategy visits leaf a twice, so Corollary 2.4's
form excludes it (`kpStrategy_not_visitsOnce`).

The citation repair has a price. Corollary 2.4 rests on Theorem 2.3
(recontamination does not help), which rests on LaPaugh's theorem. So the
proof of ns ≥ vs + 1, repaired this way, depends on LaPaugh even for
recontamination-free strategies. The argument below does not.

### The corrected argument

Order by *clearing time*, not by first placement. For a recontamination-free
strategy, let τ(v) be the first time from which no contaminated edge touches
v. Since the strategy is recontamination-free, this never reverses. Order
the vertices v₁, …, v_n by τ, and consider time t = τ(v_i). Then:

- v_i carries a searcher at t, because its last contaminated edge was
  cleared at t, and clearing needs both endpoints guarded.
- Every vertex after position i with a neighbour at or before position i
  also carries a searcher at t. Either its own last contaminated edge was
  cleared at t, or it still touches a contaminated edge. In the second case,
  were it unguarded, the contamination would reach the clear edge to its
  earlier neighbour through it, a recontamination.

So at time t the vertices counted by the vertex separation at position i,
together with v_i, all hold searchers. Hence vs + 1 ≤ ns for every monotone
strategy, and the monotonicity theorem extends this to all strategies.

This is the argument formalised as `vertexSeparation_add_one_le_of_monotone`
in `NodeSearch.lean`. On the counterexample, the clearing times computed from
the game itself are 12, 8, 10 and 12 for c, a, b and d, and ordering by them
gives separator sets of size 1 = ns − 1 (`kpClearTime_eq`,
`dBy_clearTime_eq`).

### The Lean proof of the counterexample

`KirousisPapadimitriouGap.lean`, 483 lines. The game's definitions are those
of `NodeSearch.lean`, checked against the paper's §2: moves place or remove
a searcher, an edge is cleared when both endpoints are guarded, and
recontamination runs along searcher-free paths. The concrete facts are
computed by `decide` through a finite simulation proved to agree with the
game (`sim_correct`).

- `kpStrategy_noRecontamination_and_clears`, `searchCost_kpStrategy`: the
  strategy clears K_{1,3}, never recontaminates, and uses 2 searchers.
- `nodeSearch_star3`, `monotoneNodeSearch_star3` (both = 2), and
  `kpStrategy_optimal`. The lower bound is the general lemma
  `two_le_of_isNodeSearch`: clearing any edge needs two searchers.
- `kpLayout_kpStrategy`: the first-acceptance order is a, b, d, c.
- `card_kpD_three`, `kpD_max_iff`: |D₃| = 3, and i₀ = 3 is the only maximiser,
  so no other choice of i₀ helps.
- `kp_claim2_fails_star3`: at every point where exactly a, b, d have accepted
  a searcher, D₃ is not inside the guarded set.
- `kirousisPapadimitriou_claim2_false`: the headline. A graph with an edge
  and an optimal recontamination-free strategy exist for which every
  maximiser i₀ has ns(G) ≤ |D_{i₀}|, and claim (2) fails at every matching
  point.

Not proved in Lean: that Corollary 2.4's normal form makes claim (2) true in
general.

### What remains open

The step from monotone to arbitrary strategies ("recontamination does not
help", [10] Theorem 2.3, via LaPaugh) is not formalised. In Lean it is a named
hypothesis, `NodeSearchMonotonicity`, and
`nodeSearch_eq_vertexSeparation_add_one_of_monotonicity` derives the full
theorem from it. It does not rest on the faulty step above.

## 2. Smaller faults recorded elsewhere

- **Lengauer (1981), Theorem 4** (the vertex separator game on G against the
  triangle graph G_du) fails as stated for K = 0 on an edgeless graph.
  Lean: `isPositiveVSG_triangleGraph_counterexample` in
  `Complex/EdgeSeparation.lean`. The theorem holds whenever G has an edge or
  K > 0.
- **Node search is not vs + 1 on edgeless graphs**; there it is 0. Both
  Kirousis & Papadimitriou papers state their equalities without excluding
  this case. Lean: `monotoneNodeSearch_ne_vertexSeparation_add_one_of_edgeless`.

These are statement edge cases, not broken arguments. The Table 1 rows that
are false as stated (PLA folding in its simple form, edge separation as
cutwidth) are in `equivalences.md`: Table 1 cited them, and their sources
never claimed the equivalence.
