# The pathwidth complex: the equivalences of Table 1

Section 3 of *The pathwidth complex* (`plan.md`), built by Ralph loop0005.
Every row states what the source proves, not what Table 1 asserts, and where
it is checked (brute force, `complex_check.py`) and proved (Lean,
`../lean/MOSPFormalization/Complex/`).

Item 01 (statement census, 2026-09-30) read every source and filled in the
table below. Item 02 (brute-force check, 2026-09-30) computed every quantity
from its own definition and checked every statement exhaustively on small
inputs; its results fill the "Checked" column and the section *Item 02: the
brute-force check* at the end. Item 03 (2026-09-30) proved the gate matrix
row in Lean (section *Item 03* at the end). Page numbers are the printed
page numbers of the source; where only a preprint is held (Kornai & Tuza,
Fomin) the preprint's own page or section is given.

## What Table 1 claims, and how it is read here

Linhares & Yanasse (2002), p. 1764 (not p. 1762 as `literature/MANIFEST.md`
says; p. 1762 carries Fig. 1), introduce Table 1 as "a set of problems that
consist of, given input Π, compute a function f(Π) that is either equal to
the number of open stacks or closely related to it (plus or minus one)". The
reference column cites where each problem was studied; the table gives no
proofs and no graph.

Two readings are kept apart throughout:

- **literal ±1**: for every input, `f` lies in `{Z − 1, Z, Z + 1}`, where
  `Z = pw(G) + 1` is the number of open stacks of the corresponding MOSP
  instance (for a graph input `G`, the instance whose matrix is the
  vertex–edge incidence matrix of `G`, which has MOSP graph `G`);
- **fixed offset**: `f = Z + c` for a constant `c ∈ {−1, 0, 1}` on every
  input, which is what "equivalent" needs if computing one is to compute the
  other.

Status labels: **confirmed** (the fixed-offset reading holds, with the stated
edge cases); **weaker than stated** (literal ±1 holds, fixed offset does not:
a band or sandwich); **misattributed** (the cited paper proves something
else); **unsourced** (only the unheld [5] is cited for it); **false** (not
within ±1 of `Z`, with a counterexample family).

## Master table

`Z` = number of open stacks; `pw` = pathwidth of the graph in the "Graph"
column; `vs` = vertex separation of the same graph.

| # | Problem | Source (Table 1 ref) | Defined on | Graph | Relation (source, theorem) | Checked | Lean | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | MOSP | Yanasse 1997 EJOR [1]; Fink & Voss 1999 [4] | 0/1 matrix (piece types × patterns) | MOSP graph: piece types, adjacent iff they share a pattern | `Z = pw + 1`; not in [1] or [4] (definitions only); Yanasse 1997a Prop. 5, Fellows & Langston 1987 Lemma 4.1 + 1989 Thm 7, with L&Y 2002 Prop. 2 | corpus; 2,130 matrices, 0 fail | `mospValue_eq_pathwidth_add_one` | confirmed (needs one requirement) |
| 2 | Gate matrix layout | Möhring 1990 [6]; Wing, Huang & Wang 1985 [8] | 0/1 net–gate matrix | net adjacency (incompatibility) graph = MOSP graph with nets as piece types | `t(M) = Z(M)` on the same matrix (L&Y Prop. 2; Möhring Thm 3.2 + left-edge p. 31); `t = pw + 1` (Möhring Prop. 3.5; F&L 1989 Thm 7) | 2,130 matrices, 0 fail | `NetGateMatrix.tracks_eq_pathwidth_add_one`, `tracks_eq_mospValue`, `tracksFor_eq_maxOpenStacks` | confirmed; **proved** (needs one 1 in M) |
| 3 | One-dimensional logic | Ohtsuki et al. 1979 [7] | gates × nets list | connection graph `H` (nets, adjacent iff a common gate) | tracks `= θ(H) = pw(H) + 1` without boundary gates (§II, Thm 3); the boundary-gate version (§IV) is a constrained variant, `pw(H) + 1 ≤ tracks_B`, gap 1 attained | 452 instances, 0 fail; boundary: 1,027, gap ≤ 1 | — | confirmed (core problem); boundary variant weaker than stated (not a fixed offset; ±1 on every instance checked) |
| 4 | PLA folding | Möhring 1990 [6] | 0/1 net–gate matrix | incompatibility graph `G` | simple folding (≤ 2 nets per track, PLAMPP p. 25): `tracks = |V(G)| − s` (Prop. 3.15), `≥ max(θ, ⌈|V|/2⌉)`; multiple folding (path partition): `= θ` (Thm 3.14) | 2,130 matrices; `I_5`: 3 vs 1 | — | **false** as stated (simple folding); confirmed for multiple folding |
| 5 | Interval thickness | Kashiwabara & Fujisawa 1979 [5], not held | graph | itself | `θ = pw + 1` (Möhring Prop. 3.5, proved there); `θ = ns` (K&P 1985 Thm) | 1,652 graphs, 0 fail | — | unsourced at [5]; relation confirmed in [6], [9] |
| 6 | Node search game | Kirousis & Papadimitriou 1985 [9] | graph | itself | `ns = θ` ([9] Thm, p. 182); `ns = vs + 1` ([10] Thm 4.1); both use monotonicity ([10] Thm 2.3 ← LaPaugh) | 1,652 graphs, 0 fail (both games) | — | confirmed for graphs with an edge; false on edgeless graphs (`ns = 0`) |
| 7 | Edge search game | Kirousis & Papadimitriou 1986 [10] | graph (multigraphs allowed) | itself | `ns − 1 ≤ es ≤ ns + 1` ([10] p. 209) ⇔ `vs ≤ es ≤ vs + 2` (Ellis, Sudborough & Turner 1994 Thm 2.1); all three values occur; `es(G) = vs(2-expansion of G)` (EST Thm 2.2) | 1,632 graphs; `es − vs ∈ {0,1,2}` | — | weaker than stated (band of width 2) |
| 8 | Narrowness | Kornai & Tuza 1992 [11] | graph | itself | `ν = pw + 1` for ≥ 1 vertex (Prop. 3.1) | 1,652 graphs, 0 fail | — | confirmed |
| 9 | Split bandwidth | Fomin 1998 [12] | connected graph, ≥ 2 vertices | itself | `pw ≤ sb ≤ pw + 1` (Thm 8); `sb = ib = 1/μ_m` (Thms 3, 6) | 1,302 graphs via `ib`; `ib − pw ∈ {0,1}` | — | weaker than stated (sandwich) |
| 10 | Graph path-width | Kinnersley 1992 [13] | graph | itself | definition (Robertson & Seymour), p. 346 | reference | `Pathwidth.lean` | definition |
| 11 | Edge separation | Lengauer 1981 [14] | graph | itself | [14] defines no edge-separation number related to `pw`: its edge game is min-cut linear arrangement (cutwidth, p. 468), its Def. 6 is modified cutwidth; neither is within ±1 (stars); its vertex game VSG is `vs` exactly | `cw`, `mcw` fail ±1 on 341, 738 of 1,644 | — | **misattributed and false** under every reading [14] supports |
| 12 | Vertex separation | Kinnersley 1992 [13] | graph | itself | `vs = pw` (Thm 3.1); Lengauer's VSG `= vs` by reversal | 1,652 graphs, 0 fail | `vertexSeparation_eq_pathwidth` | confirmed |

