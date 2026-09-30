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

### 1.13 Progressive black-white pebbling
**Instance.** A dag $D = (V, A)$ and a positive integer $K$.
**Question.** Can $D$ be pebbled progressively with at most $K$ pebbles on it
at any instant? The rules: every vertex starts pebble-free and ends
pebble-free; a white pebble may be placed on a pebble-free vertex at any time;
a white pebble on $v$ may be turned black once every immediate predecessor of
$v$ carries a pebble; a black pebble may be removed at any time; and each
vertex receives and loses a pebble exactly once.
The least such $K$ is $\mathrm{pbw}(D)$. (Lengauer 1981, pp. 466–467, after
Cook & Sethi; Kirousis & Papadimitriou 1986, p. 206.) The dag built from
a graph $G$ is $G_d$, with a vertex for each vertex and each edge of $G$ and arcs
$v \to \{v, w\}$, $w \to \{v, w\}$ (Lengauer, Def. 1b). Lengauer's $D_u$,
built from a dag, is item 04's.

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

**(E10) Progressive pebbling of $G_d$.** For every graph and every $K \ge 0$,
$$\mathrm{vs}(G) \le K \iff \mathrm{pbw}(G_d) \le K + 2,$$
so if $E \ne \emptyset$,
$$\mathrm{pbw}(G_d) = \mathrm{vs}(G) + 2 = \mathrm{pw}(G) + 2 = \mathrm{VSG}(G) + 2,$$
and $\mathrm{pbw}(G_d) = 1$ if $G$ is edgeless with $V \ne \emptyset$.
Lengauer 1981, Thm 3, which states the instance form for positive $K$. Lean:
`pebblesWithin_lengauerD_iff`, `isPositiveVSG_iff_isPositivePBWP_lengauerD`,
`pbw_lengauerD_eq_pathwidth`, `pbw_lengauerD_of_edgeless`
(`Complex/Pebbling.lean`).

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
$\mathrm{es} = \mathrm{vs} = 1$, $K_{1,3}$ has $\mathrm{vs} = 1$,
$\mathrm{es} = 2$, and $K_{3,3}$ has $\mathrm{vs} = 3$, $\mathrm{es} = 5$. Ellis, Sudborough & Turner 1994, Thm 2.1; Kirousis &
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

---

## 3. Proofs

Each result of section 2 is proved twice. The first proof is written for a
mathematician. The second, *in plain English*, says the same thing for
someone who knows what a graph is and nothing more. The formal proofs follow
the Lean development, which is the authority where the two differ in detail.
They are complete for the classical results, and the two long ones, (E7) and
(B2), are given as the argument's structure with the key steps proved.

Throughout, for a path decomposition $X_1, \dots, X_r$ and a vertex $v$, let
$\mathrm{first}(v)$ and $\mathrm{last}(v)$ be the least and greatest indices
of bags containing $v$. The interval property says
$v \in X_i \iff \mathrm{first}(v) \le i \le \mathrm{last}(v)$.

### Two lemmas used repeatedly

**Lemma H (Helly for intervals).** Pairwise intersecting intervals
$[a_1, b_1], \dots, [a_m, b_m]$ of a line have a common point.

*Proof.* Let $a = \max_i a_i$. For any $i, j$, the intervals $[a_i,b_i]$ and
$[a_j,b_j]$ meet, so $a_j \le b_i$. Hence $a \le b_i$ for every $i$, and
$a \in [a_i, b_i]$ for every $i$. $\square$

*In plain English.* If every two of a set of stretches of road overlap, then
some single spot lies on all of them. Take the latest starting point. Every
stretch starts no later than that spot, and none can end before it, or it
would miss the stretch that starts there.

**Lemma C (cliques sit in a bag).** In a path decomposition of $G$, every
clique of $G$ lies inside a single bag.

*Proof.* For $u \in K$, the bags containing $u$ form the integer interval
$[\mathrm{first}(u), \mathrm{last}(u)]$. For $u, v \in K$ the edge $uv$ lies
in some bag, so the two intervals meet. By Lemma H all the intervals share an
index $i$, and $K \subseteq X_i$. $\square$ (Lean:
`PathDecomposition.exists_bag_of_isClique`.)

