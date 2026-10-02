# Plan: ARC Phase 3, from discovered structure to optimal layouts

Status: plan only. Date: 2026-10-02.

## Goal

After the JavaScript control app has run `discoverStructure` on an ARC task,
it passes the result to an exact pathwidth solver in the same page or Worker.
It then uses the optimal layout to propose an order over the task's entities:
an order in which to read, align, transform or explore them. The solver is the
one in this repository (`pathwidth_solver/`), Chu & Stuckey's
customer search ported to graphs, with the dominance rules repaired to match
the Lean soundness theorem (`paper2/solver_fix.md`). It is ported to
TypeScript inside the Form_Discovery module, so the app stays one
dependency-free module. The app and module live in Form_Discovery
(github.com/Alex-Linhares/Form_Discovery, working copy
`~/dev/Kemp_Tanembaum_matlab_code`); this plan lives here because the solver,
its oracle and its proofs do.

```ts
import { discoverStructure, layoutStructure } from "structure-discovery";

const s = discoverStructure({ entities, relations, features, forms });
const L = layoutStructure(s, { budgetMs: 200 });   // lays out ericHarry(s.best)
// L.width   -> 3                          vertex separation = pathwidth
// L.proof   -> "refutation" | "bound" | "" (empty means budget ran out, upper bound only)
// L.order   -> ["c", "a", "f", ...]       a closing order realising the width
// L.bags    -> [["c","a"], ["a","f","b"], ...]   the path decomposition
// L.frontier-> [1, 2, 3, 2, ...]          boundary size after each step
```

## What this is, and what it is not

Pathwidth does not solve ARC. It is a structural measurement with a
constructive witness: the width says how much has to be held open at once when
the entities are swept in a line, and the order is a sweep that achieves it.
The hypothesis this phase tests is that the sweep is useful to an ARC solver in
three places:

- **Canonical order within a grid.** Many tasks act on objects in a sequence,
  such as sorting, connecting, counting or recolouring by rank. An optimal
  layout of the entity relation graph is an order that respects the structure
  rather than reading order. Ties are broken deterministically, so the same
  structure gives the same order across the train pairs.
- **Correspondence across pairs.** If the transformed graphs of the input and output of a
  pair have the same width and similar frontier profiles, aligning their orders
  is a cheap candidate matching for the rule inducer to test.
- **Exploration in ARC-AGI-3.** On a graph of game states, the node search
  number is pathwidth + 1 (proved in `lean/MOSPFormalization/Complex/NodeMonotonicity.lean`).
  That number is the smallest frontier a systematic sweep of the state space
  needs, so the layout is an exploration schedule with a known memory cost.

It is not a rule inducer and not a grid parser. As in Form_Discovery's `PLAN_ARC_AGI_JS.md`, the
caller segments the grid. This phase adds one function and one view to the app.

## Which graph to lay out

The input to the pathwidth solver is the **Eric-Harry transformation from the
found form**: the graph obtained by applying the Eric-Harry transformation to
the form `discoverStructure` selects. The solver lays out that graph and nothing else.

- `layoutStructure(s)` computes the Eric-Harry transformation of `s.best`,
  then solves its pathwidth. The transformation is its own function,
  `ericHarry(form)`, with its own tests, so it can be inspected and checked
  apart from the solver.
- **Its definition is to be supplied by the owner and is not yet in this plan.**
  Until it is, everything that depends on it is blocked: the size of the
  transformed graph, and so the mask width (`Uint32` or multiword), the budget,
  and whether WebAssembly is needed. No stand-in graph is laid out in its place.
- The closed-form widths of the bare forms (a chain 1, a ring 2, an r × c grid
  min(r, c)) remain as checks on the solver. They are not the input.
- For ARC-AGI-3, the same transformation is applied to the form found over the
  game's states.

## The solver in TypeScript

- A port of `pathwidth/search.py` (`decide`), `bounds.py` (greedy order,
  degeneracy, contraction degeneracy) and `solve.py` (the descent from an upper
  bound, component splitting, and re-measuring the witness): about 800 lines.
  It goes in `pathwidth.ts` beside the module's `forms`, `search`, `score` and
  `index`, and keeps the module under its 2,000-line budget only if the
  structure-discovery core stays near 1,200 lines, which is worth checking first.
- Neighbourhoods as bitmasks. `Uint32` covers a transformed graph of at most 32 vertices.
  A multiword mask (`Uint32Array`) covers larger transformed graphs, matching the multiword
  C engine `closing_search_w.c`.
- **The repaired rules only.** The definite move fires only when the candidate
  passes the matching test (`HasDefiniteMatching`), and the better move only
  under `IsRepairedBetter`. The published rules are not ported, since they can
  discard the last solution at a node (`CLAUDE.md`, Chu & Stuckey Theorem 1).
