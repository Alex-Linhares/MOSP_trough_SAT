# Plan: ARC Phase 3, from the found form to the program's step order

Status: plan only. Date: 2026-10-02.

## Goal

After the JavaScript control app has run `discoverStructure` on an ARC task,
it applies the **Eric-Harry transformation to the found form**. The result is a
program: the sequence of steps to be taken. The app passes that program to an
exact pathwidth solver in the same page or Worker. The solver returns an order
of the steps, the step sequence to execute, that keeps the fewest intermediate
values alive at once, with a proof that no valid order does better.

The solver is the one in this repository (`pathwidth_solver/`): Chu &
Stuckey's customer search ported to graphs, with the dominance rules repaired
to match the Lean soundness theorem (`paper1/solver_fix.md`). It is ported to
TypeScript inside the Form_Discovery module, so the app stays one
dependency-free module. The app and module live in Form_Discovery
(github.com/Alex-Linhares/Form_Discovery, working copy
`~/dev/Kemp_Tanembaum_matlab_code`). This plan lives here because the solver,
its oracle and its proofs do.

```ts
import { discoverStructure, ericHarry, scheduleProgram } from "structure-discovery";

const s = discoverStructure({ entities, relations, features, forms });
const P = ericHarry(s.best);          // the program: a DAG of values and operations
const L = scheduleProgram(P, { budgetMs: 200 });
// L.order    -> ["in0", "in1", "op3", "op1", ...]   the step sequence, a topological order of P
// L.width    -> 3       registers needed: the vertex separation of L.order
// L.proof    -> "refutation" | "bound" | ""   (empty: budget ran out, an upper bound only)
// L.live     -> [1, 2, 3, 2, ...]   values alive after each step
// L.lower    -> 2       pathwidth of P's underlying undirected graph, a proved floor
```

## Why pathwidth, and why the program

The connection is the compiler problem of reordering straight-line code, that
is, code with no branches or loops, so that every value it computes fits in a
machine register and none is spilled to memory:

- The code is a **directed acyclic graph**. Its nodes are the input values and
  the values the operations compute. An edge x → y means value x is an input to
  operation y.
- A **topological order** of the DAG is a valid reordering of the code.
- The **number of registers** that order needs is its vertex separation number:
  after each step, the values already computed that some later step still reads.
- The minimum over all topological orders is the register sufficiency problem.
  It is NP-complete (Sethi 1975) and linear-time for a fixed number of registers
  (Bodlaender, Gustedt & Telle 1998, the reference behind the Wikipedia account
  of this application). **Both are to be obtained for `literature/`; neither is
  held yet.**

The plan's reading is that the Eric-Harry transformation of the found form is
exactly such straight-line code. The steps of the ARC program are the
operations, the grid's objects and parameters are the inputs, and an order of
the steps is the program as it will run. The solver chooses, among the orders
that respect the data flow, the one with the smallest working memory, and
proves it minimal.

Three things follow, and the plan is built on them:

- **The search needs a precedence constraint.** Unconstrained vertex separation
  ranges over every ordering. Here only topological orders are programs. In the
  customer search's terms, a step can be closed only once all its inputs are
  closed. Each node's candidates shrink to the steps whose predecessors are all
  in the closed set.
- **Unconstrained pathwidth is a free lower bound.** Topological orders are a
  subset of all orders, so the pathwidth of the DAG's underlying undirected
  graph, which the existing solver computes and proves, is a floor on the
  registers. When the unconstrained optimum happens to be topological, the
  schedule is proved optimal with no further search.
- **Reordering straight-line code does not change what it computes.** Every
  returned order can be executed and its output grid compared with the original
  order's. That is a correctness check independent of the solver.

Pathwidth does not solve ARC. It does not find the program; the found form and
the Eric-Harry transformation do. What it adds is the best order in which to
run that program, and the cost of running it.

## The program the solver receives

- `ericHarry(form)` returns a DAG: nodes with a kind (input or operation),
  directed edges from each value to the operations that read it, and the
  operation each node performs, so the program can be executed. It is its own
  function, with its own tests, so it can be inspected apart from the solver.