*In plain English.* Each vertex lives in an unbroken run of bags. Two
neighbours must meet in some bag, so their runs overlap. For a group of
mutual neighbours all the runs overlap pairwise, so by Lemma H one bag holds
the whole group.

### (E1) $\mathrm{vs} = \mathrm{pw}$

*Proof.* ($\mathrm{pw} \le \mathrm{vs}$.) Let $L$ be a layout with
$\max_i |V_L(i)| = k$, and put $V_L(0) = \emptyset$. Define
$X_i = V_L(i-1) \cup \{L^{-1}(i)\}$ for $1 \le i \le n$, so $|X_i| \le k+1$.
Every $v$ lies in $X_{L(v)}$. For an edge $uv$ with $L(u) < L(v) = j$, the
vertex $u$ is in $V_L(j-1)$, so $u, v \in X_j$. Finally
$u \in X_i \iff L(u) \le i \le \max(\{L(u)\} \cup \{L(v) : uv \in E\})$,
an interval. So $(X_i)$ is a path decomposition of width $\le k$.

($\mathrm{vs} \le \mathrm{pw}$.) Let $(X_i)$ have width $k$. Order the
vertices by $\mathrm{first}$, breaking ties arbitrarily, to get $L$. Fix
$1 \le i < n$, let $w = L^{-1}(i+1)$ and $f = \mathrm{first}(w)$. Take
$u \in V_L(i)$, with a neighbour $v$, $L(v) \ge i+1$. Then
$\mathrm{first}(u) \le f \le \mathrm{first}(v)$. The edge $uv$ lies in a bag
$X_s$ with $s \ge \mathrm{first}(v) \ge f$. Since
$\mathrm{first}(u) \le f \le s$ and $u \in X_s$, the interval property gives
$u \in X_f$. So $V_L(i) \subseteq X_f \setminus \{w\}$, because $w \in X_f$
but $L(w) > i$. Hence $|V_L(i)| \le k$. $\square$ (Kinnersley 1992, Thm 3.1.)

*In plain English.* Vertex separation asks you to line the vertices up so
that, at every cut in the line, few vertices on the left still have
unfinished business on the right. Path-width asks for a row of overlapping
boxes covering the graph. From a good lineup, make one box per vertex: the
vertex itself plus everything to its left still waiting for a neighbour.
Conversely, from good boxes, line the vertices up in the order they first
appear. Everything on the left of a cut that still has a neighbour on the
right must sit in the box where the next vertex first appears, alongside that
vertex. So both measures come out the same.

### (E2) $Z(M) = \mathrm{pw}(G_M) + 1$

*Proof.* ($Z \le \mathrm{pw} + 1$.) Take a path decomposition of $G_M$ of
width $k$. The rows $R_c = \{r : M_{rc} = 1\}$ of each column $c$ form a
clique of $G_M$, so by Lemma C they lie in some bag $X_{b(c)}$. Order the
columns by $b(c)$ to get $\pi$. If row $r$ is active at the position of
column $c$, there are columns $x, y$ of $r$ with
$\pi(x) \le \pi(c) \le \pi(y)$, so $b(x) \le b(c) \le b(y)$. As
$r \in X_{b(x)} \cap X_{b(y)}$, the interval property gives $r \in X_{b(c)}$.
So at most $|X_{b(c)}| \le k+1$ rows are active there.

($\mathrm{pw} + 1 \le Z$.) Take $\pi$ with at most $Z$ active rows at every
position. Let $X_j$ be the set of rows active at position $j$, and add a
singleton bag $\{r\}$ for each row with no 1. Rows sharing a column $c$ are
both active at $\pi(c)$. A row with a 1 is active exactly on the positions
between its first and last column, which is an interval. So this is a path
decomposition of width $\max(Z, 1) - 1 = Z - 1$, using $Z \ge 1$ because $M$
has a 1. $\square$

*In plain English.* Draw one dot per customer, and join two dots whenever
some pattern serves both. A production order gives, at each moment, a box
holding the customers whose stacks are open. Those boxes cover the drawing,
and each customer's stack is open over one unbroken stretch of time. So the
boxes form a path decomposition, as wide as the most stacks ever open.
Conversely, from any good row of boxes, each pattern's customers are all
mutual neighbours, so some box holds them all. Cutting the patterns in box
order never opens more stacks than a box holds.

