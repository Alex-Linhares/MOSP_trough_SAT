# The benchmark hunt: catalogue

For the dataset of section 4 of *The pathwidth complex* (`../plan.md`). The
scope is the problems proved *exactly* equivalent to pathwidth:
pathwidth, vertex separation, MOSP, gate matrix layout (including multiple
folding), one-dimensional logic, interval thickness, narrowness, node search,
and Lengauer's vertex separator game. A certified pathwidth value answers all
of them at once.

Three searches, 2026-09-30, each with its own detailed catalogue: URLs,
licences, sha256 values, and what could not be verified.

- `hunt_graphs.md` — graph collections (pathwidth, vertex separation, and
  treewidth sets used for pathwidth).
- `hunt_matrix.md` — matrix and circuit collections (MOSP, gate matrix
  layout, one-dimensional logic).
- `hunt_citers.md` — the experimental papers among the works citing Table 1's
  papers or using its problems' names (about 145), and the instance sets they
  used (24).

Downloads are in `raw/`, which is git-ignored: 13 collections, about 1.7 GB
unpacked. Nothing in `raw/` is part of the repository.

## 1. Held or downloaded, in scope

"Solvable?" is a first guess at whether the exact search can certify the
optimum. The customer search has certified MOSP optima up to about 125
customers, and pathwidth instances are MOSP instances with one pattern per
edge, so the vertex count is the customer count. It must be priced before a
run.

| Collection | Problem | Instances | Size | Optima published? | Where | Solvable? |
|---|---|---|---|---|---|---|
| 2005 Constraint Modelling Challenge | MOSP | 5,806 | to 134 × 49 | yes, certified here | `../../benchmarks/instances/` | done |
| Faggioli & Bentivoglio 1998 | MOSP | 300 | to 50 × 40 | yes, certified here | held | done |
| SCOOP (selected) | MOSP | 24 | to 134 × 49 | yes, certified here | held | done |
| Chu & Stuckey 2009 | MOSP | 200 | 30-125 | yes, certified here | held | done |
| Carvalho & Soma 2015 | MOSP | 150 | 150-200 square | "optimal" per instance in a spreadsheet, certifier unstated | `raw/carvalho_soma2015/` | beyond what we have certified; to price |
| Frinhani, Carvalho & Soma 2018, large | MOSP | 610 | 400-1000 square | heuristic only | `raw/frinhani2018_large/` | almost certainly not exactly |
| VLSI gate-matrix circuits (wli, wsn, v4000, v4050, v4090, v4470, x0, w1-w4) | gate matrix layout, one-dim. logic | 11 | 10-202 nets | best tracks published | `raw/lorena_vlsi/`, Wayback copies of Lorena's INPE page | likely, all small |
| VSPLIB 2012: grids, trees | vertex separation | 50 + 50 | to 2,916 vertices | yes, by construction | `raw/vsplib/` | known without solving; small ones as checks |
| VSPLIB 2012: Harwell-Boeing | vertex separation | 73 | 24-960 vertices | heuristic best-knowns only | `raw/vsplib/` | small ones only |
| Small (Martí et al. 2008) | vertex separation / pathwidth | 84 | 16-24 vertices | yes, Mallach 2018 Tables 4-5 | `raw/cmplib_small/` | yes |
| Rome graphs | pathwidth | 11,534 files, some duplicates | 10-110 vertices | no per-graph values ever published | `raw/rome/` | yes, the largest new contribution |
| PACE 2017 exact | treewidth, used for pathwidth | 200 | 48-3,706 vertices | treewidth, not pathwidth | `raw/pace2017_tw/` | small ones only |
| PACE 2017 bonus | treewidth | 100 | 92-420 vertices | treewidth for 91 | `raw/pace2017_tw_bonus/` | some |
| PACE 2016 | treewidth | 283 | up to 24 million vertices | treewidth for 208 | `raw/pace2016_tw/` | small ones only |
| PACE 2017 heuristic | treewidth | 200 | up to 15 million vertices | no | `raw/pace2017_tw/` | small ones only |
| freetdi named graphs | treewidth | 150 | 4-3,282 vertices | treewidth upper bounds | `raw/freetdi_named-graphs/` | small ones |
| freetdi control-flow graphs | treewidth | 1,817 | 1-1,452 vertices | treewidth decompositions | `raw/freetdi_CFGs/` | most are low-width; to price |
| TreewidthLIB, colouring subset | treewidth | 58, excluding 24 preprocessed copies | 5-864 vertices | lost with the site | `raw/treewidthlib/` | small ones |

## 2. Exist, but must be requested

- **TreewidthLIB in full**, including Mallach's barley, mainuk, mildew and
  water. The graph files are no longer served, and the Wayback Machine never
  archived them. Ask Hans Bodlaender, Utrecht.
- **Becceneri, Yanasse & Soma 2004**, 710 random MOSP instances, 10-150. Never
  published. The Carvalho group at UFOP, or INPE, may hold them.
- **SCOOP, the full 187.** The site is dead and was never archived; only the
  24 we hold are public. Ask the SCOOP partners.
- **De Giovanni, Massi & Pezzella 2012**, large random and real electronics
  instances, MOSP. Not public; ask the authors (Padova). Low priority.

## 3. Found, but need work before use

- **Planning-competition "openstacks" domain** (2006-2014), MOSP written as
  planning problems, in `github.com/aibasel/downward-benchmarks`. Needs a
  converter to matrices, and a check for overlap with the Challenge set.
- **NCI chemical graphs**, used by Ikeda & Nagamochi (2015) for exact
  pathwidth. Molecules in SDF format; the graphs must be extracted.
- **SDCC control-flow graphs**, Conrado et al. (2023), Zenodo
  doi:10.5281/zenodo.8312920. Not downloaded yet.
- **MCNC / LGSynth PLA matrices.** In scope only as multiple folding, which is
  gate matrix layout. Not downloaded yet.
- **PT-MOSP** (`github.com/Laps-F/PT-MOSP`) mirrors the MOSP sets, CC BY-NC
  4.0. It is the source of the Carvalho & Soma and large Frinhani copies,
  because ResearchGate returns 403. Its licence matters for redistribution.

## 4. Not obtainable

- The five circuits printed in Hu & Chen (1990): v1, vc1, vw1, vw2, wan. Only
  sizes and track counts are published, in Table II, p. 844, and the netlists
  would have to be taken from their source papers.
- The x1-x9 circuits, whose values appear only in a PT-MOSP spreadsheet with
  no source.
- Yanasse's random sets (1997b; Yanasse & Limeira 2004), and the random PLA
  matrices of the 1980s papers.

## 5. Out of scope

- Collections made for problems that are not exact equivalents: cutwidth
  (CMPLIB's grids and Harwell-Boeing sets), gate matrix *connection cost*,
  minimization of order spread (MORP), simple two-per-track PLA folding, and
  Devadas's (1986) area-optimised array circuits.
- No collection exists for interval thickness, node search or narrowness.
  The papers on them use pathwidth or vertex-separation instances.

## Next

1. Deduplicate: the Rome graphs up to isomorphism, the PACE and freetdi sets
   against each other, and VSPLIB against CMPLIB's Harwell-Boeing graphs (5 of
   36 shared names differ in size).
2. Price the run with the cost model (`../../reports/ml_nature.md` §19), by
   collection, and decide the size cut-off.
3. Write the four requests in §2.
4. Fix the dataset format and the checker, then run.
