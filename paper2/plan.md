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

**Done (2026-09-30, loop0005).** Every row is settled and proved in Lean.
The problems and the transformations, with formal and plain-English proofs,
are in `problem_transformations.md`. The evidence behind each row is in
`equivalences.md`, and faults in published proofs are in
`proof_reductions.md`. The Lean is in `../lean/MOSPFormalization/Complex/`.
In summary: seven problems are equal to pathwidth + 1 or to pathwidth, split
bandwidth and edge search are bands, and PLA folding and edge separation are
false as Table 1 states them. The one stated gap, LaPaugh's theorem, is
needed by no row.

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
§32). The two-key rule as the starting layout (§28; it improves the upper
bound and small instances, and leaves certification cost at 100-125
customers unchanged, §28 addendum), and the hardness ridge (§11, §25). The
graph version of the search, with a C engine to 1,024 vertices and a first
benchmark run (Rome 11,183 / 11,534 proved, 97.0%, at ≤ 600 s per graph), is
`../pathwidth_solver/`, transferred 2026-09-30 (`TRANSFER.md` there).

**To do.** State each dominance rule as a lemma about vertex-separation
layouts and prove it (in Lean where feasible — the bugs show why). Decide how
much of the soundness history belongs in this paper.

**The benchmark and the dataset** (decided 2026-09-29: benchmark everything,
and publish the result as a dataset). Because the problems are one complex, a
single certified pathwidth value answers every problem in the table at once,
through its offset. So the run covers three kinds of input:

- **MOSP instances** — the certified corpus as it stands.
- **Pathwidth benchmarks** — standard graph collections (e.g. the instances of
  Coudert, Mazauric & Nisse 2014, TreewidthLIB, PACE), each turned into a MOSP
  instance with one pattern per edge, and compared against published pathwidth
  solvers.
- **The other problems in the table** — every published benchmark collection
  we can find for any of the twelve problems (decided 2026-09-29: all of
  them, not a sample), each translated through its equivalence. Section 3's
  proofs are what make each translation sound, so a collection enters only
  once its equivalence is proved.

The shared artifact is **a large dataset of instances with certified optimal
pathwidth**. Each instance has its graph, the problem it came from, the
optimum, a witness layout, the value under every problem in the table, and a
proof of optimality (a DRAT refutation or a search certificate) that a third
party can check without our code.

**Scope, decided 2026-09-30: only the problems proved *exactly* equivalent.**
These are pathwidth, vertex separation, MOSP, gate matrix layout (including
multiple folding), one-dimensional logic, interval thickness, narrowness,
node search, and Lengauer's vertex separator game. Dropped: split bandwidth
and edge search, which are bands, not equalities; simple PLA folding and
cutwidth / edge separation, which are false as stated. A certified pathwidth
value is then an exact answer for every problem kept. The hunt's catalogue is
`benchmarks/README.md`; downloads go to `benchmarks/raw/` (git-ignored).

**Where to look.** Held already, all MOSP: the 2005 Constraint Modelling
Challenge (Harvey, Miller, Shaw, Simonis, Wilson), Faggioli & Bentivoglio,
SCOOP and Chu & Stuckey (`../benchmarks/instances/`). Leads as first
listed, from memory and the papers in hand, with the hunt's findings
(2026-09-30; details in `benchmarks/README.md`):

| Problem | Where instances may be | Status |
|---|---|---|
| gate matrix layout | the VLSI circuits used in the GMLP heuristic literature (e.g. Oliveira & Lorena 2002, Linhares's own work) | found: 11 circuits, best tracks published (`benchmarks/raw/lorena_vlsi/`) |
| PLA folding | MCNC / Espresso PLA benchmark circuits | in scope only as multiple folding; MCNC / LGSynth not downloaded yet |
| one-dimensional logic | same circuit sources as gate matrix layout | found: the same 11 circuits |
| vertex separation | VSPLIB (cited by Coudert, Mazauric & Nisse 2014), with grids, trees and Harwell-Boeing graphs from the VSP metaheuristic papers | found: VSPLIB and the Small set held |
| pathwidth | TreewidthLIB; PACE 2016-17 treewidth sets; Coudert et al.'s graphs | found: Rome, PACE 2016-17, freetdi, TreewidthLIB's colouring subset (the rest must be requested) |
| node / edge search | probably no benchmark sets; the graph-searching papers are theoretical | none exists; edge search is out of scope (a band) |
| narrowness, split bandwidth, edge separation, interval thickness | almost certainly none, since the names are barely used | none exists; split bandwidth and edge separation are out of scope |

A survey pass through the citers of each Table 1 paper, which
`data/openalex_citations.json` already lists, is the systematic way to find
the rest: any experimental paper among them had instances. Done 2026-09-30
(`benchmarks/hunt_citers.md`: about 145 experimental papers, 24 instance
sets).

**To do for the dataset.** Choose the collections from the catalogue and get
their licences; send the four requests of `benchmarks/README.md` §2.
Deduplicate. Fix a file format and a checker. Record provenance for every value, as
`solutions/` does. Price the run with the cost model of
`../reports/ml_nature.md` §19 before starting it.

## 5. Closing

**Argues.** What the complex is, what is proved and where, what remains open
(the missing Table 1 reference; any Table 1 claim that turned out false or
only an inequality; the pathwidth-treewidth gap on trees of cliques, where no
degree or clique bound can close it).

**To do.** Write last.

## Decisions

- **The definite move** (decided 2026-10-01): Chu & Stuckey's Theorem 1 is
  false as published (`paper2/search_soundness.md`, loop0006 item 08). The
  paper states the gap and the repaired rule, which is proved sound in Lean.
  The solver is not changed. Section 4's soundness theorem covers the repaired
  rule, and says exactly what holds for the code as it stands.
- **Venue: INFORMS Journal on Computing first** (decided 2026-09-29). The
  journal expects the code and data behind a paper to be deposited in its
  own repository; check the current rules before submission and build the
  dataset to satisfy them.
- **The paper gets its own GitHub repository, holding the Lean, the code and
  the data** (decided 2026-09-29; scope widened 2026-09-30), separate from
  this one. The paper cites it. **It is the last thing to do**, once the paper
  and the dataset are final, so that what is published is what the paper
  describes. The Lean part follows `lean_repo_plan.md`.
- **Section 4 benchmarks all three kinds of input** (decided 2026-09-29):
  MOSP instances, pathwidth benchmarks, and instances of the other problems
  in the table, released together as one dataset.

## Still open

- Length, and how the proofs of section 3 split between the paper, an
  appendix and the Lean repository.
- What to call the dataset, and where to host it beyond the journal's own
  repository.

## Remaining work, in order

1. **Section 1:** obtain the thesis PDF and record what it proved and what it
   only cited.
2. **Section 2:** choose the paper's three figures and write the method
   paragraph, including the relevance correction.
3. **Section 4:** state the dominance rules as lemmas about layouts. The graph
   solver and a first benchmark run exist, transferred from `~/dev/pathwidth`
   (`../pathwidth_solver/TRANSFER.md`), and the benchmark hunt is done
   (`benchmarks/README.md`). Deduplicate the collections, fix the dataset
   format and checker (and the two result-file fixes the transfer document
   lists), price the run, and run it.
4. **Section 5,** then the LaTeX draft of the whole paper.
5. **Last: the paper's repository**, with the Lean (`lean_repo_plan.md`),
   the code, and the dataset, built from the final versions of each.
