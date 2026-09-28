# Machine learning and measurement — to do

*Started 2026-09-28. Ideas that came up in discussion and are not yet an item
in any loop. Each entry names where the idea comes from (a findings section
`§n` of `reports/ml_nature.md`, or "conversation"), what would settle it, and
a rough cost. Nothing here is started. The synthesis's open-questions list
(`reports/ml_nature_summary.md` §10) is the longer, priced list; this file is
the short one for the next plan. The rules still apply: a prediction is never
a bound; no solver default changes without a paired measurement in nodes;
every claim states its size range.*

## Solver ideas from the min-fill observation (conversation, 2026-09-28)

- [ ] **Min-fill ordering as a layout: a new upper-bound heuristic with a
      witness.** Read the min-fill elimination ordering of the MOSP graph as a
      linear layout of the customers; its vertex separation is a valid upper
      bound on pathwidth, and the proof's construction (`MOSPGraph.lean`,
      bags = open customers; or order patterns by a bag containing their
      clique) turns it into a production order that achieves it. Measure it as
      a strategy in `satisfiability/heuristics.py` against `mcn`, the two-key
      rule, `cs-dfs` and `rule+cs-dfs`, over the corpus, grouped by file ∪
      class. §4 measured the bandwidth-of-RCM analogue (weak, MAE 1.9); this
      one is unmeasured, and `tw_min_fill + 1` tracks the optimum closely
      (§4), so it is a cheap experiment. *Cost: one session.*
- [ ] **Exact treewidth + 1 as a `_lower_bound` component.** A theorem
      (`treewidth_add_one_le_mospValue`, §39). §24 measured the floor rising on
      933 corpus instances and 67 gap instances becoming bound-certified, at
      0.2–1 s per instance. What decides it: a descent timing over the 25
      hardest instances, as `reports/expansion_bound.md` §6 did — a floor
      shortens a descent only where it equals the optimum. Blocked where
      `pw > tw` (about half the gap instances, §21). *Cost: one session.*
- [ ] **Min-fill + 1 as the descent's starting `k`.** Safe, because both
      answers are verified; the gain is bounded to the satisfiable calls above
      the optimum, which are under 5% of a descent (§18, §19). Measure the
      saving in nodes and seconds on the corpus at 41–100 before deciding it
      is worth a line of code. *Cost: half a session.*
- [ ] **Replace `customer_inter/reduction.py`'s ordering heuristic with the
      proof's construction.** The current "sort patterns by earliest/latest
      customer position" need not realise the optimum from an optimal layout;
      ordering patterns by a bag of the path decomposition containing their
      clique does, by theorem. Then `pathwidth_to_mosp` becomes exact and the
      old "customer graph overcounts" table entries can be regenerated
      (`CLAUDE.md`, corrected 2026-09-27). *Cost: one session.*

## Proposed in the findings and waiting for a decision (§28–§40)

- [x] *(done 2026-09-28)* `rule+cs-dfs` as the upper-bound strategy wherever `cs-dfs` is used
      (§28: 780 better / 12 worse over `cs-dfs`, 57% of its time). Owner's
      default change. *Cost: minutes, plus a corpus re-sweep.*
- [ ] The `bm-first` rule composition: 15% cheaper in nodes at 41–100, 2%
      dearer below; tune (move the citation check out of the subset loop) and
      re-measure in seconds on the two day-long 125 × 125 classes (§31).
- [ ] A C emitter for the search certificate (§32), and certificates for the
      eight `Random-100-100-2/4` instances the differential harness cannot
      afford (§33). *Cost: two sessions; the eight instances need hours each.*
- [ ] Satisfiable-side speed-ups that never pay on refutations: degree fan
      order in `ratchet` and the `k ≥ optimum` calls of a descent (§20, −35%
      witness nodes at 75), a relabelling portfolio on witness searches (§18,
      §33: 8–13× where hard, 6% of a refutation). Paired in nodes.
- [ ] Re-certify the withdrawn 125 × 125 entries on the fixed C: §35 prices
      a pre-fix ridge refutation at a median of 55 h on one core, ×/÷ 10 per
      instance, and post-fix at ≥ 2.3× (100 cell) to ~20× (the one ridge
      instance measured). Decide first what to record for the entries
      re-certified on the pre-fix library.
- [ ] Pre-encoding re-cover for SAT: the greedy cover cuts CaDiCaL's
      conflicts to 0.77 of the base's at the median (§30). Measure as a
      preprocessing step in `decide_mosp`, never touching the search.

## The open problems (unpriced)

- [ ] **A pathwidth lower bound that sees separators of trees of cliques.**
      Degree, clique and treewidth bounds are provably blocked on about half
      the gap instances (§6, §21); no formula over thirty invariants (§24) and
      no branching-aware bound at any separator the clique structure exposes
      (§38) beats `max(lb_best, tw + 1)`; the expansion bound is the only one
      on record that passes the treewidth ceiling. The harness
      (`learning/bound_harness.py`) takes any candidate as a function.
- [ ] **Why the reachable region of the closed-set lattice peaks at excess ≈ 2**
      (§36): the count of closed sets reachable through fitting steps equals
      the node count; a derivation of its peak in the generator's parameters
      would be the ridge's theory.
- [ ] **Lean**: move `pathGraph_isTree` and `pathGraph_induce_interval_connected`
      to `ForMathlib/`; the component-form corollaries of the branch lemma;
      the encoding's correctness (`encode_mosp_decision` satisfiable iff
      MOSP ≤ k), which would make §17's DRAT proofs end-to-end certificates.
      The one remaining `sorry` is the §24 conjecture and stays a statement.

## Literature and bibliography

- [ ] Read the full Möhring (1990) chapter (35 pp., in `literature/` since
      2026-09-27) and record in `literature/MISSING.md` what it settles for
      Table 1's gate matrix layout and PLA folding entries.
- [ ] Kashiwabara & Fujisawa (1979), the last Table 1 reference not held.
- [ ] Trace citations with OpenAlex and Semantic Scholar (both answer per DOI;
      Google Scholar blocks clients) for Kinnersley 1992, Yanasse 1997a and
      Chu & Stuckey 2009, and file the relevant citers under `paper2/`. The
      Kinnersley list already surfaced pathwidth SAT encodings (2017), exact
      pathwidth branch-and-bound (2014), and VNS for vertex separation (2012)
      that this project has never compared against.
- [ ] Bodlaender, Koster & Wolle (2006) and the drat-trim paper are cited in
      `reports/latex/references.bib` from standard references; obtain and
      file them.

## Paper (`reports/latex/`)

- [ ] Decide whether the body, not only a footnote, should carry the caveat
      that some 125 × 125 optimality claims rest on refutations made under
      the pre-fix rule.
- [ ] Add the popularity measurement (`paper2/popularity.md`) as a short
      section on where the problem lives in the literature.
- [ ] Re-attach the rebuilt PDF to the existing Zotero item (key QN7U6UDH)
      rather than creating a new one; the connector's `saveAttachment` needs
      the item's session, so create a named session and item id first.
