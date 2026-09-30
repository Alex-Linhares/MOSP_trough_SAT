# Problem transformations

Section 3 of *The pathwidth complex* in paper form: first each problem of
Table 1, stated as a decision problem in the style of Garey & Johnson, then the
transformations between them, from exact equalities to bands, then what is not
proved, then what is false. Every statement is proved in Lean unless it says
otherwise. The Lean names refer to `../lean/MOSPFormalization/` and
`Complex/`. The evidence, the census of the sources and the brute-force check
are in `equivalences.md`, and the faults in published proofs are in
`proof_reductions.md`.

**Conventions.** Graphs are finite and simple, $G = (V, E)$, $n = |V|$. A
*layout* is a bijection $L : V \to \{1, \dots, n\}$. For a 0/1 matrix $M$ with
rows $R$ and columns $C$, the *MOSP graph* $G_M$ has vertex set $R$, with
$r \sim r'$ iff some column $c$ has $M_{rc} = M_{r'c} = 1$. Each column becomes a
clique on its rows. For a column permutation $\pi$, row $r$ is *active at
position* $j$ if some columns $x, y$ with $M_{rx} = M_{ry} = 1$ satisfy
$\pi(x) \le j \le \pi(y)$.

---

## 1. The problems

### 1.1 Path-width
**Instance.** A graph $G = (V, E)$ and an integer $k \ge 0$.
**Question.** Is there a sequence $X_1, \dots, X_r \subseteq V$ with
$\bigcup_i X_i = V$, every edge inside some $X_i$,
$X_i \cap X_\ell \subseteq X_j$ whenever $i \le j \le \ell$, and
$|X_i| \le k + 1$ for all $i$?
The least such $k$ is $\mathrm{pw}(G)$. (Kinnersley 1992, p. 346.)

### 1.2 Vertex separation
**Instance.** A graph $G$ and an integer $k$.
**Question.** Is there a layout $L$ such that for every $1 \le i < n$,
$$|V_L(i)| \le k, \qquad V_L(i) = \{\, u : L(u) \le i,\ \exists v\ (uv \in E,\ L(v) > i) \,\}?$$
The least such $k$ is $\mathrm{vs}(G)$. (Kinnersley 1992, p. 346.)

### 1.3 Minimization of open stacks (MOSP)
**Instance.** A 0/1 matrix $M \in \{0,1\}^{R \times C}$, with rows the piece
types (customers) and columns the patterns, and an integer $k$.
**Question.** Is there a permutation $\pi$ of the columns such that at every
position $j$ at most $k$ rows are active?
The least such $k$ is $Z(M)$. (Linhares & Yanasse 2002, eqs. (1)-(2).)

### 1.4 Gate matrix layout
**Instance.** A net–gate matrix $M \in \{0,1\}^{N \times G}$, with rows the
nets and columns the gates, and an integer $k$.
**Question.** Is there a permutation $\pi$ of the gates and a track
assignment $h : N \to \{1, \dots, k\}$ such that any two nets active at a
common position receive different tracks?
The least such $k$ is $t(M)$. (Möhring 1990, p. 18; Wing, Huang & Wang 1985,
Problem 1.)

### 1.5 One-dimensional logic (gate assignment)
**Instance.** A set of gates $T$, a set of nets $V$, for each gate
$t$ the nets $V(t) \subseteq V$ it connects, and an integer $k$.
**Question.** Is there an ordering of the gates such that the intervals the
nets span have an interval graph of clique number at most $k$? The number
of tracks equals that clique number.
Its *connection graph* is $H = (V, \{xy : \exists t,\ x, y \in V(t)\})$. In the
*boundary* variant, two gates $t_l, t_r$ are pinned to the two ends. (Ohtsuki
et al. 1979, §II-III, §IV.)

### 1.6 PLA folding
**Instance.** A net–gate matrix $M$ and an integer $k$.
**Question.** Is there a gate permutation $\pi$ and a track assignment as in
§1.4 that puts **at most two nets on each track**, using at most $k$ tracks?
The least such $k$ is $\mathrm{pla}(M)$. With no bound on the nets per track
(*multiple folding*), the problem is §1.4 itself. (Möhring 1990, p. 25; path
partitions, p. 36.)