Summary: **six confirmed** (MOSP, gate matrix layout, one-dimensional logic,
narrowness, node search with the edgeless exception, vertex separation), plus
path-width as the reference definition; **one unsourced** at its citation but
proved elsewhere (interval thickness); **two weaker than stated** (edge search,
a band; split bandwidth, a sandwich), both of which still meet the literal ±1
wording; **two false as stated** (PLA folding in its standard two-nets-per-track
form; edge separation, which is also misattributed).

## The census, problem by problem

### 1. MOSP — [1] Yanasse 1997 (EJOR), [4] Fink & Voss 1999

- **Definition.** [1] p. 455: "We assume that a stack is opened for every new
  panel type cut and it remains opened until the last piece of that panel type
  is cut. We also assume that a completed stack can be removed only after a
  pattern is completely cut, hence, the maximum number of stacks occurs just
  after some pattern is cut and before any completed part stack is removed."
  [4] §1.1.1 (preprint p. 2), with `C` an m × n matrix whose **rows are
  patterns** and columns order types: "an order j may be defined open at
  position i₀ of the pattern sequence if (Σ_{i ≤ i₀} c_{π_i,j})(Σ_{i ≥ i₀}
  c_{π_i,j}) > 0". Linhares & Yanasse 2002, p. 1760, eqs. (1)–(2), with the
  I × J matrix P whose **rows are piece types**: `q_ij = 1` iff some patterns
  x, y containing piece i satisfy `π(x) ≤ j ≤ π(y)`, and `Z_MOSP(P) = min_π
  max_j Σ_i q_ij`. The three agree up to transposition of the matrix.
- **Input.** 0/1 matrix. **Graph.** The MOSP graph: piece types (customers),
  adjacent iff some pattern contains both (Yanasse 1997a Prop. 5).
- **Relation.** Neither [1] nor [4] relates MOSP to any graph parameter; [1]
  relates it to tool switching (Props. 1–2). The relation `Z = pw + 1` is
  Yanasse 1997a Prop. 5 (the MOSP graph) with L&Y 2002 Prop. 2 (MOSP = GMLP)
  and Fellows & Langston 1989 Thm 7 (GMLP cost k ⇔ pathwidth k − 1), whose
  sketch rests on F&L 1987 Lemma 4.1. Proved in Lean,
  `mospValue_eq_pathwidth_add_one`, hypothesis: at least one requirement
  (with none, `Z = 0` while `pw + 1 = 1`).
- **Status.** Confirmed. The Table 1 references are sources for the problem,
  not for the equivalence.

### 2. Gate matrix layout — [6] Möhring 1990, [8] Wing, Huang & Wang 1985

- **Definition.** Möhring p. 18: an m × n net–gate matrix M, rows nets,
  columns gates; for a gate permutation π the augmented matrix M^π fills in
  every 0 between a row's leftmost and rightmost 1; "Nets of the augmented
  net-gate matrix may share the same row (called track) if they have no gate
  in common"; MPP: "Find a permutation of the columns and an assignment of the
  augmented rows (nets) to tracks such that the number of tracks is minimum",
  value `t(M)`. The gate matrix permutation problem GMPP (pp. 23–24) is the
  MPP with no restriction. Wing et al. p. 222, Problem 1: "Given the net-gates
  sets X(n_i), n_i ∈ N, of a circuit, find a pair of gate and net assignment
  functions f: G → C and h: N → R, respectively, such that card[R] is
  minimum." L&Y 2002 p. 1762 eq. (3): `Z_GMLP(P) = max_j Σ_i q_ij`, the same
  formula as `Z_MOSP`.
- **Input.** 0/1 matrix. **Graph.** Möhring p. 29: "the intersection graph of
  the rows ... called the net adjacency graph [DKL87], or incompatibility
  graph"; Wing p. 222 "connection graph H" (after Ohtsuki). This is the MOSP
  graph with nets in the role of piece types and gates in the role of
  patterns.
- **Relation.** Möhring Thm 3.2 (p. 29): `t(M) = min{χ(H) | H interval, E(G) ⊆
  E(H)}`; p. 31 (left-edge algorithm): "the minimum number of tracks for an
  augmented net-gate matrix M^π is equal to the maximum column sum of M^π", so
  `t(M) = Z_MOSP(M)` on the same matrix, no transposition (rows = nets =
  piece types, columns = gates = patterns); this is L&Y Prop. 2 (p. 1763,
  "follows trivially from their definitions"). Prop. 3.5 (p. 32): "pw(G) =
  t(G) − 1", proved there in both directions. F&L 1989 Thm 7 states the same
  for graphs (matrix with two 1s per column, one column per edge; Kinnersley
  p. 346 uses exactly this form).