- **The transformation's definition is to be supplied by the owner and is not
  yet in this plan.** Until it is, the following are blocked: the size of the
  programs, and so the mask width (`Uint32` or multiword), the budget, and
  whether WebAssembly is needed. No stand-in program is scheduled in its place.
- If the transformation turns out to give an undirected graph, so that every
  order is a valid program, the precedence constraint is switched off and the
  problem is plain pathwidth. The solver supports both modes.
- For ARC-AGI-3, the same transformation is applied to the form found over the
  game's states.

## The solver in TypeScript

- A port of `pathwidth/search.py` (`decide`), `bounds.py` (greedy order,
  degeneracy, contraction degeneracy) and `solve.py` (the descent from an upper
  bound, component splitting, and re-measuring the witness): about 800 lines.
  It goes in `pathwidth.ts` beside the module's `forms`, `search`, `score` and
  `index`. That keeps the module under its 2,000-line budget only if the
  structure-discovery core stays near 1,200 lines, which is worth checking first.
- **Precedence mode**, added to the port and to the Python reference together:
  - a predecessor mask per vertex;
  - a step is a candidate only when its predecessor mask lies inside the closed
    set;
  - the greedy upper bound is a topological greedy;
  - the cost of an order is its vertex separation, the live values.

  Fix the register convention in the tests before anything else: whether the
  register for the value being computed counts on top of the live values.
- **Which rules may run in precedence mode.** The repaired rules are proved
  sound for unconstrained orders (`lean/MOSPFormalization/Search/`). Their proofs
  move a step earlier or swap two steps, and under precedence a moved step might
  run before one of its inputs. Precedence mode therefore starts with:
  - the memo and the old move only, which compare prefixes with the same closed
    set and so need no reordering argument;
  - the definite and better moves off.

  Each of those two is switched on only after both of these:
  - a brute-force check on every DAG at the sizes the census in
    `learning/pwtw_exhaust.py` reaches, with the full search and the rule
    agreeing on every instance;
  - its proof restated with the precedence hypothesis in `Search/`.

  This is the lesson of `CLAUDE.md`'s Chu & Stuckey entry: a rule that is not
  proved for the setting it runs in can discard the last solution at a node.
- The repaired rules in unconstrained mode, as in the existing solver. The
  published rules are not ported.
- A time budget checked inside the search, not only between calls. A result
  that runs out of budget keeps its order and width as an upper bound, with an
  empty `proof`. That is this repository's provenance rule, and the app
  displays it.
- Pure, seeded, no global state, and runs in a Web Worker so the page stays
  responsive. An optional `onStep` callback reports each refuted width, for the
  view below.
- **WebAssembly is the fallback, not the plan.** If the TypeScript port is too
  slow on the largest programs, compile `closing_search_w.c` (with precedence
  mode added) with Emscripten and call it from the same interface. Decide on
  measured timings, not before.

## Parity and correctness

Form_Discovery's fixture policy applies, with this repository's solver as the
oracle:

- A generator script in Form_Discovery's `tools/` runs the Python solver on a
  fixed set of inputs. It writes width, proof, order and **node count** to
  `tests/fixtures/pathwidth/*.json`, hashed in `SHA256SUMS`. The set has two
  parts.
  - *Unconstrained*: the DEFINITE_CEX graph and the two Bug B graphs from
    `paper1/search_check.py`, every graph on at most 7 vertices, random graphs
    at 8–30 vertices, the VSPLIB trees and grids, and a Rome sample.
  - *Precedence*: every DAG on at most 7 vertices, random DAGs at 8–30, and
    expression trees.
- The TypeScript solver must match **node for node**, not only in width. That is
  the standard this repository holds its C and Python to, and the only one that
  catches a rule implemented differently. Equal widths can hide an unsound rule
  that happened not to fire.