### (E3) $t(M) = Z(M)$

*Proof.* Fix the gate order $\pi$, and let $A_j$ be the set of nets active at
position $j$. (Lower bound.) Nets in $A_j$ are pairwise active at a common
position, so they need distinct tracks, and $t_\pi \ge \max_j |A_j|$. (Upper
bound, left-edge.) Net $r$ is active on an interval
$I_r = [\ell_r, \rho_r]$. Process the nets by increasing $\ell_r$, giving each
the least track not used by an earlier net whose interval contains $\ell_r$.
Those earlier nets are in $A_{\ell_r} \setminus \{r\}$, so at most
$\max_j |A_j| - 1$ tracks are blocked, and $\max_j |A_j|$ tracks suffice.
So $t_\pi = \max_j |A_j|$, which is the number of open stacks of $\pi$ on the
same matrix, with nets as customers and gates as patterns. Minimise over
$\pi$. $\square$

*In plain English.* Once the gates are in order, each wire runs over an
unbroken stretch. Wires that are running at the same point need separate
tracks. Sweeping from left to right and giving each new wire the lowest free
track never needs more tracks than the most wires running at one point. That
number is exactly the open-stacks count of the same table read as a cutting
problem, so the two problems are one problem with different words.

### (E4) $\theta(G) = \mathrm{pw}(G) + 1$

*Proof.* ($\le$.) From a decomposition of width $k$, give $v$ the interval
$[\mathrm{first}(v), \mathrm{last}(v)]$, and let $H$ be their intersection
graph. Every edge of $G$ lies in a bag, so $G \subseteq H$. A clique of $H$ is
a family of pairwise meeting intervals, which share an index $i$ (Lemma H),
so it lies in $X_i$. Hence $\omega(H) \le k+1$.
($\ge$.) Take an interval model $\{J_v\}$ of $H \supseteq G$ with
$\omega(H) = \theta$. Let $p_1 < \dots < p_r$ be the left endpoints, and
$X_s = \{v : p_s \in J_v\}$. Each $X_s$ is a clique of $H$, so
$|X_s| \le \theta$. Each $v$ lies in the bag at its own left endpoint. For an
edge $uv$, the point $\max(\text{left}(J_u), \text{left}(J_v))$ lies in both
intervals and is some $p_s$. The bags containing $v$ are those $p_s$ in
$J_v$, consecutive because $J_v$ is an interval. So
$\mathrm{pw} \le \theta - 1$. $\square$ (Möhring 1990, Prop. 3.5.)

*In plain English.* An interval graph is what you get by giving each vertex a
stretch of road and joining two vertices when their stretches overlap. A row
of boxes turns into stretches: a vertex's stretch runs from its first box to
its last. A group of mutual neighbours in the result then shares a box, so no
group is bigger than a box. Going back, stand at each place where a stretch
begins, and make a box of all the stretches passing through that place.

### (E5) One-dimensional logic: tracks $= \theta(H) = \mathrm{pw}(H) + 1$

*Proof.* A gate order gives each net the interval its gates span. Nets that
share a gate overlap, so the intersection graph $I_\pi$ of these intervals
contains $H$. By the argument of (E3), the tracks needed equal
$\omega(I_\pi) \ge \theta(H)$. Conversely, take an interval model $\{J_v\}$
of $H' \supseteq H$ with $\omega(H') = \theta(H)$. For each gate $t$, the
nets $V(t)$ form a clique of $H$, so their intervals share a point $p_t$
(Lemma H). Order the gates by $p_t$. Net $v$'s span runs between points of
$J_v$, so two nets that overlap in this order have intervals $J$ that meet.
So $I_\pi \subseteq H'$ and $\omega(I_\pi) \le \theta(H)$. Every net must lie
on some gate, or it has no span. The last equality is (E4). $\square$
(Ohtsuki et al. 1979, Thm 3.)