- **Caveat.** Wing's full problem (p. 221) also demands that the layout be
  *realizable* (vertical diffusion runs must not overlap transistors); their
  Problem 1 drops that constraint, and it is Problem 1 that Table 1's
  problem is. Möhring (p. 24) likewise sets aside the p/n split and nets that
  need more than one row.
- **Status.** Confirmed: `t(M) = Z(M) = pw(G_M) + 1`, exact. For item 03: the
  map is the identity on the matrix in L&Y's and Möhring's orientation; it is a
  transposition only against Fink & Voss's orientation.

### 3. One-dimensional logic — [7] Ohtsuki, Mori, Kuh, Kashiwabara & Fujisawa 1979

- **Definition.** §II (pp. 676–677): gates `T = {t_l, t_1, …, t_m, t_r}` with
  boundary gates `t_l, t_r`, nets `V = {v_1, …, v_n}`, `V(t)` the nets at gate
  t, assumptions `|V(t)| ≥ 1` and `|T(v)| ≥ 2` (eqs. 3–4); each placement
  (gate permutation) gives each net a closed interval, "the necessary number of
  tracks is the chromatic number of the corresponding interval graph", equal to
  its clique number. Connection graph (eqs. 5–6): `H = (V, E)`, `E = {(x, y) |
  ∃t: x, y ∈ V(t)}`. The problem (p. 677): "given a graph H, find a supergraph
  by adding a set of edges, which is an interval graph and has the least
  clique number", with the boundary gates ignored "for the time being".
- **Input.** Gate–net incidence (a 0/1 matrix). **Graph.** `H` = MOSP graph
  with nets as piece types.
- **Relation.** Every placement gives an interval supergraph of `H` with tracks
  = clique number (p. 676); Thm 3 (p. 678): from a *minimal* augmentation, a
  gate sequence realises exactly that interval graph. Together: min tracks =
  `θ(H)`, hence `pw(H) + 1` by Möhring Prop. 3.5. Not stated as one numbered
  theorem in [7]. It is the same matrix problem as gate matrix layout (Wing
  et al. cite [7] as [3] for exactly this).
