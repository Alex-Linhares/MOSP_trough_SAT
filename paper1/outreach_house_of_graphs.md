# Email to House of Graphs (draft, 2026-10-18)

Send after the arXiv preprint is out; then add its link beside the GitHub one. The
repository is public (checked 2026-10-18).
To: Jan Goedgebeur <jan.goedgebeur@kuleuven.be>
Cc: Kris Coolsaet <kris.coolsaet@ugent.be>, Sven D'hondt <dhondtsven36@gmail.com>,
Gauvain Devillez <gauvain.devillez@umons.ac.be>

---

**Subject:** Pathwidth as a House of Graphs invariant: a program and values for all 29,995 graphs

Dear Professor Goedgebeur,

Your 2022 paper on House of Graphs 2.0 invites readers with well-tested
programs for invariants the database does not yet hold to get in touch.
I'm writing to offer one for **pathwidth**, which House of Graphs doesn't
currently list.

Horacio Hideki Yanasse and I have been working on exact pathwidth, starting from
its equivalence with the minimization of open stacks problem. Our preprint, *The
pathwidth complex*, is on GitHub at
https://github.com/Alex-Linhares/MOSP_trough_SAT/blob/main/paper1/latex/main.pdf. Its solver corrects two dominance rules
of Chu and Stuckey's published search, which turned out to be unsound, and adds a
lower bound from contraction minors. The key theorems are proved in Lean 4,
in https://github.com/Alex-Linhares/MOSP_trough_SAT/tree/main/lean/MOSPFormalization;
none of these files contains a `sorry`:

- open stacks = pathwidth + 1: `MOSPGraph.lean`;
- the contraction-minor lower bound: `Minor.lean`;
- the counterexample to the published definite move, and the corrected rule:
  `Search/DefiniteMove.lean`;
- the instance on which the previous algorithm reports a wrong optimum:
  `Search/WrongOptimum.lean`;
- pathwidth of grids, which settles the 50 VSPLIB grid instances: `Grid.lean`.

To see whether it would be useful to you, we ran it on every graph in House of
Graphs, at your 5-minute limit per graph:

- **pathwidth proved on 26,432 of the 29,995 graphs**, and a witness layout
  (an upper bound we check by recomputing its vertex separation) for every one;
- **on 1,948 of the 5,506 graphs with no stored treewidth** (mostly timeouts),
  pathwidth is proved;
- our value is never below your stored treewidth, as it must not be, and it
  exceeds it on 9,221 of the 24,489 graphs that have one.

A second pass on the remaining 3,563 is running.

The program is a single C file with no dependencies beyond libc. It reads
graph6 and prints the pathwidth, how it was proved (an exhausted search, a
matching lower bound, or a refuted minor), and optionally the layout:
https://github.com/Alex-Linhares/MOSP_trough_SAT/tree/main/pathwidth_solver/cli. We'd be glad to adapt it to however your invariant
computers are called. We can also send our values and layouts as a
cross-check for your server's own computation.

Would you be interested in adding pathwidth to House of Graphs?

With best regards,

Alexandre Linhares
ORCID 0000-0002-4227-6879
