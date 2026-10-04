# Papers not yet downloaded

These papers are referenced in the project but could not be downloaded due to paywalls or server issues.

## Paywalled

- ~~**Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350.~~ — **OBTAINED 2026-09-27**, see below.

- ~~**Yanasse, H.H.** (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463.~~ — **OBTAINED 2026-09-27**, see below.

- **Faggioli, E. & Bentivoglio, C.A.** (1998). Heuristic and exact methods for the cutting sequencing problem. *European Journal of Operational Research*, 110(3), 564-575. DOI: 10.1016/S0377-2217(97)00269-7 — Elsevier paywall.

- ~~**Chu, G. & Stuckey, P.J.** (2009)~~ — NOW AVAILABLE as `chu_stuckey_2009.pdf`.
- **Chu, G.** (2011). *Improving combinatorial optimization*. PhD thesis, University of Melbourne. hdl:11343/36679 — in `literature/` as `chu_2011_phd_thesis_improving_combinatorial_optimization.pdf`, downloaded from Minerva Access on 2026-10-02. Chapter 6 restates the customer search. Theorem 6.3.6 is the CP 2009 Theorem 1 unchanged. Theorem 6.3.8 states the better move with premise `close(q, S) ≥ open(q, S ∪ {r})`. Both are false on `cexGraph`; see `paper2/prior_art_counterexample.md`.

- ~~**Yanasse, H.H. & Senne, E.L.F.** (2010)~~ — NOW AVAILABLE as `yanasse_senne_2010_properties_preprocessing.pdf`. Note the DOI recorded here previously (`10.1016/S0377-2217(09)00632-8`) was wrong; the correct one is **10.1016/j.ejor.2009.09.017**.

- ~~**Fellows, M.R. & Langston, M.A.** (1989). On search, decision, and the efficiency of polynomial-time algorithms. *Proc. 21st ACM STOC*, 501-512.~~ — **OBTAINED 2026-09-27**, see below.

- ~~**Fellows, M.R. & Langston, M.A.** (1987). Nonconstructive advances in polynomial-time complexity. *Information Processing Letters*, 26, 157-162.~~ — **OBTAINED 2026-09-27**, see below.

- **Guimaraes, G.G., Poldi, K.C. & Martin, M.** (2025). Mathematical models for the one-dimensional cutting stock problem with setups and open stacks. *Journal of Combinatorial Optimization*. DOI: 10.1007/s10878-025-01276-5 — Springer paywall.

- **Poldi, K.C. et al.** (2025). On formulations for the one-dimensional cutting stock with a limited number of open stacks problem. *International Journal of Production Research*, 64(4), 1358-1385. DOI: 10.1080/00207543.2025.2568739 — Taylor & Francis paywall.

## Highest priority — harder to obtain than they look

These were identified from the reference lists of papers we hold. *Pesquisa
Operacional* is open access on SciELO, but **only digitised from 2001 onward**,
so the two 1990s papers below are not downloadable there despite the journal
being free. Routes worth trying instead: the INPE digital library (Yanasse is at
INPE/LAC and institutional repositories often hold pre-digitisation work),
Becceneri's 1999 thesis, Becceneri et al. (2004) in *Computers & Operations
Research* which implements the same arc contraction operation, or writing to the
authors.

- ~~**Yanasse, H.H.** (1997a). A transformation for solving a pattern sequencing problem in the wood cut industry. *Pesquisa Operacional*, 17, 57-70.~~ — **OBTAINED 2026-09-27** from the author, see below. It settles the 1997c question: this is the paper.

- ~~**Yanasse, H.H., Becceneri, J.C. & Soma, N.Y.** (1999)~~ — **OBTAINED 2026-09-22**, see below.

- ~~**Yanasse, H.H.** (1997c).~~ — **SETTLED 2026-09-27: 1997c is 1997a**, *Pesquisa Operacional* 17(1), 57-70. That paper contains everything the "1997c" citations are for: the minimum-degree bound (Proposition 3: a connected graph of minimum valency n forces n + 1 open stacks), the clique bound (Corollary 2, via Proposition 2's subinstance monotonicity), and the MOSP graph itself (Proposition 5: any MOSP reduces to one with at most two panel types per pattern by replacing each pattern with a clique on its panel types, with optimal solutions corresponding both ways in polynomial time). The APORS'97 three-author paper is a different, later statement of the bounds.

## Obtained since

- **39 papers from `~/dev/pathwidth`, transferred 2026-09-30** — the literature folder of the graph pathwidth solver now in `../pathwidth_solver/` (`../pathwidth_solver/TRANSFER.md`), copied here under their original `YEAR-Author-Title-Venue.pdf` names; 11 further files there were byte-identical to papers already held and were skipped. 35 are new papers, mostly on exact and approximate pathwidth and treewidth, with reading notes in `pathwidth_solvers_README.md`; four are second copies of papers held (Yanasse & Senne 2010, the INRIA report version of Coudert, Mazauric & Nisse 2014, Kobayashi, Komuro & Tamaki 2014, Mallach 2018). Among the new ones are three entries this file listed as missing: De La Banda & Stuckey (2007), Yanasse & Limeira (2004) and Lopes & Valério de Carvalho (2015), struck through below.

- **Ding, J., Zhou, T., Lü, Z. & Yuan, Y.** (2017). A quality and distance guided metaheuristic algorithm for vertex separation problem. *IEEE Access*, 5, 19251-19261. doi:10.1109/ACCESS.2017.2740418 — in `literature/` as `ding_zhou_lu_yuan_2017_quality_distance_guided_metaheuristic_vsp_ieee_access.pdf`, obtained 2026-09-30. One of the six works citing both a MOSP paper and a graph-theory paper (`paper2/popularity.md`). Instances: VSPLIB ("http://www.optsicom.es/vsp/", now dead), 162 in total: 62 Harwell-Boeing, plus grids and trees. It improves 33 best-known values, so VSPLIB's HB values are heuristic, not optima. It quotes the HB edge range 34-3721, the same figure `paper2/benchmarks/hunt_graphs.md` found inconsistent with the files (46-7442). Resolved 2026-09-30: the page's range is wrong, and it halves the true counts at both ends; the files match the original Matrix Market matrices.

- **Devadas, S.** (1986). Topological optimization of multiple level array logic. Memorandum UCB/ERL M86/95, Electronics Research Laboratory, University of California, Berkeley, 12 December 1986. 127 pp. — in `literature/` as `devadas_1986_topological_optimization_multiple_level_array_logic_ucb_erl_m86_95.pdf`, obtained 2026-09-30. PLA / multiple-level array logic folding; appears among the relevant PLA-folding works in `paper2/data/relevance_labels.json`. Not read yet; a candidate source of PLA instances for the benchmark hunt (`paper2/plan.md` section 4). The hunt (2026-09-30) put its area-optimised array circuits out of scope (`paper2/benchmarks/README.md` §5).

- **Ellis, J.A., Sudborough, I.H. & Turner, J.S.** (1994). The vertex separation and search number of a graph. *Information and Computation*, 113(1), 50-79. doi:10.1006/inco.1994.1064 — in `literature/` as `ellis_sudborough_turner_1994_vertex_separation_search_number.pdf`, obtained 2026-09-28. Read in full. Contents: `vs(G) ≤ s(G) ≤ vs(G) + 2` for the edge search number (Theorem 2.1), `s(G) = vs(G')` for the 2-expansion (Theorem 2.2), a recursive characterization of trees with vertex separation k (Theorem 3.1), smallest trees of vertex separation k have `m(k) = ⌊5·3^k/6⌋` vertices so `vs(T) = O(log n)`, and a linear-time tree algorithm. **It has no general-graph lower bound of any kind**, so it does not anticipate the expansion bound (see *Prior art to settle* below). Its survey paragraph also records that Fellows & Langston (1989) show gate matrix layout cost = path width + 1, the same link our chain uses.

- **Coudert, D., Mazauric, D. & Nisse, N.** (2014). Experimental evaluation of a branch and bound algorithm for computing pathwidth. *SEA 2014*, LNCS 8504, 46-58. doi:10.1007/978-3-319-07959-2_5 — in `literature/` as `coudert_mazauric_nisse_2014_branch_and_bound_pathwidth_sea.pdf`, extracted from the proceedings on 2026-09-28. Prefix-layout branch and bound for vertex separation of digraphs. Two pruning rules that are the pathwidth-side counterparts of Chu & Stuckey (2009): Lemma 3, a *greedy step* that appends a vertex whose out-neighbours are already inside `S ∪ N⁺(S)` (Chu & Stuckey's definite move), and Lemma 4, a table of already-explored prefix sets (their nogood memo). Preprocessing by arc contraction and the degree-1/degree-2 rules of Bodlaender et al. No lower bound beyond the incumbent. Exact to about 60 vertices.

- **Kobayashi, Y., Komuro, K. & Tamaki, H.** (2014). Search space reduction through commitments in pathwidth computation: an experimental study. *SEA 2014*, LNCS 8504, 388-399. doi:10.1007/978-3-319-07959-2_33 — in `literature/` as `kobayashi_komuro_tamaki_2014_commitments_pathwidth_sea.pdf`, extracted 2026-09-28. Memoized backtracking over vertex-separation prefix sets with *commitments* (Tamaki): an extension `T ⊇ S` may be taken without branching when every intermediate set has border at least `d(T)`. Depth-1 commitments are extremely effective on TreewidthLIB; depth 2-10 add little. Depth-1 is again the definite-move family. The full SEA 2014 proceedings stay in `~/Downloads` and are not committed (12 MB).

- **Mallach, S.** (2018). Linear ordering based MIP formulations for the vertex separation or pathwidth problem. *Journal of Discrete Algorithms*, 52-53, 156-167. doi:10.1016/j.jda.2018.11.012 — in `literature/` as `mallach_2018_linear_ordering_mip_vertex_separation_pathwidth.pdf`, obtained 2026-09-28. Shows the earlier position- and set-assignment MIPs have LP relaxations with worst-possible (zero) lower bounds, and gives a linear-ordering MIP whose relaxation is provably nonzero; still weak on grids (constant 2 against pathwidth n) and on dense queen graphs, and the author notes combinatorial treewidth bounds are usually stronger. Relevant to item 7 only as a negative: an LP relaxation is not where a strong MOSP floor will come from.

- **Grigoriev, A., Kobayashi, Y., Tamaki, H. & van der Zanden, T.C.** (2025). A polynomial delay algorithm generating all potential maximal cliques in triconnected planar graphs. arXiv:2506.12635v3 — in `literature/` as `grigoriev_kobayashi_tamaki_vanderzanden_2025_potential_maximal_cliques_planar.pdf`, obtained 2026-09-28. Treewidth of planar graphs via Bouchitté-Todinca. MOSP graphs are unions of cliques and rarely planar, so this bears only on the exact-treewidth ideas in `reports/machine_learning_todo.md`, and weakly.

- **Yanasse, H.H.** (1997b). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463. — in `literature/` as `yanasse_1997b_pattern_sequencing_open_stacks_ejor.pdf`, sent by the author 2026-09-27; Table 1 ref [1], the MOSP paper (received 1994, accepted 1995). What is in it. §1: the problem in the wood-cutting setting with the 6-pattern example; Conjectures 1-4 that MOSP shares an optimal solution with the order-spread (MORP), discontinuities (MDP) and tool-switching (MTSP) problems; NP-hardness "still an open question". §2: a mathematical formulation through Tang & Denardo's tool-switching model — Propositions 1-2 give `MOSP = min C such that MTSP(C) needs exactly M − C switches`. §3: **a branch and bound whose nodes are pairs `(S_o, S_u)` of open and unfinished part types and whose branching chooses the next part type to complete** — the customer-closing-order state space that Chu & Stuckey (2009) and `satisfiability/customer_search.py` search, with the observation that the patterns needed to complete a part type can be sequenced in any order without changing the open stacks at the end; bounds LB1 (largest pattern, the trivial bound), LB2 (min over successors), LB3 (from the predecessor), UB = `|S_u|`; depth-first with the greedy choice "the node with the least open stacks". §4: the matrix computations (`N_i`, the row-OR of the patterns containing type `i`; `(N_i ∨ N_ant)·e'` = stacks open after completing `i`); **dominated panel types** (`T_i ⊆ T_j`: completing `j` completes `i`) used to break ties and to fathom — the subset rule, in 1994; the sets `U^j` that avoid re-branching on a type already considered elsewhere at the same level — a memo. §4 also lists the heuristics one could build, including "next pattern ... the one that results in the least number of open stacks", the first key of the two-key rule at pattern level. So the exact method the repository runs is, in its state space and two of its rules, this paper's.

- **Ohtsuki, T., Mori, H., Kuh, E.S., Kashiwabara, T. & Fujisawa, T.** (1979). One-dimensional logic gate assignment and interval graphs. *IEEE Transactions on Circuits and Systems*, 26(9), 675-684. — in `literature/` as `ohtsuki_mori_kuh_kashiwabara_fujisawa_1979_one_dimensional_logic.pdf`, sent 2026-09-27; Table 1 ref [7]. The interval-graph route to the whole family, and the earliest paper in Table 1. Nets ↔ vertices and gates ↔ the sets `V(t)`; the **connection graph** `H` joins two nets that share a gate — the MOSP graph with nets as customers and gates as patterns (eq. 5-6). For a gate permutation the nets become intervals; tracks = chromatic number = clique number of the resulting interval graph (Fig. 3), so the problem is: find an interval supergraph `Ĥ = (V, E ∪ F)` of `H` with minimum clique number (§III), which is NP-complete by Kashiwabara & Fujisawa [11] — Table 1's ref [5], still missing, is cited here for exactly that. Theorem 1 (Fulkerson & Gross) is the consecutive-ones characterisation; Theorem 3 reads a gate sequence off an ordering of the dominant cliques; §IV gives a polynomial algorithm for a *minimal* (not minimum) augmentation, Theorem 4, extended to fixed boundary gates in Theorem 5; §V reports 30 random minimal augmentations per instance on seven 48-gate circuits (Table IV). In our terms: the optimum is `1 +` the pathwidth of the connection graph because pathwidth is one less than the least clique number of an interval supergraph — the interval-thickness link, stated here in 1979 with the MOSP graph already drawn.

- **Wing, O., Huang, S. & Wang, R.** (1985). Gate matrix layout. *IEEE Transactions on Computer-Aided Design*, 4(3), 220-231. — in `literature/` as `wing_huang_wang_1985_gate_matrix_layout.pdf`, sent 2026-09-27; Table 1 ref [8]. CMOS gate matrix layout as a two-stage problem: gate assignment `f`, then net-to-row assignment `h` with vertical diffusion runs to keep realisable. §V restates Ohtsuki's connection graph and interval graph `I(L)`, with three "self-evident" facts: `I(L) ⊇ H`, rows = largest dominant clique of `I(L)`, and **rows ≥ max nets per gate** — the trivial lower bound `lb_p`, in the VLSI literature. Appendix A is a greedy heuristic (`Algorithm Interval Graph`) that places dominant cliques left or right of the partial matrix to minimise the growth of the largest clique and the fill-in, with random restarts; Fig. 13's histogram of 90 trials on a 144-net circuit spans clique sizes 34-55, which is the spread of a constructive heuristic on one instance and a period reference point for §7's rule and §29's MCNh. Series-connected transistors are merged into one net (§IV), a domain reduction with no MOSP analogue.

- **Lengauer, T.** (1981). Black-white pebbles and graph separation. *Acta Informatica*, 16(4), 465-475. — in `literature/` as `lengauer_1981_black_white_pebbles_graph_separation.pdf`, sent 2026-09-27; Table 1 ref [14]. **Table 1 lists it under "edge separation"; its subject is the vertex separator game.** VSG (p. 467): pebble the vertices of an undirected graph in some order; the cut after each move is the set of pebble-free vertices adjacent to a pebbled one; `VSG(G)` is the least achievable maximum cut — vertex separation, with the note that in general `VSG(S) ≠ VSG(S̄)` for the reversed order (the asymmetry `reports/ml_nature.md` §8 measured on closing orders). Lengauer says explicitly (p. 468) that the *edge*-separator version of the same game is min-cut linear arrangement. Theorems 2-4 relate VSG to the progressive black-white pebble game on dags with shifts of one and two (via the graphs `G_u`, `G_d`, `G_du`); **Theorem 7 proves VSG NP-complete** by reduction from a modified min-cut linear arrangement, which is the result Kinnersley (1992) cites as [11] for VERTEX SEPARATION. So Table 1's attribution of *edge separation* to [14] is loose; the paper is the NP-completeness reference for vertex separation, and hence for pathwidth via Kinnersley.

- **Fellows, M.R. & Langston, M.A.** (1987). Nonconstructive advances in polynomial-time complexity. *Information Processing Letters*, 26, 157-162. — in `literature/` as `fellows_langston_1987_nonconstructive_advances_ipl.pdf`, obtained 2026-09-27. The letter Fellows & Langston (1989) cite as [FL1] and Kinnersley (1992) as [4]. §4 is the gate matrix layout part and carries three lemmas, all with full proofs. **Lemma 4.1**: `GML(M, k)` iff `GML(x(M), k)`, where `x(M)` expands every column with `j > 2` ones into its ⁽ʲ₂⁾ two-ones columns — proved in both directions (forward: keep the permutation, place the expanded columns adjacently; backward: for each original column take the first and last of its expanded columns, all its nets are pairwise connected and hence open across that span, so one of them can be replaced by the original column and the rest deleted without adding a track, then iterate). With the map `g` (rows → vertices, two-ones columns → edges), that is **Yanasse (1997a) Proposition 5 in matrix vocabulary, ten years earlier**: the same reduction, the same both-ways correspondence of optimal solutions. **Lemma 4.2**: the "yes" family for fixed `k` is minor-closed (deleting a column or row and contracting an edge — replacing two rows by their element-wise OR — never adds a track). **Lemma 4.3**: a planar graph of cost `> k` exists for every `k`, built by joining three copies of the previous one at a new vertex `d` adjacent to one vertex in each (Fig. 2); the proof is the **pathwidth branch rule** in full — with columns `i₁ < i₂ < i₃` from the three copies each carrying `k + 1` entries, `d` or the copy's attachment vertex spans `i₂` and forces `k + 2`. Theorem 4.4, `GML ∈ P` for fixed `k`, and the remark that GML is self-reducible (decision to construction), plus the two obstructions for `k = 2`, `K₃` and the subdivided claw.

  **This completes the chain on the literature's own proofs.** Theorem 7 of the 1989 paper sketches decomposition → layout and cites Lemma 4.1 for the expansion step, which is now in hand with its proof; the converse direction remains the elementary one written out under the 1989 entry. And the two routes from MOSP to the graph — Linhares & Yanasse (2002) through gate matrix layout, and Yanasse (1997a) through the clique-per-pattern graph — meet here: Proposition 5 and Lemma 4.1 are the same statement.

- **Fellows, M.R. & Langston, M.A.** (1989). On search, decision, and the efficiency of polynomial-time algorithms. *Proc. 21st ACM STOC*, 501-512. — in `literature/` as `fellows_langston_1989_search_decision_efficiency_stoc.pdf`, obtained 2026-09-27. Reference [15] of Linhares & Yanasse (2002) (Theorem 1 there, `GMLP ∈ FPT`, hence Corollary 1, `MOSP ∈ FPT`) and reference [6] of Kinnersley (1992). **Theorem 7** (p. 503-504): *those graphs that correspond to gate matrix layout cost k are exactly those graphs with path-width k − 1*, where a matrix is mapped to a graph by first expanding every column into two-ones columns and then reading rows as vertices and columns as edges — Yanasse (1997a) Proposition 5's clique-per-pattern construction in the VLSI vocabulary. **The paper proves one direction only**, and says so: from a path decomposition of width k − 1 it builds the matrix whose columns are the bags, expands each bag into its pairwise columns, and cites [FL1] Lemma 4.1 for the expansion preserving the cost, giving layout cost ≤ k. The converse — a layout of cost k yields a path decomposition of width ≤ k − 1 — is not written out but is elementary: take as bags the sets of rows active at each column; the consecutive-ones property makes each row's bags an interval, so the intersection condition holds, every edge (two rows sharing a column) lies in that column's bag, and no bag exceeds k rows. It is the layout-to-decomposition half of Kinnersley's Theorem 3.1 with "active at column i" in place of `V_L(i)`.

  **With this paper the MOSP–pathwidth chain closes on papers we hold**: MOSP = GML (Linhares & Yanasse 2002, Proposition 2, by definition); GML cost = pathwidth + 1 (Fellows & Langston 1989, Theorem 7, one direction sketched there and the converse elementary as above); pathwidth = vertex separation (Kinnersley 1992, Theorem 3.1, both directions); and, on the MOSP side, the graph is Yanasse (1997a) Proposition 5's. The Lean development holds the vs = pw half without gaps (`VSEquivPW.lean`); `Reduction.lean` holds `mosp ≤ pathwidth + 1` — the direction Fellows & Langston sketch — with one `sorry`, and lacks the elementary converse, which is loop0004 item 12. *(Superseded later on 2026-09-27: that `Reduction.lean` statement was over the pattern graph and false, and is deleted; `MOSPGraph.lean` proves `mospValue = pathwidth (mospGraph) + 1` in both directions, `sorry`-free.)* The 1989 paper also carries Theorem 8's table of pathwidth upper bounds for related layout problems (min cut linear arrangement k, search number k + 3) and the general nonconstructivity results (Theorems 13-16) that Linhares & Yanasse §2.2 rely on.

- **Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350. — in `literature/` as `kinnersley_1992_vertex_separation_equals_pathwidth.pdf`, obtained 2026-09-27. Reference [13] of Table 1 in Linhares & Yanasse (2002). Three things in it bear on the repository. (1) **Theorem 3.1**, `vs(G) = pw(G)`, proved in both directions by exactly the two constructions the Lean development uses: from a layout `L`, the bags `X_i = V_L(i − 1) ∪ {L⁻¹(i)}` (`LayoutToDecomposition.lean`); from a path decomposition, the layout that walks the bags in order (`DecompositionToLayout.lean`). `VSEquivPW.lean` is a faithful formalisation of this proof. (2) **Corollary 3.2**: if `vs(G) = k` then gate matrix layout cost and node search number both equal `k + 1`, via Fellows & Langston's Theorem 7 and Kirousis & Papadimitriou's Theorem 4.1. With Linhares & Yanasse (2002) Proposition 2 (open stacks = GML tracks) this is the published chain behind `MOSP = pathwidth + 1`; Yanasse's clique-per-pattern graph (1997a, Proposition 5) is the other route, through the MOSP graph. (3) **Theorem 4.1** (Ellis, Sudborough & Turner) and **Corollary 4.2**: for a tree, `gml(T) > k` iff some vertex induces three or more subtrees each of cost ≥ k; and, quoted from Fellows & Langston (1987) [4], that making a new vertex adjacent to one vertex in each of three graphs of GML cost `k` gives cost at least `k + 1` (the premise of Theorem 4.3). **That is the pathwidth branch rule** `reports/ml_nature.md` §24 stated in treewidth form and loop0004 item 11 tests as its first candidate over cut vertices: it is a known lemma, to be cited, not claimed. The paper also gives the tree-obstruction recurrence `v(k) = 3v(k − 1) + 1` and the counts of tree obstructions for `k`-GML (2, 10, 117,480 for k = 2, 3, 4).

- **Yanasse, H.H.** (1997a). A transformation for solving a pattern sequencing problem in the wood cut industry. *Pesquisa Operacional*, 17(1), 57-70. — in `literature/` as `yanasse_1997a_transformation_pattern_sequencing_wood.pdf`, sent by the author 2026-09-27. **This is "Yanasse (1997c)".** Five propositions: (1) reversing a pattern sequence reverses the open-stack profile — the symmetry `reports/ml_nature.md` §8 measures, with Corollary 1 that every MOSP with more than one pattern has multiple optima; (2) adding patterns cannot lower the optimum — the subinstance bound `satisfiability/relaxation.py` uses; (3) minimum valency n forces n + 1 stacks; Corollary 2, the clique bound; (4) a clique of size n ≥ 4 forces n − 1 open stacks over four *consecutive* patterns; (5) the reduction of any MOSP to the two-panel case through the clique-per-pattern graph — the MOSP graph, with the observation (p. 68) that many different instances share one graph and hence one optimum, which §1 and §13 measure. The paper conjectures NP-hardness, later proved by Linhares & Yanasse (2002).

- **Becceneri, J.C., Yanasse, H.H. & Soma, N.Y.** (2004). A method for solving the minimization of the maximum number of open stacks problem within a cutting process. *Computers & Operations Research*, 31(14), 2315-2332. — in `literature/` as `becceneri_yanasse_soma_2004_method_mosp_cutting.pdf`, sent by the author 2026-09-27. Settles the three things it was wanted for. **The Minimal Cost Node heuristic (§4) is an arc-traversal heuristic, not a node-closing one**: it keeps `Ω(k)`, the degree of node k over arcs not yet traversed, takes the node of smallest Ω, then two adjacent nodes n₁, n₂ with Ω(n₁) = Ω(k) and the pairwise smallest Ω, traverses the arc (n₁, n₂), then greedily traverses every arc between already-open nodes; the pattern sequence is read off the arc sequence by sequencing a pattern when all its nodes are first open. That is why our node-closing `mcn` does not reproduce MCNh's numbers. **The dominance rules (§5)**: the Global dominance proposition (if `N[j] ⊆ N[i]` then some optimal sequence closes j before i, with proof) — our subset rule — and the note that using it inside their branch-and-bound *worsened* performance, so it was not used; the Equivalency proposition (`N[i] = N[j]` or `N(i) = N(j)`: sequence them consecutively, and delete one — Fig. 3's reduction 8 → 5 nodes, with the hierarchy caveat that equivalences found after a reduction must respect the earlier ones). **The arc contraction heuristic (§5)**: lb_c = max over contractions of (min degree + 1), contracting the arc whose ends have the smallest indices in the vertex set sorted by non-decreasing degree, re-sorted every iteration; O(n³); with lb_p (largest pattern) and lb_d (min degree + 1) as its floor — contraction degeneracy + 1 again, and their Fig. 7 example where lb_p = 3, lb_d = 2, lb_c = 6. Also: pattern dominance (§3, `P_j ⊆ P_i`), the tree/cycle/1-tree component pre-solve from Yanasse (1996), the exact method (branch-and-bound with the Limeira/Yanasse local dominance, MCN as incumbent, lb_c as floor, equivalent nodes deleted first), and their generator ("start with a complete graph and delete a percentage of arcs", instances `Gxyz`). Their own verdict (§6–§7): the heuristic is "quite good", the lower bound "quite poor" for small C — the degree-family verdict `reports/ml_nature.md` §6 reaches.

- **Yanasse, H.H., Becceneri, J.C. & Soma, N.Y.** (1999). Bounds for a problem of sequencing patterns. *Pesquisa Operacional*, 19(2), 249-277. — in `literature/` as `yanasse_becceneri_soma_1999_bounds_sequencing_patterns.pdf`. **The most actionable missing reference, and it settles what it was wanted for.** It gives five bounds. LB4 is degeneracy + 1 ("find an induced subgraph whose minimum degree is maximized", by repeatedly deleting the smallest-degree node). LB5, the arc contraction bound, repeatedly contracts an arc at a minimum-degree node and keeps the largest LB4 seen — **that is contraction degeneracy (MMD+) + 1, the bound `satisfiability/mosp_solver.py::_contraction_degeneracy` computes.** So the two are the same bound and no novelty may be claimed for ours; the only difference is the tie-break (their least degree sum, our least common neighbours). See `reports/lower_bounds.md` §3.

- **Yanasse, H.H., Becceneri, J.C. & Soma, N.Y.** (1997). Lower bounds for the problem of sequencing cutting patterns. APORS'97, Melbourne; also CNMAC XX, Gramado; published in the *Anais da II Oficina de Problemas de Corte & Empacotamento*, 2-6. — in `literature/` as `yanasse_becceneri_soma_1997_lower_bounds_apors.pdf`. The 1999 paper's LB1-LB3 in earlier form, with the same worked instance. **Possibly the "Yanasse (1997c)" that Yanasse & Senne (2010) cite for the MOSP graph and the clique / minimum-degree bounds** — it states the minimum-degree bound as Proposition 2 and the subgraph bound via Proposition 1, over the graph with nodes as order parts. It does *not* contain a clique bound, so if 1997c is the source of that, 1997c is a different paper still.

- **Yanasse, H.H., Becceneri, J.C. & Soma, N.Y.** (2007). Um algoritmo exato com ordenamento parcial para solução de um problema de programação da produção: experimentos computacionais. *Gestão & Produção*, 14(2), 353-361. — in `literature/` as `yanasse_becceneri_soma_2007_algoritmo_exato.pdf`. In Portuguese. States the partial-ordering rules precisely, which Yanasse & Senne only reference:
  - **Type I**: adjacent nodes i, j both of degree 2 — some optimal solution labels them consecutively.
  - **Type II**: if `A_j ⊆ A_i ∪ {i}` then i dominates j, and some optimal solution labels j before i. If `A_j = A_i`, they are equivalent, and Becceneri et al. (2004) reduce the graph keeping only one.

  Measured on our instances: the *reduction* rules essentially never fire (0 type-I pairs and 0 equivalences on SP2/SP3/SP4), but *dominance* relations are common — 28, 21 and 27 pairs respectively. Those are symmetry-breaking constraints rather than reductions, and are unexploited by our encoding.

## Also missing, newly identified

- ~~**De La Banda, M.G. & Stuckey, P.J.** (2007). Dynamic programming to minimize the maximum number of open stacks. *INFORMS Journal on Computing*, 19, 607-617. DOI: 10.1287/ijoc.1060.0205~~ — the DP that Chu & Stuckey (2009) extends. **OBTAINED 2026-09-30** with the `~/dev/pathwidth` transfer, as `2007-Garcia-de-la-Banda-Stuckey-Dynamic-Programming-Minimize-Maximum-Open-Stacks-IJOC.pdf`.

- ~~**Becceneri, J.C., Yanasse, H.H. & Soma, N.Y.** (2004). A method for solving the minimization of the maximum number of open stacks problem within a cutting process. *Computers & Operations Research*, 31(14), 2315-2332.~~ — **OBTAINED 2026-09-27** from the author, see below.

  Partially substituted by Poliquit (2008), a Master's thesis of the same title now in `literature/`, which states the MCN algorithm in full (§3) and covers arc contraction (§4.2) and a lower bound implementation (§4.4). Its statement is explicitly for instances with at most two piece types per pattern, so it does not transfer directly to the general case.

- ~~**Yanasse, H.H. & Limeira, M.S.** (2004). Refinements on an enumeration scheme for solving a pattern sequencing problem. *International Transactions in Operational Research*, 11, 277-292. DOI: 10.1111/j.1475-3995.2004.00458.x~~ — **OBTAINED 2026-09-30** with the `~/dev/pathwidth` transfer, as `2004-Yanasse-Limeira-Refinements-Enumeration-Scheme-Pattern-Sequencing-ITOR.pdf`.

## Table 1 of Linhares & Yanasse (2002) — the equivalent problems

Table 1 of `Linhares and Yanasse - 2002 - Connections between cutting-pattern
sequencing, VL.pdf` (p. 1764) asserts twelve problems equivalent up to ±1,
resting on twelve distinct references. **Eleven are held** (see
`../paper2/literature/MANIFEST.md`), including the full Möhring chapter; **one
is not**, Kashiwabara & Fujisawa [5]. When this section was written five were
held and seven were not; two of the seven, Kinnersley [13] and Yanasse [1], are
listed under **Paywalled** above, and the other five are below, four of them
since obtained:

- **Kashiwabara, T. & Fujisawa, T.** (1979). NP-completeness of the problem of finding a minimum clique number interval graph containing a given graph as a subgraph. *Proc. 1979 IEEE International Symposium on Circuits and Systems*, Tokyo, 657-660. No DOI — Table 1 ref [5], *interval thickness*. **The hardest of the twelve**: 1979 conference proceedings, not indexed by OpenAlex at all, never digitised by IEEE. Needs a library holding physical IEEE conference records.

- ~~**Möhring, R.H.** (1990). Graph problems related to gate matrix layout and PLA folding. In *Computational Graph Theory*, Computing Supplementum 7, Springer-Verlag Wien, 17-51. DOI: 10.1007/978-3-7091-9076-0_2~~ — Table 1 refs [6], *gate matrix layout* and *PLA folding*. **OBTAINED IN FULL 2026-09-27**: the 35-page chapter, extracted (pp. 20–54 of the file) from the full book PDF *Computational Graph Theory* (Tinhofer, Mayr, Noltemeier, Sysło eds., 1990) downloaded via institutional access and kept in `~/Downloads`; in `literature/` as `mohring_1990_gate_matrix_layout_pla_folding.pdf` and in `paper2/literature/` as `06_mohring_1990.pdf`. The two-page Springer preview held earlier that day was deleted. Contents: interval-graph augmentation with minimum clique size (= pathwidth + 1), node search, vertex separation, MPQ-trees / interval orders, matching problems with side constraints.

- ~~**Ohtsuki, T., Mori, H., Kuh, E.S., Kashiwabara, T. & Fujisawa, T.** (1979). One-dimensional logic gate assignment and interval graphs. *IEEE Transactions on Circuits and Systems*, 26(9), 675-684.~~ — **OBTAINED 2026-09-27**, see below.

- ~~**Wing, O., Huang, S. & Wang, R.** (1985). Gate matrix layout. *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, 4(3), 220-231.~~ — **OBTAINED 2026-09-27**, see below.

- ~~**Lengauer, T.** (1981). Black-white pebbles and graph separation. *Acta Informatica*, 16(4), 465-475.~~ — **OBTAINED 2026-09-27**, see below.

Obtained since: **Kirousis, L.M. & Papadimitriou, C.H.** (1985). Interval graphs
and searching. *Discrete Mathematics*, 55(2), 181-184. DOI:
10.1016/0012-365X(85)90046-9 — Table 1 ref [9], *node search game*; the
interval-thickness = node-search-number link. Now in
`../paper2/literature/09_kirousis_papadimitriou_1985.pdf`. It was never
paywalled — Elsevier's open archive carries it free — and only ScienceDirect's
block on non-browser clients stood in the way; a browser fetched it at once.
Worth remembering for any other Elsevier open-archive item.

Sources checked for the then-missing seven and found to hold nothing: OpenAlex, Semantic
Scholar, CORE (rate-limited without an API key), Internet Archive Scholar
(`api.fatcat.wiki` unreachable throughout), the publishers, the authors' own
pages, and the Wayback Machine where an author page is dead.

## Prior art to settle (not missing — unidentified)

- ~~**The neighbourhood-expansion lower bound** of `satisfiability/expansion_bound.py`~~
  — **settled 2026-09-28: not new.** `vs(G) ≥ max_i (i − max{t : f(t) ≤ i})` with
  `f(t) = min_{|C|=t}|N[C]|` is the classical vertex-isoperimetric bound
  `vs(G) ≥ max_i Φ(i)`, `Φ(i) = min_{|S|=i} |∂_in S|`: the interior of an `i`-set
  is exactly a `C` with `N[C] ⊆ S`, so `i − M(i) = Φ(i)`. Sources to cite:
  - **Harper, L.H.** (1966). Optimal numberings and isoperimetric problems on graphs. *Journal of Combinatorial Theory*, 1(3), 385-393. doi:10.1016/S0021-9800(66)80059-5 — the method. Not held.
  - **Chandran, L.S. & Kavitha, T.** (2006). The treewidth and pathwidth of hypercubes. *Discrete Mathematics*, 306(3), 359-365. doi:10.1016/j.disc.2005.12.011 — applied to pathwidth. In `literature/` as `chandran_kavitha_2006_treewidth_pathwidth_hypercubes.pdf`, obtained 2026-09-30.
  - **Lin, L. & Lin, Y.** (2025). Discrete isoperimetric method for bandwidth, pathwidth and treewidth of hypercubes. *Discrete Applied Mathematics*, 363, 201-214. doi:10.1016/j.dam.2024.12.001 — abstract read 2026-09-28: pw(Q_d) = bw(Q_d) by Harper's method, tw(Q_d) open. Not held.
  - **Harper, L.H.** (2004). *Global Methods for Combinatorial Isoperimetric Problems*. Cambridge University Press. doi:10.1017/CBO9780511616679 — the book-length treatment. Not held.
  - **Díaz, J., Petit, J. & Serna, M.** (2002). A survey of graph layout problems. *ACM Computing Surveys*, 34(3), 313-356. doi:10.1145/568522.568523 — survey of layout lower bounds. In `literature/` as `diaz_petit_serna_2002_survey_graph_layout_problems.pdf` (44 pp.), obtained 2026-09-30.

  Read on the way and not containing it: Ellis, Sudborough & Turner (1994),
  Coudert, Mazauric & Nisse (2014), Kobayashi, Komuro & Tamaki (2014), Mallach
  (2018). What remains ours is the exact capped computation of `f` and the
  corpus measurement, not the bound.

## Server issues

- ~~**Lopes, I.C. & De Carvalho, J.M.V.** (2015). Graph properties of minimization of open stacks problems and a new integer programming model. *Pesquisa Operacional*, 35(2), 213-250. DOI: 10.1590/0101-7438.2015.035.02.0213 — SciELO open access, but server returned 502/504 errors. Retry later.~~ — **OBTAINED 2026-09-30** with the `~/dev/pathwidth` transfer, as `2015-Lopes-Valerio-de-Carvalho-Graph-Properties-Minimization-Open-Stacks-New-Integer-Programming-Model-PesqOper.pdf`.

## Random bipartite graphs, cores and random intersection graphs (item 09 of loop0004, 2026-09-28)

None of these is held; `reports/ml_nature.md` §36 cites them from memory for
the thresholds it computes itself in the configuration model, and every
citation there should be checked against the paper before it is quoted
outside this repository.

- Pittel, Spencer & Wormald (1996), "Sudden emergence of a giant k-core in a
  random graph", *J. Combin. Theory B* 67 — the k-core threshold of G(n, p).
- Molloy (2005), "Cores in random hypergraphs and Boolean formulas", *Random
  Structures & Algorithms* 27.
- Fernholz & Ramachandran (2007), "The k-core and branching processes",
  *Combin. Probab. Comput.* 16; Riordan (2008), "The k-core and branching
  processes", *Combin. Probab. Comput.* 17 — cores for general degree sequences,
  the peeling fixed point used in `learning/cover_excess.py`.
- Luby, Mitzenmacher, Shokrollahi & Spielman (2001), "Efficient erasure
  correcting codes", *IEEE Trans. Inform. Theory* 47 — the 2-core (stopping
  set) of a bipartite factor graph with given degree distributions.
- Dubois & Mandler (2002), "The 3-XORSAT threshold", *FOCS*; Mézard,
  Ricci-Tersenghi & Zecchina (2003), "Two solutions to diluted p-spin models
  and XORSAT problems", *J. Stat. Phys.* 111 — a threshold set by the 2-core of
  the factor graph having as many constraints as variables.
- Karoński, Scheinerman & Singer-Cohen (1999), "On random intersection
  graphs: the subgraph problem", *Combin. Probab. Comput.* 8; Fill, Scheinerman
  & Singer-Cohen (2000), *Random Structures & Algorithms* 16 — G(n, m, p) and
  its equivalence to G(n, p̂) only for m ≫ n⁶.
- Behrisch (2007), "Component evolution in random intersection graphs",
  *Electron. J. Combin.* 14; Lagerås & Lindholm (2008), "A note on the
  component structure in random intersection graphs with tunable
  clustering", *Electron. J. Combin.* 15 — the giant component at m = Θ(n).
- Stark (2004), "The vertex degree distribution of random intersection
  graphs", *Random Structures & Algorithms* 24; Deijfen & Kets (2009),
  *Probab. Engrg. Inform. Sci.* 23 — compound-Poisson degrees at m = Θ(n).
- Rybarczyk (2011), "Diameter, connectivity and phase transition of the
  uniform random intersection graph", *Discrete Math.* 311 — connectivity.
- Schmidt-Pruzan & Shamir (1985), *Combinatorica* 5; Karoński & Łuczak (2002),
  *J. Comput. Appl. Math.* 142 — the giant component of random hypergraphs
  (already cited in §25).

## Citers of Chu & Stuckey (2009) not read (loop0008 item 01, 2026-10-03)

The prior-art sweep (`paper2/prior_art_counterexample.md`, "Every citer, swept";
`python3 -m paper2.prior_art_sweep`) could not get a full text for these 14
works citing the CP paper. Neither the indexes nor a web search found an open
copy. They are listed in order of how likely they are to restate the definite
or better move:

- **De Giovanni, L., Massi, G., Pezzella, F., Pfetsch, M.E., Rinaldi, G. & Ventura, P.** (2013). A heuristic and an exact method for the gate matrix connection cost minimization problem. *ITOR* 20(5), 627-643. doi:10.1111/itor.12025. **This is an exact method, so it is the first to fetch.**
- **Chu, G. & Stuckey, P.J.** (2012). Inter-instance nogood learning in constraint programming. CP 2012, LNCS 7514. doi:10.1007/978-3-642-33558-7_19. The report version, "Inter-problem nogood learning", was read.
- **De Giovanni, L., Massi, G. & Pezzella, F.** (2013). An adaptive genetic algorithm for large-size open stack problems. *IJPR* 51(3), 682-697. doi:10.1080/00207543.2012.657256.
- **DeGiovanni, L., Massi, G. & Pezzella, F.** (2010). Preliminary computational experiments with a genetic algorithm for the open stack problem. Technical report.
- **Carvalho, M.A.M. & Soma, N.Y.** (2015). A breadth-first search applied to the minimization of the open stacks. *JORS* 66, 936-946. doi:10.1057/jors.2014.60.
- **Lima, J.R. & Carvalho, M.A.M.** (2017). Descent search approaches applied to the minimization of open stacks. *C&IE* 112, 175-186. doi:10.1016/j.cie.2017.08.016.
- **Santos, V.G.M. & Carvalho, M.A.M.** (2018). Adaptive large neighborhood search applied to the design of electronic circuits. *ASOC*. doi:10.1016/j.asoc.2018.08.017.
- **Arbib, C., Marinelli, F. & Ventura, P.** (2016). One-dimensional cutting stock with a limited number of open stacks. *ITOR*. doi:10.1111/itor.12134. Its 2010 report (TRCS 007/2010) was read.
- **Arbib, C., Marinelli, F. & Pezzella, F.** (2012). An LP-based tabu search for batch scheduling in a cutting process with finite buffers. *IJPE*. doi:10.1016/j.ijpe.2011.12.003.
- **Visentin, A., Prestwich, S., Rossi, R. & Tarim, S.A.** (2019). Modelling dynamic programming-based global constraints in constraint programming. WCGO 2019. doi:10.1007/978-3-030-21803-4_42. The Edinburgh repository returned 403; the GCAI 2018 precursor was read.
- **Stivala, A.** (2010). *Algorithms for the study of RNA and protein structure*. PhD thesis, University of Melbourne. Not found on Minerva Access by search.
- **Doulabi, S.H.H., Rousseau, L.-M. & Pesant, G.** (2016). A constraint-programming-based branch-and-price-and-cut approach for operating room planning and scheduling. *IJOC* 28(3). doi:10.1287/ijoc.2015.0686.
- Camanho et al. (2022), *ITOR*, doi:10.1111/itor.13129, and Amirteimoori et al. (2024), *ITOR*, doi:10.1111/itor.13560. Both are probably false index links: their titles concern efficiency analysis.

Among the citers of the thesis only, one unread work could bear on the rules:
**Gange, G., Chu, G. & Stuckey, P.J.** (2019). Certifying optimality in
constraint programming. Copy at
https://people.eng.unimelb.edu.au/pstuckey/papers/certified-cp.pdf, where the
site's bot check refused the fetch.

**Obtained in the same sweep.** Fink, C. (2012), *O problema de minimização de
pilhas abertas — novas contribuições*, PhD thesis, ICMC-USP,
doi:10.11606/t.55.2012.tde-19022013-084858. It is in `literature/` as
`fink_2012_phd_thesis_mosp_novas_contribuicoes.pdf`, from
http://www.teses.usp.br/teses/disponiveis/55/55134/tde-19022013-084858/publico/TeseRevisada.pdf
(fetched 2026-10-03). Its pp. 27–28 restate CP 2009 Theorem 1.

## IJOC papers to obtain (2026-10-04)

From the IJOC sweep, `paper2/ijoc_literature.md`, in order of importance. All are paywalled or blocked by a bot check; none was circumvented.

- Fischetti, M. & Salvagnin, D. (2010). Pruning moves. *IJOC* 22(1), 108-119. doi:10.1287/ijoc.1090.0329
- Fukasawa, R. & Poirrier, L. (2017). Numerically safe lower bounds for the capacitated vehicle routing problem. *IJOC* 29(3), 544-557. doi:10.1287/ijoc.2017.0747
- Garcia de la Banda, M., Stuckey, P.J. & Chu, G. (2011). Solving talent scheduling with dynamic programming. *IJOC* 23(1), 120-137. doi:10.1287/ijoc.1090.0378 (author copy behind a browser check: people.eng.unimelb.edu.au/pstuckey/papers/rehearsal.pdf)
- Belov, G. & Scheithauer, G. (2007). Setup and open-stacks minimization in one-dimensional stock cutting. *IJOC* 19(1), 27-35. doi:10.1287/ijoc.1050.0132
- Caprara, A. & Salazar-González, J.J. (2005). Laying out sparse graphs with provably minimum bandwidth. *IJOC* 17(3), 356-373. doi:10.1287/ijoc.1040.0083
- Halbig, K., Hümbs, L., Rösel, F., Schewe, L. & Weninger, D. (2024). Computing optimality certificates for convex mixed-integer nonlinear problems. *IJOC* 36(6), 1579-1610. doi:10.1287/ijoc.2022.0099 (Edinburgh preprint behind a browser check)
- Sewell, E.C. & Jacobson, S.H. (2012). A branch, bound, and remember algorithm for the simple assembly line balancing problem. *IJOC* 24(3), 433-442. doi:10.1287/ijoc.1110.0462
- Gmys, J. (2022). Exactly solving hard permutation flowshop scheduling problems on peta-scale GPU-accelerated supercomputers. *IJOC* 34(5), 2502-2522. doi:10.1287/ijoc.2022.1193 (HAL hal-03689608 behind a browser check)
- Hicks, I.V. (2005). Planar branch decompositions I: the ratcatcher. *IJOC* 17(4), 402-412. doi:10.1287/ijoc.1040.0075
- Hicks, I.V. (2005). Planar branch decompositions II: the cycle method. *IJOC* 17(4), 413-421. doi:10.1287/ijoc.1040.0074
- Bergman, D., Cire, A.A., van Hoeve, W.-J. & Hooker, J.N. (2016). Discrete optimization with decision diagrams. *IJOC* 28(1), 47-66. doi:10.1287/ijoc.2015.0648
- Cook, W. & Seymour, P. (2003). Tour merging via branch-decomposition. *IJOC* 15(3), 233-248. doi:10.1287/ijoc.15.3.233.16078
- Cook, W., Dash, S., Fukasawa, R. & Goycoolea, M. (2009). Numerically safe Gomory mixed-integer cuts. *IJOC* 21(4), 641-649. doi:10.1287/ijoc.1090.0324
- Malapert, A., Cambazard, H., Guéret, C., Jussien, N., Langevin, A. & Rousseau, L.-M. (2012). An optimal constraint programming approach to the open-shop problem. *IJOC* 24(2), 228-244. doi:10.1287/ijoc.1100.0446
- Barr, R.S. & Hickman, B.L. (1993). Reporting computational experiments with parallel algorithms. *ORSA J. Comput.* 5(1), 2-18. doi:10.1287/ijoc.5.1.2
- Margulies, S., Ma, J. & Hicks, I.V. (2013). The Cunningham-Geelen method in practice. *IJOC* 25(4), 599-610. doi:10.1287/ijoc.1120.0524
- Anjos, M.F. & Vannelli, A. (2008). Computing globally optimal solutions for single-row layout problems using semidefinite programming and cutting planes. *IJOC* 20(4), 611-617. doi:10.1287/ijoc.1080.0270
- Buchheim, C., Wiegele, A. & Zheng, L. (2010). Exact algorithms for the quadratic linear ordering problem. *IJOC* 22(1), 168-177. doi:10.1287/ijoc.1090.0318
- Qiu, Y., Cherniavskii, M., Goldengorin, B. & Pardalos, P.M. (2026). A computational study of the tool replacement problem. *IJOC* 38(1), 86-101. doi:10.1287/ijoc.2023.0474