- Known values pinned separately:
  - square grids have width equal to their side;
  - Ellis–Sudborough–Turner trees have the width their name encodes;
  - on expression trees, the register count equals the Sethi–Ullman number, which
    is optimal on trees and computed by an independent labelling (Sethi & Ullman
    1970, to be obtained).
- Every returned order is checked before it is returned, so a wrong answer
  cannot leave the function:
  - it is topological in precedence mode;
  - it is re-measured by an independent `vertexSeparation(order)`;
  - it is **executed**, and its output must equal the output of the order the
    transformation gave.

## The view in the control app

- After the structure panel, a program panel draws the DAG with its steps placed
  left to right in the returned order. Under it, a register strip shows the
  values alive after each step, with the maximum (the width) and the floor (the
  unconstrained pathwidth) marked.
- A proof badge reads **proved**, **proved by bound**, or **upper bound**
  (budget). Upper bounds are never shown as the optimum.
- Beside it, the transformation's own order with its register count, so the
  saving is visible.
- `onStep` animates the descent (width k found, k − 1 refuted) for a slow,
  readable demonstration mode.

## Measurement

Each use has its own question and its own kill criterion. Run on the programs
the transformation produces for the ARC-AGI-1 evaluation set, and for the 50
ARC-AGI-3 frames labelled in Phase 2 of Form_Discovery's `PLAN_ARC_AGI_JS.md`.

- **The saving.** Registers of the optimal order against four baselines:
  - the transformation's own order;
  - a topological greedy;
  - the best of 100 random topological orders;
  - Sethi–Ullman on the programs that are trees.

  Report the distribution of the saving, and how often the unconstrained floor
  already proves the optimum. **Kill** the precedence search if the greedy
  matches the optimum on nearly all programs. Then the greedy plus the floor is
  the product.
- **Width as a prior.** Among candidate programs for one task, do the correct
  ones (those that map every train input to its output) have lower width than
  the incorrect ones? If so, width is a simplicity prior a program search can
  use. **Kill** if correct and incorrect programs are not separated on held-out
  tasks.
- **Correctness.** The execution check passes on every program scheduled, with
  zero exceptions. This is a gate, not a statistic.
- **Cost.** Wall time per call in the browser, in nodes and milliseconds, by
  program size. The target is under 50 ms for a program of at most 32 nodes,
  with a stated budget for larger ones. Report the share of calls that end on
  budget.
- **Width as a feature.** Report whether the program's width separates the forms
  `discoverStructure` confuses, chain against tree in particular. This is the
  cheapest possible payoff, and it is measured even if every kill above fires.

## Dependencies and order of work

- Form_Discovery's `PLAN_ARC_AGI_JS.md` Phases 1–2 (core and calibration) come
  first. This plan needs a working `discoverStructure` and the labelled set. It
  also needs the definition of the Eric-Harry transformation.
- Its Phase 3 says "npm package", which conflicts with the 2026-10-02 edit
  ("never published anywhere"). This plan assumes the edit wins: the module is
  built and used locally, and the demo page loads it from a relative path.
- The order of work:
  - precedence mode in the Python solver here, with the rules off;
  - the brute-force check of each rule under precedence, and its proof in Lean;
  - the TypeScript port and its parity fixtures;
  - the execution check;
  - the view;
  - the measurements.

  The work in this repository runs under its own gate. Each Form_Discovery step
  is one Ralph loop item there, with its gate (`make test`) green.
- The two repositories stay separate. The fixtures are the only thing carried
  across from here. They are regenerated by the tool when `pathwidth_solver/`
  changes, with the reason recorded in Form_Discovery's `ANOMALIES.md`, as for
  any oracle change.

## Done when

- `scheduleProgram` runs from the control app in a Worker. It matches the Python
  solver node for node on the committed fixtures, in both modes. It labels every
  result with its proof kind, and every returned order passes the execution
  check.
- Every dominance rule that runs in precedence mode has a brute-force check and
  a Lean proof for that mode.
- The program panel and register strip show any ARC task's programs.
- The saving and the width prior each have a reported result, kept or killed by
  their criterion, with the size range they cover stated.