- **Boundary gates.** §IV (p. 680) adds the constraint that `t_l, t_r` sit at
  the two ends (a "B augmentation"), assuming `V(t_l) ∩ V(t_r) = ∅` (eq. 14).
  *Corrected by item 02.* Item 01 claimed a family `kK_2` (k nets
  `a_i ∈ V(t_l)`, k nets `b_i ∈ V(t_r)`, inner gates `{a_i, b_i}`) with
  tracks `k + 1` against `pw + 1 = 2`. That misread `H`: eq. (6) ranges over
  all of `T`, boundary gates included, so the `a_i` form a clique, as do the
  `b_i`, and `H` is two `K_k` joined by a perfect matching, with `pw(H) + 1 =
  k + 1` = the tracks (checked k = 1..4; pinning the boundary gates costs
  nothing there). The pin does cost something elsewhere: nets a–e with
  connection graph the path a-b-c-d-e, `t_l = {c}`, `t_r = {a}`, inner gates
  `{a,b}, {b,c}, {c,d}, {d,e}, {e}` need 3 tracks pinned and 2 free
  (`boundary_path_instance`). Over 1,027 random instances (3–6 nets, 4–7
  gates) the pinned optimum exceeds `pw(H) + 1` by 0 on 980 and by 1 on 47,
  never by more. Always `≥ pw(H) + 1` (a pinned placement is a placement).
  An upper bound of `pw(H) + 1 + |V(t_l)| + |V(t_r)|` is expected (stretch the
  pinned nets' intervals to the ends of an optimal model) but not proved
  here: realising the stretched model as a pinned gate sequence needs
  Ohtsuki's B-augmentation argument. Whether a gap of 2 occurs is open.
- **Status.** Confirmed for the problem as posed in §II–III; the boundary
  version is a constrained variant, the analogue of Möhring's Weinberger MPP:
  not a fixed offset (gap 0 or 1), within ±1 on everything checked.

### 4. PLA folding — [6] Möhring 1990

- **Definition.** PLAMPP, p. 25: "Find a permutation of the gates G_1, …, G_n
  and a feasible assignment of at most two nets to a track (PLA layout) such
  that the number of tracks is minimum." Prop. 3.15 (p. 38): "the minimum
  number of tracks for a PLA folding is equal to |V(G)| − s, where s is the
  maximum number of green directed arcs that can be added to G" forming a
  matching in the complement of G with no alternating cycle. Block,
  constrained and constrained-block folding (pp. 25–26) are further
  restrictions. Separately, p. 36: a *path partition* ("multiple folding") of
  G, tracks as directed paths of any length in the complement.
- **Input.** 0/1 matrix. **Graph.** The incompatibility graph.
- **Relation.** Multiple folding: Thm 3.14 (p. 36), a path partition with t
  paths gives an interval augmentation with ω = t and conversely, so its
  minimum is `θ = pw + 1`, exact. Simple (two-per-track) folding: every PLA
  layout is a feasible MPP layout, so `tracks ≥ t(M) = pw + 1`, and each track
  holds at most two nets, so `tracks ≥ ⌈|V|/2⌉`. Möhring proves only
  reductions for it (Thm 4.5: gate matrix layout of G reduces to constrained
  folding of a bipartite double of G, `t(G) = |V(G)| − |F|`), never an
  equivalence on the same instance.
- **Counterexample (to be checked by item 02).** The 5 × 5 identity matrix
  (five nets, each on its own gate): the incompatibility graph is edgeless,
  `t = pw + 1 = 1`, but two-per-track folding needs `⌈5/2⌉ = 3` tracks, a gap
  of 2. Connected family: the path P_n as a matrix with one gate per edge,
  `t = 2`, folding `≥ ⌈n/2⌉`, gap ≥ 2 from n = 7.
- **Status.** False as stated for PLA folding in the sense Möhring defines it
  (and the sense the PLA literature he cites uses, [HNS82]); confirmed if
  "PLA folding" means multiple folding. Item 09 decides which to formalise;
  both, preferably.

### 5. Interval thickness — [5] Kashiwabara & Fujisawa 1979 (not held)

- **Definition.** From [9] p. 182: "The interval thickness of a graph G,
  denoted by θ(G), is the smallest max-clique over all interval supergraphs
  of G." Möhring p. 31: "The smallest clique size ω(H) of an interval graph
  augmentation of G is also called the interval thickness of G", with an
  interval graph defined by intervals of a linear order, adjacent iff they
  intersect (p. 28, eq. 3.2). Supergraph means same vertex set, more edges.
- **Relation.** Möhring Prop. 3.5 (p. 32), `pw(G) = t(G) − 1`, proved there:
  bags of a path decomposition as maximal cliques of an interval supergraph
  (Fulkerson–Gross, Thm 3.4), and a consecutive clique arrangement as a path
  decomposition. [9] Thm: `θ = ns`.
- **Edge cases.** Empty vertex set: `θ = 0`, while the Lean `pathwidth` is ℕ-
  valued and 0 there, so `θ = pw + 1` needs at least one vertex.
- **Status.** Unsourced at its Table 1 citation; the relation itself is proved
  in [6] and follows from [9] + [10].

### 6. Node search game — [9] Kirousis & Papadimitriou 1985

- **Definition.** [9] p. 181: "A searching strategy S is a sequence of moves
  where the player either places a searcher on a node of the graph that
  carries no searcher or deletes the searcher of a guarded node. The edges of
  the graph are initially considered contaminated by a gas. The object of a
  searching strategy is to clear all edges. The clearing of an edge is
  accomplished once both its endpoints concurrently carry a searcher. A clear
  edge may be recontaminated once there appears a path that carries no
  searchers and that connects this edge with a contaminated one." ns(G): the
  least maximum number of searchers (p. 182). Same in [10] §2 p. 208.
- **Relation.** [9] Theorem (p. 182): "For any graph G, ns(G) = θ(G)." Its
  proof of `θ ≤ ns` takes an optimal *recontamination-free* strategy, which
  exists by [10] Thm 2.3 (`pns = ns`), itself derived from LaPaugh's theorem
  for edge search ([10] Thm 2.1). [10] Thm 4.1 (p. 216): "For an arbitrary
  graph G, ns(G) = vs(G) + 1"; its `vs ≤ ns − 1` direction also uses an
  optimal recontamination-free strategy. The Lemma of [9] (p. 182): a strategy
  in which each node takes a searcher once and loses it only after all its
  neighbours have taken one is recontamination-free.
- **Which paper proves what** (item 01's question): **[9] (1985) proves
  interval thickness = node search number; [10] (1986) proves node search =
  vs + 1** (Thm 4.1), monotonicity of node search (Thm 2.3), `es(G) =
  ns(G_v) − 1` for the three-edge subdivision `G_v` (Thm 2.5), and `mpb = ns =
  mpbw` (Thm 3.1). Table 1's pairing of node search with [9] is right.
- **Edge case.** On an edgeless graph there is nothing to clear, so by the
  letter of the definition `ns = 0`, while `vs + 1 = θ = 1` (with ≥ 1 vertex).
  Both theorems hold for every graph with at least one edge (then `ns ≥ 2`).
  Möhring's Thm 3.9 (p. 34) restates [9] with the same gap.
- **Status.** Confirmed, for graphs with at least one edge. The monotone game
  gives both equalities by elementary arguments (items 10, 12); the full game
  needs monotonicity (item 14).

### 7. Edge search game — [10] Kirousis & Papadimitriou 1986

- **Definition.** [10] §2 p. 208 (after Megiddo et al.; Parsons 1976): moves
  are sliding a searcher along an edge, placing a searcher, deleting a
  searcher; "An edge with at least one guarded endpoint is cleared by sliding
  along it a searcher, and then placing this searcher on the unguarded
  endpoint ... If all other edges incident on the first guarded vertex are
  clear, the guard itself may be used for the sliding"; recontamination by
  unguarded paths; es(G) the least maximum number of searchers. EST 1994 p. 53
  gives the same game, and allows multigraphs and loops, which can change es
  but not vs (p. 50).
- **Relation.** [10] p. 209 (unnumbered, proved in the text): "for any graph
  G, ns(G) − 1 ≤ es(G) ≤ ns(G) + 1", with examples of all three cases (Fig. 1:
  es 1, ns 2; Fig. 2: 2, 2; Fig. 3: es 5, ns 4). With Thm 4.1 this is `vs ≤ es
  ≤ vs + 2`, stated in [10] p. 216 as due to Turner, and proved as EST 1994
  Thm 2.1 (p. 54) from Lemma 2.1 (`vs ≤ s`, which uses LaPaugh's theorem) and
  Lemma 2.2 (`s ≤ vs + 2`, the procedure `search1`). Tightness: K_{3,3} has
  vs 3, s 5 (EST p. 57, via cutwidth for max degree 3), and there is a tree
  with the same difference (EST §3.3, Fig. 3.6). Exact under a transformation:
  EST Thm 2.2, `s(G) = vs(G')` with G' the 2-expansion (each edge subdivided
  twice).
- **Status.** Weaker than stated. `es ∈ {pw, pw + 1, pw + 2} = {Z − 1, Z, Z + 1}`
  meets the literal ±1 wording; it is not a fixed offset (K_2: es = 1 = Z − 1;
  K_{3,3}: es = 5 = Z + 1).

### 8. Narrowness — [11] Kornai & Tuza 1992

- **Definition.** §2 (preprint p. 2): for an in-sequence `(v_1, …, v_n)`, "In
  the i-th step, put vertex v_i from the IM into the shack; move all v_j (j ≤
  i) with no neighbors v_k, k > i, from the shack to the OM; then go to the
  (i+1)-st step. The maximum number of vertices in the shack during this
  process ... will be called the narrowness of the in-sequence". "Definition.
  [TK] The narrowness ν(G) of a graph G = (V, E) is the minimum value of
  ν(v_1, …, v_n) taken over all permutations." Prop. 2.1: in- and
  out-sequences give the same value (reverse the sequence).
- **Relation.** Prop. 3.1 (p. 3): "For every graph G with at least one vertex,
  ν(G) = π(G) + 1", proved both ways from path decompositions.
- **Note for item 04.** The maximum is reached just after an insertion, so
  `ν(v_1, …, v_n) = 1 + max_i |{j < i : v_j has a neighbour v_k, k ≥ i}|`,
  which is the vertex separation of the same sequence plus one; per sequence,
  not only at the optimum. The empty graph (ν = 0) is excluded by the source.
- **Status.** Confirmed, exact.

### 9. Split bandwidth — [12] Fomin 1998

- **Definition.** §3.2 (preprint p. 7): node splitting of v: partition its
  neighbourhood into M and N (either may be empty), "delete vertex v with all
  incident edges, add new vertices u and w with edge (u, w), and make u
  adjacent to all vertices of M and w to all vertices of N". "A graph Γ* is
  said to be a split of Γ if Γ* can be obtained from Γ by a sequence of node
  splittings. The split bandwidth of graph Γ, denoted by sb(Γ), is min{b(Γ*) :
  Γ* is a split of Γ}." Bandwidth b as usual (§2). The paper considers "only
  connected graphs with at least two vertices" (p. 1).
- **Relation.** Thm 8 (p. 11): "For any graph Γ, pw(Γ) ≤ sb(Γ) ≤ pw(Γ) + 1."
  Upper bound: a path decomposition with all bags of size k + 1 gives a
  numbering of interval bandwidth ≤ k + 1, and `sb = ib` (Thm 6). Lower bound:
  Γ is a minor of any split, and `pw ≤ bandwidth`. Also Thm 3: `1/μ_m = ib`
  (monotone helicopter search), Thm 2: `1/μ_1 = b`. Fomin's concluding
  remarks leave open when `pw = sb`.
- **Both values occur** (by hand; item 02 to check): K_2 has `sb = b = 1 =
  pw`. K_{1,3} has `pw = 1` but `sb = 2`: splits of a tree are trees, a
  splitting never reduces the number of leaves, and a tree of bandwidth 1 is a
  path, which has two.
- **Status.** Weaker than stated (a sandwich). `sb ∈ {Z − 1, Z}` meets the
  literal ±1 wording.

### 10. Graph path-width — [13] Kinnersley 1992

- **Definition.** p. 346: "a sequence X_1, …, X_r of subsets of V is a
  path-decomposition of G if (a) ∪X_i = V, (b) for every edge e of E, some X_i
  contains both endpoints of e, and (c) for 1 ≤ i ≤ j ≤ k ≤ r, X_i ∩ X_k ⊆
  X_j. The path-width of G ... is the minimum value h ≥ 0 such that G has a
  path-decomposition X_1, …, X_r with |X_i| ≤ h + 1". Matches
  `PathDecomposition.lean` (bags indexed by `Fin (length + 1)`, at least one
  bag; ℕ-valued width, so `pw = 0` on the empty graph).
- **Status.** The reference definition.

### 11. Edge separation — [14] Lengauer 1981

This is item 01's first specific question. What [14] contains:

- **Definition 1** (p. 468): the undirected graph `G_u` of a dag (edges plus a
  clique on each vertex's immediate predecessors), and (p. 469) the dag `G_d`
  of an undirected graph (a new sink over each edge).
- **The vertex separator game VSG** (p. 467), unnumbered: "(i) All vertices
  start out pebble-free. (ii) All vertices end up pebbled. (iii) A move
  consists of placing a pebble on a pebble-free vertex. The vertex cut after
  the i-th move consists of all vertices that are pebble-free and adjacent to
  a pebbled vertex after the i-th move." `(G, K)` is positive "if VSG(S) ≤ K",
  K a positive integer; VSG(G) is the least such K. The vertex cut is exactly
  the Lean `activeSuffix`, and reversing the strategy turns it into
  Kinnersley's `V_L(i)`, so **VSG(G) = vs(G)** for every graph with an edge
  (on edgeless graphs VSG = 1 by the positivity of K, vs = 0).
- **The edge version** (p. 468): "if we use edge separators instead of vertex
  separators in the above definition, we define a well known problem on
  undirected graphs, namely, the min-cut linear arrangement problem" —
  **cutwidth**. §4 (p. 475) repeats: VSG "is the vertex separator version of
  an edge separator game that is better known as the min-cut linear
  arrangement problem".
- **Theorems 2–4** (pp. 469, 472), all exact:
  Thm 2: `(G, K)` positive for PBWP ⇔ `(G_u, K − 1)` positive for VSG, so
  `pbw(G) = VSG(G_u) + 1`;
  Thm 3: `(G, K)` positive for VSG ⇔ `(G_d, K + 2)` positive for PBWP;
  Thm 4: `(G, K)` positive for VSG ⇔ `(G_du, K + 1)` positive for VSG, where
  `G_du` adds a triangle on every edge, so `vs(G_du) = vs(G) + 1` for G with an
  edge.
- **Definition 6** (p. 473), MMCLA, *modified* min-cut: a labelling λ with
  `width(v_i) = |{{v_j1, v_j2} ∈ E : λ(v_j1) < i < λ(v_j2)}|`, edges passing
  strictly over a vertex, not between two vertices. **Theorem 7** (NP-
  completeness of VSG) builds G' by replacing each vertex by an (N + 1)-clique
  and proves `(G, K)` positive for MMCLA ⇔ `(G', K + N)` positive for VSG, i.e.
  `vs(G') = mcw(G) + N` with `N = |V(G)|`: an offset of N under a blow-up, not
  a ±1 relation on the same graph. (L&Y 2002 Prop. 1 uses modified cutwidth,
  from Garey & Johnson, for its own NP-hardness proof of MOSP.)
- **What "edge separation" can mean, and why each reading fails.**
  (a) Cutwidth: `cw(K_{1,n}) = ⌈n/2⌉` while `pw = 1`; `K_{1,7}` (8 vertices)
  already gives `cw = 4 = Z + 2`. (b) Modified cutwidth (Def. 6):
  `mcw(K_{1,n}) = ⌈n/2⌉ − 1`, so `K_{1,9}` (10 vertices) gives `mcw = 4 = Z +
  2`. (c) Lengauer's vertex game is vs exactly, but that is Table 1's
  "vertex separation" row, attributed there to [13]. Neither (a) nor (b) is a
  lower-bound failure: `vs ≤ cw` is standard, and `vs ≤ mcw + 1` is a
  candidate for item 02 to test (it holds on paths and stars).
- **Status.** Misattributed ([14] is about vertex separation and
  black–white pebbling) and false under the readings (a) and (b) that [14]
  supports. Item 08 formalises VSG = vs and Thms 2–4 where in reach, and a
  star counterexample for the cutwidth readings.

### 12. Vertex separation — [13] Kinnersley 1992

- **Definition.** p. 346: `V_L(i) = {u ∈ V | L(u) ≤ i and there is some v ∈ V
  such that uv ∈ E and L(v) > i}`, `vs_L(G) = max_{1 ≤ i < |V|} |V_L(i)|`,
  `vs(G) = min_L vs_L(G)`. [10] p. 216 and EST p. 52 agree. The Lean
  `vertexSeparation` counts the suffix side (Lengauer's convention); the two
  agree by reversing the layout.
- **Relation.** Thm 3.1 (p. 346): "For any graph G, vs(G) = pw(G)"; the proof
  treats simple connected graphs, and the statement extends to disconnected
  ones by concatenating layouts. Cor. 3.2 (p. 347): `gml(G) = ns(G) = vs(G) +
  1`, from Thm 3.1 with F&L 1989 Thm 7 and [10] Thm 4.1.
- **Status.** Confirmed; `vertexSeparation_eq_pathwidth` in `VSEquivPW.lean`.

## Item 01's specific questions, answered

1. **Edge separation (Lengauer 1981).** No "edge separation" number related to
   pathwidth appears in [14]. Its edge game is min-cut linear arrangement
   (cutwidth); its Definition 6 is modified cutwidth; both have unbounded gap
   to pathwidth on stars. Its Theorems 2–4 are exact relations between PBWP
   and VSG under transformations, and VSG is vertex separation. Table 1's row
   is misattributed and, under either edge reading, false.
2. **Möhring (1990) on PLA folding and gate matrix layout.** Gate matrix
   layout: `t(M)` = min over interval supergraphs of the incompatibility
   graph of the chromatic (= clique) number (Thm 3.2), = max column sum of
   the augmented matrix under the best permutation (p. 31), = `pw + 1`
   (Prop. 3.5, proved), = node search number (Thm 3.9, citing [9]). PLA
   folding (at most two nets per track): `|V| − s` for a maximum folding set
   (Prop. 3.15, citing [HNS82]), equivalent to a maximum Z_{m,m} subgraph
   (Prop. 3.16), NP-hard (Thms 4.5–4.6); **no ±1 relation** to `pw`. Multiple
   folding (path partitions) is equivalent to interval graph augmentation
   exactly (Thm 3.14).
3. **Ohtsuki et al. (1979) on one-dimensional logic.** Tracks = clique number
   of the interval graph of the placement (§II); the optimum = least clique
   number of an interval supergraph of the connection graph (§II–III, with
   Thm 3 for realisability); NP-complete (citing [11] = [5] of Table 1).
   Boundary gates are a constrained variant (§IV).
4. **Kirousis & Papadimitriou.** 1985 [9]: interval thickness = node search
   number. 1986 [10]: node search = vs + 1 (Thm 4.1), and the edge-search band
   `ns − 1 ≤ es ≤ ns + 1`.

## Statements for item 02 to check

Every statement below is a candidate for a Lean theorem. Item 02 implements
each quantity from its own definition above (not via pathwidth) and checks
on all graphs to 6 vertices, random graphs to 8, matrices to 5 × 5.

1. `Z(M) = t(M)` (gate matrix layout, tracks by feasible track assignment) on
   every matrix; `Z(M) = pw(G_M) + 1` when M has a 1.
2. One-dimensional logic without boundary gates `= θ(H) = pw(H) + 1`; with
   boundary gates, the `kK_2` family exceeds `pw + 2` from k = 3. *(Item 02:
   false as stated — `H` includes the boundary gates; see §3.)*
3. Simple PLA folding: `tracks ≥ max(pw + 1, ⌈|V|/2⌉)`; the 5 × 5 identity has
   tracks 3 against `pw + 1 = 1`; multiple folding `= pw + 1`.
4. `θ = pw + 1` for ≥ 1 vertex.
5. `ns = θ = vs + 1` for graphs with ≥ 1 edge, both for the monotone game and,
   where feasible, with recontamination; `ns = 0` on edgeless graphs.
6. `vs ≤ es ≤ vs + 2`, all three values attained (K_2, K_{3,3}); `es(G) =
   vs(2-expansion)`; `ns − 1 ≤ es ≤ ns + 1`.
7. `ν = pw + 1` for ≥ 1 vertex, and per sequence `ν(seq) = vs(seq) + 1`.
8. `pw ≤ sb ≤ pw + 1` on connected graphs with ≥ 2 vertices; `sb(K_2) = 1`,
   `sb(K_{1,3}) = 2`. (Splits are unbounded in number; the checker needs a
   bound — at most `|E|` splittings suffice? — or `ib` via numberings of
   bounded length. To settle in item 02.)
9. `vs = pw`; `VSG = vs` on graphs with an edge.
10. Lengauer Thm 4: `vs(G_du) = vs(G) + 1` for G with an edge; Thm 7's
    `vs(G') = mcw(G) + N` on small G.
11. `cw` and `mcw` are not within ±1 of `pw + 1` (stars `K_{1,7}`, `K_{1,9}`);
    `vs ≤ cw`; candidate `vs ≤ mcw + 1`.

## Item 02: the brute-force check

`paper2/complex_check.py` (`python -m paper2.complex_check`, 2.5 min on 32
cores; report in `paper2/data/complex_check.json`; tests in
`tests/test_complex_check.py`). Every quantity is computed from the source's
own definition, never through pathwidth:

| Quantity | Implemented as | Source |
|---|---|---|
| `pw` | search over bag sequences, state (introduced, current bag), interval property enforced | Kinnersley p. 346 |
| `vs` | literal minimum over all permutations of `max_i |V_L(i)|` (prefix side) | Kinnersley p. 346 |
| VSG | literal minimum over pebbling orders of the largest vertex cut | Lengauer p. 467 |
| `θ` | (a) interval models with integer endpoints in `0..n−1`, adjacent ⇒ intersecting, clique = max point load, n ≤ 6; (b) interval models as open/close event words, all n; (a) = (b) on all 208 graphs to 6 vertices | K&P 1985 p. 182; Möhring p. 31 |
| `ν` | literal shack process over all in-sequences; out-sequences to 6 vertices | Kornai & Tuza §2, Prop. 2.1 |
| `ns` | game-state search over (guarded set, contaminated edges), place/remove, clearing, recontamination through unguarded vertices; and the monotone game (recontaminating moves forbidden) | K&P 1985 p. 181 |
| `es` | the same with searcher multiplicities and slides; slide clears the edge, then recontamination; both games | K&P 1986 p. 208 |
| `ib` | Fomin's numberings (surjections of any length), decided exactly by a finite automaton over per-vertex gap ages, so no length bound is needed | Fomin §3.1 |
| `sb` | explicit node splittings (up to 3, isomorphism-deduplicated) and bandwidth; an upper bound, compared with `ib` | Fomin §3.2 |
| `Z` | L&Y eqs. (1)–(2) over all column orders | L&Y 2002 p. 1760 |
| `t` | column order plus an explicit track assignment (tracks hold gate-disjoint augmented nets), minimised; not the max column sum | Möhring p. 18 |
| PLA | the same with at most two nets per track | Möhring p. 25 |
| 1-dim logic | the same on Ohtsuki instances (`|V(t)| ≥ 1`, `|T(v)| ≥ 2`), optionally with `t_l`, `t_r` pinned | Ohtsuki §II, §IV |
| `cw`, `mcw` | literal minimum over permutations (DP over prefix sets for the 8- and 10-vertex stars) | Lengauer p. 468, Def. 6 |

The three prefix-set DPs (`vs_dp`, `cutwidth_dp`, `modified_cutwidth_dp`)
are exact because each layout's cost is a max of terms that depend only on
the prefix and the next vertex; the tests check each against the literal
minimum. `vs_dp` is used only on the constructed graphs (2-expansions,
`G_du`, Lengauer's blow-up), never for the `vs = pw` check itself.

**Inputs.** All 1,252 graphs on 1–7 vertices (networkx atlas); 400 random
graphs on 7 and 8 vertices (`p ∈ {0.25, 0.4, 0.55, 0.7}`, seed 20260930);
630 matrices up to 4 × 4, one per class under row and column permutation,
plus 1,500 random 5 × 5, 2,130 in total; 1,027 random Ohtsuki instances with
two disjoint boundary gates. Edge search runs to 20 edges (1,632 graphs),
the 2-expansion check to `n + 2m ≤ 18` (181), `G_du` to `n + m ≤ 16` (680).

**Results** (checked / failed):

| # | Statement (item 01 list) | checked | failed |
|---|---|---|---|
| 1 | `Z = t` | 2,130 | 0 |
| 1 | `Z = pw(G_M) + 1` when M has a 1 | 2,130 | 0 |
| 2 | 1-dim logic tracks `= θ(H) = pw(H) + 1` | 452 | 0 |
| 2b | pinned boundary tracks `≥` free tracks `= pw(H) + 1` | 1,027 | 0 |
| 2b | pinned boundary tracks within 1 of `pw(H) + 1` | 1,027 | 0 (gap 1 on 47) |
| 3 | PLA `≥ max(pw + 1, ⌈nets/2⌉)` | 2,130 | 0 |
| 3 | multiple folding (`= t`) `= pw + 1` | 2,130 | 0 |
| 4 | `θ = pw + 1`, ≥ 1 vertex (event words / model search) | 1,652 / 208 | 0 / 0 |
| 5 | `ns = vs + 1` and `ns = θ`, ≥ 1 edge | 1,644 | 0 |
| 5 | monotone `ns` = `ns`; `ns = 0` edgeless | 1,652; 8 | 0; 0 |
| 6 | `vs ≤ es ≤ vs + 2`; `ns − 1 ≤ es ≤ ns + 1`; monotone `es` = `es` | 1,632 | 0 |
| 6 | `es = vs(2-expansion)` | 181 | 0 |
| 7 | `ν = pw + 1`; in- = out-narrowness | 1,652; 208 | 0; 0 |
| 7 | per sequence `ν(seq) = vs(seq) + 1` | tests (C5, all 120 orders) | 0 |
| 8 | `pw ≤ ib ≤ pw + 1`, connected, ≥ 2 vertices; `ib ≤ bw` | 1,302 | 0 |
| 9 | `vs = pw`; VSG `= vs` (≥ 1 edge) | 1,652; 1,644 | 0; 0 |
| 10 | `vs(G_du) = vs + 1` (Lengauer Thm 4) | 680 | 0 |
| 10 | `vs(G') = mcw(G) + N` (Thm 7) | 7 graphs, N ≤ 4 | 0 |
| 11 | `vs ≤ cw`; `vs ≤ mcw + 1` | 1,652 | 0 |
| 11 | `cw` within 1 of `pw + 1` | 1,644 | 341 |
| 11 | `mcw` within 1 of `pw + 1` | 1,644 | 738 |

Values attained: `es − vs ∈ {0, 1, 2}` (K_2: 0; K_{1,3}: 1; K_{3,3}: 2,
es 5 as EST state); `ib − pw ∈ {0, 1}` (K_2, K_4: 0; K_{1,3}, K_{3,3}: 1);
`cw − (pw + 1)` from −1 to 7; `mcw − (pw + 1)` from −2 to 3 (K_2 has mcw 0
against Z = 2, so even the literal ±1 reading fails downward). Named values:
`cw(K_{1,7}) = 4`, `mcw(K_{1,9}) = 4`, as item 01 computed. PLA: identity
matrices `I_3, I_4, I_5` fold to 2, 2, 3 tracks against `t = 1`; incidence
matrices of `P_5, P_6, P_7` to 3, 3, 4 against `t = 2` — the gap of 2 appears
at `I_5` and `P_7`, not in the exhaustive range (to 4 × 4, where PLA −
(pw + 1) ∈ {0, 1}).

**Split bandwidth, how far.** Item 01's open design point is settled by not
bounding splits at all: `ib` is decided over numberings of every length by a
finite automaton (per vertex: unseen, open with the age of its last
occurrence, closed with that age; ages must stay below `b` while the vertex
still owes an occurrence), and `sb = ib` is Fomin Thm 6. `sb` from its own
definition is computed only as an upper bound through at most three explicit
splittings, on K_2, P_3, K_{1,3}, C_4, K_3, K_4: it equals `ib` on all six
(K_{1,3}: 2 = pw + 1; the others: pw). So the check of `pw ≤ sb ≤ pw + 1` at
scale rests on Fomin Thm 6; the six direct values are the independent part.

**Verdict changes.** One: the boundary-gate variant of one-dimensional logic
(§3), which item 01 called "not ±1" on a misread connection graph, is a band
`{pw + 1, pw + 2}` on everything checked, not a fixed offset. Everything
else item 01 stated is confirmed as stated, including every counterexample
(PLA `I_5`, the two stars, `ns = 0` on edgeless graphs) and every band (es,
sb). The search games agree with their monotone versions on every graph
checked, which is the monotonicity theorems (K&P 1986 Thm 2.3; LaPaugh) seen
at small size; items 10–11 prove the monotone relations only.

**Not checked.** `sb` directly beyond the six graphs above; Lengauer Thm 7 at
N ≥ 5 (the blow-up has N(N + 1) vertices); edge search above 20 edges;
Lengauer Thms 2–3 (black–white pebbling on dags, outside the twelve rows).

## Item 03: gate matrix layout in Lean

`lean/MOSPFormalization/Complex/GateMatrix.lean`, namespace
`MOSPFormalization.Complex.NetGateMatrix`, sorry-free (axioms: `propext`,
`Classical.choice`, `Quot.sound`).

**Definition, from Möhring p. 18, with no stacks or pathwidth in it.** A
net–gate matrix is a relation `conn : N → Gt → Prop` (rows nets, columns
gates). For a gate order `π` (a `LinearLayout Gt`), `augmented π n j` is entry
`(n, j)` of `M^π`: some gate of `n` is at or before `j` and some at or after.
`ShareGate π n n'` holds if the two augmented rows have a common column.
`IsTrackAssignment π h`, for `h : N → Fin k`, says that no two nets on one
track share a gate. `tracksFor π` is the least `k` for the fixed order, and
`tracks` (= `t(M)`) is the least `k` over all orders. `netGraph` is Möhring's
net adjacency graph (p. 29: the intersection graph of the rows of `M`).

**Theorems.**

| Lean | Statement | Source |
|---|---|---|
| `columnSum_eq_openStacksAt` | column sum of `M^π` at `j` = open stacks of the same matrix at `j` | definitions |
| `openStacksAt_le_of_isTrackAssignment` | nets open at one column need distinct tracks | pigeonhole |
| `exists_isTrackAssignment` | `maxOpenStacks π` tracks suffice (if M has a 1) | left-edge algorithm, Möhring p. 31 |
| `tracksFor_eq_maxOpenStacks` | min tracks for `π` = max column sum of `M^π` (if M has a 1) | Möhring p. 31 |
| `tracks_eq_mospValue` | `t(M) = Z_MOSP(M)`, identity map `toMOSP` (if M has a 1) | L&Y 2002 Prop. 2 |
| `tracks_eq_pathwidth_add_one` | `t(M) = pw(netGraph M) + 1` (if M has a 1) | Möhring Prop. 3.5; F&L 1989 Thm 7 |
| `netGraph_eq_mospGraph` | net adjacency graph = MOSP graph of `toMOSP` | definitions |
| `tracks_eq_one_of_forall_not` | M all zero, at least one net: `t = 1` | edge case |
| `tracks_eq_zero_of_isEmpty` | no nets: `t = 0` | edge case |

**The proof.** The map is the identity on the matrix, as item 01 found. Nets
are customers and gates are patterns; nothing is transposed. The real content
is the left-edge theorem for a fixed gate order.

- Lower bound: the nets open at one column pairwise share that column, so
  they need distinct tracks.
- Upper bound: induct over the nets in order of their leftmost gate
  (`Finset.induction_on_max_value`). Every earlier net that conflicts with the
  new net `a` is open at `a`'s leftmost gate, and so is `a`. That makes fewer
  than `maxOpenStacks π` conflicting nets, so a free colour exists
  (`isActive_first_of_shareGate`).

`t = Z` then follows by taking a MOSP-optimal order.
`mospValue_eq_pathwidth_add_one` closes the chain.

**Edge case, and a convention difference from the checker.** The Lean
definition gives every net a track, so on an all-zero matrix with at least
one net it gives `t = 1` (and `Z = 0`). `gate_matrix_tracks` in
`complex_check.py` drops rows with no 1 before assigning tracks, and gives 0.
The two agree whenever `M` has a 1: an empty net conflicts with nothing and
can share any track. This is the case the three main theorems cover. The
all-zero case is a convention; Möhring's nets always meet a gate. The Lean
theorems state both degenerate values explicitly, so the difference is
visible rather than hidden.