- A time budget checked inside the search, not only between calls. A result
  that runs out of budget keeps its order and width as an upper bound, with an
  empty `proof`. That is this repository's provenance rule, and the app displays it.
- Pure, seeded, no global state, and runs in a Web Worker so the page stays
  responsive. An optional `onStep` callback reports each refuted width, for the
  view below.
- **WebAssembly is the fallback, not the plan.** If the TypeScript port is too
  slow on the largest transformed graphs, compile `closing_search_w.c` with Emscripten and call it
  from the same interface. Decide on measured state-graph timings, not before.

## Parity with the Python solver

Form_Discovery's fixture policy applies, with this repository's solver as the oracle:

- A generator script in Form_Discovery's `tools/` runs the Python solver
  (`pathwidth.solve_masks`) on a fixed set of graphs. It writes width, proof,
  order and **node count** to `tests/fixtures/pathwidth/*.json`, hashed in
  `SHA256SUMS`. The set covers the DEFINITE_CEX graph and the two Bug B graphs
  from `paper2/search_check.py`, every graph on at most 7 vertices, random
  graphs at 8–30 vertices, the VSPLIB trees and grids, and a Rome sample.
- The TypeScript solver must match **node for node**, not only in width. That is
  the standard this repository holds its C and Python to, and the only one that catches a
  rule implemented differently. Equal widths can hide an unsound rule that
  happened not to fire.
- Known values pinned separately: square grids have width equal to their side,
  and Ellis–Sudborough–Turner trees have the width their name encodes.
- Every returned order is re-measured by an independent `vertexSeparation(order)`
  before it is returned, so a wrong width cannot leave the function.

## The view in the control app

- After the structure panel, a layout panel draws the chosen graph with
  vertices placed left to right in the returned order. Under it, a frontier
  strip shows the boundary size after each step, with its maximum (the width)
  marked.
- A proof badge reads **proved**, **proved by bound**, or **upper bound**
  (budget). Upper bounds are never shown as "pathwidth".
- On a task, the panels for every train input and output sit side by side with
  their widths and frontier profiles, so the correspondence hypothesis can be
  judged by eye before it is measured.
- `onStep` animates the descent (width k found, k − 1 refuted) for a slow,
  readable demonstration mode.

## Measurement

Each use has its own question and its own kill criterion. Run on the
ARC-AGI-1 evaluation set, plus the 50 ARC-AGI-3 frames labelled in Phase 2 of
Form_Discovery's `PLAN_ARC_AGI_JS.md`.

- **Order.** Hand-label about 60 tasks whose output depends on an object order
  (sorting, chaining, ranking). Compare the layout order with four baselines:
  reading order, BFS from the top-left object, Fiedler order, and the two-key
  greedy rule (`rule+cs-dfs`'s seed, `reports/ml_nature.md` §7). Score is Kendall τ against the order the output
  implies. **Kill** if the layout does not beat the best baseline by a clear
  margin on held-out tasks, and then keep only the width as a feature.
- **Correspondence.** On train pairs with a known object matching, measure how
  often aligned layout orders give the matching, against matching by colour and
  position. **Kill** under the same rule.
- **Exploration.** On the transformed graphs of ARC-AGI-3 forms, compare the frontier of the layout
  sweep with BFS and DFS frontiers at equal coverage. The width is a proved
  minimum, so this measures how far the usual sweeps are from optimal, not
  whether the layout wins.
- **Cost.** Wall time per call in the browser, in nodes and milliseconds, by
  graph size. The target is under 50 ms for a transformed graph of at most 32 vertices, and a
  stated budget for the larger transformed graphs. Report the share of calls that end on budget.
- **Width as a feature.** Report whether width separates the forms
  `discoverStructure` confuses, chain against tree in particular. This is the
  cheapest possible payoff, and it is measured even if every kill above fires.

## Dependencies and order of work

- Form_Discovery's `PLAN_ARC_AGI_JS.md` Phases 1–2 (core and calibration) come first. This plan
  needs a working `discoverStructure` and the labelled set.
- Its Phase 3 says "npm package", which conflicts with the 2026-10-02 edit
  ("never published anywhere"). This plan assumes the edit wins: the module is
  built and used locally, and the demo page loads it from a relative path.
- The port, then the parity fixtures, then the view, then the measurements. Each
  step is one Ralph loop item in Form_Discovery with its gate (`make test`) green.
- Both repositories are private and stay separate. The fixtures are the only
  thing carried across from here, regenerated by the tool when `pathwidth_solver/`
  changes, with the reason recorded in Form_Discovery's `ANOMALIES.md` as for any oracle change.

## Done when

- `layoutStructure` runs from the control app in a Worker. It matches the
  Python solver node for node on the committed fixtures and labels every result
  with its proof kind.
- The layout panel and frontier strip show any ARC task's train pairs.
- Each of the three hypotheses has a reported result, kept or killed by its
  criterion, with the size range it covers stated.