### 1.7 Interval thickness
**Instance.** A graph $G$ and an integer $k$.
**Question.** Is there an interval graph $H$ on the same vertex set with
$E(G) \subseteq E(H)$ and clique number $\omega(H) \le k$?
The least such $k$ is $\theta(G)$. (Kirousis & Papadimitriou 1985, p. 182;
Möhring 1990, p. 31.)

### 1.8 Node search
**Instance.** A graph $G$ and an integer $k$.
**Question.** Is there a sequence of moves that clears every edge and never
uses more than $k$ searchers at once? Each move places a searcher on a vertex
or removes one. All edges start contaminated. An edge is cleared when both
its endpoints are guarded at the same time. A clear edge is recontaminated
when a searcher-free path joins it to a contaminated edge.
The least such $k$ is $\mathrm{ns}(G)$, and $\mathrm{mns}(G)$ over strategies
that never recontaminate. (Kirousis & Papadimitriou 1985, p. 181; 1986, §2.)

### 1.9 Edge search
**Instance.** A graph $G$ and an integer $k$.
**Question.** Is there a sequence of moves that clears every edge with at
most $k$ searchers? Moves place, remove, or *slide* a searcher along an
edge. An edge is cleared by sliding a searcher along it from a guarded
endpoint. Recontamination is as in §1.8.
The least such $k$ is $\mathrm{es}(G)$, and $\mathrm{pes}(G)$ for progressive
strategies. (Kirousis & Papadimitriou 1986, p. 208; Ellis, Sudborough & Turner
1994, p. 53.)

### 1.10 Narrowness
**Instance.** A graph $G$ and an integer $k$.
**Question.** Is there an ordering $v_1, \dots, v_n$ such that the following
process never holds more than $k$ vertices in the *shack*? At step $i$, put
$v_i$ in the shack, then remove every $v_j$ ($j \le i$) that has no
neighbour $v_\ell$ with $\ell > i$.
The least such $k$ is $\nu(G)$. (Kornai & Tuza 1992, §2.)

### 1.11 Split bandwidth
**Instance.** A graph $G$ and an integer $k$.
**Question.** Is there a *split* $G^*$ of $G$ with bandwidth
$b(G^*) \le k$? A split is a graph obtained by repeated *node splitting*:
replace a vertex $v$ by an edge $uw$, and partition $v$'s neighbours between
$u$ and $w$.
The least such $k$ is $\mathrm{sb}(G)$. (Fomin 1998, §3.2.)

### 1.12 Edge separation (three readings)
Table 1 cites Lengauer (1981) for "edge separation". That paper supports three
problems:

- **Min-cut linear arrangement (cutwidth).** *Instance:* $G$, $k$.
  *Question:* is there a layout $L$ with
  $|\{uv \in E : L(u) \le i < L(v)\}| \le k$ for all $i$? Value
  $\mathrm{cw}(G)$. (Lengauer, p. 468.)
- **Modified min-cut linear arrangement.** The same, counting only edges that
  pass strictly over a vertex, $|\{uv \in E : L(u) < i < L(v)\}| \le k$. Value
  $\mathrm{mcw}(G)$. (Lengauer, Definition 6.)
- **Vertex separator game.** *Instance:* $G$ and a positive integer $K$.
  *Question:* is there an order in which to pebble every vertex so that after
  each move at most $K$ unpebbled vertices are adjacent to a pebbled one?
  Value $\mathrm{VSG}(G)$. (Lengauer, p. 467.)

---

## 2. The transformations

Ordered from strongest to weakest: exact equalities, then bands, then what is
stated but not proved, then what is false as Table 1 has it.

### 2.1 Exact equalities

**(E1) Vertex separation is path-width.** For every graph,
$$\mathrm{vs}(G) = \mathrm{pw}(G).$$
Kinnersley 1992, Thm 3.1. Lean: `vertexSeparation_eq_pathwidth`.

