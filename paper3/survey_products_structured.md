# Pathwidth of structured and product graphs: a literature survey for paper 3

*Survey of 2026-10-09. Topic: closed formulas and bounds for pathwidth on special
graph classes and graph products, with an eye to "applied mathematics of
pathwidth". Throughout, pw = vertex separation (Kinnersley 1992) = node search
number − 1 = interval thickness − 1, and for a MOSP instance whose MOSP graph is
G, MOSP = pw(G) + 1 (`lean/MOSPFormalization/MOSPGraph.lean`).*

Conventions. "Read" means the statement was read in the PDF at the page given.
"Secondary" means it was read only as quoted in another held paper, which is
named. "Abstract only" means nobody here has seen the text. Nothing below is
cited from memory. Solver checks use `pathwidth_solver` (`pathwidth.solve.solve`,
repaired rules, the default) and, at n ≤ 18, also the independent subset DP
`fixed_parameter_algorithm.pathwidth.compute_pathwidth`. Every solver value is
proved: a refutation of width − 1, or a lower bound that meets it, unless the
row says "UNPROVED". The scripts and raw output are in the session scratchpad
(`p3survey/check.py`, `check2.py`, `harper.py`, `mospprod.py`), not in the
repository.

## 1. The table

| Class | Result | Status | Source, theorem, page | Held? | Our solver |
|---|---|---|---|---|---|
| Complete graph K_n | pw = n − 1 | closed (trivial) | clique containment, e.g. Bodlaender & Möhring TR RUU-CS-90-07, Lemma 3.1, p. 5 | yes, `1990-Bodlaender-Mohring-Pathwidth-Treewidth-Cographs-TR-RUU-CS-90-7.pdf` | K5 = 4, K10 = 9 ✓ |
| Join G × H (complete join) | pw(G × H) = min(pw(G) + \|V(H)\|, pw(H) + \|V(G)\|) | closed | Bodlaender & Möhring TR 1990, Lemma 3.4(iv), p. 6 (journal: SIAM J. Discrete Math. 6 (1993)) | yes (scan, read as page images) | via the next three rows ✓ |
| Complete bipartite K_{m,n} | pw = min(m, n) | closed, corollary of the join lemma | as above | yes | K2,5 = 2, K3,3 = 3, K3,7 = 3, K5,6 = 5 ✓ |
| Complete multipartite K_{n1,…,nk} | pw = Σ n_i − max n_i | closed, corollary of the join lemma by induction | as above | yes | K2,2,2 = 4, K1,2,3 = 3, K3,3,4 = 6, K2,4,4,5 = 10 ✓ |
| Wheel W_n = K_1 × C_n | pw = 3 | closed (join lemma with pw(C_n) = 2) | as above | yes | W4, W6, W12 = 3 ✓ |
| Cycle C_n | pw = 2 | closed (folklore) | no paper read for it | – | C3, C8, C15 = 2 ✓ |
| Path power P_n^k | pw = k (n > k) | folklore; P_n^k is an interval graph of clique number k + 1 | no paper read | – | P10^2, P15^2 = 2; P12^3, P20^3 = 3 ✓ |
| Cycle power C_n^k | pw = 2k (n large) | folklore upper bound; no source read | – | – | C10^2, C15^2 = 4; C12^3, C20^3 = 6 ✓ |
| 2D grid P_m □ P_n, m ≤ n | pw = bw = m | closed | Otachi & Suda 2011, Cor. 2.6 (p. 3) + Thm 3.1 (p. 4); Ellis & Warren 2008 (secondary, quoted by Clarke et al. 2019, p. 2) | Otachi–Suda yes; Ellis–Warren no | all 2 ≤ m ≤ 6, m ≤ n ≤ 8 ✓ (25 graphs) |
| d-dim grid ∏ P_{n_i}, n_1 ≤ … ≤ n_d | pw = bw = vbw (isoperimetric "simplicial order" exists); = ∏_{i<d} n_i if Σ_{i<d}(n_i − 1) ≤ n_d | closed in that regime; general d ≥ 4 open | Otachi & Suda 2011, Cor. 2.6 (p. 3), Thm 3.1 (p. 4) | yes, `2011-Otachi-Suda-…-arXiv.pdf` | P2×P3×P4 = 6, P3×P3×P5 = 9 ✓ |
| 3D grid P_{n1} □ P_{n2} □ P_{n3}, n1 ≤ n2 ≤ n3 | pw = bw = n1 n2 if n1 + n2 − 2 ≤ n3; otherwise n1 n2 − ⌊(n1 + n2 − n3 − 1)² / 4⌋ | closed | Otachi & Suda 2011, Thm 4.2, p. 6 (cube case FitzGerald 1974 for bw) | yes | P3^3 = 8, P4^3 = 14, P3×P4×P4 = 11 (formula 11) ✓; P5^3: upper bound 21 = formula, refutation of 20 not finished in 300 s |
| 4D cube grid P_n^4 | vbw = ⌊(8n³ + 3n² + 4n)/12⌋ | **conjecture** (verified by them for vbw to n = 100) | Otachi & Suda 2011, Conj. 5.1, p. 9 | yes | P2^4 = Q4 = 7 ✓; **P3^4 = 21 = conjectured value**, proved by our solver (refutation, 32 s) |
| Even torus ∏ C_{2n_i} | pw = bw = vbw = vbw(P_2^d □ ∏ P_{n_i}); = 2^d ∏_{i<d} n_i if Σ_{i<d} n_i ≤ n_d − 1 | closed in that regime | Otachi & Suda 2011, Cor. 2.7, 2.9 (p. 3–4), Thm 3.3 (p. 5); rests on Riordan 1998, Bezrukov & Leck 2009 | yes | C4×C6 = 8 ✓ |
| 2D torus C_n □ C_n | pw = 2n − 1 | closed | Ellis & Warren 2008 (secondary: Gima et al. 2026, p. 1) | Ellis–Warren no | C3² = 5, C4² = 7, C5² = 9, C6² = 11, C7² = 13 ✓ |
| 2D torus C_m □ C_n, m < n | pw = 2m (our measurement); tw = 2m if n − m ≥ 2, tw ∈ {2m − 1, 2m} if n − m = 1 | tw closed except \|m−n\| ≤ 1; pw: Ellis–Warren not read | Aidun et al. 2020, Thm 1.2, p. 1–2; Ellis & Warren 2008 not read | Aidun yes | 14 graphs, 3 ≤ m < n ≤ 9: all 2m ✓ |
| Torus treewidth T_n | tw(C_n □ C_n) = 2n − 1 for n ≥ 5; tw(T_4) = 6 | closed (2026) | Gima, Morimoto, Okada, Otachi 2026, Thm 1.1, p. 1 | yes, `2026-Gima-…-arXiv.pdf` | pw(T_4) = 7 > tw(T_4) = 6: a pw > tw example |
| Cylinder (stacked prism) C_m □ P_n | tw = min(m, 2n) for m ≠ 2n | tw closed except m = 2n; pw not stated | Aidun et al. 2020, Thm 1.1, p. 1 | yes | pw = min(m, 2n) on all 23 measured (m ≤ n: = m; 2n ≤ m: = 2n), so pw = tw there |
| Hypercube Q_d | pw = bw = max_s b_v(s, Q_d) = Σ_{m=0}^{d−1} C(m, ⌊m/2⌋) | **closed** | Chandran & Kavitha 2006, Thm 2, p. 361 (via Harper's Lemma 3; optimal decomposition §3, Lemma 5, p. 363) | yes | Q3 = 4, Q4 = 7, Q5 = 13, Q6 = 23 ✓ |
| Hypercube treewidth | tw(Q_d) = Θ(2^d/√d) | **open** exactly; Chandran–Kavitha say it may equal pw | Chandran & Kavitha 2006, Thm 3, p. 363 and remark p. 360 | yes | – |
| Hypercube (Lin & Lin) | pw(Q_d) = bw(Q_d) by Harper's method; tw open | abstract only (per `MISSING.md`) | Lin & Lin 2025, DAM 363, 201–214 | **no** (paywalled) | – |
| Generalized hypercube H(t, 2, n) (distance ≤ t) | pw = bw = Σ_{k=⌊(n−t)/2⌋}^{⌊(n−t)/2⌋+t−1} C(n,k) + Σ_{a=0}^{⌊(n−t−1)/2⌋} [C(t+2a, t+a−1) − C(t+2a, a−1)] | closed | Wang, Cao, Lv & Lu 2026, Thm 1, p. 2 | yes, `2026-Wang-…-EJC.pdf` | H(2,2,4) = 12, H(2,2,5) = 22, H(3,2,5) = 28, H(2,2,6) = 42, H(3,2,6) = 53, all = formula ✓ |
| Hamming K_q^d (q ≥ 3) | tw = Θ(q^d/√d) | pw **open** for d ≥ 3 | Chandran & Kavitha 2006, Thm 3 (p. 363); Wang et al. 2026, Thm 2 (p. 2) for H(t,q,n) | yes | K3^3 = 13, K4^3 = 31, K3^4 = 34 (proved, 318 s) |
| Rook graph K_m □ K_n = L(K_{m,n}), m ≤ n | pw = (m/2) n + m/2 − 1 (m even), ⌈m/2⌉ n − 1 (m odd) | closed | Clarke, Messinger & Power 2019, Cor. 15, arXiv p. 10; for m = n also Harvey & Wood 2015, Thm 3 (k = 2), p. 3 | yes, both | K3□K3 = 5, K3□K4 = 7, K4□K4 = 9, K4□K5 = 11, K5□K5 = 14 ✓ |
| L(K_n) = J(n, 2) | tw = pw = ((n−1)/2)² + n − 2 (n odd), (n−2)n/4 + n − 2 (n even) | closed | Harvey & Wood 2015, Thm 1, p. 2; Fabila-Monroy et al. 2025, Thm 3, p. 2 | yes, both | L(K5) = 7, L(K6) = 10, L(K7) = 14 ✓ |
| L(K_{c,…,c}) (regular complete multipartite) | tw = pw, explicit quadratic in c, k (three parity cases) | closed; general K_{n1..nk}: bounds | Harvey & Wood 2015, Thm 3, p. 3; Thm 2, p. 2 | yes | via rook rows ✓ |
| Johnson J(n, k), k ≥ 3 | tw = Θ(n^k); explicit upper bound; conjectured tight and pw = tw | **conjecture** | Fabila-Monroy et al. 2025, Thm 4 (p. 3), Conj. 21 (p. 20) | yes | J(6,3) = 13, J(7,3) = 22 |
| Kneser K(n, k), k ≥ 3, n ≥ 4k² − 4k + 3 | tw = C(n−1, k) − 1 | tw closed; **pw not studied** | Harvey & Wood 2014, Thm 1, p. 2; conjectured for n ≥ 3k, Conj. 12, p. 9 | yes | K(9,3): **pw = 55 = conjectured tw** (n = 9 below their range); K(7,3) = 13, K(8,3) = 32 |
| Kneser K(n, 2) | tw = C(n−1, 2) − 1 for n ≥ 6; tw(Petersen) = 4 | tw closed; pw not studied | Harvey & Wood 2014, Thm 2, p. 2 | yes | **pw = C(n−1, 2) = tw + 1 for n = 6…10** (10, 15, 21, 28, 36); Petersen pw = 5 = tw + 1 |
| Generalized Kneser K(n, k, t), t ≥ 2 | tw = C(n,k) − C(n−t, k−t) − 1 for n large | tw closed; pw not studied | Liu, Cao & Lu 2022, Thm 2, p. 2 | yes | – |
| q-Kneser graphs | tw known for large n | abstract only | Cao, Liu, Lu & Lv, DAM 2023 (arXiv 2101.04518) | no (arXiv available, not read) | – |
| Bipartite Kneser BK(n, k) | tw = C(n, k) − 1 if 3C(n−k, k) ≥ 2C(n, k), k ≥ 2 | tw closed | Wang et al. 2026, Thm 3, p. 2 | yes | – |
| Generalized Petersen G(n, k) | 2k + 1 ≤ tw ≤ pw ≤ 2k + 2 for n ≥ 8(2k + 2)² | bounds, gap 1 | Wang et al. 2026, Thm 5, p. 3 | yes | **pw = 2k + 2** for k = 1 (n = 12…30), k = 2 (n = 12…40), k = 3 (n = 15…40); Petersen G(5,2) = 5; G(8,3) = 6 |
| Cartesian G □ H, general | pw(G □ H) ≤ pw(G ⊠ H) ≤ (pw(G) + 1)\|V(H)\| − 1 | upper bound | Hickingbotham & Wood 2023, Lemma 19, arXiv p. 15 | yes | – |
| Cartesian, lower | pw(G □ H) ≥ ½(tw(G) + 1)(pw(H) + 1) − 1; tw(G □ H) ≥ ½(tw(G)+1)(tw(H)+1) − 1 | lower bound; whether tw(G) → pw(G) is **open** (Question 22) | Kaul 2026, Cor. 11 (p. 6), Thm 3 (p. 3), Question 22 (p. 12) | yes | – |
| Cartesian, k-connected | tw(G □ H) ≥ k(n − 2k + 2) − 1 for k-connected G, H on ≥ n vertices | lower bound | Wood 2013, Thm 2, p. 2 | yes | – |
| Strong G ⊠ H | pw(G ⊠ H) ≥ (pw(G) + 1)(pw(H) + 1) − 1 (tight for cliques) | lower bound (2026) | Kaul 2026, Thm 2, p. 2 | yes, `2026-Kaul-…-arXiv.pdf` | king P_n ⊠ P_n: **pw = n + 1** (n = 3…8; Kaul gives 3); C_m ⊠ C_n: **2m + 2** for 4 ≤ m ≤ n ≤ 7 (Kaul gives 8) |
| Lexicographic G[K_n] | pw = n(pw(G) + 1) − 1 (our measurement; equals Kaul's lower bound since G[K_n] = G ⊠ K_n) | lower bound proved (Kaul Thm 2), upper bound by blowing up bags | Kaul 2026, Thm 2, p. 2 (G ∘ K_n = G ⊠ K_n) | yes | P4[K3] = 5, C5[K2] = 5, P5[K4] = 7, Petersen[K2] = 11 ✓ |
| Tensor (direct) G × H | bounded-pathwidth characterisation only | qualitative | Hickingbotham & Wood 2023, §4.2 | yes | P5×P5 = 3, C6×C6 = 7, C5×C7 = 11, K4×K4 = 12, K3×P6 = 4 (no formula to compare) |
| Circulants | none found | no source | – | – | C16(1,4) = 7, C12(1,3) = 6, C13(1,5) = 6, C15(1,2,4) = 8 |
| Isoperimetric lower bound (general) | pw(G) ≥ b_v(s, G) = min_{\|S\|=s} \|N(S)\| for every s | theorem | Chandran & Kavitha 2006, Thm 1, p. 361 (Harper 1966 for bandwidth); Otachi & Suda 2011, Thm 2.2 and Cor. 2.4 (isoperimetric order ⇒ vbw = pw = bw), p. 2–3 | yes | exact max_s b_v equals pw on all 19 symmetric graphs tested (§2) |

## 2. What our solver showed

**No published formula disagreed with the solver.** Every closed formula we
could instantiate agreed on every case: grids (25), 3D grids (4 proved, including
Otachi–Suda's non-cubic case), hypercubes Q3–Q6, generalized hypercubes
H(t, 2, n) (7), rook graphs (5), L(K_n) (3), complete multipartite (8), cycles,
wheels, path and cycle powers, and the torus values quoted from Ellis & Warren.
The solver and the subset DP agreed on all 74 graphs with n ≤ 18, and the
53 closed formulas instantiated in the first batch all matched. About 190
graphs in all, roughly 20 minutes on one core.

Values that go beyond what was read:

1. **4D grid.** pw(P_3^4) = 21, proved, matching Otachi & Suda's Conjecture
   5.1. They verified the *vertex boundary width* formula numerically; this is
   an independent check of pathwidth itself, though for grids the two are equal
   by their Corollary 2.6.
2. **Kneser graphs, pathwidth.** pw(K(n, 2)) = C(n−1, 2) for n = 6, …, 10, one
   above the treewidth Harvey & Wood proved; pw(K(5,2)) = 5 = tw + 1. For k = 3,
   pw(K(9, 3)) = 55 = C(8, 3) − 1, which is Harvey & Wood's *conjectured*
   treewidth (their Conjecture 12 covers n ≥ 3k = 9; their theorem needs
   n ≥ 27). Since tw ≤ pw, this proves tw(K(9,3)) ≤ 55, the upper half of the
   conjecture at that point.
3. **Generalized Petersen.** pw(G(n, k)) = 2k + 2 at every measured point for
   k = 1, 2, 3, the upper end of Wang et al.'s interval, although our n are
   below their 8(2k + 2)² threshold.
4. **Strong products.** pw(P_n ⊠ P_n) = n + 1 for n = 3…8 and
   pw(C_m ⊠ C_n) = 2m + 2 for 4 ≤ m ≤ n ≤ 7: well above Kaul's lower bound
   (pw(G) + 1)(pw(H) + 1) − 1, which Kaul shows is attained by products of
   cliques and which we found attained by every G ⊠ K_n we measured.
5. **Cylinders and tori.** pw(C_m □ P_n) = min(m, 2n) and pw(C_m □ C_n) = 2m
   for m < n on every measured case, so pw equals Aidun et al.'s treewidth
   wherever theirs is determined, and on the n = m + 1 cases where it is not,
   pw = 2m.
6. **Harper's bound is exact on everything symmetric we tried.** The exact
   vertex-isoperimetric value max_s min_{|S|=s} |∂S| (inner and outer, by
   enumerating all 2^n subsets, n ≤ 20) equals pw on all 19 graphs tested: Q4,
   rook K3□K3 and K4□K4, tori C4×C4, C3×C5, C4×C5, Petersen, K(6,2), J(6,2),
   J(6,3), G(8,3), G(10,2), king P4⊠P4, C4⊠C4, grid 4×5, K4×K4 (tensor),
   P5[K4], the prism C8□P2 and the circulant C16(1,4). This includes graphs
   with pw > tw (Petersen, K(6,2), T_4). This is the expansion bound of
   `reports/expansion_bound.md`, computed exactly instead of capped. On the MOSP
   corpus it fails on trees of cliques; on vertex-transitive and product graphs
   it is tight in every case we measured.
7. **Hamming graphs**: pw(K_3^3) = 13, pw(K_4^3) = 31, pw(K_3^4) = 34, all
   proved (the last in 318 s). No formula exists to compare them with; they
   are data for the open problem in §3.

**MOSP realisations, checked.** For graphs G1, G2 with edge-incidence matrices
M1, M2 (customers = vertices, one two-customer pattern per edge, no isolated
vertices):

- the Kronecker product M1 ⊗ M2 has MOSP graph exactly G1 ⊠ G2 (pattern (e, f)
  is the K4 on e × f);
- [M1 ⊗ I, I ⊗ M2] has MOSP graph exactly G1 □ G2.

Checked by isomorphism on four pairs (P3·P3, C4·P3, P4·C3, C5·P2) and solved
with `solve_mosp_exact`; the values equal pw + 1 of the product graph. So
Kaul's Theorem 2 says, in MOSP terms, **MOSP(M1 ⊗ M2) ≥ MOSP(M1) · MOSP(M2)**,
the open-stacks value is supermultiplicative under the Kronecker product of
instances, with equality on every measured case where one factor's MOSP graph is complete
(the lexicographic rows), and strict otherwise (MOSP(M1) · MOSP(M2) = 4 against
the actual 5 for P3 · P3). A grid
P_m □ P_n is the MOSP graph of [M_{P_m} ⊗ I_n, I_m ⊗ M_{P_n}]: an m × n array
of customers whose products are its horizontal and vertical neighbour pairs.

## 3. Open problems stated in the literature

- **Treewidth of hypercubes and Hamming graphs, exactly.** Only Θ(2^d/√d) is
  known; Chandran & Kavitha (2006, p. 360) suggest tw(Q_d) may equal pw(Q_d).
  Lin & Lin (2025) apparently still leave tw open (abstract only).
- **Pathwidth of Hamming graphs K_q^d, d ≥ 3.** Not found anywhere. The
  bandwidth of 3-dimensional Hamming graphs is the subject of Balogh, Bezrukov,
  Harper & Seress (2008, not read).
- **4D grids**: Otachi & Suda, Conjecture 5.1, pw(P_n^4) = ⌊(8n³ + 3n² + 4n)/12⌋;
  and d-dimensional grids outside the "large last factor" regime.
- **Johnson graphs**: Fabila-Monroy et al., Conjecture 21: pw(J(n,k)) = tw(J(n,k))
  = their Theorem 4 upper bound.
- **Kneser graphs**: Harvey & Wood, Conjecture 12: tw(K(n,k)) = C(n−1,k) − 1 for
  n ≥ 3k.
- **Products**: Kaul, Question 22 (does pw(G □ H) ≥ ½(pw(G)+1)(pw(H)+1) − 1
  hold?); Hickingbotham & Wood / Kaul Question 23 (is tw(G ⊠ H) = O(tw(G □ H))?).
- **Tori and cylinders**: tw(C_n □ C_{n+1}) ∈ {2n − 1, 2n} and
  tw(C_{2n} □ P_n) ∈ {2n − 1, 2n}, each value attained for some n (Aidun et al.).
- **Generalized Petersen**: whether tw, pw are 2k + 1 or 2k + 2 (Wang et al.).

## 4. Applied-mathematics opportunities

1. **Pathwidth of Kneser graphs.** Nobody has studied it, and the data are
   clean: pw(K(n,2)) = C(n−1, 2) = tw + 1 for 6 ≤ n ≤ 10, while for k = 3 the
   one point measured has pw = the conjectured tw. A conjecture
   "pw(K(n,k)) = C(n−1,k) − [k ≥ 3]" (or a cleaner form) can be tested to
   K(11,2), K(10,3), K(11,3) with our solver, and the exact Harper value equals
   pw on K(6,2), which suggests the proof route: an Erdős–Ko–Rado-type
   vertex-isoperimetric inequality for one set size, plus an explicit layout.
   This is the most "new theorem within reach" item found.
2. **Isoperimetric exactness as an organising principle, measured.** Every
   closed formula in the table except the join-type ones is proved by
   exhibiting an isoperimetric (nested) order: grids, even tori, hypercubes,
   generalized hypercubes (Otachi–Suda Cor. 2.4; Chandran–Kavitha Thm 2; Wang
   et al. via Hales numberings). Our exact Harper computation found
   pw = max_s b_v(s) on all 19 symmetric graphs tested, including ones with no
   known nested order (Kneser, Johnson, Petersen-type, strong products,
   circulants). A systematic census — every vertex-transitive graph to 20–24
   vertices, or every Cayley graph of small groups — of where Harper's bound is
   exact would be new, cheap with our tools, and would separate the classes
   where a closed formula is "just" an isoperimetric problem from those where
   it is not. The repository already owns both halves: the expansion bound and
   an exact pathwidth solver that reaches 80+ vertices on these graphs.
3. **MOSP of product instances.** The two matrix constructions above make
   Cartesian and strong products of MOSP graphs *natural MOSP instances*
   (Kronecker products of order matrices; block "row-and-column" designs), and
   Kaul's 2026 theorem becomes a statement about open stacks:
   MOSP(M1 ⊗ M2) ≥ MOSP(M1) · MOSP(M2). Closed-form families then give exact
   benchmark instances with known optima at any size: grids (pw = min(m,n)),
   3D grids (Otachi–Suda), hypercubes (Σ C(m, ⌊m/2⌋)), generalized hypercubes,
   rook graphs, L(K_n). At 125 customers these are far larger than the
   Chu & Stuckey instances we certify in a day, and they come with proofs
   instead of solver certificates; they are also an honest test of whether the
   solver's hardness depends on symmetry. Measured strong-product values
   (king graphs n + 1, C_m ⊠ C_n 2m + 2) suggest formulas worth proving.
4. Smaller items, each one session of solver time: Otachi–Suda Conjecture 5.1
   at P_4^4 (256 vertices, likely beyond reach) and P_3^5; pw(K_q^3) against the
   bandwidth values of Balogh et al. (2008); pw(G(n,k)) = 2k + 2 for small k and
   all n; Fabila-Monroy et al. Conjecture 21 at J(7,3), J(8,3) (pw = 22 measured
   for J(7,3); compare with their Theorem 4 bound).

## 5. Papers to obtain

| Paper | DOI | Why | Availability |
|---|---|---|---|
| Lin, L. & Lin, Y. (2025). Discrete isoperimetric method for bandwidth, pathwidth and treewidth of hypercubes. *DAM* 363, 201–214 | 10.1016/j.dam.2024.12.001 | the most recent hypercube paper; what it adds beyond Chandran–Kavitha is unknown | paywalled; no preprint found |
| Ellis, J. & Warren, R. (2008). Lower bounds on the pathwidth of some grid-like graphs. *DAM* 156(5), 545–555 | 10.1016/j.dam.2007.02.006 | source of pw(P_m □ P_n), pw(C_n □ C_n) = 2n − 1, cylinders, presumably C_m □ C_n | Elsevier open archive (Unpaywall: OA, publisher); ScienceDirect blocks scripted download, fetch in a browser |
| Kiyomi, M., Okamoto, Y. & Otachi, Y. (2016). On the treewidth of toroidal grids. *DAM* 198, 303–306 | 10.1016/j.dam.2015.06.027 | tw(T_4) = 6, tw(T_n) ≥ 2n − 2 | open archive; browser |
| Kozawa, K., Otachi, Y. & Yamazaki, K. (2014). Lower bounds for treewidth of product graphs. *DAM* 162, 251–258 | 10.1016/j.dam.2013.08.005 | tw(G ⊠ H) ≥ (tw(G)+1) had(H) − 1 and Cartesian bounds | open archive; browser |
| Harper, L.H. (1966). Optimal numberings and isoperimetric problems on graphs. *J. Combin. Theory* 1(3), 385–393 | 10.1016/S0021-9800(66)80059-5 | the method; hypercube vertex-isoperimetric order | open archive; browser |
| Harper, L.H. (1999). On an isoperimetric problem for Hamming graphs. *DAM* 95, 285–309 | 10.1016/S0166-218X(99)00082-7 | Hamming vertex-isoperimetry, needed for pw(K_q^d) | open archive; browser |
| Balogh, J., Bezrukov, S.L., Harper, L.H. & Seress, Á. (2008). On the bandwidth of 3-dimensional Hamming graphs. *TCS* 407 | 10.1016/j.tcs.2008.07.029 | bw(K_n^3) as an upper bound to compare with pw | open archive; browser |
| Chandran, L.S., Kavitha, T. & Subramanian, C.R. (2003). Isoperimetric inequalities and the width parameters of graphs. COCOON, LNCS 2697, 385–393 | 10.1007/3-540-45071-8_39 | general isoperimetric bounds on tw/pw | paywalled |
| Djelloul, S. (2009). Treewidth and logical definability of graph products. *TCS* 410, 696–710 | 10.1016/j.tcs.2008.10.019 | pw(G □ P_n) ≤ \|V(G)\| (used by Otachi–Suda) | open archive; browser |
| Wang, X., Wu, X. & Dumitrescu, S. (2009). On explicit formulas for bandwidth and antibandwidth of hypercubes. *DAM* 157, 1947–1952 | not looked up | first explicit proof of Harper's hypercube formula | not looked up |
| Bezrukov, S.L. & Leck, U. (2009). A simple proof of the Karakhanyan–Riordan theorem on the even discrete torus. *SIAM J. Discrete Math.* 23, 1416–1421 | not looked up | even-torus reduction behind Otachi–Suda Cor. 2.9 | not looked up |
| Ellis, J. (2023). Computing the pathwidth and bandwidth of solid, convex grids. SSRN preprint | 10.2139/ssrn.4592858 | grid-like graph classes, same author as the 2008 paper | Unpaywall reports an accepted version in a repository; not fetched |
| Xue, Y., Yang, B. & Zilles, S. (2024). The zero-visibility cops and robber game on graph products. *TCS* 1007, 114676 | 10.1016/j.tcs.2024.114676 | product bounds tied to pathwidth | paywalled |
| Cao, M., Liu, K., Lu, M. & Lv, Z. Treewidth of the q-Kneser graphs, *DAM* 2023 | 10.1016/j.dam.2023.09.004 | Kneser family | arXiv 2101.04518 free; not read |
| Harper, L.H. (2004). *Global Methods for Combinatorial Isoperimetric Problems*. CUP | 10.1017/CBO9780511616679 | book-length treatment | purchase/library |

## 6. Held for this survey (added to `literature/` 2026-10-09)

All open access, each opened and its title page checked against the citation.

- `2011-Otachi-Suda-Bandwidth-Pathwidth-Three-Dimensional-Grids-DM-arXiv.pdf` — arXiv 1101.0964; *Discrete Math.* 311 (2011), doi 10.1016/j.disc.2011.02.019.
- `2013-Wood-Treewidth-Cartesian-Products-Highly-Connected-JGT-arXiv.pdf` — arXiv 1105.1586; *J. Graph Theory* 73(3) (2013) 318–321.
- `2014-Harvey-Wood-Treewidth-Kneser-Graph-Erdos-Ko-Rado-EJC.pdf` — *Electron. J. Combin.* 21(1) #P1.48, doi 10.37236/3971.
- `2015-Harvey-Wood-Treewidth-Line-Graph-Complete-Multipartite-JGT-arXiv.pdf` — arXiv 1210.8205v2; journal version *J. Graph Theory* 79 (2015) 48–54, doi 10.1002/jgt.21813 (complete-graph part only).
- `2019-Clarke-Messinger-Power-Bounding-Search-Number-Graph-Products-KMJ-arXiv.pdf` — arXiv 1604.04509; *Kyungpook Math. J.* 59(1) (2019) 175–190.
- `2020-Aidun-Dean-Morrison-Yu-Yuan-Treewidth-Gonality-Glued-Grid-Graphs-DAM-arXiv.pdf` — arXiv 1808.09475; *DAM* 279 (2020) 1–11.
- `2022-Liu-Cao-Lu-Treewidth-Generalized-Kneser-Graphs-EJC.pdf` — *Electron. J. Combin.* 29(1) #P1.57, doi 10.37236/10035.
- `2023-Hickingbotham-Wood-Structural-Properties-Graph-Products-JGT-arXiv.pdf` — arXiv 2110.00721; *J. Graph Theory* (2023), doi 10.1002/jgt.23023.
- `2025-Fabila-Monroy-et-al-Treewidth-Token-Johnson-Graphs-DAM-arXiv.pdf` — arXiv 2402.17962v3; *DAM* (2025), doi 10.1016/j.dam.2025.11.042.
- `2026-Gima-Morimoto-Okada-Otachi-Treewidth-nxn-Toroidal-Grid-arXiv.pdf` — arXiv 2605.21015.
- `2026-Kaul-Treewidth-Products-High-Treewidth-arXiv.pdf` — arXiv 2607.16778.
- `2026-Wang-Cao-Lv-Lu-Treewidth-Generalized-Hamming-Bipartite-Kneser-Generalized-Petersen-EJC.pdf` — *Electron. J. Combin.* 33(1) #P1.7, doi 10.37236/12892.

Already held and used: `chandran_kavitha_2006_treewidth_pathwidth_hypercubes.pdf`;
`1990-Bodlaender-Mohring-Pathwidth-Treewidth-Cographs-TR-RUU-CS-90-7.pdf`
(added by the parallel survey the same day; a scan, read as page images).
