# loop0005 — the pathwidth complex: items

Phase 1 settles statements (no Lean). Phase 2 proves what is within reach.
Phase 3 is graph searching. Then assembly and a reserve.

- [ ] **01 Statement census.** For each of the twelve Table 1 problems, read
  its source in `paper2/literature/` (and the extra sources in TASK.md) and
  write down, in `paper2/equivalences.md`: the source's own definition
  (quoted, with page and numbered definition), the input it is defined on
  (graph, matrix, circuit), the transformation to a graph if any, and the
  exact relation to pathwidth or vertex separation the source proves
  (equality, inequality, offset; theorem number). Mark each Table 1 claim as
  *confirmed*, *weaker than stated* (e.g. a sandwich), *misattributed* (the
  cited paper proves something else), *unsourced* (only [5], not held), or
  *false*. Settle specifically: what "edge separation" in Table 1 can mean
  given Lengauer (1981), Definitions 1-6 and Theorems 2-4; what exactly
  Möhring (1990) proves for PLA folding and gate matrix layout; what
  Ohtsuki et al. (1979) prove for one-dimensional logic; which of Kirousis &
  Papadimitriou (1985, 1986) proves interval thickness = node search number
  and node search = vs + 1. Build the master table. No code.

- [ ] **02 Brute-force checker.** `paper2/complex_check.py`: implement each
  problem from its *own* definition (not via pathwidth) as an exhaustive
  solver for small inputs — pathwidth (path decompositions), vertex
  separation (layouts), interval thickness (interval supergraphs), narrowness
  (in-sequences), node search and edge search numbers (game-state search over
  contaminated sets, with and without recontamination where feasible), split
  bandwidth (node splits, as far as feasible), gate matrix layout and MOSP
  (matrices), one-dimensional logic, PLA folding and the edge-separation
  variant item 01 settled, each per item 01's definitions. Check every item-01
  relation on all graphs up to 6 vertices (networkx atlas) and random graphs
  to 8, and matrices up to 5×5. Report agreement or counterexamples in
  `paper2/equivalences.md`; update each row's status. Tests on hand-checked
  graphs (path, star, cycle, K4, K3,3).

- [ ] **03 Gate matrix layout.** `Complex/GateMatrix.lean`: define gate matrix
  layout cost from its source (Wing et al. 1985 / Möhring 1990, matrix form),
  prove it equals `mospValue` of the corresponding instance (Linhares &
  Yanasse 2002 Prop. 2: a relabelling of rows/columns or a transposition —
  item 01 says which), and conclude `= pathwidth + 1` of the right graph from
  `mospValue_eq_pathwidth_add_one`.

- [ ] **04 Narrowness.** `Complex/Narrowness.lean`: define narrowness of an
  in-sequence exactly as Kornai & Tuza (1992) §2, prove their Proposition 2.1
  (in- and out-sequences agree) if needed, and Proposition 3.1,
  `narrowness G = pathwidth G + 1` for every graph with at least one vertex.

- [ ] **05 Interval thickness.** `Complex/IntervalThickness.lean`: define
  interval graphs by interval models and interval thickness as the minimum
  clique number of an interval supergraph on the same vertices; prove
  `intervalThickness G = pathwidth G + 1` (path decomposition → interval
  model from each vertex's bag interval; interval model → decomposition from
  the points). State the empty-graph convention.

- [ ] **06 One-dimensional logic.** `Complex/OneDimLogic.lean`: formalise
  Ohtsuki et al. (1979)'s gate-assignment problem as item 01 states it and
  prove its relation (expected: via interval graphs, so reuse item 05).

- [ ] **07 Split bandwidth.** `Complex/SplitBandwidth.lean`: define node
  splitting and split bandwidth as Fomin (1998) §3.2 and prove Theorem 8,
  `pw ≤ sb ≤ pw + 1` (upper: his layout construction from a path
  decomposition with equal-size bags; lower: pw is minor-monotone and
  `pw ≤ bandwidth`, the latter in `Sandwich.lean`). If minor-monotonicity is
  the obstacle, prove the special case splits need and say so. Record that
  this is a sandwich in the master table.

- [ ] **08 Edge separation.** `Complex/EdgeSeparation.lean`: formalise the
  statement item 01 settled (Lengauer's vertex separator game and/or his
  modified min-cut arrangement, Definition 6 and Theorem 4) and prove it. If
  Table 1's "edge separation" is ordinary min-cut linear arrangement
  (cutwidth), prove a counterexample to its equivalence with pathwidth ± 1 on
  a small graph found by item 02.

- [ ] **09 PLA folding.** `Complex/PLAFolding.lean`: formalise PLA folding as
  Möhring (1990) states it and prove the relation item 01 found; if it is not
  an equivalence up to ±1, prove the correct relation and a counterexample to
  Table 1's claim.

- [ ] **10 Node search, monotone.** `Complex/NodeSearch.lean`: define node
  searching (Kirousis & Papadimitriou) with strategies as sequences of
  place/remove moves and contamination, define *monotone* strategies, and
  prove `monotoneNodeSearch G = vertexSeparation G + 1`. State the full
  theorem (recontamination does not help) as a named gap in
  allowed_sorries.txt only if its proof does not fit.

- [ ] **11 Edge search, monotone.** `Complex/EdgeSearch.lean`: define edge
  searching (Parsons; Ellis, Sudborough & Turner 1994 §1) and prove, for
  progressive strategies, `vs ≤ s ≤ vs + 2` (their Lemmas 2.1-2.2); state
  LaPaugh's theorem (recontamination does not help) as a named gap if needed.

- [ ] **12 Interval thickness = node search.** `Complex/IntervalSearch.lean`:
  connect items 05 and 10 (Kirousis & Papadimitriou 1985) and, with item 05,
  close the chain interval thickness = node search = vs + 1 = pw + 1 for the
  monotone game. Add Lean counterexamples for any Table 1 claim items 01-02
  found false that no earlier item has proved.

- [ ] **13 Assemble.** Finish `paper2/equivalences.md` as section 3 of the
  paper: the master table (every problem, source, relation, Lean name,
  status: proved / sandwich / monotone only / stated gap / false as stated),
  a figure-ready diagram of the equivalence chain as a Mermaid or DOT graph,
  and a list of every allowed sorry with its reason. Write
  `paper2/lean_repo_plan.md`: which files move to the paper's own Lean
  repository, their dependency order, and what of the existing
  `lean/MOSPFormalization/` they need.

- [ ] **14 Reserve.** The best remaining gap: attempt the full node search
  theorem (monotonicity, Kirousis & Papadimitriou 1986 / Bienstock &
  Seymour) or LaPaugh's theorem, whichever item 10-11 left closer. One
  session; if it does not close, record how far it got and stop.