*In plain English.* The gates of a logic array must be put in a row, and each
wire then covers the stretch between its first and last gate. The fewest
tracks is the thickest pile-up of wires, so the question is which pile-ups
the connection pattern forces. Given the best possible set of stretches,
each gate's wires all overlap, so they share a spot. Put each gate at that
spot. No wire then reaches beyond its intended stretch, so the pile-ups are
no worse than planned.

### (E6) $\nu(G) = \mathrm{pw}(G) + 1$

*Proof.* Fix an ordering $\sigma = (v_1, \dots, v_n)$. After step $i - 1$ the
shack holds exactly those $v_j$, $j \le i-1$, with a neighbour $v_\ell$,
$\ell > i-1$, which is $V_\sigma(i-1)$. Step $i$ adds $v_i$. The shack is
largest just after an insertion, so
$\nu(\sigma) = 1 + \max_{0 \le i < n} |V_\sigma(i)| = \mathrm{vs}_\sigma + 1$,
for $n \ge 1$. Minimise over $\sigma$ and apply (E1). $\square$ (Kornai & Tuza
1992, Prop. 3.1. Lean states it with the suffix convention, as
$\nu(\sigma) = \mathrm{vs}(\sigma^{\mathrm{rev}}) + 1$.)

*In plain English.* The shack is a short-term memory. Each word goes in, and
a word leaves once nothing later depends on it. Just after a new word
arrives, the shack holds that word plus every earlier word still waiting for
a later one. That is exactly the count vertex separation measures, plus one.

### (E7) $\mathrm{ns} = \mathrm{mns} = \mathrm{vs} + 1$ when $E \ne \emptyset$

*Proof.* Three inequalities.

(i) $\mathrm{ns} \le \mathrm{mns}$: a monotone strategy is a strategy.

(ii) $\mathrm{mns} \le \mathrm{vs} + 1$: the *shack strategy*. For an
ordering $\sigma$, at step $i$ place a searcher on $v_i$, then remove the
searchers of all $v_j$ with no neighbour after $v_i$. The guarded set after
step $i$ is the shack of (E6), so the cost is $\nu(\sigma)$. An edge
$v_j v_\ell$ with $j < \ell$ is cleared at step $\ell$, because $v_j$ is
still guarded, having the later neighbour $v_\ell$. There is no
recontamination: after step $i$ every contaminated edge has an endpoint
outside $P_i = \{v_1, \dots, v_i\}$. A searcher-free path from a clear edge
to a contaminated one would leave $P_i$, and its last vertex in $P_i$ has a
later neighbour, so it is guarded, a contradiction. By (E6),
$\min_\sigma \nu(\sigma) = \mathrm{vs} + 1$.