**(E2) MOSP is path-width plus one.** If $M$ has at least one 1,
$$Z(M) = \mathrm{pw}(G_M) + 1.$$
Yanasse 1997a, Prop. 5; Fellows & Langston 1989, Thm 7; Linhares & Yanasse
2002, Prop. 2. Lean: `mospValue_eq_pathwidth_add_one`.

**(E3) Gate matrix layout is MOSP, on the same matrix.** If $M$ has at least
one 1,
$$t(M) = Z(M) = \mathrm{pw}(G_M) + 1.$$
For a fixed gate order, the fewest tracks equals the largest column sum of the
augmented matrix (the left-edge algorithm). Möhring 1990, p. 31, Prop. 3.5.
Lean: `NetGateMatrix.tracks_eq_mospValue`, `tracks_eq_pathwidth_add_one`.

**(E4) Interval thickness.** If $V \ne \emptyset$,
$$\theta(G) = \mathrm{pw}(G) + 1.$$
Möhring 1990, Prop. 3.5. Table 1's own source, Kashiwabara & Fujisawa (1979),
is not held. Lean: `intervalThickness_eq_pathwidth_add_one`.

**(E5) One-dimensional logic.** If every net lies on some gate, the least
number of tracks is $\theta(H)$. If moreover some gate connects a net, it is
$$\theta(H) = \mathrm{pw}(H) + 1.$$
Ohtsuki et al. 1979, §II-III, Thm 3. Lean: `LogicArray.tracks_eq_intervalThickness`,
`LogicArray.tracks_eq_pathwidth_add_one`.

**(E6) Narrowness.** If $V \ne \emptyset$,
$$\nu(G) = \mathrm{pw}(G) + 1,$$
and for each ordering $\sigma$, $\nu(\sigma) = \mathrm{vs}(\sigma^{\mathrm{rev}}) + 1$.
Kornai & Tuza 1992, Prop. 3.1. Lean: `narrowness_eq_pathwidth_add_one`.

**(E7) Node search.** For every graph, $\mathrm{ns}(G) = \mathrm{mns}(G)$
(recontamination does not help). If $E \ne \emptyset$,
$$\mathrm{ns}(G) = \mathrm{vs}(G) + 1 = \mathrm{pw}(G) + 1 = \theta(G).$$
Kirousis & Papadimitriou 1985, Thm; 1986, Thm 2.3, Thm 4.1. Lean:
`nodeSearchMonotonicity`, `nodeSearch_eq_vertexSeparation_add_one`,
`nodeSearch_chain`. The Lean proof of monotonicity follows Bienstock &
Seymour (1991), not LaPaugh. The published proof of $\mathrm{vs} \le \mathrm{ns} - 1$
has a gap, repaired by ordering vertices by clearing time; see
`proof_reductions.md` §1.

**(E8) Multiple folding.** With no bound on nets per track, the least number of
tracks is $t(M) = \mathrm{pw}(G_M) + 1$. Möhring 1990, Thm 3.14. Lean:
`NetGateMatrix.foldTracks_eq_pathwidth_add_one`.

**(E9) Lengauer's vertex separator game.** For every graph,
$\mathrm{VSG}(G) = \max(1, \mathrm{vs}(G))$. If $E \ne \emptyset$, the triangle
graph $G_{du}$, which adds a triangle on every edge, satisfies
$$\mathrm{vs}(G_{du}) = \mathrm{vs}(G) + 1.$$
Lengauer 1981, Thm 4. Lean: `vsg_eq_max`, `vertexSeparation_triangleGraph`.

### 2.2 Bands

**(B1) Split bandwidth.** For every graph,
$$\mathrm{pw}(G) \le \mathrm{sb}(G) \le \mathrm{pw}(G) + 1.$$
Both ends occur: $K_2$ has $\mathrm{sb} = \mathrm{pw} = 1$, and $K_{1,3}$ has
$\mathrm{pw} = 1$ and $\mathrm{sb} = 2$. Fomin 1998, Thm 8, which assumes a
connected graph with at least two vertices; the Lean proof needs neither. Lean:
`pathwidth_le_splitBandwidth_le_pathwidth_add_one`.

