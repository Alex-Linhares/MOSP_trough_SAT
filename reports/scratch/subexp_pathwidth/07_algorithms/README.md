# loop0014 item 07 — new exact algorithms by exact linear transformation

Report: `reports/subexp_pathwidth.md` §7. Code: `learning/subexp_algorithms.py`,
tests `tests/test_subexp_algorithms.py`.

- `check_atlas7.log`, `check.json`: the full check (every atlas graph to 7
  vertices, generated cobipartite / starlike graphs, random matrices).
  Regenerate: `nice -n 19 python3 -m learning.subexp_algorithms --nmax 7 > check_atlas7.log` (91 s).
- `gustedt.txt`, `kitsunai.txt`, `bentert.txt` (git-ignored, regenerable):
  `pdftotext -layout` of the held PDFs
  `literature/1993-Gustedt-Pathwidth-Chordal-Graphs-DAM.pdf`,
  `literature/2016-Kitsunai-...-Algorithmica.pdf`,
  `literature/2025-Exponential-Time-Approximation-Schemes-Vertex-Ordering-ITCS.pdf`.
- `refuter.md`: the refuter subagent's reading of §7.1's proofs (one subagent, the only one used).
- `gate.log`: the gate run.
