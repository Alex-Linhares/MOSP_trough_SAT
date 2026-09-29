# The pathwidth complex — plan

A plan, not a draft. Each section lists what it argues, what already exists in
this repository to support it, and what is still to do.

## 1. The story

**Argues.** During the PhD (Linhares, *Industrial pattern sequencing problems:
some complexity results and new local search models*, 2001 in OpenAlex, with
Yanasse) the twelve problems were collected from operations research, VLSI
design and graph theory. They appeared as Table 1 of Linhares & Yanasse
(2002), *Computers & Operations Research* 29, 1759-1772, asserted equivalent
up to ±1 — with no proofs and no explanation of which graph or which ±1. This
paper supplies what that table left out.

**Exists.** The table itself (`../literature/`, Linhares & Yanasse 2002); the
twelve references it rests on, eleven held (`literature/MANIFEST.md`); the
thesis appears in OpenAlex as the most-connected work in the citation network
(it cites eleven of the twelve Table 1 papers; `popularity.md`).

**To do.** Obtain the thesis PDF and record what it proved and what it only
cited. Kashiwabara & Fujisawa (1979), the interval-thickness reference, is
still missing and was never digitised.

## 2. Why "the pathwidth complex"

**Argues.** Taken as a whole, the twelve problems are one object seen from
three disciplines, and the name the literature has converged on is
pathwidth. The evidence is bibliometric:

- pathwidth has 1,213 relevant works, more than three times the other eleven
  names combined, and is the only name still growing;
- three of the names (narrowness, split bandwidth, edge separation) have no
  relevant works at all, and two more have a handful;
- the VLSI names belong to the 1980s, the graph-searching names peaked in the
  1990s-2000s, and MOSP is the operations-research generation;
- the communities barely cite each other: only six works cite both a MOSP
  paper and a graph-theory paper.

**Exists.** `popularity.md` (method, the 2026-09-29 relevance correction,
caveats) and six figures in `figures/` — name usage (bars), name usage against
citations (scatter), citation network, rate heatmap, small multiples, citers
by decade. Regenerate: `python -m paper2.citation_graph`,
`python -m paper2.trends`.

**To do.** Decide which three figures go in the paper (suggested: the bar
chart, the heatmap, the citation network). State the relevance check in the
paper's method paragraph, since it changed two conclusions.

## 3. The equivalences, proved

**Argues.** Each of the twelve problems, stated precisely, with the graph it
lives on and the exact offset from pathwidth, and a proof. The central chain:
MOSP = gate matrix layout cost (Linhares & Yanasse 2002, Prop. 2) = pathwidth
+ 1 of the clique-per-pattern graph (Fellows & Langston 1989, Thm 7, with
their 1987 Lemma 4.1 = Yanasse 1997a, Prop. 5), and pathwidth = vertex
separation (Kinnersley 1992). The rest attach to it: interval thickness =
pathwidth + 1, node search number = vertex separation + 1 (Kirousis &
Papadimitriou 1985, 1986), edge search within +2 (Ellis, Sudborough & Turner
1994), narrowness (Kornai & Tuza 1992), split bandwidth (Fomin 1998),
one-dimensional logic and PLA folding (Ohtsuki et al. 1979; Möhring 1990),
edge separation (Lengauer 1981).

**Exists, in Lean** (`../lean/MOSPFormalization/`): `mospValue = pathwidth
(mospGraph) + 1`, both directions, `sorry`-free (`MOSPGraph.lean`);
vertex separation = pathwidth (`VSEquivPW.lean`); degeneracy ≤ pathwidth ≤
bandwidth, treewidth ≤ pathwidth, the branch lemma (`Sandwich.lean`). The
star counterexample showing the pattern graph is the wrong graph
(`MOSPGraphExamples.lean`).

**To do.** One table: problem, graph, offset, source, proof status (paper /
Lean). Then the missing links in Lean, in rough order of difficulty: interval
thickness (interval supergraphs), node search, gate matrix layout as a matrix
problem, one-dimensional logic, PLA folding, edge search (the +2 is an
inequality, not an equality), narrowness, split bandwidth, edge separation.
Decide which of Table 1's "±1" claims are equalities, which are inequalities,
and whether any is false as stated — the Lean development has already found
two false statements (`CLAUDE.md`), so each needs a small-instance check
before it is stated.

## 4. Chu & Stuckey as a pathwidth solver

**Argues.** Chu & Stuckey's (2009) complete search over customer closing
orders is, read mathematically, a search over vertex-separation layouts of
the MOSP graph, and its dominance rules are theorems about layouts. Stated
that way, it is an exact pathwidth solver, and it solves thousands of
instances: any graph becomes a MOSP instance with one pattern per edge, whose
optimum is pathwidth + 1.

**Exists.** The implementation (`../satisfiability/customer_search.py` and
its C core); the certified corpus of 6,376 instances and the generated
ensembles (37,800 at n ≤ 40, 6,747 at 50-75); the soundness story — two
`better_move` bugs found by the differential harness, the fix, DRAT proofs for
92% at n ≤ 40, and the search certificate (`../reports/ml_nature.md` §15, §17,
§32). The two-key rule as the starting layout (§28), and the hardness ridge
(§11, §25).

**To do.** State each dominance rule as a lemma about vertex-separation
layouts and prove it (in Lean where feasible — the bugs show why). Run the
solver on standard pathwidth benchmarks (e.g. the graphs of Coudert, Mazauric
& Nisse 2014, or PACE instances) through the one-pattern-per-edge encoding,
and compare with published pathwidth solvers. Decide how much of the
soundness history belongs in this paper.

## 5. Closing

**Argues.** What the complex is, what is proved and where, what remains open
(the missing Table 1 reference; any Table 1 claim that turned out false or
only an inequality; the pathwidth-treewidth gap on trees of cliques, where no
degree or clique bound can close it).

**To do.** Write last.

## Open decisions

- Venue and length.
- Whether the Lean development is a companion artifact or part of the paper.
- Whether section 4's benchmark run is on MOSP instances, pathwidth
  benchmarks, or both.