**(B2) Edge search.** For every graph,
$$\mathrm{vs}(G) \le \mathrm{es}(G) \le \mathrm{vs}(G) + 2,$$
and the same for $\mathrm{pes}$. All three offsets occur: $K_2$ has
$\mathrm{es} = \mathrm{vs} = 1$, and $K_{3,3}$ has $\mathrm{vs} = 3$,
$\mathrm{es} = 5$. Ellis, Sudborough & Turner 1994, Thm 2.1; Kirousis &
Papadimitriou 1986, p. 209. Lean: `vertexSeparation_le_edgeSearch_le_add_two`,
`vertexSeparation_le_progressiveEdgeSearch_le_add_two`.

### 2.3 Stated, not proved

**(N1) Edge search monotonicity (LaPaugh 1993).** $\mathrm{es}(G) = \mathrm{pes}(G)$.
Stated in Lean as the proposition `EdgeSearchMonotonicity` and never assumed
by any result above. (B2) is proved for the full game without it.

**(N2) Boundary one-dimensional logic.** With the two boundary gates pinned
to the ends, the least number of tracks $\mathrm{tracks}_B$ satisfies
$\mathrm{pw}(H) + 1 \le \mathrm{tracks}_B$ (Lean:
`LogicArray.pathwidth_add_one_le_tracksPinned`). The brute-force check found
$\mathrm{tracks}_B \in \{\mathrm{pw}(H) + 1, \mathrm{pw}(H) + 2\}$ on all 1,027
instances it tried. An upper bound is not proved, and whether a gap of 2
occurs is open.

### 2.4 False as Table 1 states them

**(F1) PLA folding (at most two nets per track).** For every matrix,
$$\max\!\left(\mathrm{pw}(G_M) + 1,\ \lceil |N|/2 \rceil\right) \le \mathrm{pla}(M),$$
but the gap to $\mathrm{pw} + 1$ is unbounded. The $5 \times 5$ identity
matrix needs 3 tracks, while $\mathrm{pw}(G_M) + 1 = 1$. The gap is unbounded
even for a connected net graph: the path $P_n$ as a matrix, one gate per
edge, has $t = 2$ and $\mathrm{pla} \ge \lceil n/2 \rceil$. Möhring 1990,
Prop. 3.15. Lean: `plaTracks_idMatrix_five`, `plaTracks_idMatrix_unbounded`,
`plaTracks_pathMatrix_unbounded`. Table 1's claim holds for multiple folding
(E8).

**(F2) Edge separation read as cutwidth.** $\mathrm{pw}(G) \le \mathrm{cw}(G)$
always, but on stars
$$\mathrm{pw}(K_{1,n}) = 1, \qquad \mathrm{cw}(K_{1,n}) = \lceil n/2 \rceil,
\qquad \mathrm{mcw}(K_{1,n}) = \lceil n/2 \rceil - 1,$$
so neither cutwidth reading is within any constant of path-width.
$K_{1,7}$ already breaks $\pm 1$ for $\mathrm{cw}$, and $K_{1,9}$ for
$\mathrm{mcw}$. Lengauer 1981, p. 468 and Definition 6. Lean:
`cutwidth_unbounded`, `modCutwidth_unbounded`,
`pathwidth_add_two_lt_cutwidth_star7`, `pathwidth_add_two_lt_modCutwidth_star9`.
The row is also misattributed: what Lengauer proves exactly is the vertex game
(E9), which is Table 1's vertex separation row.

**(F3) Edge cases of true rows.** On a graph with no edges, $\mathrm{ns} = 0$
while $\mathrm{vs} + 1 = \theta = 1$ (for $V \ne \emptyset$). Both Kirousis &
Papadimitriou equalities need $E \ne \emptyset$. For a matrix with no 1s,
$Z = 0$ while $\mathrm{pw} + 1 = 1$. Lengauer's Theorem 4 fails for $K = 0$ on
an edgeless graph. Lean: `nodeSearch_ne_intervalThickness_of_edgeless`,
`monotoneNodeSearch_ne_vertexSeparation_add_one_of_edgeless`,
`isPositiveVSG_triangleGraph_counterexample`.