(iii) $\mathrm{vs} + 1 \le \mathrm{ns}$, for arbitrary strategies (Bienstock &
Seymour's crusade method on vertex sets). Let $\partial A = N(A) \setminus A$.
Because $|\partial A| = |N[A]| - |A|$, with $N[A \cup B] = N[A] \cup N[B]$ and
$N[A \cap B] \subseteq N[A] \cap N[B]$, the function $|\partial \cdot|$ is
submodular:
$$|\partial(A \cup B)| + |\partial(A \cap B)| \le |\partial A| + |\partial B|.$$
A *chain of width* $\le K$ is a sequence $\emptyset = A_0, A_1, \dots, A_m = V$,
each step adding at most one vertex and removing any number, with every
$|\partial A_i| \le K$.

(a) From a strategy with $\le k$ searchers, the *clean sets* give a chain of
width $\le k - 1$. The clean set is the set of vertices touching no
contaminated edge. In a closed position its boundary is guarded, and a vertex
that becomes clean is guarded. Lean: `exists_chain_step`.

(b) Any chain of width $\le K$ can be made increasing. Take one of least
weight $\sum_i (|\partial A_i| \cdot (n+1) + |A_i|)$. If
$A_j \not\subseteq A_{j+1}$, replace $A_j$ by $A_j \cap A_{j+1}$ if that does
not enlarge its boundary. Otherwise replace $A_{j+1}$ by $A_j \cup A_{j+1}$,
whose boundary is then smaller, by submodularity. Either way the weight
falls, a contradiction. Lean: `exists_monotone_chain`.

(c) An increasing chain adding one vertex at a time is a layout whose prefixes
are the $A_i$. Their boundaries are the sets vertex separation counts, read
from the other end. So $\mathrm{vs} \le K$.

Then (a) to (c) give $\mathrm{vs} \le k - 1$, that is,
$\mathrm{vs} + 1 \le \mathrm{ns}$. Combining,
$\mathrm{ns} \le \mathrm{mns} \le \mathrm{vs} + 1 \le \mathrm{ns}$, so all are
equal, and $\theta = \mathrm{pw} + 1 = \mathrm{vs} + 1$ by (E1), (E4).
$E \ne \emptyset$ is needed because on an edgeless graph there is nothing to
clear and $\mathrm{ns} = 0$. $\square$

The Kirousis & Papadimitriou (1986) proof of (iii) for monotone strategies
orders vertices by first placement, which fails. `proof_reductions.md` §1
gives the counterexample and the repair.

*In plain English.* Picture a building full of gas, where rooms are vertices
and corridors are edges. A corridor is aired out when both its ends are
guarded at once, and gas creeps back along any unguarded route. Sweeping
room by room in a good order, and leaving each room only once all its
neighbours have been visited, needs one guard more than the vertex
separation. The hard part is showing no clever strategy does better, even
one that lets gas back in and re-sweeps. Track the set of rooms that are
fully clean. Its doorways to dirty rooms must be guarded, so it never has
more exits than there are guards, less one. The clean set may shrink and
grow erratically, but a counting trick shows the erratic history can always
be straightened into one that only grows, without widening any doorway. A
steadily growing clean set is just a lineup of the rooms, so its doorway
count is the vertex separation. Hence recontamination never helps.

### (E8) Multiple folding

*Proof.* With no bound on nets per track, a folding is exactly a gate
permutation with a track assignment as in §1.4, so the minimum is $t(M)$. It
equals $\mathrm{pw}(G_M) + 1$ by (E3) and (E2). $\square$

*In plain English.* If any number of wires may share a track, "folding" is
just gate matrix layout under another name.

### (E9) Lengauer's vertex separator game

*Proof.* After $i$ moves the pebbled set is the prefix $P_i$ of the pebbling
order, and the vertex cut is $\partial P_i = N(P_i) \setminus P_i$. So the
cost of an order is $\max_i |\partial P_i|$, which is the vertex separation of
the reversed layout. Minimising over orders gives $\mathrm{vs}(G)$. The game
requires $K \ge 1$, which accounts for the $\max(1, \cdot)$. For Theorem 4,
$G_{du}$ adds for each edge $e = uv$ a new vertex $e'$ adjacent to $u$ and
$v$. (Upper bound.) Place each $e'$ just before the first of its endpoints in
an optimal layout of $G$. Each cut gains at most one vertex. (Lower bound.)
An induction along the layout that $G_{du}$ induces on $V$ shows some cut
gains exactly one. Lean proves this directly, in place of Lengauer's
normal-form Lemma 5. $\square$

*In plain English.* Lengauer's game pebbles the vertices one by one and
charges, at each moment, for the unpebbled vertices touching pebbled ones.
That charge is vertex separation read from the other end. His Theorem 4 says
that putting a little triangle on every edge raises the answer by exactly
one.

### (E10) Progressive pebbling of $G_d$

Write $\partial S = N(S) \setminus S$, so that the vertex separation of a
layout is $\max_i |\partial P_i|$ over its prefixes $P_i$ (the convention of
(E9)). In a progressive play a vertex passes once through the phases
pebble-free, white, black, cleared.

*Proof.* ($\Leftarrow$) Take a layout with $|\partial P_i| \le K$ for all $i$
and clear its vertices in order. To clear $v_i$: place and turn a pebble on
every pebble-free vertex of $N[v_i]$ (vertices of $G$ have no predecessors in
$G_d$, so they turn at once); then, for each edge $e$ at $v_i$ not yet
cleared, place a white pebble on $e$, turn it (both ends are black) and
remove it; then remove $v_i$. Before step $i$ the black vertices are exactly
$\partial P_{i-1}$, and $\partial P_{i-1} \cup N[v_i] \setminus P_{i-1} =
\partial P_i \cup \{v_i\}$. So during the step at most
$|\partial P_i| + 1 + 1 \le K + 2$ pebbles are on the dag, the last one for
the edge vertex in play. If $G$ is edgeless there are no edge vertices and
$\partial P_i = \emptyset$, so one pebble suffices.

($\Rightarrow$) Take a play with at most $K + 2$ pebbles and lay out $V$ in
the order its vertices lose their pebble. Fix a cut, let $S$ be the vertices
cleared by then and $B = \partial S$; suppose $B \ne \emptyset$. For every
edge $ab$ with $a \in S$, $b \notin S$, the edge vertex $ab$ is turned while
$a$ and $b$ carry pebbles, hence before $a$ is cleared, hence before the cut.
Let $e = ab$ be the one of these edges turned last, at time $\tau$. At $\tau$,
the vertex $e$ is white, $a$ is pebbled, and every $w \in B$ is pebbled: $w$
has an edge $uw$ with $u \in S$, turned at a time $\le \tau$ with $w$
pebbled, and $w$ is not cleared until after the cut. These $|B| + 2$
vertices of $G_d$ are distinct, so $|B| + 2 \le K + 2$.

For the number form, an edge $ab$ forces three pebbles (when $ab$ turns,
$a$ and $b$ are pebbled too), so every feasible budget has the form $K + 2$.
On an edgeless graph with a vertex, one pebble is needed and suffices, while
$\mathrm{vs} + 2 = 2$. Lengauer's instance form, for $K \ge 1$, follows with
$\mathrm{VSG} = \max(1, \mathrm{vs})$ (E9). $\square$

Lengauer proves Theorem 3 by applying his Theorem 2 to $G_d$ and then his
Theorem 4. The proof above works on $G_d$ directly and needs neither.

*In plain English.* Turn each edge of a graph into a small task that needs
its two endpoints "on the table" at once. Working through the vertices in a
good order, you keep on the table only the vertices still waiting for a
neighbour, plus the one you are finishing and one edge task, which is the
vertex separation plus two. Conversely, look at any schedule at the moment the
last edge crossing a cut is done. Its task, one endpoint, and every vertex
waiting on the far side of the cut are all on the table together. So no
schedule beats vertex separation plus two. A graph with no edges is the
exception: one slot is enough.

### (B1) $\mathrm{pw} \le \mathrm{sb} \le \mathrm{pw} + 1$

*Proof.* (Lower.) Splitting $v$ into an edge $uw$ can be undone by
contracting $uw$. Replacing $u$ and $w$ by $v$ in every bag of a
decomposition of the split gives a decomposition of $G$ of no greater width.
The bags containing $u$ and those containing $w$ form two intervals that
meet, because the edge $uw$ lies in a bag, so $v$'s bags form an interval. So
$\mathrm{pw}(G) \le \mathrm{pw}(G^*)$. Also $\mathrm{pw} \le b$: for a layout of
bandwidth $b$, the windows $\{v_i, \dots, v_{i+b}\}$ form a decomposition of
width $b$. Hence $\mathrm{pw}(G) \le b(G^*)$ for every split $G^*$.
(Upper.) Take an ordering $\sigma$ with $\nu(\sigma) = \mathrm{pw} + 1$ (E6).
Split each vertex $v$ into a path of copies, one for each step at which $v$
is in the shack, and attach the original edge $uv$ at step
$\max(\sigma(u), \sigma(v))$. Each splitting is a node splitting. Lay out the
copies by (step, position in $\sigma$). Consecutive copies of one vertex, and
the two ends of an attached edge, are then at most $\nu(\sigma)$ apart. So
$\mathrm{sb} \le \nu(\sigma) = \mathrm{pw} + 1$. This construction is the Lean
proof. It differs from Fomin's, which goes through interval bandwidth.
$\square$

*In plain English.* Splitting a vertex means stretching it into two joined
halves, dividing its connections between them. Stretching can't make a graph
easier in the path-width sense, and a narrow band layout is a special case of
a path decomposition. That gives the lower bound. For the upper bound, stretch
each vertex into a chain of copies, one for each moment it sits in the
narrowness shack. The copies then line up so that nothing connected is ever
more than a shack-width apart.

### (B2) $\mathrm{vs} \le \mathrm{es} \le \mathrm{vs} + 2$

*Proof.* (Upper.) Follow the shack ordering. Each step places a searcher on
$v_i$ and clears its edges to earlier guarded neighbours by sliding one extra
searcher along each, then removes the vertices whose edges are all clear.
This is Ellis, Sudborough & Turner's procedure `search1`. It costs
$\nu(\sigma) + 1 = \mathrm{vs} + 2$ and never recontaminates, for the reason
given in (E7)(ii). (Lower.) Run the chain argument of (E7)(iii) on the clean
sets of an edge-search strategy. At most one vertex becomes clean unguarded
in a single step, because a slide clears one edge. So the chain has width
$\le k$, not $k - 1$, and $\mathrm{vs} \le \mathrm{es}$. The progressive case
is the same argument restricted to strategies without recontamination.
$\square$

*In plain English.* Edge searching lets a guard walk along a corridor, which
clears it on the way. You can do the node-search sweep with one extra guard
for the walking, so edge search costs at most two more than vertex
separation. The clean-set argument still works, except that one freshly
cleaned room may have been left unguarded, so the edge search number is at
least the vertex separation.

### (F1) PLA folding

*Proof.* A PLA layout is a track assignment, so $\mathrm{pla} \ge t$, and
each track holds at most two nets, so
$\mathrm{pla} \ge \lceil |N|/2 \rceil$. For the identity matrix $I_n$, every
net is on its own gate, so $G_M$ is edgeless and $\mathrm{pw} + 1 = 1$. The
nets pair up two per track, so $\mathrm{pla}(I_n) = \lceil n/2 \rceil$, and
$\mathrm{pla}(I_5) = 3$. For the path matrix of $P_n$, with one gate per edge,
$G_M = P_n$, so $t = \mathrm{pw}(P_n) + 1 = 2$ while
$\mathrm{pla} \ge \lceil n/2 \rceil$. $\square$

*In plain English.* Simple folding allows only two wires per track. Five
wires that never interact need just one track in ordinary layout, but three
when each track holds two. The gap grows with the number of wires, so no
fixed "±1" can hold.

### (F2) Cutwidth is not within a constant of path-width

*Proof.* ($\mathrm{pw} \le \mathrm{cw}$.) Each $u \in V_L(i)$ has an edge
from position $\le i$ to position $> i$. Distinct $u$ give distinct edges, so
$|V_L(i)| \le$ the cut at $i$. Then apply (E1). (Stars.)
$\mathrm{pw}(K_{1,n}) = 1$, using bags $\{c, \ell_i\}$. In any layout, let the
centre $c$ have $a$ leaves on its left and $b$ on its right, with
$a + b = n$. The gap just left of $c$ is crossed by $a$ edges, and the gap
just right by $b$, so $\mathrm{cw} \ge \lceil n/2 \rceil$. Placing the centre in
the middle attains it. For modified cutwidth, on the side with
$\ge \lceil n/2 \rceil$ leaves, the leaf nearest $c$ is passed over strictly
by the edges to all the others on that side, so
$\mathrm{mcw} \ge \lceil n/2 \rceil - 1$. $\square$

*In plain English.* Cutwidth counts the wires crossing each gap, not the
vertices waiting behind it. A star is as simple as a graph gets for
path-width, since one hub is linked to many leaves. But wherever the hub goes
in a line, half the leaves are on one side and all their wires cross the gap
next to the hub. So the count grows with the number of leaves while
path-width stays at 1.

### (F3) Edge cases

*Proof.* On an edgeless graph with $V \ne \emptyset$, the empty strategy
clears every edge, so $\mathrm{ns} = 0$, while $\mathrm{vs} = 0$ and
$\theta = 1$, so $\mathrm{vs} + 1 = \theta = 1 \ne 0$. For a matrix with no 1s,
no row is ever active, so $Z = 0$, while $\mathrm{pw}(G_M) + 1 = 1$. Lengauer's
Theorem 4 at $K = 0$ on an edgeless graph: the left side is false, since
$K$ must be positive, while the right side, at $K + 1 = 1$, is true.
$\square$

*In plain English.* With nothing to search, no searchers are needed, but the
formulas still say one. The published theorems simply forgot to exclude the
empty case.
